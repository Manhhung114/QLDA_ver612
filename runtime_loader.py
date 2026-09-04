from __future__ import annotations

import gzip
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def compiled_app(gzip_path: str, entry_path: str):
    """Decompress/compile the V6.21 WebOpt source once per Railway process."""
    source = gzip.decompress(Path(gzip_path).read_bytes()).decode("utf-8")
    return compile(source, entry_path, "exec")
