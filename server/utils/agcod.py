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
from pydantic.alias_generators import to_camel

from .tokens import make_token

logger = logging.getLogger(__name__)


def hostname_from_url(url: str) -> str:
    """Return the hostname from a URL."""
    hostname = urlparse(url).hostname
    if hostname is None:
        raise ValueError(f"URL {url} has no hostname")
    return hostname


def dt_from_timestamp(timestamp: str) -> datetime.datetime:
    """Convert an AGCOD timestamp to a datetime."""
    return datetime.datetime.strptime(timestamp, "%Y%m%dT%H%M%S%z")


Method: t.TypeAlias = t.Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
Invoker: t.TypeAlias = t.Callable[[Method, str, bytes | None, dict | None], dict]


def _httpx_invoker(
    method: Method, url: str, body: bytes | None, headers: dict | None
) -> dict:
    """Invoke an HTTP request."""
    response = httpx.request(method, url, content=body, headers=headers)
    # TODO: for now, we just blow up in a generic way if the response is bad.
    # AGCOD has a specific error format that we should parse and raise to provide
    # detail.
    response.raise_for_status()
    maybe_response = response.json()
    if not isinstance(maybe_response, dict):
        raise ValueError(f"Unexpected AGCOD response type: {type(maybe_response)}")
    return maybe_response


class AmazonClient:
    """Client for interacting with the an Amazon Signature V4 style API."""

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    aws_service: str

    _invoker: Invoker

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        aws_service: str,
        *,
        _invoker: Invoker = _httpx_invoker,
    ):
        """Initialize the client."""
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region
        self.aws_service = aws_service
        self._invoker = _invoker

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
        response = self._invoker(
            "POST", aws_request.url, aws_request.body, aws_request.headers
        )
        logger.debug("AWSClient Response: %s", response)
        return response


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
        *,
        _invoker: Invoker = _httpx_invoker,
    ):
        """Initialize the client."""
        self.aws_endpoint_host = aws_endpoint_host
        self.aws_target_prefix = aws_target_prefix
        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region,
            aws_service=aws_service,
            _invoker=_invoker,
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


# I would use `type StatusCode = ...` except mypy still has an open issue
# for supporting PEP 695. Ugh; all the other type checkers support it!
StatusCode: t.TypeAlias = t.Literal["SUCCESS", "FAILURE", "RESEND"]
CardStatus: t.TypeAlias = t.Literal["Fulfilled", "RefundedToPurchaser", "Expired"]


class BaseCamelModel(p.BaseModel):
    """A base class for models that use camelCase."""

    model_config = p.ConfigDict(alias_generator=to_camel)


class MonetaryValue(BaseCamelModel):
    """A monetary value with a currency code."""

    amount: int
    currency_code: str


class CardInfo(BaseCamelModel):
    """Information about a gift card returned by the AGCOD API."""

    @p.field_validator("expiration_date", mode="before")
    def validate_dt_or_none(cls, value: str | None) -> datetime.datetime | None:
        """Validate the expiration date."""
        if value is None:
            return None
        return dt_from_timestamp(value)

    card_number: str | None
    card_status: CardStatus
    expiration_date: datetime.datetime | None
    value: MonetaryValue


class CreateGiftCardResponse(BaseCamelModel):
    """Response from the CreateGiftCard API."""

    @p.field_validator("gc_expiration_date", mode="before")
    def validate_dt_or_none(cls, value: str | None) -> datetime.datetime | None:
        """Validate the expiration date."""
        if value is None:
            return None
        return dt_from_timestamp(value)

    card_info: CardInfo
    creation_request_id: str
    gc_claim_code: str
    gc_expiration_date: datetime.datetime | None
    gc_id: str
    status: StatusCode


class GetAvailableFundsResponse(BaseCamelModel):
    """Response from the GetAvailableFunds API."""

    @p.field_validator("timestamp", mode="before")
    def validate_dt(cls, value: str) -> datetime.datetime:
        """Validate the timestamp."""
        return dt_from_timestamp(value)

    available_funds: MonetaryValue
    status: StatusCode
    timestamp: datetime.datetime


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
        *,
        _invoker: Invoker = _httpx_invoker,
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
            _invoker=_invoker,
        )

    @classmethod
    def from_settings(cls) -> t.Self:
        """Create a client from Django settings."""
        aws_access_key_id = t.cast(str | None, settings.AWS_ACCESS_KEY_ID)
        aws_secret_access_key = t.cast(str | None, settings.AWS_SECRET_ACCESS_KEY)
        aws_region = t.cast(str | None, settings.AWS_REGION)
        endpoint_host = t.cast(str | None, settings.AGCOD_ENDPOINT_HOST)
        parter_id = t.cast(str | None, settings.AGCOD_PARTNER_ID)

        if aws_access_key_id is None:
            logger.warning("Missing AWS_ACCESS_KEY_ID")

        if aws_secret_access_key is None:
            logger.warning("Missing AWS_SECRET_ACCESS_KEY")

        if aws_region is None:
            logger.warning("Missing AWS_REGION")

        if endpoint_host is None:
            logger.warning("Missing AGCOD_ENDPOINT_HOST")

        if parter_id is None:
            logger.warning("Missing AGCOD_PARTNER_ID")

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

    def make_request_id(self, token: str | None) -> str:
        """Generate a creation request ID."""
        if token is None:
            token = make_token(32)
        return f"{self.partner_id}-{token}"

    def create_gift_card(
        self,
        amount: int,
        *,
        creation_request_id: str | None = None,
        currency_code: str = "USD",
    ) -> CreateGiftCardResponse:
        """
        Create a gift card, or check the status of an existing gift card.

        If creation_request_id is not provided, a random ID will be generated.

        AGCOD's CreateGiftCard request is idempotent, so re-use of the same
        (creation_request_id, amount, currency_code) tuple will return the
        same gift card information rather than funding a new one. Amazon's
        documentation strongly recommends never storing the returned
        gc_claim_code in a local database; instead, store the creation
        details and re-check the status of the gift card as needed.
        """
        creation_request_id = creation_request_id or self.make_request_id(None)
        data = {
            "creationRequestId": creation_request_id,
            "partnerId": self.partner_id,
            "value": {
                "currencyCode": currency_code,
                "amount": amount,
            },
        }
        response_data = self.post_json_rpc("CreateGiftCard", data)
        return CreateGiftCardResponse.model_validate(response_data)

    def check_gift_card(
        self,
        amount: int,
        creation_request_id: str,
        *,
        currency_code: str = "USD",
    ) -> CreateGiftCardResponse:
        """Check the status of an existing gift card."""
        # You should only call this with pre-existing values, otherwise
        # a gift card will be created. It's all a little awkwardly expressed
        # here, but so be it.
        return self.create_gift_card(
            amount=amount,
            creation_request_id=creation_request_id,
            currency_code=currency_code,
        )

    def get_available_funds(self) -> GetAvailableFundsResponse:
        """Get the available funds for the partner."""
        data = {
            "partnerId": self.partner_id,
        }
        response_data = self.post_json_rpc("GetAvailableFunds", data)
        return GetAvailableFundsResponse.model_validate(response_data)
