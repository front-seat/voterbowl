import datetime
import logging

from django.db import transaction

from server.utils.agcod import AGCODClient
from server.utils.email import send_template_email
from server.utils.tokens import make_token

from .models import Contest, EmailValidationLink, GiftCard, School, Student

logger = logging.getLogger(__name__)


class GiftCardPreconditionError(Exception):
    """Raised when a gift card cannot be issued due to a precondition."""

    pass


def _issue_gift_card(student: Student, contest: Contest) -> tuple[GiftCard, str]:
    """
    Low level routine to issue a new gift card.

    Should not be called directly. Use get_or_issue_gift_card instead, which
    checks preconditions and handles transactions.
    """
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
    gift_card = GiftCard.objects.create(
        student=student,
        contest=contest,
        amount=contest.amount,
        creation_request_id=response.creation_request_id,
    )
    return gift_card, response.gc_claim_code


def _get_claim_code(gift_card: GiftCard) -> str:
    """Return the claim code for a gift card if it is not currently known."""
    client = AGCODClient.from_settings()
    try:
        response = client.check_gift_card(
            gift_card.amount, gift_card.creation_request_id
        )
    except Exception as e:
        logger.exception(f"AGCOD failed for gift card {gift_card.creation_request_id}")
        raise ValueError(
            f"AGCOD failed for gift card {gift_card.creation_request_id}"
        ) from e
    return response.gc_claim_code


def get_or_issue_gift_card(
    student: Student, contest: Contest, when: datetime.datetime | None = None
) -> tuple[GiftCard, str]:
    """
    Issue a gift card to a student for a contest.

    If the student has already received a gift card for the contest,
    return the existing gift card.

    If the student is not eligible for the contest at this time,
    raise a GiftCardPreconditionError. If another error occurs, raise
    an arbitrary exception.

    Returns a tuple of the gift card and, if the gift card was issued,
    the claim code.
    """
    # Precondition: student must have a validated email address.
    if not student.is_validated:
        raise GiftCardPreconditionError(f"Student {student.email} is not validated")

    # Precondition: student must go to the same school as the contest.
    if student.school != contest.school:
        raise GiftCardPreconditionError(
            f"Student {student.email} is not eligible for contest '{contest.name}'"
        )

    # In a transaction, check if the student has already received a gift card
    # for the contest. If not, issue a new gift card.
    with transaction.atomic():
        try:
            gift_card = GiftCard.objects.get(student=student, contest=contest)
        except GiftCard.DoesNotExist:
            gift_card = None

        if gift_card is not None:
            claim_code = _get_claim_code(gift_card)
            return gift_card, claim_code

        # Precondition: the contest must be ongoing to truly issue a gift card.
        if not contest.is_ongoing(when):
            raise GiftCardPreconditionError(f"Contest '{contest.name}' is not ongoing")

        return _issue_gift_card(student, contest)


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
    student: Student, contest: Contest, email: str
) -> EmailValidationLink:
    """Generate a validation link to a student for a contest."""
    link = EmailValidationLink.objects.create(
        student=student, contest=contest, email=email, token=make_token(12)
    )
    success = send_template_email(
        to=email,
        template_base="email/validate",
        context={
            "student": student,
            "contest": contest,
            "email": email,
            "link": link,
            "title": f"Get my ${contest.amount} gift card",
        },
    )
    if not success:
        logger.error(f"Failed to send email validation link to {email}")
    return link
