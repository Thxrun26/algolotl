# Algolotl — single-container deploy (backend serves the static frontend)
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY web ./web
ENV ALGO_ENVIRONMENT=production
EXPOSE 8000
# Data dir persists users+progress; mount a volume in prod.
ENV ALGO_DATA_DIR=/data
VOLUME ["/data"]
CMD ["python","-m","uvicorn","app.main:app","--app-dir","backend","--host","0.0.0.0","--port","8000"]
