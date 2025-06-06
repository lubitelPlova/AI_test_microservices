# Используем официальный образ Python с указанной версией
FROM python:3.12.9-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libsm6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-multipart

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска приложения (укажите ваш основной файл)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]