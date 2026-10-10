FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 依赖单独一层，改代码时不必重装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 数据库放在被挂载的数据卷里（docker-compose 把 ./data 挂到 /app/data）
RUN mkdir -p /app/data && \
    python -c "import app, app.config, app.fetcher, app.fulltext, app.scheduler, app.search, app.schema, app.security, app.urlsafety, app.web.routes"

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/healthz', timeout=3)"

CMD ["python", "main.py"]
