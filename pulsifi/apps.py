"""
    App configurations in pulsifi application.
"""

from django.apps import AppConfig


class PulsifiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Pulsifi"
    verbose_name = "Pulsifi"