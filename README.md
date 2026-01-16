# LUMEN | Gallery Management System

![Status](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)
![Stack](https://img.shields.io/badge/Django-5.0%20%7C%20Tailwind-black?style=for-the-badge)

**Lumen** — профессиональный сервис для фотографов, предназначенный для управления процессом отбора фотографий (Likedown). Забудьте о списках номеров файлов в мессенджерах — предоставьте клиенту удобный и красивый интерфейс.

---

## 🛠 Технологический стек

*   **Backend:** Python 3.13, Django 5.0 (ORM Aggregations, Custom Auth)
*   **Frontend:** Tailwind CSS (Custom Design), JavaScript (Fetch API, SortableJS)
*   **Database:** SQLite (Development) / PostgreSQL (Production ready)
*   **Analytics:** Chart.js + Django ORM

---

## 📸 Основные возможности

*   **Role-Based Access:** Четкое разделение на Фотографов и Клиентов.
*   **Smart Limits:** Установка персональных и общих лимитов на выбор фото.
*   **Live Analytics:** Визуализация активности клиентов через интерактивные графики.
*   **Mass Upload:** Быстрая загрузка сотен фотографий в один клик.

---

## 🚀 Запуск локально

1.  **Клонирование репозитория:**
    ```bash
    git clone https://github.com/maria-antonova616/Lumen.git
    cd Lumen
    ```

2.  **Настройка окружения:**
    ```bash
    py -3.13 -m venv venv
    # Windows:
    venv\Scripts\activate
    ```

3.  **Установка зависимостей:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Подготовка базы данных:**
    ```bash
    python manage.py migrate
    ```

5.  **Создание Администратора:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Запуск сервера:**
    ```bash
    python manage.py runserver
    ```
    Проект будет доступен по адресу: `http://127.0.0.1:8000`

---

## 📝 Учетные данные для демо (при деплое)

*   **Admin:** `admin` / `admin123`
*   **Photographer:** `demo_photo` / `pass123`
*   **Client:** `demo_client` / `pass123`
