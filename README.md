# Cafe-Manager: Система управления заказами в кафе

Cafe-Manager - это веб-приложение на Django, предназначене для управления заказами в кафе.  Приложение позволяет добавлять, просматривать, редактировать и удалять заказы, а также предоставляет API для взаимодействия с заказами.

## Функциональные возможности

*   **Добавление заказов:**  Создание новых заказов с указанием номера стола и списка блюд (с ценами).  Общая стоимость заказа рассчитывается автоматически.
*   **Просмотр заказов:** Отображение списка всех заказов с возможностью фильтрации по статусу, номеру стола и поиска по названиям блюд.  Также отображается общая выручка по оплаченным заказам.
*   **Редактирование заказов:**  Изменение номера стола, списка блюд и статуса заказа.
*   **Удаление заказов:**  Удаление заказов из системы.
*   **API:**  REST API для программного взаимодействия с заказами (создание, чтение, обновление, удаление).
*   **Расчет выручки:**  Отображение общей суммы заказов со статусом "Оплачено".
*   **Подробная фильтрация:** Фильтрация по статусу, номеру столика и сортировка.

## Технологический стек

*   **Python 3.8+**
*   **Django 4+**
*   **Django REST Framework**
*   **drf-spectacular** (для генерации документации API)
*   **SQLite** (база данных по умолчанию, для разработки)
*   **HTML/CSS** (Bootstrap, но стилизация минимальная)
*   **Unittest** (для тестирования)

## Структура проекта

Проект имеет стандартную структуру Django-приложения:

*   `cafe`:  Основной проект Django.  Содержит настройки проекта (`settings.py`) и глобальные URL-маршруты (`urls.py`).
*   `orders`:  Django-приложение, содержащее всю логику, связанную с заказами.
    *   `models.py`:  Определение модели `Order`.
    *   `views.py`:  Представления (views) для обработки запросов, связанных с заказами (CRUD + API).
    *   `forms.py`:  Django-формы для создания и редактирования заказов, а также форма фильтрации.
    *   `urls.py`:  URL-маршруты приложения `orders`.
    *   `serializers.py`: Сериализаторы Django REST Framework для преобразования данных модели `Order` в JSON и обратно.
    *   `templates/orders/`:  HTML-шаблоны для отображения страниц приложения.
    *   `admin.py`: Регистрация модели в админ-панели Django.
    *   `tests.py`: Юнит-тесты.

## Установка и запуск

1.  **Клонирование репозитория:**

    ```bash
    git clone <ссылка на репозиторий>
    cd <папка проекта>
    ```

2.  **Создание и активация виртуального окружения (рекомендуется):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    venv\Scripts\activate  # Для Windows
    ```

3.  **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Применение миграций:**

    ```bash
    python manage.py migrate
    ```

5.  **Создание суперпользователя Django (для доступа к админ-панели):**

    ```bash
    python manage.py createsuperuser
    ```
    Следуйте инструкциям, чтобы ввести имя пользователя, email и пароль.

6.  **Запуск сервера разработки:**

    ```bash
    python manage.py runserver
    ```

7.  **Доступ к приложению:**

    *   **Веб-интерфейс:**  Откройте браузер и перейдите по адресу `http://127.0.0.1:8000/`.
    *   **API:**  Доступ к API осуществляется по адресу `http://127.0.0.1:8000/api/orders/`.  Документация API доступна по адресам:
        *   Swagger UI: `http://127.0.0.1:8000/api/docs/`
        *   Redoc: `http://127.0.0.1:8000/api/redoc/`
    * **Админ-панель:** Доступна по адресу `http://127.0.0.1:8000/admin/`. Используйте учетные данные суперпользователя, созданные ранее.

## API

Приложение предоставляет REST API для работы с заказами.

*   **GET `/api/orders/`:**  Получить список всех заказов (с возможностью фильтрации и поиска).
*   **POST `/api/orders/`:**  Создать новый заказ.
*   **GET `/api/orders/{id}/`:**  Получить информацию о заказе с указанным ID.
*   **PUT `/api/orders/{id}/`:**  Полностью обновить заказ с указанным ID.
*   **PATCH `/api/orders/{id}/`:**  Частично обновить заказ с указанным ID.
*   **DELETE `/api/orders/{id}/`:**  Удалить заказ с указанным ID.

Для фильтрации и поиска при GET-запросах к `/api/orders/` можно использовать следующие параметры:

*   `status`:  Фильтрация по статусу заказа (pending, ready, paid).
*   `table_number`: Фильтрация по номеру стола.
*    `search`: Полнотекстовый поиск в списке блюд.
*   `ordering`: Сортировка (total_price, created_at).

Пример запроса на создание заказа (POST `/api/orders/`):

```json
{
    "table_number": 5,
    "items": [
        {"name": "Cappuccino", "price": "3.50"},
        {"name": "Croissant", "price": "2.00"}
    ],
    "total_price": "5.50",
    "status": "pending"
}
```
Пример запроса на получение списка заказов, отфильтрованного по статусу "pending" и отсортированного по общей стоимости по возрастанию:

```
/api/orders/?status=pending&ordering=total_price
```

## Тестирование

В проекте реализованы юнит-тесты, покрывающие основные функции приложения (CRUD операции, парсинг входных данных, работа сериализатора, формы, модели).  Для запуска тестов выполните команду:

```bash
python manage.py test orders
```

## Обработка ошибок

Приложение обрабатывает различные типы ошибок:

*   **400 Bad Request:**  Возвращается при некорректных входных данных (например, при создании заказа с неправильным форматом списка блюд или при редактировании заказа).
*   **404 Not Found:**  Возвращается, если заказ с указанным ID не найден (при редактировании, удалении или просмотре).
*   **500 Internal Server Error:** Возвращается при возникновении внутренних ошибок сервера. Подробности ошибки выводятся в консоль.

## Дополнительно

*   В формах реализована валидация вводимых данных.
*   Используется `Decimal` для точного представления цен.
*   Код подробно документирован (комментарии, docstrings).
*   Использованы принципы ООП (модель `Order`, сериализатор `OrderSerializer`, формы).

## Сложности

Самой трудной частью оказались юнит-тесты.  Потребовалось значительное время, чтобы разобраться с мокированием (mocking) зависимостей, корректной настройкой тестовой среды и написанием тестов, покрывающих различные сценарии использования и обработки ошибок.  Особенно непросто было тестировать взаимодействие с базой данных и проверять правильность формирования HTTP-ответов.
