import base64
import datetime
import hashlib
import secrets
import typing as t

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template import Context, Template
from django.urls import reverse
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

    # Fields that define how the school handles email addresses.
    # This allows us both to validate that a school-matching email address is
    # used, and to normalize email addresses for deduplication.
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
    students: "StudentManager"
    email_validation_links: "EmailValidationLinkManager"

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

    def most_recent_past(
        self, when: datetime.datetime | None = None
    ) -> "Contest | None":
        """Return the single most recent past contest, if any."""
        return self.past(when).order_by("-end_at").first()

    def current(self, when: datetime.datetime | None = None) -> "Contest | None":
        """Return the single current contest."""
        return self.ongoing(when).first()


class Contest(models.Model):
    """A single contest in the competition."""

    objects = ContestManager()

    # For now, we assume that each contest is associated with a single school.
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="contests"
    )

    # Contests have strictly defined start and end times.
    start_at = models.DateTimeField(blank=False)
    end_at = models.DateTimeField(blank=False)

    # For now, we assume:
    #
    # 1. Anyone who checks their voter registration during the contest period
    #    is a winner.
    # 2. All winners receive the same Amazon gift card amount as a prize.
    amount = models.IntegerField(
        blank=False, help_text="The USD amount of the gift card.", default=5
    )
    in_n = models.IntegerField(
        blank=False,
        help_text="1 in_n students will win a gift card.",
        default=1,
    )

    contest_entries: "ContestEntryManager"

    @property
    def name(self) -> str:
        """Render the contest name template."""
        if self.in_n > 1:
            template_str = "${{ contest.amount }} Amazon Gift Card Giveaway (1 in {{ contest.in_n }} wins)"  # noqa
        else:
            template_str = "${{ contest.amount }} Amazon Gift Card Giveaway"
        context = {"school": self.school, "contest": self}
        return Template(template_str).render(Context(context))

    @property
    def is_giveaway(self) -> bool:
        """Return whether the contest is a giveaway."""
        return self.in_n == 1

    @property
    def description(self) -> str:
        """Render the contest description template."""
        template_str = "{{ school.short_name }} students: check your voter registration to win a ${{ contest.amount }} Amazon gift card."  # noqa
        context = {"school": self.school, "contest": self}
        return Template(template_str).render(Context(context))

    def mint_winner(self) -> bool:
        """Determine whether to mint a new contest winner."""
        return secrets.randbelow(self.in_n) == 0

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

    def __str__(self):
        """Return the contest model's string representation."""
        return f"Contest: {self.name} for {self.school.name}"


class StudentManager(models.Manager):
    """A custom manager for the student model."""

    def validated(self):
        """Return all students with validated email addresses."""
        return self.filter(email_validated_at__isnull=False)

    def not_validated(self):
        """Return all students without validated email addresses."""
        return self.filter(email_validated_at__isnull=True)


class Student(models.Model):
    """
    A student that visited our website and checked their voter registration.

    Unless an email address is validated, we should not generate a gift card.
    """

    objects = StudentManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="students"
    )

    # Email management is a little complex for us.
    email = models.EmailField(
        blank=False,
        help_text="The first email address we ever saw for this user.",
        unique=True,
    )
    hash = models.CharField(
        blank=False,
        max_length=64,
        unique=True,
        help_text="A unique ID for the student derived from their email address.",
    )
    other_emails = models.JSONField(
        default=list,
        blank=True,
        help_text="The second+ emails for this user. These may not be validated.",
    )
    email_validated_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        db_index=True,
        help_text="The time the email was validated.",
    )

    # Other identifying information
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    phone = models.CharField(max_length=255, blank=True, default="")

    contest_entries: "ContestEntryManager"
    email_validation_links: "EmailValidationLinkManager"

    @property
    def is_validated(self) -> bool:
        """Return whether the student's email address is validated."""
        return self.email_validated_at is not None

    def mark_validated(self, when: datetime.datetime | None = None) -> None:
        """Mark the student's email address as validated."""
        self.email_validated_at = self.email_validated_at or when or django_now()
        self.save()

    @property
    def name(self) -> str:
        """Return the student's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def anonymized_name(self) -> str:
        """Return the student's anonymized name."""
        return f"{self.first_name} {self.last_name[0]}."

    def add_email(self, email: str) -> None:
        """Add an email address to the student's list of emails."""
        if email != self.email and email not in self.other_emails:
            self.other_emails.append(email)
            self.save()


