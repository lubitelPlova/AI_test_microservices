# Используем официальный легковесный образ Nginx
FROM nginx:1.25-alpine

# Удаляем дефолтный конфиг Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копируем статические файлы фронтенда
COPY ./ /usr/share/nginx/html/

# Копируем наш кастомный конфиг Nginx
COPY ./nginx.conf /etc/nginx/conf.d/

# Права для Nginx (важно для Alpine)
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Опционально: для SPA с роутингом создаем fallback index.html
RUN echo 'Fallback HTML' > /usr/share/nginx/html/40x.html && \
    echo 'Fallback HTML' > /usr/share/nginx/html/50x.html

# Запускаем Nginx в foreground режиме
CMD ["nginx", "-g", "daemon off;"]