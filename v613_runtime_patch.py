from __future__ import annotations


def install_db_patch() -> None:
    """Install V6.14 atomic revision-resubmit behavior onto CloudDatabase."""
    from cloud_db import CloudDatabase, _now

    # Keep the V6.13 recovery helper for already-stuck records, but V6.14 no longer
    # relies on timestamp comparison for normal Save -> Resubmit behavior.
    if not hasattr(CloudDatabase, "repair_revision_resubmit_if_saved"):
        def repair_revision_resubmit_if_saved(
            self,
            project_id: int,
            record_kind: str,
            subtype: str,
            record_id: int,
            submitted_by: str = "",
            submitted_name: str = "",
        ) -> dict:
            kind = str(record_kind or "").strip().lower()
            if kind not in {"document", "drawing"}:
                return {"repaired": False, "reason": "unsupported_kind"}
            table = "documents" if kind == "document" else "drawings"
            with self.connect() as c:
                wf = c.execute(
                    "SELECT * FROM approval_workflows WHERE project_id=? AND record_kind=? AND subtype=? AND record_id=?",
                    (project_id, kind, subtype, record_id),
                ).fetchone()
                if not wf:
                    return {"repaired": False, "reason": "no_workflow"}
                if str(wf["current_stage"] or "") != "CONTRACTOR":
                    return {"repaired": False, "reason": "not_waiting_contractor", "current_stage": str(wf["current_stage"] or "")}
                row = c.execute(f"SELECT updated_at FROM {table} WHERE id=?", (record_id,)).fetchone()
                if not row:
                    return {"repaired": False, "reason": "record_missing"}
                record_updated = str(row["updated_at"] or "")
                workflow_updated = str(wf["updated_at"] or "")
                if not record_updated or record_updated <= workflow_updated:
                    return {
                        "repaired": False, "reason": "record_not_saved_after_return",
                        "record_updated_at": record_updated, "workflow_updated_at": workflow_updated,
                    }
                actor_email = str(submitted_by or wf["submitted_by"] or "").strip().lower()
                wid = self._resubmit_approval_workflow_in_connection(c, int(wf["id"]), actor_email, str(submitted_name or ""))
                repaired_wf = c.execute("SELECT * FROM approval_workflows WHERE id=?", (wid,)).fetchone()
                step = c.execute(
                    "SELECT * FROM approval_steps WHERE workflow_id=? AND stage_code=?",
                    (wid, repaired_wf["current_stage"]),
                ).fetchone()
                return {
                    "repaired": True, "workflow_id": wid,
                    "status": str(repaired_wf["overall_status"] or ""),
                    "current_stage": str(repaired_wf["current_stage"] or ""),
                    "revision_no": int(repaired_wf["revision_no"] or 0),
                    "next_email": str(step["approver_email"] or "") if step else "",
                    "next_name": str(step["approver_name"] or "") if step else "",
                }
        CloudDatabase.repair_revision_resubmit_if_saved = repair_revision_resubmit_if_saved

    if getattr(CloudDatabase, "_v614_atomic_revision_save", False):
        return

    def save_document(self, project_id: int, doc_type: str, data: dict, doc_id: int | None = None) -> int:
        fields = ["code","subject","discipline","contractor","issuer","assignee","issue_date","due_date","closed_date",
                  "status","priority","related_wbs","description","response","note","cost_impact","time_impact_days"]
        vals = [data.get(f, "") for f in fields]
        with self.connect() as c:
            if doc_id:
                c.execute(
                    f"UPDATE documents SET {','.join(f'{f}=?' for f in fields)},updated_at=? WHERE id=?",
                    vals + [_now(), doc_id],
                )
                # V6.14 HARD GUARANTEE: successful Save and resubmit are one DB transaction.
                wf = c.execute(
                    "SELECT * FROM approval_workflows WHERE project_id=? AND record_kind='document' AND subtype=? AND record_id=?",
                    (project_id, doc_type, doc_id),
                ).fetchone()
                if wf and str(wf["current_stage"] or "") == "CONTRACTOR":
                    self._resubmit_approval_workflow_in_connection(
                        c, int(wf["id"]), str(wf["submitted_by"] or ""), ""
                    )
                return doc_id
            cur = c.execute(
                f"INSERT INTO documents(project_id,doc_type,{','.join(fields)},created_at,updated_at) VALUES(?,?,{','.join('?' for _ in fields)},?,?)",
                [project_id, doc_type] + vals + [_now(), _now()],
            )
            return int(cur.lastrowid)

    def save_drawing(self, project_id: int, drawing_type: str, data: dict, drawing_id: int | None = None) -> int:
        fields = ["drawing_no","title","discipline","revision","issuer","receiver","received_date","issue_date","due_date",
                  "priority","description","status","related_wbs","reference_no","note"]
        vals = [data.get(f, "") for f in fields]
        with self.connect() as c:
            if drawing_id:
                c.execute(
                    f"UPDATE drawings SET {','.join(f'{f}=?' for f in fields)},updated_at=? WHERE id=?",
                    vals + [_now(), drawing_id],
                )
                wf = c.execute(
                    "SELECT * FROM approval_workflows WHERE project_id=? AND record_kind='drawing' AND subtype=? AND record_id=?",
                    (project_id, drawing_type, drawing_id),
                ).fetchone()
                if wf and str(wf["current_stage"] or "") == "CONTRACTOR":
                    self._resubmit_approval_workflow_in_connection(
                        c, int(wf["id"]), str(wf["submitted_by"] or ""), ""
                    )
                return drawing_id
            cur = c.execute(
                f"INSERT INTO drawings(project_id,drawing_type,{','.join(fields)},created_at,updated_at) VALUES(?,?,{','.join('?' for _ in fields)},?,?)",
                [project_id, drawing_type] + vals + [_now(), _now()],
            )
            return int(cur.lastrowid)

    CloudDatabase.save_document = save_document
    CloudDatabase.save_drawing = save_drawing
    CloudDatabase._v614_atomic_revision_save = True


