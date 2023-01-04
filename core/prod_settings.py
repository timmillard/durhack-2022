"""
    Production Django settings for Pulsifi project.
"""

from .base_settings import *

# Getting setting default values for some settings that are collected from the attached environment variables file (if they are not specified in the file, these default values will be used)
env = Env(
    ALLOWED_HOSTS=(list, ["pulsifi"]),
    ALLOWED_ORIGINS=(list, ["https://pulsifi.tech"]),
    LOG_LEVEL=(str, "WARNING")
)

# Confirming that the supplied environment variable values for these settings are one of the valid choices
_LOG_LEVEL_choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
if env("LOG_LEVEL").upper() not in _LOG_LEVEL_choices:
    raise ImproperlyConfigured(f"LOG_LEVEL must be one of {_LOG_LEVEL_choices}")

# Namespace resolving settings - SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
ALLOWED_ORIGINS = env("ALLOWED_ORIGINS")  # TODO: work out how to host site
CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS.copy()

# Logging settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": env("LOG_LEVEL").upper()}
}
