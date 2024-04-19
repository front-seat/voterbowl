import logging

from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import EmailValidationLink, School
from .ops import (
    get_or_create_student,
    get_or_issue_gift_card,
    send_gift_card_email,
    send_validation_link_email,
)

logger = logging.getLogger(__name__)


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    """Render the voterbowl homepage."""
    return render(request, "home.dhtml")


@require_GET
def school(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Render a school landing page.

    Show details about the current contest, if there is one.

    If not, show details about the most recently completed contest,
    if there is one.

    Otherwise, show generic text encouraging the visitor to check their
    voter registration anyway.
    """
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current()
    past_contest = school.contests.most_recent_past()
    return render(
        request,
        "school.dhtml",
        {
            "school": school,
            "current_contest": current_contest,
            "past_contest": past_contest,
        },
    )


@require_GET
def check(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Render a school-specific 'check voter registration' form page.

    This does something useful whether or not the school has a current contest.
    """
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current()
    return render(
        request, "check.dhtml", {"school": school, "current_contest": current_contest}
    )


class FinishCheckForm(forms.Form):
    """Data POSTed to finish_check when user has completed a registration check."""

    _school: School

    def __init__(self, data, school: School):
        """Construct a FinishCheckForm."""
        super().__init__(data)
        self._school = school

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    def clean_email(self):
        """Ensure the email address is not already in use."""
        email = self.cleaned_data["email"]

        # DEBUG-mode email address bypass.
        if (
            settings.DEBUG
            and email.endswith("@example.edu")
            or email.endswith(".example.edu")
        ):
            self.cleaned_data["hash"] = "dbg-" + email
            return email
        self._school.validate_email(email)
        self.cleaned_data["hash"] = self._school.hash_email(email)
        return email

    def has_only_email_error(self):
        """Check if the only error is in the email field."""
        return "email" in self.errors and len(self.errors) == 1


@require_POST
@csrf_exempt  # CONSIDER: maybe use Django's CSRF protection even here?
def finish_check(request: HttpRequest, slug: str) -> HttpResponse:
    """
    View that is POSTed to when a student has completed a registration check.

    There may or may not be a current contest associated with the check.

    In addition, while we know the student's email ends with *.edu, we do not
    yet know if it is a valid email address for the school.
    """
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current()
    form = FinishCheckForm(request.POST, school=school)
    if not form.is_valid():
        if not form.has_only_email_error():
            raise PermissionDenied("Invalid")
        return render(
            request,
            "fail_check.dhtml",
            {
                "school": school,
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "current_contest": current_contest,
            },
        )
    email = form.cleaned_data["email"]

    # Create a new student if necessary.
    student = get_or_create_student(
        school=school,
        hash=form.cleaned_data["hash"],
        email=email,
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"],
    )

    # Always send a validation link EVEN if the student is validated.
    # This ensures we never show a gift code until we know the visitor
    # has access to the email address.
    send_validation_link_email(student, school, current_contest, email)

    return render(
        request,
        "finish_check.dhtml",
        {
            "school": school,
            "current_contest": current_contest,
            "email": email,
        },
    )


@require_GET
def validate_email(request: HttpRequest, slug: str, token: str) -> HttpResponse:
    """
    View visited when a user clicks on a validation link in their email.

    There may or may not be a current contest associated with the validation.

    If the student reaches this point, we know they have a valid email that
    matches the school in question.
    """
    link = get_object_or_404(EmailValidationLink, token=token)
    school = get_object_or_404(School, slug=slug)
    if link.school != school:
        raise PermissionDenied("Invalid email validation link URL")

    # The student is validated now!
    link.consume()

    # If there's a contest associated with the validation, get a gift card.
    gift_card, claim_code, error = None, None, False
    if link.contest is not None:
        try:
            gift_card, claim_code, created = get_or_issue_gift_card(
                link.student, link.contest
            )
            if created:
                send_gift_card_email(link.student, gift_card, claim_code, link.email)
        except Exception:
            # If we fail to issue or re-obtain a gift card,
            # log the error and report to the student.
            logger.exception(
                "Failed to obtain gift card student: {link.student} token: {token}"
            )
            gift_card, claim_code, error = None, None, True

    return render(
        request,
        "verify_email.dhtml",
        {
            "school": school,
            "student": link.student,
            "gift_card": gift_card,
            "claim_code": claim_code,
            "error": error,
        },
    )
