"""
    Production Django settings for Pulsifi project.
"""

from .base_settings import *

#Getting setting default values for some settings that are collected from the attached environment variables file (if they are not specified in the file, these default values will be used)
env = Env(
    ALLOWED_HOSTS=(list, ["pulsifi"]),
    ALLOWED_ORIGINS=(list, ["https://pulsifi.tech"])
)


# Namespace resolving settings - SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
ALLOWED_ORIGINS = env("ALLOWED_ORIGINS")  # TODO: work out how to host site
CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS.copy()
