"""Client for interacting with the AGCOD (Amazon Gift Codes On Demand) API."""

import datetime
import json
import logging
import typing as t
from urllib.parse import urlparse

import httpx
import pydantic as p
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSPreparedRequest, AWSRequest
from botocore.credentials import Credentials
from django.conf import settings
from pydantic.alias_generators import to_snake

logger = logging.getLogger(__name__)


def hostname_from_url(url: str) -> str:
    """Return the hostname from a URL."""
    hostname = urlparse(url).hostname
    if hostname is None:
        raise ValueError(f"URL {url} has no hostname")
    return hostname


class AmazonClient:
    """Client for interacting with the an Amazon Signature V4 style API."""

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    aws_service: str

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        aws_service: str,
    ):
        """Initialize the client."""
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region
        self.aws_service = aws_service

    def _credentials(self) -> Credentials:
        """Return botocore credentials."""
        return Credentials(
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )

    def _sigv4_auth(self) -> SigV4Auth:
        """Return a SigV4 auth record."""
        return SigV4Auth(
            self._credentials(),
            self.aws_service,
            self.aws_region,
        )

    def _signed_request(
        self, method: str, url: str, body: bytes, *, headers: dict | None = None
    ) -> AWSRequest:
        """Make a generic AWS request and sign it."""
        request = AWSRequest(
            method=method,
            url=url,
            data=body,
            headers=headers or {},
        )
        self._sigv4_auth().add_auth(request)
        return request

    def _signed_json_request(
        self,
        method: str,
        url: str,
        data: dict,
        *,
        headers: dict | None = None,
    ) -> AWSRequest:
        """Make a signed JSON request."""
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json")
        return self._signed_request(
            method=method,
            url=url,
            body=json.dumps(data).encode("utf-8"),
            headers=headers,
        )

    def _prepared_json_request(
        self, method: str, url: str, data: dict, *, headers: dict | None = None
    ) -> AWSPreparedRequest:
        """Prepare a signed JSON request."""
        return self._signed_json_request(method, url, data, headers=headers).prepare()

    def post_json(self, url: str, data: dict, *, headers: dict | None = None) -> dict:
        """POST a JSON request and receive a JSON reply."""
        aws_request = self._prepared_json_request("POST", url, data, headers=headers)
        logger.debug("AWSClient Request: %s", aws_request)
        response = httpx.post(
            url=aws_request.url,
            headers=aws_request.headers,
            data=aws_request.body,
        )
        response.raise_for_status()
        logger.debug("AWSClient Response: %s", response)
        return response.json()


class AmazonJSONRPCClient(AmazonClient):
    """An base AmazonClient that supports their JSON RPC API house style."""

    aws_endpoint_host: str
    aws_target_prefix: str

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        aws_service: str,
        aws_endpoint_host: str,
        aws_target_prefix: str,
    ):
        """Initialize the client."""
        self.aws_endpoint_host = aws_endpoint_host
        self.aws_target_prefix = aws_target_prefix
        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region,
            aws_service=aws_service,
        )

    def _amz_date_now(self) -> str:
        """Return the current date in the Amazon format."""
        return datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")

    def _amz_target(self, api: str) -> str:
        """Return the x-amz-target header."""
        return f"{self.aws_target_prefix}.{self.aws_service}.{api}"

    def post_json_rpc(
        self, api: str, data: dict, *, headers: dict | None = None
    ) -> dict:
        """POST a JSON RPC request and receive a JSON RPC reply."""
        headers = headers or {}
        headers.setdefault("host", self.aws_endpoint_host)
        headers.setdefault("x-amz-date", self._amz_date_now())
        headers.setdefault("x-amz-target", self._amz_target(api))
        url = f"https://{self.aws_endpoint_host}/{api}"
        return self.post_json(url, data, headers=headers)


class BaseCamelModel(p.BaseModel):
    """A base class for models that use camelCase."""

    model_config = p.ConfigDict(alias_generator=to_snake)


class CardValue(BaseCamelModel):
    """The value of a gift card."""

    amount: int
    currency_code: str


class CardInfo(BaseCamelModel):
    """Information about a gift card returned by the AGCOD API."""

    card_number: str | None
    card_status: t.Literal["Fulfilled", "RefundedToPurchaser", "Expired"]
    expiration_date: str | None
    value: CardValue


class CreateGiftCardResponse(BaseCamelModel):
    """Response from the CreateGiftCard API."""

    card_info: CardInfo
    creation_request_id: str
    gc_claim_code: str
    gc_expiration_date: str | None
    gc_id: str
    status: t.Literal["SUCCESS", "FAILURE"]


class AGCODClient(AmazonJSONRPCClient):
    """Client for interacting with the AGCOD (Amazon Gift Codes On Demand) API."""

    # A useful URL for testing is the API Scratchpad:
    # https://s3.amazonaws.com/AGCOD/htmlSDKv2/htmlSDKv2_NAEUFE/index.html

    partner_id: str

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        aws_endpoint_host: str,
        partner_id: str,
    ):
        """Initialize the AGCOD client."""
        self.partner_id = partner_id
        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region,
            aws_service="AGCODService",
            aws_endpoint_host=aws_endpoint_host,
            aws_target_prefix="com.amazonaws.agcod",
        )

    @classmethod
    def from_settings(cls):
        """Create a client from Django settings."""
        aws_access_key_id = t.cast(str | None, settings.AWS_ACCESS_KEY_ID)
        aws_secret_access_key = t.cast(str | None, settings.AWS_SECRET_ACCESS_KEY)
        aws_region = t.cast(str | None, settings.AWS_REGION)
        endpoint_host = t.cast(str | None, settings.ACGOD_ENDPOINT_URL)
        parter_id = t.cast(str | None, settings.ACGOD_PARTNER_ID)

        if aws_access_key_id is None:
            logger.warning("Missing AWS_ACCESS_KEY_ID")

        if aws_secret_access_key is None:
            logger.warning("Missing AWS_SECRET_ACCESS_KEY")

        if aws_region is None:
            logger.warning("Missing AWS_REGION")

        if endpoint_host is None:
            logger.warning("Missing ACGOD_ENDPOINT_HOST")

        if parter_id is None:
            logger.warning("Missing ACGOD_PARTNER_ID")

        if None in (
            aws_access_key_id,
            aws_secret_access_key,
            aws_region,
            endpoint_host,
            parter_id,
        ):
            raise ValueError("Missing AGCOD settings")

        # Make the type checker happy
        assert aws_access_key_id is not None
        assert aws_secret_access_key is not None
        assert aws_region is not None
        assert endpoint_host is not None
        assert parter_id is not None

        return cls(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region,
            aws_endpoint_host=endpoint_host,
            partner_id=parter_id,
        )

    def create_gift_card(
        self,
        request_id_suffix: str,
        amount: int,
        currency: str = "USD",
    ) -> CreateGiftCardResponse:
        """
        Create a gift card.

        The request_id_suffix is a unique identifier for the request and
        must be stored by the caller.
        """
        data = {
            "creationRequestId": f"{self.partner_id}-{request_id_suffix}",
            "partnerId": self.partner_id,
            "value": {
                "currencyCode": currency,
                "amount": amount,
            },
        }
        response_data = self.post_json_rpc("CreateGiftCard", data)
        return CreateGiftCardResponse.model_validate(response_data)
