from pathlib import Path

# QLDA V6.12 source loader.
# The complete Streamlit application is stored in v612_source/streamlit_app/*.pyfrag
# to keep the GitHub deployment files manageable while preserving the exact source.
_PART_DIR = Path(__file__).resolve().parent / "v612_source" / "streamlit_app"
_parts = sorted(_PART_DIR.glob("part_*.pyfrag"))
if not _parts:
    raise RuntimeError("QLDA V6.12 source bundle is incomplete: no streamlit_app parts found.")
_source = "".join(p.read_text(encoding="utf-8") for p in _parts)
exec(compile(_source, str(Path(__file__).resolve()), "exec"), globals(), globals())
