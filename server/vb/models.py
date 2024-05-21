import base64
import datetime
import hashlib
import secrets
import typing as t

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
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
    percent_voted_2020 = models.IntegerField(
        blank=True,
        default=0,
        help_text="If known, the percentage of students who voted in 2020 (like 70).",
    )

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
    allow_subdomains = models.BooleanField(
        default=True,
        help_text="Whether to allow arbitrary subdomains in school emails.",
    )

    logo: "Logo"
    contests: "ContestManager"
    students: "StudentManager"

    def normalize_email(self, address: str) -> str:
        """Normalize an email address for this school."""
        domains = Domains(self.mail_domains[0], tuple(self.mail_domains[1:]))
        return normalize_email(
            address,
            tag=self.mail_tag if self.mail_tag else None,
            dots=self.mail_dots,
            domains=domains,
            allow_subdomains=self.allow_subdomains,
        )

    def hash_email(self, address: str) -> str:
        """
        Hash an email address for this school.

        These hashes are not suitable for sharing with third parties, since
        they are trivial to reverse-engineer.
        """
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

    @property
    def relative_url(self) -> str:
        """Return the relative URL for the school."""
        return reverse("vb:school", args=[self.slug])

    @property
    def absolute_url(self) -> str:
        """Return the absolute URL for the school."""
        return f"{settings.BASE_URL}{self.relative_url}"


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


class ContestKind(models.TextChoices):
    """The various kinds of contests."""

    # Every student wins a prize (gift card; charitable donation; etc.)
    GIVEAWAY = "giveaway", "Giveaway"

    # Every student rolls a dice; some students win a prize.
    DICE_ROLL = "dice_roll", "Dice roll"

    # A single student wins a prize after the contest ends.
    SINGLE_WINNER = "single_winner", "Single winner"

    # No prizes are awarded.
    NO_PRIZE = "no_prize", "No prize"


class ContestWorkflow(models.TextChoices):
    """The various workflows for contests."""

    # Issue an amazon gift card and email automatically
    AMAZON = "amazon", "Amazon"

    # No automated workflow; manual intervention may be required
    NONE = "none", "None"


class ContestTool(models.TextChoices):
    """The registration tool for the contest."""

    VOTE_AMERICA = "vote_america", "Vote America"
    ROCK_THE_VOTE = "rock_the_vote", "Rock the Vote"


class Contest(models.Model):
    """A single contest in the competition."""

    objects: ContestManager = ContestManager()

    # For now, we assume that each contest is associated with a single school.
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="contests"
    )

    # Contests have strictly defined start and end times.
    start_at = models.DateTimeField(blank=False)
    end_at = models.DateTimeField(blank=False)

    # We support running contests with different registration tools.
    tool = models.CharField(
        max_length=32,
        choices=ContestTool.choices,
        blank=False,
        default=ContestTool.VOTE_AMERICA,
    )

    # The assumptions here have changed basically weekly as we gather more
    # data and learn more. As of this writing, our current assumptions are:
    #
    # 1. We support four kinds of contest:
    #
    #   - Giveaway: every student immediately wins a prize.
    #   - Dice roll: every student rolls a dice and may immediately win a prize.
    #   - Single winner: a single student wins a prize after the contest ends.
    #   - No prize: no prizes are awarded.

    kind = models.CharField(
        max_length=32,
        choices=ContestKind.choices,
        blank=False,
        default=ContestKind.GIVEAWAY,
    )

    in_n = models.IntegerField(
        blank=False,
        help_text="1 in_n students will win a prize.",
        default=1,
    )

    # 2. Some contests require automated workflows to award prizes. Currently
    #    we only have one such action: 'amazon', for issuing Amazon gift cards
    #    and sending emails to the winners.

    workflow = models.CharField(
        max_length=32,
        choices=ContestWorkflow.choices,
        blank=False,
        default=ContestWorkflow.AMAZON,
    )

    # 3. Prizes need short and long descriptions.
    #
    #    For instance, historically we used "gift card" and "Amazon gift card"
    #    as our descriptions.
    #
    #    Newer examples include "gift card" and "prepaid Visa gift card", or
    #    "donation" and "donation to charity".
    #
    #    Monetary prizes have a dollar amount associated with them.
    amount = models.IntegerField(
        blank=False, help_text="The amount of the prize.", default=0
    )

    prize = models.CharField(
        max_length=255,
        blank=True,
        default="gift card",
        help_text="A short description of the prize, if any.",
    )
    prize_long = models.CharField(
        max_length=255,
        blank=True,
        default="Amazon gift card",
        help_text="A long description of the prize, if any.",
    )

    contest_entries: "ContestEntryManager"

    @property
    def has_immmediate_winners(self) -> bool:
        """Return whether the contest has immediate winners."""
        return self.is_giveaway or self.is_dice_roll

    def most_recent_winner(self) -> "ContestEntry | None":
        """
        Return the most recent winner for this contest.

        Return None if there is not yet a winner, or if the contest has no
        immediate winners.
        """
        if not self.has_immmediate_winners:
            return None
        return self.contest_entries.winners().order_by("-created_at").first()

    @property
    def is_dice_roll(self) -> bool:
        """Return whether the contest is a dice roll."""
        return self.kind == ContestKind.DICE_ROLL

    @property
    def is_giveaway(self) -> bool:
        """Return whether the contest is a giveaway."""
        return self.kind == ContestKind.GIVEAWAY

    @property
    def is_single_winner(self) -> bool:
        """Return whether the contest is a single winner."""
        return self.kind == ContestKind.SINGLE_WINNER

    @property
    def is_no_prize(self) -> bool:
        """Return whether the contest is a no prize."""
        return self.kind == ContestKind.NO_PRIZE

    @property
    def is_monetary(self) -> bool:
        """Return whether the contest has a monetary prize."""
        return self.amount > 0

    def roll_die_and_get_winnings(self) -> tuple[int, int]:
        """
        Roll a fair die from [0, self.in_n).

        Return a tuple of the roll and the amount won (or 0 if no win).
        """
        if self.is_no_prize or self.is_single_winner:
            return (1, 0)
        if self.is_giveaway:
            return (0, self.amount)
        # self.is_dice_roll
        roll = secrets.randbelow(self.in_n)
        amount_won = self.amount if roll == 0 else 0
        return roll, amount_won

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

    @property
    def name(self) -> str:
        """Render an administrative name for the template."""
        if self.is_no_prize:
            return "No prize"
        elif self.is_giveaway:
            # 1 Tree Planted, $5 Amazon Gift Card
            if self.is_monetary:
                return f"${self.amount:,} {self.prize_long.title()} Giveaway"
            return f"{self.prize_long.title()}"
        elif self.is_dice_roll:
            if self.is_monetary:
                return f"${self.amount:,} {self.prize_long.title()} Contest (1 in {self.in_n} wins)"  # noqa
            return f"{self.prize_long.title()} (1 in {self.in_n} wins)"
        elif self.is_single_winner:
            if self.is_monetary:
                return f"${self.amount:,} {self.prize_long.title()} Drawing"
            return f"{self.prize_long.title()} Drawing"
        raise ValueError("Unknown contest kind")

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
        help_text="The second+ emails for this user. These *are* validated.",
    )
    email_validated_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        db_index=True,
        help_text="The first time *any* email for this student was validated.",
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
        return (self.email_validated_at is not None) or len(self.other_emails) > 0

    def mark_validated(
        self,
        email: str,
        when: datetime.datetime | None = None,
    ) -> None:
        """
        Mark a given email address as validated for a student.

        If the email is *not* the current primary email, make it so, moving
        the current primary email to the list of other emails.
        """
        # Get a set of all emails for this student, including the new one.
        all_emails = set(self.other_emails + [self.email] + [email])
        assert email in all_emails  # how could this not be true?

        # Remove the new one from the set and make it our new primary
        all_emails.remove(email)
        self.email = email

        # Take all remaining emails and make them "other" emails
        self.other_emails = list(all_emails)

        # Mark the student as having at least one validated email.
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

    def __str__(self) -> str:
        """Return myself as a string."""
        return f"{self.name} <{self.email}>"


