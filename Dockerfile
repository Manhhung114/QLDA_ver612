FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=10000 \
    QLDA_DB_PATH=/var/data/qlda_cloud.db

RUN apt-get update && apt-get install -y --no-install-recommends \
      default-jre-headless \
      curl \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --prefer-binary -r requirements.txt

COPY . /app
RUN mkdir -p /var/data && chmod 0777 /var/data

EXPOSE 10000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT:-10000}/_stcore/health" || exit 1

CMD ["/bin/sh", "-c", "streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-10000} --server.headless=true --browser.gatherUsageStats=false"]
