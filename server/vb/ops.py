import datetime
import logging

from django.db import transaction

from server.utils.agcod import AGCODClient
from server.utils.email import send_template_email
from server.utils.tokens import make_token

from .models import Contest, ContestEntry, EmailValidationLink, School, Student

logger = logging.getLogger(__name__)


class ContestEntryPreconditionError(Exception):
    """Raised when a contest cannot be entered due to a precondition."""

    pass


# -----------------------------------------------------------------------------
# Contest Management
# -----------------------------------------------------------------------------


def _create_contest_entry(student: Student, contest: Contest) -> ContestEntry:
    """
    Low level routine to enter a contest and, possibly, mint a winner.

    Should not be called directly. Use enter_contest instead, which
    checks preconditions and handles transactions.
    """
    # Decide if the student is a winner! If the contest is 1-in-1 then
    # this will always be True.
    minted = contest.mint_winner()
    return ContestEntry.objects.create(
        student=student,
        contest=contest,
        amount=contest.amount if minted else 0,
    )


def enter_contest(
    student: Student, contest: Contest, when: datetime.datetime | None = None
) -> tuple[ContestEntry, bool]:
    """
    Return a contest entry for a student.

    If the student has already entered the contest, return their existing entry.
    Otherwise, assuming they are eligible, create a new entry.

    If the student is not eligible, raise a ContestEntryPreconditionError.

    The entry may or may not be a winner. If it is, an `amount` will be set.
    No gift card is issued at this time.
    """
    # Precondition: student must go to the same school as the contest.
    if student.school != contest.school:
        raise ContestEntryPreconditionError(
            f"Student {student.email} is not eligible for contest '{contest.name}'"
        )

    # In a transaction, check if the student has already entered the contest.
    # If they haven't, enter them (assuming further preconditions are met).
    with transaction.atomic():
        try:
            contest_entry = ContestEntry.objects.get(student=student, contest=contest)
            return contest_entry, False
        except ContestEntry.DoesNotExist:
            contest_entry = None

        # Precondition: the contest must be ongoing in order to win.
        if not contest.is_ongoing(when):
            raise ContestEntryPreconditionError(
                f"Student {student.email} cannot enter inactive '{contest.name}'"
            )

        return _create_contest_entry(student, contest), True


# -----------------------------------------------------------------------------
# Gift Card Management
# -----------------------------------------------------------------------------


def get_or_issue_prize(
    contest_entry: ContestEntry,
) -> tuple[ContestEntry, str | None]:
    """
    Issue a gift card for a contest entry, if applicable.

    Return the gift card claim code, if any.

    Raise an exeption if unable to issue a gift card or obtain the claim code.
    """
    # For each contest the student has entered, issue a gift card if they won.
    if contest_entry.is_winner:
        if contest_entry.has_issued:
            return contest_entry, _get_claim_code(contest_entry)
        else:
            contest_entry, claim_code = _create_gift_card(contest_entry)
            send_gift_card_email(contest_entry, claim_code)
            return contest_entry, claim_code
    else:
        return contest_entry, None


def _create_gift_card(contest_entry: ContestEntry) -> tuple[ContestEntry, str]:
    """Create a new gift card for a student in the amount of `amount`."""
    client = AGCODClient.from_settings()
    try:
        response = client.create_gift_card(contest_entry.amount)
    except Exception as e:
        logger.exception(
            f"AGCOD failed for contest entry {contest_entry.pk} {contest_entry.student.email}"  # noqa
        )
        raise ValueError(
            f"AGCOD failed for contest entry {contest_entry.pk} {contest_entry.student.email}"  # noqa
        ) from e
    contest_entry.creation_request_id = response.creation_request_id
    contest_entry.save()
    return contest_entry, response.gc_claim_code


def _get_claim_code(contest_entry: ContestEntry) -> str:
    """
    Return the gift card claim code for a contest entry, if any.

    Raise an exception if unable to obtain the claim code.
    """
    # Otherwise, they do!
    client = AGCODClient.from_settings()
    try:
        response = client.check_gift_card(
            contest_entry.amount, contest_entry.creation_request_id
        )
    except Exception as e:
        logger.exception(
            f"AGCOD failed for gift card {contest_entry.creation_request_id}"
        )
        raise ValueError(
            f"AGCOD failed for gift card {contest_entry.creation_request_id}"
        ) from e
    return response.gc_claim_code


# -----------------------------------------------------------------------------
# Student Management
# -----------------------------------------------------------------------------


def get_or_create_student(
    school: School, hash: str, email: str, first_name: str, last_name: str
) -> Student:
    """Get or create a student by hash."""
    student, _ = Student.objects.get_or_create(
        hash=hash,
        school=school,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        },
    )
    return student


# -----------------------------------------------------------------------------
# Emails
# -----------------------------------------------------------------------------


def send_validation_link_email(
    student: Student, email: str, contest_entry: ContestEntry | None
) -> EmailValidationLink:
    """Generate a validation link to a student for a contest."""
    link = EmailValidationLink.objects.create(
        student=student,
        email=email,
        contest_entry=contest_entry,
        token=make_token(12),
    )
    if contest_entry and contest_entry.is_winner:
        button_text = f"Get my ${contest_entry.amount} gift card"
    else:
        button_text = "Validate my email"
    success = send_template_email(
        to=email,
        template_base="email/validate",
        context={
            "student": student,
            "contest_entry": contest_entry,
            "email": email,
            "link": link,
            "button_text": button_text,
        },
    )
    if not success:
        logger.error(f"Failed to send email validation link to {email}")
    return link


def send_gift_card_email(
    contest_entry: ContestEntry,
    claim_code: str,
) -> None:
    """Send a gift card email to a student if they won."""
    assert contest_entry.is_winner
    success = send_template_email(
        to=contest_entry.student.email,
        template_base="email/code",
        context={
            "student": contest_entry.student,
            "school": contest_entry.student.school,
            "contest_entry": contest_entry,
            "claim_code": claim_code,
        },
    )
    if not success:
        logger.error(f"Failed to send gift card email to {contest_entry.student.email}")