class EmailValidationLinkManager(models.Manager):
    """A custom manager for the email validation link model."""

    def consumed(self):
        """Return all email validation links that are consumed."""
        return self.filter(consumed_at__isnull=False)

    def not_consumed(self):
        """Return all email validation links that are not consumed."""
        return self.filter(consumed_at__isnull=True)


class EmailValidationLink(models.Model):
    """A single email validation link for a student in a contest."""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="email_validation_links"
    )

    email = models.EmailField(
        blank=False,
        help_text="The specific email address to be validated.",
    )

    # TODO
    #
    # As of this writing, contest_entry should *never* be null when we create
    # an email validation link. More than that: it should *always* be a winning
    # contest entry. For historical reasons, we have null=True here; I haven't
    # wanted to go back and clean up the production database for this.
    contest_entry = models.ForeignKey(
        "ContestEntry",
        on_delete=models.CASCADE,
        related_name="email_validation_links",
        blank=True,
        null=True,
        default=None,
        help_text="The contest entry, if any, associated with this email validation link.",  # noqa
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
        return reverse("vb:validate_email", args=[self.student.school.slug, self.token])

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
        self.student.mark_validated(self.email, when)


class ContestEntryManager(models.Manager):
    """A custom manager for the contest entry model."""

    def winners(self):
        """Return all contest entries that won a prize."""
        return self.filter(roll=0)

    def losers(self):
        """Return all contest entries that did not win a prize."""
        return self.exclude(roll=0)


class ContestEntry(models.Model):
    """
    A contest entry by a single student for a single contest.

    When contest entries are created, they are either winners or losers.

    Winning contest entries have a prize amount associated with them.
    At some later point, the prize amount can be issued as a gift card; this
    is represented by a creation request ID.
    """

    objects = ContestEntryManager()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="contest_entries"
    )
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="contest_entries"
    )

    roll = models.IntegerField(
        blank=False,
        db_index=True,
        help_text="The result of the entry dice roll. 0 is a win.",
    )

    @property
    def is_winner(self) -> bool:
        """Return whether the student won a prize."""
        return self.roll == 0

    # The prize, if any, is a gift card.
    #
    # TODO: these next three fields are tied to the contest entry for
    # historical reasons, but they should be moved to a separate model with a
    # one-to-one relationship.
    amount_won = models.IntegerField(
        blank=False,
        default=0,
        help_text="The USD amount won.",
    )
    creation_request_id = models.CharField(
        blank=True,
        max_length=255,
        default="",
        help_text="The creation code for the gift card, if a prize was issued.",
    )

    @property
    def has_issued(self) -> bool:
        """Return whether a gift card has been issued."""
        return bool(self.creation_request_id)

    @property
    def needs_to_issue(self) -> bool:
        """Return whether a gift card needs to be issued."""
        return self.is_winner and not self.has_issued

    def clean(self):
        """Clean the contest entry model."""
        if (self.roll == 0) and (self.amount_won == 0):
            raise ValidationError("Winning contest entries must have a prize amount.")
        if (self.roll != 0) and (self.amount_won != 0):
            raise ValidationError(
                "Non-winning contest entries must not have a prize amount."
            )
        super().clean()

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
        return f"Contest entry for {self.student.name} in {self.contest.name} (${self.amount_won} won)"  # noqa
