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


def _create_losing_contest_entry(student: Student, contest: Contest) -> ContestEntry:
    """Create a contest entry for a student who did not win."""
    return ContestEntry.objects.create(student=student, contest=contest)


def _create_contest_entry(
    student: Student, contest: Contest
) -> tuple[ContestEntry, str | None]:
    """
    Low level routine to enter a contest and, possibly, issue a gift card.

    Should not be called directly. Use enter_contest instead, which
    checks preconditions and handles transactions.
    """
    # Decide if the student is a winner! If the contest is 1-in-1 then
    # this will always be True.
    minted = contest.mint_winner()
    if not minted:
        return _create_losing_contest_entry(student, contest), None

    # The student won, so issue a gift card!
    client = AGCODClient.from_settings()
    try:
        response = client.create_gift_card(contest.amount)
    except Exception as e:
        logger.exception(
            f"AGCOD failed for student {student.email} and contest {contest.pk}"
        )
        raise ValueError(
            f"AGCOD failed for student {student.email} and contest {contest.pk}"
        ) from e
    contest_entry = ContestEntry.objects.create(
        student=student,
        contest=contest,
        amount=contest.amount,
        creation_request_id=response.creation_request_id,
    )
    return contest_entry, response.gc_claim_code


def _get_claim_code(contest_entry: ContestEntry) -> str | None:
    """
    Return the gift card claim code for a contest entry, if any.

    Raise an exception if unable to obtain the claim code.
    """
    # Non-winning contest entries don't have a claim code.
    if not contest_entry.is_winner:
        return None

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
    # Precondition: student must have a validated email address.
    if not student.is_validated:
        raise ContestEntryPreconditionError(f"Student {student.email} is not validated")

    # Precondition: student must go to the same school as the contest.
    if student.school != contest.school:
        raise ContestEntryPreconditionError(
            f"Student {student.email} is not eligible for contest '{contest.name}'"
        )

    # In a transaction, check if the student has already entered the contest.
    # If they haven't, see if they're a winner. And if they are, issue a gift card.
    with transaction.atomic():
        try:
            contest_entry = ContestEntry.objects.get(student=student, contest=contest)
        except ContestEntry.DoesNotExist:
            contest_entry = None

        # The student already entered this contest. Return their wininng claim
        # code, *if any*. (The entry may not have been a winner.)
        if contest_entry is not None:
            claim_code = _get_claim_code(contest_entry)
            return contest_entry, claim_code, False

        # Precondition: the contest must be ongoing in order to win.
        if not contest.is_ongoing(when):
            return _create_losing_contest_entry(student, contest), None, True

        contest_entry, claim_code = _create_contest_entry(student, contest)
        return contest_entry, claim_code, True


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
    student.add_email(email)
    return student


def send_validation_link_email(
    student: Student, school: School, contest: Contest | None, email: str
) -> EmailValidationLink:
    """Generate a validation link to a student for a contest."""
    link = EmailValidationLink.objects.create(
        student=student,
        school=school,
        contest=contest,
        email=email,
        token=make_token(12),
    )
    if contest:
        if contest.is_giveaway:
            button_text = f"Get my ${contest.amount} gift card"
        else:
            button_text = f"See if I won a ${contest.amount} gift card"
    else:
        button_text = "Validate my email"
    success = send_template_email(
        to=email,
        template_base="email/validate",
        context={
            "student": student,
            "contest": contest,
            "email": email,
            "link": link,
            "button_text": button_text,
        },
    )
    if not success:
        logger.error(f"Failed to send email validation link to {email}")
    return link


def send_gift_card_email(
    student: Student,
    contest_entry: ContestEntry,
    claim_code: str,
    email: str,
) -> None:
    """Send a gift card email to a student if they won."""
    assert contest_entry.is_winner
    success = send_template_email(
        to=email,
        template_base="email/code",
        context={
            "student": student,
            "school": student.school,
            "contest_entry": contest_entry,
            "claim_code": claim_code,
        },
    )
    if not success:
        logger.error(f"Failed to send gift card email to {email}")
