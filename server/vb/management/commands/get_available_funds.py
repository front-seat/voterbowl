import typing as t

from django.core.management.base import BaseCommand

from server.utils.agcod import AGCODClient


class Command(BaseCommand):
    """Get available funds remaining for generating gift codes using the AGCOD API."""

    help = (
        "Get available funds remaining for generating gift codes using the AGCOD API."
    )

    def handle(self, **options: t.Any):
        """Handle the command."""
        client = AGCODClient.from_settings()
        try:
            response = client.get_available_funds()
        except Exception as e:
            self.stderr.write(f"Failed to get available funds: {e}")
            return
        self.stdout.write(response.model_dump_json(indent=2))
