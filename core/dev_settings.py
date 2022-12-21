"""
    Development Django settings for Pulsifi project.
"""

from .base_settings import *

#Getting setting default values for some settings that are collected from the attached environment variables file (if they are not specified in the file, these default values will be used)
env = Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ["localhost"])
)


# Namespace resolving settings
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
