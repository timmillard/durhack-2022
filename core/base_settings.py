"""
    Base Django settings for Pulsifi project.

    Partially generated by 'django-admin startproject' using Django 4.1.3.
"""
from pathlib import Path
from re import search as re_search

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
# noinspection PyPackageRequirements
from environ import Env
from tldextract import tldextract

# noinspection SpellCheckingInspection
env = Env(
    USERNAME_MIN_LENGTH=(int, 4),
    ACCOUNT_EMAIL_VERIFICATION=(str, "mandatory"),
    ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS=(int, 1),
    AVATAR_GRAVATAR_DEFAULT=(str, "mp"),
    VERSION=(str, "0.1"),
    EMAIL_HOST=(str, "smtppro.zoho.eu"),
    EMAIL_PORT=(int, 465),
    EMAIL_HOST_USER=(str, "no-reply@pulsifi.tech"),
    EMAIL_USE_SSL=(bool, True),
    PULSIFI_ADMIN_COUNT=(int, 1),
    MESSAGE_DISPLAY_LENGTH=(int, 15),
    FOLLOWER_COUNT_SCALING_FUNCTION=(str, "linear"),
    PASSWORD_SIMILARITY_TO_USER_ATTRIBUTES=(float, 0.627)
)

# Confirming that the supplied environment variable values for these settings are one of the valid choices
if not env("USERNAME_MIN_LENGTH") > 1:
    raise ImproperlyConfigured("USERNAME_MIN_LENGTH must be an integer greater than 1.")
_ACCOUNT_EMAIL_VERIFICATION_choices = ("mandatory", "optional", "none")
if env("ACCOUNT_EMAIL_VERIFICATION") not in _ACCOUNT_EMAIL_VERIFICATION_choices:
    raise ImproperlyConfigured(f"ACCOUNT_EMAIL_VERIFICATION must be one of {_ACCOUNT_EMAIL_VERIFICATION_choices}.")
if not env("ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS") > 0:
    raise ImproperlyConfigured("ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS must be an integer greater than 0.")
# noinspection SpellCheckingInspection
_AVATAR_GRAVATAR_DEFAULT_choices = ("404", "mp", "identicon", "monsterid", "wavatar", "retro", "robohash")
if env("AVATAR_GRAVATAR_DEFAULT") not in _AVATAR_GRAVATAR_DEFAULT_choices:
    raise ImproperlyConfigured(f"AVATAR_GRAVATAR_DEFAULT must be one of {_AVATAR_GRAVATAR_DEFAULT_choices}.")
if re_search(r"^\d*(?:\.\d*)+$", env("VERSION")) is None:
    raise ImproperlyConfigured("VERSION must be in this format: \"<number>.<number>.<number>\".")
if not tldextract.extract(env("EMAIL_HOST")).domain or not tldextract.extract(env("EMAIL_HOST")).suffix:
    raise ImproperlyConfigured("EMAIL_HOST must be a a valid email host name with a valid domain name & suffix.")
if not 0 < env("EMAIL_PORT") <= 65535:
    raise ImproperlyConfigured("EMAIL_PORT must be a valid port number (an integer between 0 and 65536).")
_EMAIL_HOST_USER_domain: str
_, _EMAIL_HOST_USER_domain = env("EMAIL_HOST_USER").split("@")
if env("EMAIL_HOST_USER").count("@") != 1 or (env("EMAIL_HOST_USER").count("@") == 1 and (not tldextract.extract(_EMAIL_HOST_USER_domain).domain or not tldextract.extract(_EMAIL_HOST_USER_domain).suffix)):
    raise ImproperlyConfigured("EMAIL_HOST_USER must be a valid email address.")
if not env("PULSIFI_ADMIN_COUNT") > 0:
    raise ImproperlyConfigured("PULSIFI_ADMIN_COUNT must be an integer greater than 0.")
if not env("MESSAGE_DISPLAY_LENGTH") > 0:
    raise ImproperlyConfigured("MESSAGE_DISPLAY_LENGTH must be an integer greater than 0.")
_FOLLOWER_COUNT_SCALING_FUNCTION_choices = ("logarithmic", "linear", "quadratic", "linearithmic", "exponential", "factorial")
if env("FOLLOWER_COUNT_SCALING_FUNCTION") not in _FOLLOWER_COUNT_SCALING_FUNCTION_choices:
    raise ImproperlyConfigured(f"FOLLOWER_COUNT_SCALING_FUNCTION must be one of {_FOLLOWER_COUNT_SCALING_FUNCTION_choices}.")
