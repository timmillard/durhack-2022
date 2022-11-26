"""
    App configurations in pulsifi application.
"""

from django.apps import AppConfig


class PulsifiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pulsifi"
    verbose_name = "Pulsifi"