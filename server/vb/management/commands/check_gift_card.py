from django.core.management.base import BaseCommand

from server.utils.agcod import AGCODClient


class Command(BaseCommand):
    """Check an existing gift card using the Amazon Gift Codes On Demand (AGCOD) API."""

    help = "Create a gift card using the Amazon Gift Codes On Demand (AGCOD) API"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument("amount", type=int)
        parser.add_argument("creation_request_id", type=str)

    def handle(self, amount: int, creation_request_id: str, **options):
        """Handle the command."""
        client = AGCODClient.from_settings()
        try:
            response = client.check_gift_card(amount, creation_request_id)
        except Exception as e:
            self.stderr.write(f"Failed to check gift card: {e}")
            return
        self.stdout.write(response.model_dump_json(indent=2))
