from __future__ import annotations

import os
import random
import re
import time
from datetime import date

from ai_service import (
    AIServiceError,
    GeminiProjectAssistant,
    OpenAIProjectAssistant,
    SYSTEM_INSTRUCTIONS,
    classify_gemini_error,
    gemini_error_to_service_error,
    openai_error_to_service_error,
)


# V6.21 WebOpt AI Fast Context
# Mục tiêu: giảm time-to-first-token. Chat chỉ gửi nhóm dữ liệu liên quan tới
# câu hỏi thay vì đóng gói toàn bộ tiến độ + hồ sơ + bản vẽ + chi phí + vật tư.

def _has_any(text: str, terms) -> bool:
    low = str(text or "").lower()
    return any(term in low for term in terms)


def _intent_flags(question: str) -> dict[str, bool]:
    q = str(question or "").lower()
    flags = {
        "schedule": _has_any(q, (
            "tiến độ", "chậm", "trễ", "delay", "schedule", "critical",
            "đường găng", "công việc", "gantt", "wbs", "kế hoạch",
        )),
        "documents": _has_any(q, (
            "rfi", "rfa", "ncr", "hồ sơ", "nghiệm thu", "biên bản",
            "ntcv", "ntvl", "kiểm định", "submittal",
        )),
        "drawings": _has_any(q, (
            "bản vẽ", "shopdrawing", "shop drawing", "drawing", "hoàn công",
            "as-built", "as built", "issued design",
        )),
        "cost": _has_any(q, (
            "chi phí", "boq", "thanh toán", "phát sinh", "variation", " vo ",
            "budget", "ngân sách", "hợp đồng", "giá trị", "giải ngân",
        )),
        "material": _has_any(q, (
            "vật tư", "thiết bị", "mua sắm", "procurement", "nhà cung cấp",
            "kho", "nhập kho", "xuất kho", "material",
        )),
        "legal": _has_any(q, (
            "qcvn", "tcvn", "quy chuẩn", "tiêu chuẩn", "nghị định", "thông tư",
            "luật", "pháp lý", "văn bản", "quy định",
        )),
    }
    if not any(flags.values()):
        flags["general"] = True
    else:
        flags["general"] = False
    return flags


