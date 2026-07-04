FROM python:3.11-slim

WORKDIR /app

# Install the project with gateway extras.
COPY pyproject.toml uv.lock README.md ./
COPY sovereign ./sovereign
COPY gateway ./gateway
RUN pip install --no-cache-dir uv && uv pip install --system ".[gateway]"

EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz').status==200 else 1)"

CMD ["uvicorn", "gateway.app:app_factory", "--factory", "--host", "0.0.0.0", "--port", "8080"]
