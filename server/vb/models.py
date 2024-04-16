import base64
import datetime
import hashlib
import typing as t

from django.core.exceptions import ValidationError
from django.db import models
from django.template import Context, Template
from django.utils.timezone import now as django_now

from server.utils.contrast import HEX_COLOR_VALIDATOR, get_text_color
from server.utils.email import Domains, normalize_email


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
    mail_tag = models.CharField(
        max_length=1,
        blank=True,
        default="+",
        help_text="The tag separator used in school emails, if any.",
    )
    mail_dots = models.BooleanField(
        default=True,
        help_text="Whether to remove dots from the local part of school emails.",
    )  # noqa

    logo: "Logo"

    contests: "ContestManager"

    def normalize_email(self, address: str) -> str:
        """Normalize an email address for this school."""
        domains = Domains(self.mail_domains[0], tuple(self.mail_domains[1:]))
        return normalize_email(
            address,
            tag=self.mail_tag if self.mail_tag else None,
            dots=self.mail_dots,
            domains=domains,
        )

    def hash_email(self, address: str) -> str:
        """Hash an email address for this school."""
        normalized = self.normalize_email(address)
        return hashlib.sha256(normalized.encode("ascii")).hexdigest()

    def is_valid_email(self, address: str) -> bool:
        """Validate an email address for this school."""
        normalized = self.normalize_email(address)
        _, domain = normalized.split("@", maxsplit=1)
        return domain == self.mail_domains[0]

    def validate_email(self, address: str) -> None:
        """Validate an email address for this school, raising an error if invalid."""
        if self.is_valid_email(address):
            return
        raise ValidationError(f"Email address is not valid for {self.name}.")

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


class ContestManager(models.Manager):
    """A custom manager for the contest model."""

    def upcoming(self, when: datetime.datetime | None = None):
        """Return all upcoming contests."""
        when = when or django_now()
        return self.get_queryset().filter(start_at__gt=when)

    def ongoing(self, when: datetime.datetime | None = None):
        """Return all ongoing contests."""
        when = when or django_now()
        return self.get_queryset().filter(start_at__lte=when, end_at__gt=when)

    def past(self, when: datetime.datetime | None = None):
        """Return all past contests."""
        when = when or django_now()
        return self.get_queryset().filter(end_at__lte=when)

    def current(self, when: datetime.datetime | None = None) -> "Contest | None":
        """Return the single current contest."""
        return self.ongoing(when).first()


class Contest(models.Model):
    """A single contest in the competition."""

    objects = ContestManager()

    name = models.CharField(
        max_length=255, blank=False, help_text="Like '$25 Amazon Gift Card Giveaway'"
    )
    start_at = models.DateTimeField(blank=False)
    end_at = models.DateTimeField(blank=False)
    template = models.TextField(
        blank=False,
        help_text="A description of the contest. Can use {{ school.name }} to insert the school's name, etc.",  # noqa
        default="{{ school.short_name }} students: check your voter registration for a 1 in 10 chance to win a $25 Amazon gift card.",  # noqa
    )

    # For now, we assume that each contest is associated with a single school.
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="contests"
    )

    def is_upcoming(self, when: datetime.datetime | None = None) -> bool:
        """Return whether the contest is upcoming."""
        when = when or django_now()
        return self.start_at > when

    def is_ongoing(self, when: datetime.datetime | None = None) -> bool:
        """Return whether the contest is ongoing."""
        when = when or django_now()
        return self.start_at <= when < self.end_at

    def is_past(self, when: datetime.datetime | None = None) -> bool:
        """Return whether the contest is past."""
        when = when or django_now()
        return self.end_at <= when

    def description(self):
        """Render the contest template."""
        context = {"school": self.school, "contest": self}
        return Template(self.template).render(Context(context))

    def __str__(self):
        """Return the contest model's string representation."""
        return f"Contest: {self.name} for {self.school.name}"


class Student(models.Model):
    """A single student in the competition."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    hash = models.CharField(
        blank=False,
        max_length=64,
        unique=True,
        help_text="A deduped, hashed version of the student's email address.",
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    email = models.EmailField(
        blank=False, help_text="The student's primary email address."
    )
    phone = models.CharField(max_length=255, blank=True, default="")
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)

    @property
    def name(self) -> str:
        """Return the student's full name."""
        return f"{self.first_name} {self.last_name}"
