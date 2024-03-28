import base64
import typing as t
from dataclasses import dataclass

from django.db import models


class ImageMimeType(models.TextChoices):
    """MIME types for images."""

    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    SVG = "image/svg+xml"


@dataclass(frozen=True)
class Logo:
    """Data for a logo display."""

    b64: str
    """Base64-encoded image data."""

    mime: str
    """MIME type of the image."""

    bg_color: str
    """Background color for when the image is displayed in a circle."""

    @classmethod
    def from_bytes(cls, bytes_: bytes, mime: str, bg_color: str) -> t.Self:
        """Create a `LogoData` instance from bytes."""
        return cls(b64=base64.b64encode(bytes_).decode(), mime=mime, bg_color=bg_color)

    @classmethod
    def from_data(cls, data: t.Any) -> t.Self:
        """Create a `Logo` instance from data."""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        b64 = data.get("b64")
        if not isinstance(b64, str):
            raise ValueError("Base64 data must be a string.")
        mime = data.get("mime")
        if not isinstance(mime, str):
            raise ValueError("MIME type must be a string.")
        bg_color = data.get("bg_color")
        if not isinstance(bg_color, str):
            raise ValueError("Background color must be a string.")
        return cls(b64=b64, mime=mime, bg_color=bg_color)

    def to_data(self) -> dict:
        """Return the logo data as a dictionary."""
        return {
            "b64": self.b64,
            "mime": self.mime,
            "bg_color": self.bg_color,
        }

    def url(self) -> str:
        """Return the logo data as a data URL."""
        return f"data:{self.mime};base64,{self.b64}"


class School(models.Model):
    """A single school in the competition."""

    name = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(max_length=255, blank=False, unique=True)

    short_name = models.CharField(max_length=255, blank=True)
    mascot = models.CharField(max_length=255, blank=True)

    logo_json = models.JSONField(default=dict, blank=True)

    mail_domains = models.JSONField(default=list, blank=True)

    @property
    def logo(self) -> Logo:
        """Return the logo data."""
        return Logo.from_data(self.logo_json)

    @logo.setter
    def logo(self, value: Logo) -> None:
        """Set the logo data."""
        self.logo_json = value.to_data()

    def __str__(self):
        """Return the school model's string representation."""
        return f"School: {self.name}"


class Student(models.Model):
    """A single student in the competition."""

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    email = models.EmailField(blank=False)
    phone = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
