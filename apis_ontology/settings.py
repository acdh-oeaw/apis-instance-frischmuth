"""
Django settings for apis_ontology project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import re
import dj_database_url
import os

from pathlib import Path
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

# Application definition

ROOT_URLCONF = "apis_ontology.urls"

WSGI_APPLICATION = "apis_ontology.wsgi.application"

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


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}


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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "de"

TIME_ZONE = "CET"

USE_I18N = True

USE_TZ = True


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

APIS_RELATIONS_FILTER_EXCLUDE.append("annotation")

APIS_DEFAULT_COLLECTION = "manual"

APIS_LIST_VIEWS_ALLOWED = False  # toggle for making list views public

APIS_DETAIL_VIEWS_ALLOWED = False  # toggle for making detail views public

# Use APIS_ENTITIES to configure display settings and functionality for
# individual fields of any entity class in models.py.

APIS_ENTITIES = {
    "Work": {
        "search": [
            "name",
            "title",
            "subtitle",
            "siglum",
            "progress_status",
            "summary",
            "context",
            "historical_events",
            "text_analysis",
            "data_source",
        ],
        "form_order": [
            "name",
            "title",
            "subtitle",
            "siglum",
            "progress_status",
            "summary",
            "context",
            "historical_events",
            "text_analysis",
            "temporal_order",
            "temporal_duration",
            "temporal_frequency",
            "figure_speech",
            "representation_of_thought",
            "focalization",
            "narrative_situation",
            "narrative_chronology",
            "narrative_level",
            "narrative_voice",
        ],
        "table_fields": [
            "name",
            "title",
            "subtitle",
            "siglum",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "summary",
            "context",
            "historical_events",
            "text_analysis",
            "temporal_order",
            "temporal_duration",
            "temporal_frequency",
            "figure_speech",
            "representation_of_thought",
            "focalization",
            "narrative_situation",
            "narrative_chronology",
            "narrative_level",
            "narrative_voice",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "title": {"method": "name_label_filter"},
            "subtitle": {"method": "name_label_filter"},
            "siglum": {"method": "name_label_filter"},
            "progress_status": {},
            "summary": {"method": "name_label_filter"},
            "context": {"method": "name_label_filter"},
            "historical_events": {"method": "name_label_filter"},
            "text_analysis": {"method": "name_label_filter"},
            "temporal_order": {},
            "temporal_duration": {},
            "temporal_frequency": {},
            "figure_speech": {},
            "representation_of_thought": {},
            "focalization": {},
            "narrative_situation": {},
            "narrative_chronology": {},
            "narrative_level": {},
            "narrative_voice": {},
            "data_source": {},
        },
    },
    "Expression": {
        "search": [
            "name",
            "title",
            "subtitle",
            "edition_type",
            "issue",
            "progress_status",
            "publication_date_iso",
            "description",
            "data_source",
        ],
        "form_order": [
            "name",
            "title",
            "subtitle",
            "progress_status",
            "description",
            "publication_date",
            "issue",
            "edition_type",
            "page_count",
            "relevant_pages",
        ],
        "table_fields": [
            "name",
            "title",
            "subtitle",
            "edition_type",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "issue",
            "description",
            "page_count",
            "publication_date_iso",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "title": {"method": "name_label_filter"},
            "subtitle": {"method": "name_label_filter"},
            "edition_type": {},
            "publication_date_iso": {},
            "issue": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "progress_status": {},
            "data_source": {},
        },
    },
    "WorkType": {
        "search": [
            "name",
            "name_plural",
            "alternative_name",
            "description",
            "progress_status",
            "data_source",
        ],
        "form_order": [
            "name",
            "name_plural",
            "alternative_name",
            "description",
            "progress_status",
        ],
        "table_fields": [
            "name",
            "name_plural",
            "alternative_name",
        ],
        "additional_cols": [
            "description",
            "progress_status",
            "data_source",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "name_plural": {"method": "name_label_filter"},
            "alternative_name": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "progress_status": {},
            "data_source": {},
        },
    },
    "PhysicalObject": {
        "search": [
            "name",
            "vorlass_doc_reference",
            "description",
            "data_source",
        ],
        "form_order": [
            "name",
            "description",
        ],
        "table_fields": [
            "name",
        ],
        "additional_cols": [
            "vorlass_doc_reference",
            "data_source",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "vorlass_doc_reference": {},
            "description": {"method": "name_label_filter"},
            "data_source": {},
        },
    },
    "Person": {
        "search": [
            "name",
            "first_name",
            "last_name",
            "alternative_name",
            "progress_status",
            "description",
            "data_source",
        ],
        "form_order": [
            "name",
            "first_name",
            "last_name",
            "alternative_name",
            "progress_status",
            "description",
        ],
        "table_fields": [
            "name",
            "last_name",
            "first_name",
            "alternative_name",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "first_name": {"method": "name_label_filter"},
            "last_name": {"method": "name_label_filter"},
            "alternative_name": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "progress_status": {},
            "data_source": {},
        },
    },
    "Organisation": {
        "search": [
            "name",
            "alternative_name",
            "progress_status",
            "description",
            "website",
            "data_source",
        ],
        "form_order": [
            "name",
            "alternative_name",
            "progress_status",
            "description",
            "website",
        ],
        "table_fields": [
            "name",
            "alternative_name",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "description",
            "website",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "alternative_name": {"method": "name_label_filter"},
            "progress_status": {},
            "description": {"method": "name_label_filter"},
            "website": {},
            "data_source": {},
        },
    },
    "Character": {
        "search": [
            "name",
            "first_name",
            "last_name",
            "alternative_name",
            "progress_status",
            "relevancy",
            "fictionality",
            "description",
            "data_source",
        ],
        "form_order": [
            "name",
            "first_name",
            "last_name",
            "alternative_name",
            "relevancy",
            "fictionality",
            "progress_status",
            "description",
        ],
        "table_fields": [
            "name",
            "last_name",
            "first_name",
            "relevancy",
            "fictionality",
            "progress_status",
        ],
        "additional_cols": [
            "alternative_name",
            "data_source",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "first_name": {"method": "name_label_filter"},
            "last_name": {"method": "name_label_filter"},
            "alternative_name": {"method": "name_label_filter"},
            "progress_status": {},
            "relevancy": {},
            "fictionality": {},
            "description": {"method": "name_label_filter"},
            "data_source": {},
        },
    },
    "MetaCharacter": {
        "search": [
            "name",
            "description",
            "progress_status",
            "data_source",
        ],
        "form_order": [
            "name",
            "description",
            "progress_status",
        ],
        "table_fields": [
            "name",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "progress_status": {},
            "data_source": {},
        },
    },
    "ResearchPerspective": {
        "search": [
            "name",
            "alternative_name",
            "description",
            "progress_status",
            "data_source",
        ],
        "form_order": [
            "name",
            "alternative_name",
            "description",
            "progress_status",
        ],
        "table_fields": [
            "name",
            "alternative_name",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "alternative_name": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "progress_status": {},
            "data_source": {},
        },
    },
    "Topic": {
        "search": [
            "name",
            "alternative_name",
            "description",
            "progress_status",
            "data_source",
        ],
        "form_order": [
            "name",
            "alternative_name",
            "description",
            "progress_status",
        ],
        "table_fields": [
            "name",
            "alternative_name",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "alternative_name": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "progress_status": {},
            "data_source": {},
        },
    },
    "Place": {
        "search": [
            "name",
            "alternative_name",
            "progress_status",
            "description",
            "latitude",
            "longitude",
            "data_source",
        ],
        "form_order": [
            "name",
            "alternative_name",
            "progress_status",
            "description",
            "latitude",
            "longitude",
        ],
        "table_fields": [
            "name",
            "alternative_name",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "description",
            "latitude",
            "longitude",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "alternative_name": {"method": "name_label_filter"},
            "progress_status": {},
            "description": {"method": "name_label_filter"},
            "latitude": {},
            "longitude": {},
            "data_source": {},
        },
    },
    "Interpretatem": {
        "search": [
            "name",
            "description",
            "progress_status",
            "data_source",
        ],
        "form_order": [
            "name",
            "description",
            "progress_status",
        ],
        "table_fields": [
            "name",
            "progress_status",
        ],
        "additional_cols": [
            "data_source",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "progress_status": {},
            "data_source": {},
        },
    },
    "Archive": {
        "search": [
            "name",
            "description",
            "location",
            "website",
            "data_source",
        ],
        "form_order": [
            "name",
            "description",
            "location",
            "website",
        ],
        "table_fields": [
            "name",
            "location",
        ],
        "additional_cols": [
            "data_source",
            "website",
            "description",
        ],
        "list_filters": {
            "name": {"method": "name_label_filter"},
            "description": {"method": "name_label_filter"},
            "location": {"method": "name_label_filter"},
            "website": {},
            "data_source": {},
        },
    },
}
