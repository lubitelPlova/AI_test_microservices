# Используем официальный образ Python с указанной версией
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \ 
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

EXPOSE 8000
# Команда для запуска приложения (укажите ваш основной файл)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