class EmailValidationLinkManager(models.Manager):
    """A custom manager for the email validation link model."""

    OLD_DELTA = datetime.timedelta(days=7)

    def consumed(self):
        """Return all email validation links that are consumed."""
        return self.filter(consumed_at__isnull=False)

    def not_consumed(self):
        """Return all email validation links that are not consumed."""
        return self.filter(consumed_at__isnull=True)

    def old(self, when: datetime.datetime | None = None):
        """Return all email validation links that are old."""
        when = when or django_now()
        return self.filter(created_at__lt=when - self.OLD_DELTA)


class EmailValidationLink(models.Model):
    """A single email validation link for a student in a contest."""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="email_validation_links"
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="email_validation_links",
    )
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="email_validation_links",
        null=True,
        # A user may still check registration outside of a contest.
        # CONSTRAINT: contest.school must == student.school
    )

    email = models.EmailField(
        blank=False,
        help_text="The specific email address to be validated.",
    )

    token = models.CharField(
        blank=False,
        max_length=255,
        unique=True,
        help_text="The current validation token, if any.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The time the email validation link was most recently created.",
    )
    consumed_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        help_text="The time the email validation link was first consumed.",
    )

    @property
    def relative_url(self) -> str:
        """Return the relative URL for the email validation link."""
        return reverse("vb:validate_email", args=[self.school.slug, self.token])

    @property
    def absolute_url(self) -> str:
        """Return the absolute URL for the email validation link."""
        return f"{settings.BASE_URL}{self.relative_url}"

    def is_consumed(self) -> bool:
        """Return whether the email validation link has been consumed."""
        return self.consumed_at is not None

    def consume(self, when: datetime.datetime | None = None) -> None:
        """Consume the email validation link."""
        when = when or django_now()
        self.consumed_at = when
        self.save()

        # Demeter says no, but my heart says yes.
        self.student.mark_validated(when)


class ContestEntryManager(models.Manager):
    """A custom manager for the contest entry model."""

    def winners(self):
        """Return all contest entries that won a prize."""
        return self.filter(amount__gt=0)

    def losers(self):
        """Return all contest entries that did not win a prize."""
        return self.filter(amount=0)


class ContestEntry(models.Model):
    """A contest entry by a single student for a single contest."""

    objects = ContestEntryManager()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="contest_entries"
    )
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="contest_entries"
    )

    # The prize, if any, is a gift card.
    amount = models.IntegerField(
        blank=False,
        default=0,
        help_text="The USD amount of the gift card. 0 means no gift card.",
    )
    creation_request_id = models.CharField(
        blank=True,
        max_length=255,
        default="",
        help_text="The creation code for the gift card, if a prize was won..",
    )
    email_sent_at = models.DateTimeField(blank=True, null=True, default=None)

    @property
    def is_winner(self) -> bool:
        """Return whether the student won a prize."""
        return self.amount > 0

    class Meta:
        """Define the contest entry model's meta options."""

        verbose_name_plural = "Contest entries"

        constraints = [
            models.UniqueConstraint(
                fields=["student", "contest"],
                # Should be renamed unique_student_contest_entry
                name="unique_student_contest_gift_card",
            )
        ]

    def __str__(self):
        """Return the gift card model's string representation."""
        return f"Contest entry for {self.student.name} in {self.contest.name} (${self.amount} won)"  # noqa
