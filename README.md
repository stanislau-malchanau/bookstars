# Bookstars

## Описание
SaaS platform that helps authors generate real, high-quality reviews for their low-content and non-fiction books on Amazon

## Требования
- Python 3.8+
- Django 4+
- PostgreSQL (рекомендуется)

## Установка

1.  Клонируйте репозиторий:
    ```bash
    git clone https://github.com/stanislau-malchanau/bookstars.git
    cd bookstars

2.  Создайте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows

3.  Установите зависимости:
    ```bash
    pip install -r requirements.txt

4.  Примените миграции:
    ```bash
    python manage.py migrate

5.  Создайте суперпользователя:
    ```bash
    python manage.py createsuperuser

6.  Запустите сервер:
    ```bash
    python manage.py runserver

7.  Откройте в браузере:
    ```bash
    http://127.0.0.1:8000

## Лицензия

MIT