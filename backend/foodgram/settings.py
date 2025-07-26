import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

DEBUG = os.getenv("DEBUG", "True") == "True"

CSRF_TRUSTED_ORIGINS = [
    "https://final-foodgram.zapto.org",
    "http://final-foodgram.zapto.org",
]
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = [
    os.getenv("LOCAL_IP"),
    "localhost",
    "127.0.0.1",
    os.getenv("DOMAIN"),
    os.getenv("YANDEX_IP"),
    "0.0.0.0",
]


INSTALLED_APPS = [
    "user.apps.UserConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "djoser",
    "api.apps.ApiConfig",
    "recipes.apps.RecipesConfig",
]

AUTH_USER_MODEL = "user.CustomUser"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "PAGE_SIZE": 6,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

DJOSER = {
    "PERMISSIONS": {
        "user_list": ["rest_framework.permissions.AllowAny"],
        "user": ["rest_framework.permissions.AllowAny"],
        "token_destroy": ["rest_framework.permissions.IsAuthenticated"],
    },
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": False,
    "SERIALIZERS": {
        "user_create": "api.serializers.CustomUserCreateSerializer",
        "user": "api.serializers.CustomUserBaseSerializer",
        "current_user": "api.serializers.CustomUserWithRecipesSerializer",
    },
}

WSGI_APPLICATION = "foodgram.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", 5432),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "collected_static"

MEDIA_URL = "/media/"

MEDIA_ROOT = "/backend_media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SHORT_LINK_BASE_URL = os.environ.get(
    "SHORT_LINK_BASE_URL", "http://short.link/"
)
