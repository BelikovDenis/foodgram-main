

Foodgram - «Продуктовый помощник»
Описание проекта

Foodgram - это веб-приложение для публикации рецептов. Пользователи могут:

    Создавать и публиковать собственные рецепты

    Просматривать рецепты других пользователей

    Подписываться на авторов

    Добавлять рецепты в избранное и список покупок

    Скачивать список ингредиентов для покупок

Демо-версия доступна по адресу: https://foodgram-belikov.servequake.com
Технологии

    Backend:

        Python 3.13

        Django 5.0.6

        Django REST Framework

        Djoser (аутентификация)

        PostgreSQL

        Gunicorn

        Nginx

    Frontend:

        React

        Redux Toolkit

        Material-UI

    Инфраструктура:

        Docker

        Docker Compose

        CI/CD (GitHub Actions)

Установка и запуск (для разработки)
Требования

    Docker

    Docker Compose

Инструкция

    Клонируйте репозиторий:

bash

git clone https://github.com/BelikovDenis/foodgram-main.git
cd foodgram-project-react

    Создайте файл .env в папке infra/ с переменными окружения:

env

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=foodgram-belikov.servequake.com

    Запустите контейнеры:

bash

docker-compose -f docker-compose.yml up -d --build

    Выполните миграции:

bash

docker-compose exec backend python manage.py migrate

    Соберите статику:

bash

docker-compose exec backend python manage.py collectstatic --no-input

    Создайте суперпользователя:

bash

docker-compose exec backend python manage.py createsuperuser

    Загрузите тестовые данные (опционально):

bash

docker-compose exec backend python manage.py loaddata fixtures.json

API Endpoints

Основные доступные endpoints:

    GET /api/recipes/ - список рецептов

    GET /api/recipes/{id}/ - детали рецепта

    POST /api/recipes/ - создание рецепта

    GET /api/tags/ - список тегов

    GET /api/ingredients/ - список ингредиентов

    POST /api/auth/token/login/ - получение токена

    GET /api/users/me/ - профиль текущего пользователя

Полная документация API доступна после запуска проекта по адресу /api/docs/
Администрирование

Админ-панель доступна по адресу: https://foodgram-belikov.servequake.com/admin

Возможности:

    Управление пользователями

    Модерация рецептов

    Управление тегами и ингредиентами

    Просмотр статистики

Развертывание на production

    Настройте сервер с Docker

    Скопируйте файлы docker-compose.production.yml и .env.production

    Запустите:

bash

docker-compose -f docker-compose.production.yml up -d --build

Лицензия

Отсутствует, берите кому надо, буду только рад.