def patch_streamlit_source(source: str) -> str:
    """Patch the validated V6.12 UI bundle into V6.14."""
    source = source.replace("Approval UI / Workflow engine: V6.12", "Approval UI / Workflow engine: V6.14")
    source = source.replace("Workflow engine: **V6.9**", "Workflow engine: **V6.14**")

    # Keep V6.13 recovery behavior for records that were already stuck before V6.14.
    needle = '''    wf = db.approval_workflow(pid, record_kind, subtype, record_id)\n    # V6.9: tất cả đầu mục đã bật phê duyệt online đều bắt buộc có file trình duyệt.\n'''
    insert = '''    wf = db.approval_workflow(pid, record_kind, subtype, record_id)\n\n    # V6.14 compatibility repair for records that were already stuck before deployment.\n    if wf and str(wf["current_stage"] or "") == "CONTRACTOR":\n        try:\n            repaired = db.repair_revision_resubmit_if_saved(\n                pid, record_kind, subtype, record_id,\n                submitted_by=str(wf["submitted_by"] or ""),\n                submitted_name=submitted_name_hint,\n            )\n            if repaired.get("repaired"):\n                next_label = APPROVAL_ROLE_LABELS.get(\n                    str(repaired.get("current_stage") or ""),\n                    str(repaired.get("current_stage") or ""),\n                )\n                st.success(f"🔄 Đã tự phục hồi lần trình lại và chuyển hồ sơ về {next_label} xử lý.")\n                st.rerun()\n        except Exception as exc:\n            st.warning(f"Chưa tự phục hồi được trạng thái trình lại: {exc}")\n        wf = db.approval_workflow(pid, record_kind, subtype, record_id)\n\n    # V6.14: tất cả đầu mục đã bật phê duyệt online đều bắt buộc có file trình duyệt.\n'''
    if needle not in source:
        raise RuntimeError("V6.14 patch failed: online approval anchor not found")
    source = source.replace(needle, insert, 1)

    # After atomic save, the workflow may already be advanced before this UI helper runs.
    # Mark the route as resubmitted so the confirmation message matches the real state.
    doc_needle = '''                    route = _ensure_approval_workflow_started(\n                        pid, "document", doc_type, int(doc_id), normalized_code, subject,\n                        submitted_email=str(identity.get("email") or ""),\n                        submitted_name=str(identity.get("name") or issuer or ""),\n                        current_identity=identity,\n                        notify=True,\n                    )\n                    st.session_state[pending_key] = doc_id\n'''
    doc_insert = '''                    route = _ensure_approval_workflow_started(\n                        pid, "document", doc_type, int(doc_id), normalized_code, subject,\n                        submitted_email=str(identity.get("email") or ""),\n                        submitted_name=str(identity.get("name") or issuer or ""),\n                        current_identity=identity,\n                        notify=True,\n                    )\n                    if is_revision_return:\n                        post_save_wf = db.approval_workflow(pid, "document", doc_type, int(doc_id))\n                        if post_save_wf and str(post_save_wf["current_stage"] or "") != "CONTRACTOR":\n                            route = {**route, "ok": True, "resubmitted": True,\n                                     "status": str(post_save_wf["overall_status"] or ""),\n                                     "current_stage": str(post_save_wf["current_stage"] or ""),\n                                     "revision_no": int(post_save_wf["revision_no"] or 0)}\n                    st.session_state[pending_key] = doc_id\n'''
    if doc_needle not in source:
        raise RuntimeError("V6.14 patch failed: document save anchor not found")
    source = source.replace(doc_needle, doc_insert, 1)

    drawing_needle = '''                    route = _ensure_approval_workflow_started(\n                        pid, "drawing", drawing_type, int(drawing_id), normalized_number, title,\n                        submitted_email=str(identity.get("email") or ""),\n                        submitted_name=str(identity.get("name") or submitter or ""),\n                        current_identity=identity,\n                        notify=True,\n                    )\n                    st.session_state[pending_key] = drawing_id\n'''
    drawing_insert = '''                    route = _ensure_approval_workflow_started(\n                        pid, "drawing", drawing_type, int(drawing_id), normalized_number, title,\n                        submitted_email=str(identity.get("email") or ""),\n                        submitted_name=str(identity.get("name") or submitter or ""),\n                        current_identity=identity,\n                        notify=True,\n                    )\n                    if is_revision_return:\n                        post_save_wf = db.approval_workflow(pid, "drawing", drawing_type, int(drawing_id))\n                        if post_save_wf and str(post_save_wf["current_stage"] or "") != "CONTRACTOR":\n                            route = {**route, "ok": True, "resubmitted": True,\n                                     "status": str(post_save_wf["overall_status"] or ""),\n                                     "current_stage": str(post_save_wf["current_stage"] or ""),\n                                     "revision_no": int(post_save_wf["revision_no"] or 0)}\n                    st.session_state[pending_key] = drawing_id\n'''
    if drawing_needle not in source:
        raise RuntimeError("V6.14 patch failed: drawing save anchor not found")
    source = source.replace(drawing_needle, drawing_insert, 1)

    source = source.replace(
        'latest_comment = str(revision_comments[-1]["comment"] or "").strip() if revision_comments else ""',
        'latest_comment = str(revision_comments[0]["comment"] or "").strip() if revision_comments else ""',
    )
    return source