if not 0.1 <= env("PASSWORD_SIMILARITY_TO_USER_ATTRIBUTES") <= 1.0:
    raise ImproperlyConfigured("PASSWORD_SIMILARITY_TO_USER_ATTRIBUTES must be a float between 0.1 and 1.0.")


def _display_user(user):
    return str(user)


# Build paths inside the project like this: BASE_DIR / "subdir"
BASE_DIR = Path(__file__).resolve().parent.parent

# Adding additional (not manually specified) environment variables as settings values
Env.read_env(BASE_DIR / ".env")

STATIC_ROOT = "/staticfiles/"
STATIC_URL = "static/"
MEDIA_ROOT = BASE_DIR / r"pulsifi\media"
MEDIA_URL = "media/"

# Default URL redirect settings (used for authentication)
LOGIN_URL = reverse_lazy("pulsifi:home")
LOGIN_REDIRECT_URL = reverse_lazy("pulsifi:feed")
LOGOUT_REDIRECT_URL = reverse_lazy("default")

# Auth model settings
AUTH_USER_MODEL = "pulsifi.User"

# Authentication configuration settings (mainly for allauth & its associated packages)
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_USER_DISPLAY = _display_user
ACCOUNT_USERNAME_MIN_LENGTH = env("USERNAME_MIN_LENGTH")
ACCOUNT_EMAIL_VERIFICATION = env("ACCOUNT_EMAIL_VERIFICATION")
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = env("ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS")
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_FORMS = {"signup": "pulsifi.forms.SignupForm"}
AVATAR_GRAVATAR_DEFAULT = env("AVATAR_GRAVATAR_DEFAULT")
# noinspection SpellCheckingInspection
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "VERIFIED_EMAIL": True,
        "APP": {
            "name": "Google",
            "client_id": "661911946943-ttrstdi5luvlfcee625gq71ikekk7qcg.apps.googleusercontent.com",
            "secret": env("OATH_GOOGLE_SECRET"),
            "key": ""
        }
    },
    "discord": {
        "VERIFIED_EMAIL": True,
        "APP": {
            "name": "Discord",
            "client_id": "1054763384391876628",
            "secret": env("OATH_DISCORD_SECRET"),
            "key": ""
        }
    },
    "github": {
        "VERIFIED_EMAIL": True,
        "APP": {
            "name": "GitHub",
            "client_id": "3c53e63beb0fb9cfcce3",
            "secret": env("OATH_GITHUB_SECRET"),
            "key": ""
        }
    },
    "microsoft": {
        "VERIFIED_EMAIL": True,
        "APP": {
            "name": "Microsoft",
            "client_id": "6f9ee230-1fc5-4d18-ace3-a45805cc4112",
            "secret": env("OATH_MICROSOFT_SECRET"),
            "key": ""
        }
    }
}

# Email settings to configure how Django should send emails
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = env("EMAIL_USE_SSL")

# Custom settings values (used to control functionality of the app)
PULSIFI_ADMIN_COUNT = env("PULSIFI_ADMIN_COUNT")
MESSAGE_DISPLAY_LENGTH = env("MESSAGE_DISPLAY_LENGTH")
FOLLOWER_COUNT_SCALING_FUNCTION = env(
    "FOLLOWER_COUNT_SCALING_FUNCTION"
)  # TODO: Add function for how delete time of pulses & replies scales with follower count (y=log_2(x+1), y=x, y=xlog_2(x+1), y=2^x-1, y=(x+1)!-1)

# Secret key that is used for important secret stuff (keep the one used in production a secret!)
SECRET_KEY = env("SECRET_KEY")

# App definitions
# noinspection SpellCheckingInspection
INSTALLED_APPS = [
    "pulsifi.apps.PulsifiConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.discord",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "allauth_2fa",
    "avatar",
    "rangefilter"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth_2fa.middleware.AllauthTwoFactorMiddleware",
]

WSGI_APPLICATION = "core.wsgi.application"

ROOT_URLCONF = "core.urls"

SITE_ID = 1

ACCOUNT_ADAPTER = "allauth_2fa.adapter.OTPAdapter"

# noinspection PyUnresolvedReferences
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages"
            ]
        }
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3"
    }
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ("username", "email", "bio"),
            "max_similarity": env("PASSWORD_SIMILARITY_TO_USER_ATTRIBUTES")
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    }
]

# Language & time settings
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True
