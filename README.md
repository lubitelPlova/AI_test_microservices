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