def _fast_project_snapshot(self, project_id, question, status_date=None) -> str:
    """Tạo snapshot theo intent, nhỏ hơn nhiều so với ProjectContextBuilder.build()."""
    status_date = status_date or date.today()
    ctx = self.context
    flags = _intent_flags(question)

    with ctx.connect() as c:
        p = ctx._project(c, project_id)

        # Tiến độ là dữ liệu nền quan trọng nhất; luôn lấy thống kê nhưng chỉ
        # xuất danh sách task chi tiết khi câu hỏi liên quan hoặc câu hỏi chung.
        tasks, tstats = ctx._tasks(c, project_id, status_date)

        docs = []
        dstats = {"total": 0, "open": 0, "overdue": 0}
        if flags["documents"] or flags["general"]:
            docs, dstats = ctx._documents(c, project_id, status_date)

        drawings = []
        drstats = {"total": 0, "approved": 0, "pending": 0}
        if flags["drawings"] or flags["general"]:
            drawings, drstats = ctx._drawings(c, project_id)

        cm = {"budgets": [], "payments": [], "variations": [], "materials": [], "procurements": [], "inventory": []}
        if flags["cost"] or flags["material"]:
            cm = ctx._cost_and_material(c, project_id)

        legal = []
        if flags["legal"]:
            legal = ctx._legal(c, question, 12)

    lines = [
        "# SNAPSHOT DỰ ÁN RÚT GỌN",
        f"Ngày báo cáo: {status_date.isoformat()}",
        f"Dự án: {p.get('code','')} - {p.get('name','')}",
        f"Thời gian: {p.get('start_date','')} → {p.get('end_date','')}",
        (
            f"Tiến độ tổng: {tstats['total']} công việc | KH TB {tstats['avg_planned']}% | "
            f"TT TB {tstats['avg_actual']}% | hoàn thành {tstats['done']} | "
            f"đang trễ {tstats['delayed']} | critical {tstats['critical']}"
        ),
    ]

    if docs or flags["documents"]:
        lines.append(
            f"Hồ sơ: {dstats['total']} | đang mở {dstats['open']} | quá hạn {dstats['overdue']}"
        )
    if drawings or flags["drawings"]:
        lines.append(
            f"Bản vẽ: {drstats['total']} | chấp thuận {drstats['approved']} | còn lại {drstats['pending']}"
        )

    # Câu hỏi tiến độ: chỉ gửi top task rủi ro. Đây là đường chạy nhanh cho nút
    # "Đánh giá tiến độ" trên giao diện.
    if flags["schedule"] or flags["general"]:
        task_limit = 28 if flags["schedule"] else 14
        lines += ["", "## CÔNG VIỆC RỦI RO/ƯU TIÊN"]
        for r in tasks[:task_limit]:
            ref = f"[TASK:{r.get('source_task_id') or r.get('id')}/{r.get('wbs','')}]"
            lines.append(
                f"{ref} {r.get('name','')} | {r.get('start_date','')}→{r.get('end_date','')} | "
                f"KH {int(r.get('planned_progress') or 0)}% | TT {int(r.get('actual_progress') or 0)}% | "
                f"Δ {r.get('_delta',0)}% | trễ {r.get('_delay_days',0)} ngày | "
                f"critical={bool(r.get('critical'))} | slack={r.get('total_slack',0)} | risk={r.get('_risk_score',0)}"
            )

    if flags["documents"] or flags["general"]:
        doc_limit = 24 if flags["documents"] else 10
        if docs:
            lines += ["", "## HỒ SƠ CẦN CHÚ Ý"]
            for r in docs[:doc_limit]:
                ref = f"[DOC:{r.get('doc_type','')}/{r.get('code','')}]"
                lines.append(
                    f"{ref} {r.get('subject','')} | trạng thái={r.get('status','')} | "
                    f"ưu tiên={r.get('priority','')} | hạn={r.get('due_date','')} | "
                    f"quá hạn={r.get('_overdue_days',0)} ngày | WBS={r.get('related_wbs','')} | xử lý={r.get('assignee','')}"
                )

    if flags["drawings"] or flags["general"]:
        drawing_limit = 20 if flags["drawings"] else 8
        if drawings:
            lines += ["", "## BẢN VẼ CẦN CHÚ Ý"]
            for r in drawings[:drawing_limit]:
                ref = f"[DRAWING:{r.get('drawing_type','')}/{r.get('drawing_no','')}/REV-{r.get('revision','')}]"
                lines.append(
                    f"{ref} {r.get('title','')} | bộ môn={r.get('discipline','')} | "
                    f"trạng thái={r.get('status','')} | ngày nhận={r.get('received_date','')} | WBS={r.get('related_wbs','')}"
                )

    if flags["cost"]:
        lines += ["", "## CHI PHÍ / THANH TOÁN / PHÁT SINH"]
        bac = sum(float(r.get("budget_total") or 0) for r in cm["budgets"])
        paid = sum(float(r.get("paid_amount") or 0) for r in cm["payments"])
        vo = sum(float(r.get("approved_amount") or 0) for r in cm["variations"])
        lines.append(f"Tổng hợp: BAC={bac:,.0f} VND | đã thanh toán={paid:,.0f} VND | VO duyệt={vo:,.0f} VND")
        for r in cm["payments"][:20]:
            lines.append(
                f"[COST:PAY/{r.get('payment_code','')}] đợt={r.get('installment','')} | "
                f"đã trả={r.get('paid_amount',0)} | KH giải ngân={r.get('planned_disbursement_pct',0)}% | trạng thái={r.get('payment_status','')}"
            )
        for r in cm["variations"][:20]:
            lines.append(
                f"[COST:VO/{r.get('vo_code','')}] {r.get('description','')} | trình={r.get('proposed_amount',0)} | "
                f"duyệt={r.get('approved_amount',0)} | trạng thái={r.get('status','')}"
            )

    if flags["material"]:
        lines += ["", "## VẬT TƯ / MUA SẮM"]
        for r in cm["procurements"][:24]:
            lines.append(
                f"[PROC:{r.get('material_code','')}/{r.get('id')}] NCC={r.get('supplier','')} | "
                f"đặt hàng={r.get('order_date','')} | giao KH={r.get('planned_delivery_date','')} | "
                f"thực tế={r.get('actual_delivery_date','')} | trạng thái={r.get('status','')}"
            )
        for r in cm["inventory"][:20]:
            lines.append(
                f"[INV:{r.get('slip_code','')}] vật tư={r.get('material_code','')} | nhập={r.get('quantity_in',0)} | "
                f"xuất={r.get('quantity_out',0)} | trạng thái={r.get('material_status','')}"
            )

    if flags["legal"] and legal:
        lines += ["", "## VĂN BẢN / TIÊU CHUẨN LIÊN QUAN"]
        for r in legal[:12]:
            number = r.get("number", "") or str(r.get("id", ""))
            lines.append(
                f"[LEGAL:{number}] {r.get('category','')} {r.get('number','')} | {r.get('title','')} | lĩnh vực={r.get('field','')}"
            )

    return "\n".join(lines)


