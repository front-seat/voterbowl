import typing as t
import unittest
from unittest import mock

from . import agcod


class AGCODTestClient(agcod.AGCODClient):
    """Test AGCOD client with mocked invoker."""

    def __init__(self, invoker: agcod.Invoker):
        """Initialize the test client."""
        super().__init__(
            aws_access_key_id="test_aws_access_key_id",
            aws_secret_access_key="test_aws_secret_access_key",
            aws_region="test_aws_region",
            aws_endpoint_host="test_aws_endpoint_host.local",
            partner_id="test_partner_id",
            _invoker=invoker,
        )


class AGCODTextMixin:
    """AGCOD test mixin."""

    RESPONSE_DATA = {
        "cardInfo": {
            "cardNumber": "test_card_number",
            "cardStatus": "Fulfilled",
            "expirationDate": None,
            "value": {
                "amount": 100,
                "currencyCode": "USD",
            },
        },
        "creationRequestId": "test_creation_request_id",
        "gcClaimCode": "test_gc_claim_code",
        "gcId": "test_gc_id",
        "gcExpirationDate": None,
        "status": "SUCCESS",
    }

    def create_gift_card_invoker(self, amount: int = 100):
        """Create a create_gift_card invoker."""
        response_data: dict[str, t.Any] = self.RESPONSE_DATA.copy()
        response_data["cardInfo"]["value"]["amount"] = amount
        invoker = mock.MagicMock()
        invoker.return_value = response_data
        return invoker


class CreateGiftCardTestCase(AGCODTextMixin, unittest.TestCase):
    """Test the create_gift_card function."""

    # TODO: flesh out the the architecture and tests if I have time

    def test_create_gift_card(self):
        """Test creating a gift card."""
        amount = 50
        invoker = self.create_gift_card_invoker(amount)
        client = AGCODTestClient(invoker)
        response = client.create_gift_card(amount)
        call_args = invoker.call_args[0]
        self.assertEqual(invoker.call_count, 1)
        self.assertEqual(call_args[0], "POST")
        self.assertTrue("/CreateGiftCard" in call_args[1])
        self.assertTrue("test_partner_id-" in call_args[2].decode())
        self.assertEqual(response.card_info.value.amount, amount)
