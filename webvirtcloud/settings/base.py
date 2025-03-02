"""
Django settings for webvirtcloud project.
"""

import os
import uuid
import base64
from pathlib import Path
from celery.schedules import crontab
from theme.crispy_forms import WEBVIRTCLOUD_CRISPY_CLASS_CONVERTERS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-8gyd_q$%c$(g$#nwqzbgaj2*(r1x8vp_l)-d+pm1+w^w9y9$v&"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ["*"]

# Authentication definition
AUTH_USER_MODEL = "account.User"

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Project application definition
INSTALLED_APPS += [
    "api",
    "size",
    "admin",
    "image",
    "lbaas",
    "region",
    "account",
    "billing",
    "compute",
    "keypair",
    "project",
    "network",
    "virtance",
    "firewall",
    "floating_ip",
    "webvirtcloud",
]

# Third party application definition
INSTALLED_APPS += [
    "theme",
    "tailwind",
    "django_htmx",
    "crispy_forms",
    "crispy_tailwind",
    "rest_framework",
    "django_filters",
    "django_tables2",
    "django_celery_results",
]

# Middleware definition
MIDDLEWARE = [
    "django_htmx.middleware.HtmxMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Rest framework definition
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "webvirtcloud.views.app_exception_handler",
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PERMISSION_CLASSES": ("webvirtcloud.permissions.IsAuthenticatedAndVerified",),
    "DEFAULT_AUTHENTICATION_CLASSES": ("webvirtcloud.authentication.TokenAuthentication",),
}

# Root URL definition
ROOT_URLCONF = "webvirtcloud.urls"

# Templates definition
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

# WSGI definition
WSGI_APPLICATION = "webvirtcloud.wsgi.application"

# Database settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "CONN_MAX_AGE": 3600,
        "NAME": os.environ.get("DB_NAME", "webvirtcloud"),
        "USER": os.environ.get("DB_USER", "django"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "django"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", 3306),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
}

# Celery settings
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@127.0.0.1:5672")
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULE = {
    "virtance_counter": {
        "task": "virtance.tasks.virtance_counter",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "virtance_backup": {
        "task": "virtance.tasks.virtance_backup",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "snapshot_counter": {
        "task": "image.tasks.snapshot_counter",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "floating_ip_counter": {
        "task": "floating_ip.tasks.floating_ip_counter",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "make_monthly_invoice": {
        "task": "billing.tasks.make_monthly_invoice",
        "schedule": crontab(minute=0, hour=0, day_of_month=1),
    },
}

# Password validation
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
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "../../", "static")
STATICFILES_DIRS = [os.path.join(os.path.join(BASE_DIR, "../"), "static")]

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login redirect url
LOGIN_URL = "/admin/sign_in/"
LOGIN_REDIRECT_URL = "/admin/"

# Crispy forms
CRISPY_TEMPLATE_PACK = "webvirtcloud"
CRISPY_ALLOWED_TEMPLATE_PACKS = ("webvirtcloud",)
CRISPY_CLASS_CONVERTERS = WEBVIRTCLOUD_CRISPY_CLASS_CONVERTERS

# Tailwind settings
TAILWIND_APP_NAME = "theme"
TAILWIND_CSS_PATH = "admin/css/styles.css"

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "WebVirtCloud <noreply@webvirt.cloud>")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

# WebVirtCloud Settings

#
# Domain and URL settings
#
# Base domain
BASE_DOMAIN = os.environ.get("DOMAIN_NAME", "webvirt.cloud")

# Security settings
SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN", f"{BASE_DOMAIN}")

# CSFR Trusted hosts
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", [f"https://{BASE_DOMAIN}", f"http://{BASE_DOMAIN}"])

#
# Panel settings
#
# Encryption key
# Generate a new own key with the following command:
# python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'
# or use the default key generated unique static node ID
UNIQ_NODE_ID = f"webvirtcloud-{uuid.getnode():x}".ljust(32, "0").encode()
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", base64.urlsafe_b64encode(UNIQ_NODE_ID).decode())

# Public images URL storage (Distributions, Applicatons)
PUBLIC_IMAGES_URL = os.environ.get("PUBLIC_IMAGES_URL", "https://cloud-images.webvirt.cloud/")

# Compute settings
COMPUTE_PORT = os.environ.get("COMPUTE_PORT", 8884)
COMPUTE_VM_IMAGES_POOL = os.environ.get("COMPUTE_VM_IMAGES_POOL", "images")
COMPUTE_CPU_RATIO_OVERCOMMIT = os.environ.get("COMPUTE_CPU_RATIO_OVERCOMMIT", 2)
COMPUTE_MEMORY_PERCENTAGE_USAGE = os.environ.get("COMPUTE_MEMORY_PERCENTAGE_USAGE", 85)
COMPUTE_STORAGE_PERCENTAGE_USAGE = os.environ.get("COMPUTE_STORAGE_PERCENTAGE_USAGE", 85)

# Virtual machine name prefix
VM_NAME_PREFIX = os.environ.get("VM_NAME_PREFIX", "Virtance-")

# Websocket settings
WEBSOCKET_HOST = os.environ.get("WEBSOCKET_HOST", "0.0.0.0")
WEBSOCKET_PORT = os.environ.get("WEBSOCKET_PORT", 6080)
WEBSOCKET_CERT = os.environ.get("WEBSOCKET_CERT", None)

# noVNC settings
NOVNC_URL = os.environ.get("NOVNC_URL", f"{BASE_DOMAIN}/novnc/")
NOVNC_PORT = os.environ.get("NOVNC_PORT", 443)
NOVNC_PASSWD_PREFIX_LENGHT = os.environ.get("NOVNC_PASSWD_PREFIX_LENGHT", 6)
NOVNC_PASSWD_SUFFIX_LENGHT = os.environ.get("NOVNC_PASSWD_SUFFIX_LENGHT", 12)

# Recovery image settings
RECOVERY_ISO_NAME = os.environ.get("RECOVERY_ISO_NAME", "finnix-125.iso")

# LBaaS settings
LBAAS_IPV4_ACCESS_LIST = os.environ.get("LBAAS_IPV4_ACCESS_LIST", [])

# Backup settings
BACKUP_PER_MONTH = os.environ.get("BACKUP_PER_MONTH", 4)
BACKUP_PERIOD_DAYS = os.environ.get("BACKUP_PERIOD_DAYS", 7)
BACKUP_COST_PERCENTAGE = os.environ.get("BACKUP_COST_PERCENTAGE", 20)

# Verification settings
VERIFICATION_ENABLED = os.environ.get("VERIFICATION_ENABLED", False)

# Registration settings
REGISTRATION_ENABLED = os.environ.get("REGISTRATION_ENABLED", False)