def _project_input_items(self, project_id, question, history=None, status_date=None):
    if not (question or "").strip():
        raise AIServiceError("Câu hỏi đang trống.")
    snapshot = _fast_project_snapshot(self, project_id, question, status_date)
    user_prompt = (
        f"Dữ liệu dự án hiện tại:\n\n{snapshot}\n\n"
        f"CÂU HỎI CỦA NGƯỜI DÙNG:\n{question.strip()}\n\n"
        "Trả lời trực tiếp, ưu tiên kết luận và hành động. Bám sát snapshot; nếu dùng số liệu "
        "hãy giữ mã [TASK:], [DOC:], [DRAWING:], [COST:], [PROC:] hoặc [LEGAL:] liên quan."
    )
    items = [{"role": "developer", "content": SYSTEM_INSTRUCTIONS}]
    # Giảm lịch sử từ 8 xuống 4 message gần nhất để giảm input token và TTFT.
    for m in list(history or [])[-4:]:
        role = m.get("role")
        content = (m.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            items.append({"role": role, "content": content})
    items.append({"role": "user", "content": user_prompt})
    return items


def _openai_stream(self, input_items, use_web=None):
    client = self._client()
    kwargs = dict(model=self.model, input=input_items, store=False)
    if self.settings.use_web if use_web is None else use_web:
        kwargs["tools"] = [{"type": "web_search"}]
    try:
        stream_method = getattr(client.responses, "stream", None)
        if callable(stream_method):
            emitted = False
            with stream_method(**kwargs) as stream:
                for event in stream:
                    if getattr(event, "type", "") == "response.output_text.delta":
                        delta = getattr(event, "delta", "") or ""
                        if delta:
                            emitted = True
                            yield str(delta)
                if not emitted:
                    try:
                        final_response = stream.get_final_response()
                        text = getattr(final_response, "output_text", "") or ""
                        if text:
                            yield text.strip()
                            return
                    except Exception:
                        pass
            if emitted:
                return

        text = self._respond(input_items, use_web=use_web)
        for part in re.findall(r"\S+\s*", text):
            yield part
    except AIServiceError:
        raise
    except Exception as exc:
        raise openai_error_to_service_error(exc) from exc


def _fast_gemini_models(self, client) -> list[str]:
    """Đường model nhanh: không gọi client.models.list() trừ khi các model nhanh đều lỗi."""
    configured = str(self.settings.model or os.environ.get("GEMINI_MODEL", "auto")).strip() or "auto"
    configured = self._normalize_model_name(configured)
    result = []
    if configured.lower() not in {"", "auto", "default"}:
        result.append(configured)
    else:
        fast_model = str(os.environ.get("GEMINI_FAST_MODEL", "gemini-2.5-flash-lite") or "").strip()
        for model in (
            fast_model,
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-3.1-flash-lite",
        ):
            model = self._normalize_model_name(model)
            if model and model not in result:
                result.append(model)
    return result[:3]


def _gemini_stream(self, input_items, use_web=None):
    client = self._client()
    emitted_any = False
    try:
        from google.genai import types

        system_parts = []
        contents = []
        for item in input_items:
            role = str(item.get("role") or "user")
            text = self._content_text(item.get("content"))
            if not text:
                continue
            if role in {"developer", "system"}:
                system_parts.append(text)
                continue
            gemini_role = "model" if role == "assistant" else "user"
            contents.append(types.Content(role=gemini_role, parts=[types.Part.from_text(text=text)]))
        if not contents:
            contents = [types.Content(role="user", parts=[types.Part.from_text(text="OK")])]

        tools = None
        if self.settings.use_web if use_web is None else use_web:
            tools = [types.Tool(google_search=types.GoogleSearch())]
        cfg = types.GenerateContentConfig(
            system_instruction="\n\n".join(system_parts) or SYSTEM_INSTRUCTIONS,
            tools=tools,
        )

        try:
            retry_attempts = max(1, min(3, int(os.environ.get("GEMINI_STREAM_RETRY_ATTEMPTS", "2"))))
        except Exception:
            retry_attempts = 2
        try:
            base_delay = max(0.15, min(2.0, float(os.environ.get("GEMINI_STREAM_RETRY_BASE_SECONDS", "0.35"))))
        except Exception:
            base_delay = 0.35

        models = _fast_gemini_models(self, client)
        last_exc = None
        tried = set()

        # Chỉ khi danh sách nhanh thất bại hoàn toàn mới dùng discovery API.
        discovery_added = False
        model_index = 0
        while model_index < len(models):
            model = models[model_index]
            model_index += 1
            if model in tried:
                continue
            tried.add(model)
            self._resolved_model = model

            for attempt in range(retry_attempts):
                emitted_this_attempt = False
                try:
                    stream = client.models.generate_content_stream(model=model, contents=contents, config=cfg)
                    for chunk in stream:
                        text = getattr(chunk, "text", "") or ""
                        if text:
                            emitted_this_attempt = True
                            emitted_any = True
                            yield str(text)
                    return
                except Exception as exc:
                    last_exc = exc
                    if emitted_this_attempt or emitted_any:
                        raise
                    info = classify_gemini_error(exc)
                    if info.code == "model_not_found":
                        break
                    if not self._is_transient_gemini_error(exc):
                        raise
                    if attempt < retry_attempts - 1:
                        delay = base_delay * (2**attempt) + random.uniform(0, base_delay * 0.2)
                        time.sleep(delay)
                        continue
                    break

            if model_index >= len(models) and not discovery_added:
                discovery_added = True
                try:
                    for candidate in self._fallback_model_sequence(client, refresh=False):
                        if candidate not in tried and candidate not in models:
                            models.append(candidate)
                        if len(models) >= 5:
                            break
                except Exception:
                    pass

        if last_exc is not None:
            raise last_exc
        raise AIServiceError(
            "Gemini không có model generateContent khả dụng cho API key hiện tại.",
            code="model_not_found",
        )
    except AIServiceError:
        raise
    except Exception as exc:
        raise gemini_error_to_service_error(exc) from exc
    finally:
        try:
            client.close()
        except Exception:
            pass


def _ask_project_stream(self, project_id, question, history=None, status_date=None, use_web=None):
    items = _project_input_items(self, project_id, question, history, status_date)
    if isinstance(self, GeminiProjectAssistant):
        yield from _gemini_stream(self, items, use_web=use_web)
    else:
        yield from _openai_stream(self, items, use_web=use_web)


def install_ai_streaming() -> None:
    """Add low-latency streaming chat to both AI providers without changing existing APIs."""
    if getattr(OpenAIProjectAssistant, "_v621_streaming_installed", False):
        return
    OpenAIProjectAssistant.ask_project_stream = _ask_project_stream
    GeminiProjectAssistant.ask_project_stream = _ask_project_stream
    OpenAIProjectAssistant._v621_streaming_installed = True
    GeminiProjectAssistant._v621_streaming_installed = True
