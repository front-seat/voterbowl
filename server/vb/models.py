import base64

from django.db import models


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

    logo_mime = models.CharField(
        max_length=255, null=False, choices=ImageMimeType.choices
    )
    logo = models.BinaryField(null=False, editable=True)

    mail_domains = models.JSONField(default=list, blank=True)

    def logo_data_url(self):
        """Return the logo as a data URL."""
        return f"data:{self.logo_mime};base64,{base64.b64encode(self.logo).decode()}"

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
