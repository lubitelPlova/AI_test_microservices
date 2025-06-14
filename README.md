### Описание проекта
Вообще это не цельный проект, а композиция микросервисов, которые я делал в рамках других проектов.
То, что получилось - это, своего рода, платформа для закрепления материалов при обучении, в которую прикручено две AI фичи: оцифровка текста и генерация теста ллмкой. 
#### Фронтенд: 
nginx веб-сервер + SPA на чистом html, JS, т.к. я вообще не умею во фронт. 
#### Бэкенд: 
##### ***main-service***
Выполняет функции авторизации через JWT и работы с бд тестов (sqlachemy, alembic, sqlite) (должен быть разделен на два микросервиса: авторизация и дата сервис).
##### ***ocr-service*** 
Оцифровка текста с разных источников (YOLOv8 + OpenCV + EasyOCR), качество оцифровки кривовато.
##### ***llm-service***
Доступ к LLM (Qwen2.5-72B-instruct) через API hf-hub. Генерация тестов и оценка тестов происходит за счет системного промпта с инструкциями + промпта с текстом. JSON который отдает LLM валидируется через pydantic. 
### Запуск
Запуск через docker compose. Находясь в корневой папке проекта, необходимо выполнить. 
``` docker
docker compose up --build
```
### Порты
Сам сайт находится на ***localhost:80***. 
Микросервисы: 
```
main_microservice - localhost:8000
ocr_microservice - localhost:8001
llm_microservice - localhost:8002
```
Документация API находится на /docs 

### Примеры работы
#### Экран авторизации
![image](https://github.com/user-attachments/assets/ce317b46-fd3f-4309-a2c0-ac1e3b7aa8d3)

#### Генерация тестов
![image](https://github.com/user-attachments/assets/983a403f-a565-4603-97df-8d339801f054)

#### Конструктов тестов
![image](https://github.com/user-attachments/assets/eec4724e-5d2e-41ef-8375-95f447d34d54)

#### Список тестов
![image](https://github.com/user-attachments/assets/d3f2f819-89d9-49e4-a4a1-547859c03058)


#### Прохождение тестов
![image](https://github.com/user-attachments/assets/1f51515c-7dc3-450f-bde6-ca5173597148)

#### Пример работы OCR
Исходник
![image2](https://github.com/user-attachments/assets/646a6b9c-d709-48cd-b6a0-c75051d8c2ba)

Результат
![image](https://github.com/user-attachments/assets/19443eec-904a-424a-985c-1ffdf478f58e)

