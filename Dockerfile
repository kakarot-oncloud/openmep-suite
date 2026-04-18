FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY streamlit_app/ ./streamlit_app/

# Create a non-root user — containers should never run as root in production.
# docker-compose.yml overrides CMD per service; this default runs the API only.
RUN groupadd -r appuser && useradd -r -g appuser appuser --home-dir /app \
    && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000 8501

# Default: runs the API service only.
# docker-compose.yml overrides this CMD per service — the 'streamlit' service
# replaces it with: streamlit run streamlit_app/app.py ...
# Never use "sh -c '... & ...'" — Docker cannot monitor or restart individual processes.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
