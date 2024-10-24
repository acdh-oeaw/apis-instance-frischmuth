"""
Django settings for apis_ontology project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import re
from pathlib import Path

import dj_database_url
from apis_acdhch_default_settings.settings import *


# General Django settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
DEV_VERSION = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "frischmuth-dev.acdh-dev.oeaw.ac.at",
]

ALLOWED_HOSTS = re.sub(
    r"https?://",
    "",
    os.environ.get("ALLOWED_HOSTS", ",".join(ALLOWED_HOSTS)),
).split(",")


# Add CORS headers to responses
# see https://github.com/adamchainz/django-cors-headers
INSTALLED_APPS += ["corsheaders", "apis_core.history"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/(\w|[-.])*frischmuth(\w|[-.])*\.oeaw\.ac\.at$",
    r"^http:\/\/localhost:\d{2,4}$",
    r"^http:\/\/127\.0\.0\.1:\d{2,4}$",
]
CORS_URLS_REGEX = r"^/(apis/)*api/.*$"


# Application definition

ROOT_URLCONF = "apis_ontology.urls"

WSGI_APPLICATION = "apis_ontology.wsgi.application"

# Custom Django logging
DJANGO_LOG_HANDLERS = ["apis_ontology.console"]

DJANGO_LOG_HANDLERS = os.getenv(
    "DJANGO_LOG_HANDLERS", ",".join(DJANGO_LOG_HANDLERS)
).split(",")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {name} {levelname}: {module}.{funcName}:{lineno} {message}",
            "style": "{",
            "datefmt": "%d/%b/%Y %H:%M:%S",  # replicates django.server format
        },
        "detailed": {
            "format": "[{asctime}] {name} {levelname}: {message}",
            "style": "{",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "concise": {
            "format": "[{asctime}] {levelname}: {message}",
            "style": "{",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "": {
            "class": "logging.NullHandler",
        },
        "apis_ontology.console": {
            "class": "logging.StreamHandler",
            "formatter": os.getenv("DJANGO_LOG_FORMATTER", "detailed"),
        },
        "imports.file": {
            "class": "logging.FileHandler",
            "filename": os.getenv("DJANGO_LOG_FILE", "imports.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "apis_ontology": {
            "handlers": ["apis_ontology.console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
        "apis_ontology.scripts": {
            "handlers": DJANGO_LOG_HANDLERS,  # defaults to apis_ontology.console
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "apis_ontology.management.commands": {
            "handlers": DJANGO_LOG_HANDLERS,
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# Django Allow CIDR
# see https://github.com/mozmeao/django-allow-cidr
# address '10.0.0.0/8' needs to be allowed for service health checks

ALLOWED_CIDR_NETS = ["10.0.0.0/8", "127.0.0.0/8"]

# Django REST framework permissions
# see https://www.django-rest-framework.org/api-guide/permissions/


REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    "rest_framework.permissions.IsAuthenticated",
)

# drf-spectacular
# see https://drf-spectacular.readthedocs.io/en/latest/settings.html

SPECTACULAR_SETTINGS["COMPONENT_SPLIT_REQUEST"] = True
SPECTACULAR_SETTINGS["COMPONENT_NO_READ_ONLY_REQUIRED"] = True
SPECTACULAR_SETTINGS["DEFAULT_GENERATOR_CLASS"] = (
    "apis_core.generic.generators.CustomSchemaGenerator"
)


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# Django-tables2 settings to override defaults
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5-responsive.html"

DJANGO_TABLES2_TABLE_ATTRS = {
    "class": "table table-hover table-striped",
    "thead": {
        "class": "table-light",
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization / Globalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
# https://docs.djangoproject.com/en/4.2/ref/settings/#globalization-i18n-l10n

LANGUAGE_CODE = "de"

TIME_ZONE = "CET"

USE_I18N = True

USE_TZ = True

# Date formats allowed in date fields in Django forms
# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
DATE_INPUT_FORMATS = [
    # %m, %d are zero-padded
    "%Y-%m-%d",  # 1996-02-29
    "%Y-%m",  # 2015-10
    "%Y",  # 1999
    "%m/%Y",  # 2/2002
    "%m.%Y",  # 2.2002
    # formats only needed for forms, not for dateparser with DMY language set
    "%d.%m.%Y",  # 9.7.1982, 18.4.1963
    "%d/%m/%Y",  # 9/7/1982, 18/4/1963
    "%d-%m-%Y",  # 23-12-1980
]

# dateparser settings used for handling incomplete/ambiguous dates
# https://dateparser.readthedocs.io/en/latest/settings.html
DATEPARSER_SETTINGS = {
    "PREFER_DAY_OF_MONTH": "first",
    "PREFER_MONTH_OF_YEAR": "first",
    "PREFER_DATES_FROM": "future",
    "TIMEZONE": TIME_ZONE,
    "REQUIRE_PARTS": ["year"],
    "STRICT_PARSING": True,
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# APIS app-specific settings

# APIS_BASE_URI is used to construct URIs to resources (allows access to
# individual objects via the API). Should be set to full web address
# where app is hosted, needs to end with a trailing slash. Example:
# APIS_BASE_URI = "https://my-project.subdomain.oeaw.ac.at/"

APIS_BASE_URI = "https://frischmuth-dev.acdh-dev.oeaw.ac.at/"

REDMINE_ID = ""

MAIN_TEXT_NAME = ""

APIS_DEFAULT_COLLECTION = "manual"

APIS_LIST_VIEWS_ALLOWED = False  # toggle for making list views public

APIS_DETAIL_VIEWS_ALLOWED = False  # toggle for making detail views public
