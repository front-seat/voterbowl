import logging

from django.db import transaction

from server.utils.agcod import AGCODClient

from .models import Contest, GiftCard, Student

logger = logging.getLogger(__name__)


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


def get_or_issue_gift_card(
    student: Student, contest: Contest
) -> tuple[GiftCard, str | None]:
    """
    Issue a gift card to a student for a contest.

    If the student has already received a gift card for the contest,
    return the existing gift card.

    If the student is not eligible, or issuing a gift card fails, an
    exception is raised.

    Returns a tuple of the gift card and, if the gift card was issued,
    the claim code.
    """
    # Precondition: student must have a validated email address.
    if not student.is_validated:
        raise ValueError(f"Student {student.email} is not validated")
    # Precondition: student must go to the same school as the contest.
    if student.school != contest.school:
        raise ValueError(
            f"Student {student.email} is not eligible for contest '{contest.name}'"
        )

    # In a transaction, check if the student has already received a gift card
    # for the contest. If not, issue a new gift card.
    with transaction.atomic():
        try:
            gift_card = GiftCard.objects.get(student=student, contest=contest)
            return gift_card, None
        except GiftCard.DoesNotExist:
            return _issue_gift_card(student, contest)


def get_claim_code(gift_card: GiftCard) -> str:
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
