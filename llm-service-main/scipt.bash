#!/bin/bash

# Проверяем наличие обоих аргументов
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Использование: $0 <расширение> <папка>"
    echo "Пример: $0 .txt ./docs"
    exit 1
fi

EXT="$1"
DIR="$2"

# Проверяем существование папки
if [ ! -d "$DIR" ]; then
    echo "Ошибка: Папка '$DIR' не существует"
    exit 1
fi

# Находим файлы рекурсивно в указанной папке
FILES=$(find "$DIR" -type f -name "*$EXT")

# Проверяем, найдены ли файлы
if [ -z "$FILES" ]; then
    echo "Файлов с расширением $EXT в папке $DIR не найдено"
    exit 1
fi

# Обрабатываем каждый файл
echo "$FILES" | while read -r file; do
    echo "{'file': '$file', 'content': \"$(cat "$file")\"}"
done