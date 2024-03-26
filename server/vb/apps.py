from django.apps import AppConfig


class VoterBowlConfig(AppConfig):
    """Voterbowl app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "server.vb"
    verbose_name = "Voter Bowl"
