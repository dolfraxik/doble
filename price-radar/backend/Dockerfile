FROM python:3.10-slim

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бэкенда
COPY ./app ./app

# Открываем порт для FastAPI/Flask (8000)
EXPOSE 8000

# Команда для запуска (предполагаем FastAPI + uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
