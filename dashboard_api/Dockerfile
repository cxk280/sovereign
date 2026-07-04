FROM python:3.11-slim

WORKDIR /app

# Install the project with dashboard extras. The API imports gateway.registry and
# reads gateway/registry.yaml + sample_data/, so those are copied in too.
COPY pyproject.toml uv.lock README.md ./
COPY sovereign ./sovereign
COPY gateway ./gateway
COPY dashboard_api ./dashboard_api
COPY sample_data ./sample_data
RUN pip install --no-cache-dir uv && uv pip install --system ".[dashboard]"

EXPOSE 8090
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8090/healthz').status==200 else 1)"

CMD ["uvicorn", "dashboard_api.app:app_factory", "--factory", "--host", "0.0.0.0", "--port", "8090"]
