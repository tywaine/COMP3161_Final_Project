FROM python:3.12-slim

WORKDIR /app/backend

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 5000

CMD sh -c "gunicorn --bind 0.0.0.0:${PORT:-5000} run:app"