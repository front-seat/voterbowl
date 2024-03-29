import base64
import typing as t

from django.db import models

from server.utils.contrast import HEX_COLOR_VALIDATOR, get_text_color


class ImageMimeType(models.TextChoices):
    """MIME types for images."""

    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    SVG = "image/svg+xml"


class School(models.Model):
    """A single school in the competition."""

    name = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(max_length=255, blank=False, unique=True)

    short_name = models.CharField(max_length=255, blank=True)
    mascot = models.CharField(max_length=255, blank=True)
    mail_domains = models.JSONField(default=list, blank=True)

    logo: "Logo"

    def __str__(self):
        """Return the school model's string representation."""
        return f"School: {self.name}"


class Logo(models.Model):
    """A single logo for a school."""

    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name="logo")
    content_type = models.CharField(
        max_length=255,
        choices=ImageMimeType.choices,
        blank=True,
    )
    data = models.BinaryField(blank=True)
    bg_color = models.CharField(
        max_length=7, validators=[HEX_COLOR_VALIDATOR], default="#0000ff"
    )
    action_color = models.CharField(
        max_length=7, validators=[HEX_COLOR_VALIDATOR], default="#ff0000"
    )

    @property
    def b64(self) -> str:
        """Return the logo image as a base64 string."""
        return base64.b64encode(self.data).decode("utf-8")

    @property
    def url(self) -> str:
        """Return the logo image as a data URL."""
        return f"data:{self.content_type};base64,{self.b64}"

    @property
    def bg_text_color(self) -> t.Literal["black", "white"]:
        """Return the ideal text color for the background color."""
        return get_text_color(self.bg_color)

    @property
    def action_text_color(self) -> t.Literal["black", "white"]:
        """Return the ideal text color for the action color."""
        return get_text_color(self.action_color)

    def __str__(self):
        """Return the logo model's string representation."""
        return f"Logo: {self.school.name}"


class Student(models.Model):
    """A single student in the competition."""

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    email = models.EmailField(blank=False)
    phone = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
