# Cafe Order System

Это веб-приложение на Django для управления заказами в кафе. Позволяет добавлять, удалять, искать, изменять и отображать заказы.

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ZoomL-Olymp/Cafe-Manager.git
   cd cafe
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Примените миграции и запустите сервер:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Структура проекта

- `cafe/` — корневая папка проекта
- `orders/` — приложение для работы с заказами
- `templates/` — HTML-шаблоны
- `static/` — статические файлы
- `requirements.txt` — зависимости
- `README.md` — документация
