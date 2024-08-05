import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-_6ax+c$!1h8e@o8q0n1xv_!_a48%*g#39qxw-e02b_!jqtfmwe"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS =['127.0.0.1']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    'django.contrib.contenttypes',
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "stocks",
    "rest_framework",
    "portfolio",
    "webui",
    "webpack_loader",
    "drf_spectacular",
]

MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

ROOT_URLCONF = "urls"

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

WSGI_APPLICATION = "wsgi.application"
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bsedata.db'),
        },
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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,"static"),
    os.path.join(BASE_DIR,"portfolio/static/portfolio"),
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

PROJECT_DIRS = {
    'reports': os.path.join(BASE_DIR, "reports/"), 
    'cache'  : os.path.join(BASE_DIR, "runtime/cache"),
    'intraday': os.path.join(BASE_DIR, "intraday/"),
    'rrg'   :   os.path.join(BASE_DIR, "runtime/rrg"),
}

RRG_PROGRESS_FILE = os.path.join(PROJECT_DIRS.get('rrg'), ".progress.json")

WEBPACK_LOADER = {
  "DEFAULT": {
    "BUNDLE_DIR_NAME": "portfolio/",
    "CACHE": not DEBUG,
    "STATS_FILE": os.path.join(BASE_DIR, "portfolio/webpack-stats.json"),
    "POLL_INTERVAL": 0.1,
    "IGNORE": [r'.+\.hot-update.js', r'.+\.map'],
  }
}


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
