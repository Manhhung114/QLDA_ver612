from __future__ import annotations

import base64
import gzip
import os
from functools import lru_cache
from pathlib import Path

# Keep the Railway WebOpt resource limits when running on Streamlit Community
# Cloud. These are set before pandas/numpy/BLAS are imported by the generated app.
for _name, _value in {
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "MALLOC_ARENA_MAX": "2",
}.items():
    os.environ.setdefault(_name, _value)

from build_v621_webopt import _finalize_source


# Streamlit Community Cloud entrypoint.
# Community Cloud clones the repository and runs this file directly. We rebuild
# the V6.21 WebOpt source entirely in memory, so no Docker build stage, Railway
# volume, or writable dist/ directory is required.
_ROOT = Path(__file__).resolve().parent
_PARTS_DIR = _ROOT / "v621_webopt_source"
_PARTS = tuple(sorted(_PARTS_DIR.glob("part_*.b64")))

if len(_PARTS) != 9:
    raise RuntimeError(
        f"QLDA V6.21 WebOpt source is incomplete: expected 9 parts, found {len(_PARTS)}."
    )

_SIGNATURE = tuple((p.name, p.stat().st_size, p.stat().st_mtime_ns) for p in _PARTS)


@lru_cache(maxsize=1)
def _compiled_community_cloud_app(signature):
    del signature  # cache key only; source is read from the repository files below.
    try:
        encoded = "".join(p.read_text(encoding="ascii").strip() for p in _PARTS)
        source = gzip.decompress(base64.b64decode(encoded)).decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"Invalid QLDA V6.21 WebOpt source bundle: {exc}") from exc

    source = _finalize_source(source)
    return compile(source, str(_ROOT / "streamlit_app_v621_webopt.py"), "exec")


exec(_compiled_community_cloud_app(_SIGNATURE), globals(), globals())
