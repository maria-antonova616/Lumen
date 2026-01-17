# LUMEN | Gallery Management System

![Status](https://img.shields.io/badge/Status-Production-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-5.0-green?style=for-the-badge)

**Lumen** — профессиональный SaaS-сервис для фотографов, автоматизирующий процесс отбора и согласования фотографий с клиентами.

**Ссылка на рабочий проект:** [https://mariaantonova616.pythonanywhere.com/](https://mariaantonova616.pythonanywhere.com/)  

---

## Возможности

### Для фотографа:
*   **Smart Upload:** Массовая загрузка сотен фото с автоматическим созданием превью.
*   **Гибкий доступ:** Настройка публичных/приватных галерей, генерация UUID-ссылок с лимитом активаций.
*   **Контроль:** Установка жестких лимитов на выбор (например, "клиент может выбрать ровно 15 фото").
*   **Live Analytics:** Интерактивные графики (Chart.js), показывающие динамику просмотров и лайков.
*   **Обратная связь:** Просмотр комментариев клиентов к каждому кадру.

### Для клиента:
*   **Удобный отбор:** Интерфейс интрактивен и интуетивен.
*   **AJAX-взаимодействие:** Мгновенные лайки и комментарии без перезагрузки страницы.
*   **Мобильность:** Адаптация интерфейса под смартфоны.

---

## Технический стек

*   **Backend:** Python 3, Django 5 (CBV, Custom User Model, ORM Aggregations).
*   **Frontend:** Tailwind CSS, JavaScript (Fetch API), Chart.js.
*   **Database:** SQLite (разработка) / PostgreSQL (продакшн).
*   **Безопасность:** CSRF protection, разграничение прав (Mixins), валидация файлов.

---

## Локальный запуск

1.  **Клонирование репозитория:**
    ```bash
    git clone https://github.com/maria-antonova616/Lumen.git
    cd Lumen
    ```

2.  **Настройка окружения:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Установка зависимостей:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройка переменных окружения:**
    Создайте файл `.env` в корне проекта (рядом с `manage.py`) и добавьте:
    ```env
    SECRET_KEY=django-insecure-key-for-dev
    DEBUG=True
    ALLOWED_HOSTS=*
    ```

5.  **Миграции и создание админа:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

6.  **Запуск сервера:**
    ```bash
    python manage.py runserver
    ```

Проект доступен по адресу: `http://127.0.0.1:8000`

---

## Тестовые аккаунты

Для проверки функционала вы можете использовать (или создать) следующие роли:

*   **Фотограф:** `demo_photo` / `pass123`
*   **Клиент:** `demo_client` / `pass123`
