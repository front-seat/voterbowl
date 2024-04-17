from django.core.management.base import BaseCommand

from server.utils.agcod import AGCODClient


class Command(BaseCommand):
    """Create a gift card using the Amazon Gift Codes On Demand (AGCOD) API."""

    help = "Create a gift card using the Amazon Gift Codes On Demand (AGCOD) API"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument("amount", type=int)

    def handle(self, amount: int, **options):
        """Handle the command."""
        client = AGCODClient.from_settings()
        try:
            response = client.create_gift_card(amount)
        except Exception as e:
            self.stderr.write(f"Failed to create gift card: {e}")
            return
        self.stdout.write(response.model_dump_json(indent=2))
