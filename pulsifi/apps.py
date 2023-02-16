"""
    App configurations in pulsifi app.
"""

from django.apps import AppConfig


class PulsifiConfig(AppConfig):
    """ Class representing the pulsifi application and its configuration. """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pulsifi"
    verbose_name = "Pulsifi"

    @staticmethod
    def ready(**kwargs) -> None:
        """
            Import function that ensures the signal handlers within this app
            are loaded and waiting for signals to be sent.
        """

        from . import signals
        signals.ready()
