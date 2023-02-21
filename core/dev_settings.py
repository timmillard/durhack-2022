"""
    Development Django settings for Pulsifi project.
"""

from .base_settings import *

# Getting setting default values for some settings that are collected from the attached environment variables file (if they are not specified in the file, these default values will be used)
env = Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ["localhost"]),
    LOG_LEVEL=(str, "INFO")
)

# Confirming that the supplied environment variable values for these settings are one of the valid choices
_LOG_LEVEL_choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
if env("LOG_LEVEL").upper() not in _LOG_LEVEL_choices:
    raise ImproperlyConfigured(f"LOG_LEVEL must be one of {_LOG_LEVEL_choices}")

# Namespace resolving settings
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Logging settings
# noinspection SpellCheckingInspection
LOGGING = {
    "version": 1,
    "formatters": {
        "pulsifi": {
            "format": "{levelname} - {module}: {message}",
            "style": "{"
        },
        "web_server": {
            "format": "[{asctime}] {message}",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "style": "{"
        }
    },
    "handlers": {
        "pulsifi": {
            "class": "logging.StreamHandler",
            "formatter": "pulsifi"
        },
        "web_server": {
            "class": "logging.StreamHandler",
            "formatter": "web_server"
        }
    },
    "loggers": {
        "django.server": {
            "handlers": ["web_server"],
            "level": env("LOG_LEVEL").upper()
        }
    },
    "root": {"handlers": ["pulsifi"], "level": env("LOG_LEVEL").upper()}
}
