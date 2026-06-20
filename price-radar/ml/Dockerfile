FROM python:3.10-slim

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код ML-скриптов
COPY ./app ./app

# Запускаем главный скрипт ML-модуля
CMD ["python", "app/main.py"]

