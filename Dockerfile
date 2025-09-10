# Берём официальный образ Python
FROM python:3.13-slim

# Делаем директорию внутри контейнера
WORKDIR /site_response_bot

# Скопируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Запускаем бота
CMD alembic upgrade head && python app/main.py
