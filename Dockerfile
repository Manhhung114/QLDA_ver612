FROM python:3.12-slim AS webopt-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /src
COPY build_v621_webopt.py ./
COPY v621_webopt_source ./v621_webopt_source
RUN python build_v621_webopt.py \
    && python -m py_compile dist/streamlit_app.py


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    MALLOC_ARENA_MAX=2 \
    PORT=10000 \
    QLDA_DB_PATH=/var/data/qlda_cloud.db

RUN apt-get update && apt-get install -y --no-install-recommends \
      default-jre-headless \
      curl \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --prefer-binary -r requirements.txt

# Final Railway image contains only the generated WebOpt app and runtime modules.
# Build source parts stay in the builder stage and are not copied into runtime.
COPY --from=webopt-builder /src/dist/streamlit_app.py ./streamlit_app.py
COPY cloud_db.py drive_gateway.py mpp_cloud_reader.py legal_documents.py settings_store.py ai_service.py legal_cache.json ./
COPY v615_runtime_patch.py v621_webopt_runtime.py ./
COPY .streamlit/config.toml ./.streamlit/config.toml

RUN python -m compileall -q /app \
    && mkdir -p /var/data \
    && chmod 0777 /var/data

EXPOSE 10000
HEALTHCHECK --interval=60s --timeout=8s --start-period=25s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT:-10000}/_stcore/health" || exit 1

CMD ["/bin/sh", "-c", "streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-10000} --server.headless=true --server.fileWatcherType=none --browser.gatherUsageStats=false"]
