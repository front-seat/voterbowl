import base64
import datetime
import typing as t

from django.db import models
from django.template import Context, Template
from django.utils.timezone import now as django_now

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

    contests: "ContestManager"

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

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    email = models.EmailField(blank=False)
    phone = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)

    @property
    def name(self) -> str:
        """Return the student's full name."""
        return f"{self.first_name} {self.last_name}"


class ActionKinds(models.TextChoices):
    """Kinds of actions in the competition."""

    FIRST_VISIT = "first_visit"
    CHECK_REGISTRATION = "check_registration"
    REGISTER = "register"


class Action(models.Model):
    """A single action in the competition."""

    taken_at = models.DateTimeField(auto_now_add=True)
    kind = models.CharField(max_length=32, choices=ActionKinds.choices, blank=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, null=True, default=None
    )

    def __str__(self):
        """Return the action model's string representation."""
        return f"Action: {self.kind} by {self.student.name} at {self.taken_at}"
