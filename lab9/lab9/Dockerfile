# Етап 1: встановлення залежностей
FROM python:3.11-slim AS builder
WORKDIR /app

# Встановлюємо системні пакети для компіляції залежностей
RUN apt-get update && apt-get install -y build-essential python3-dev wget && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Етап 2: production
FROM python:3.11-slim
WORKDIR /app

# Копіюємо пакети з builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Створюємо директорію для бази
RUN mkdir -p /app/data && chmod 755 /app/data

# Копіюємо код
COPY . .

# Змінні середовища
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATABASE_PATH=/app/data/database.db

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5000/ || exit 1

# Запуск Flask‑додатку
CMD ["python", "app.py"]
