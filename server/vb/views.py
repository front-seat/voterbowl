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
    send_validation_link_email,
)


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    """Render the voterbowl homepage."""
    return render(request, "home.dhtml")


@require_GET
def school(request: HttpRequest, slug: str) -> HttpResponse:
    """Render a school page."""
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current()
    return render(
        request, "school.dhtml", {"school": school, "current_contest": current_contest}
    )


@require_GET
def check(request: HttpRequest, slug: str) -> HttpResponse:
    """Render a school-specific check registration page."""
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


@require_POST
@csrf_exempt  # CONSIDER: maybe use Django's CSRF protection even here?
def finish_check(request: HttpRequest, slug: str) -> HttpResponse:
    """Handle a check registration form submission."""
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current()
    if not current_contest:
        raise ValueError("No active contest TODO")
    form = FinishCheckForm(request.POST, school=school)
    if not form.is_valid():
        raise PermissionDenied("Invalid form")
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
    send_validation_link_email(student, current_contest, email)

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
    """Handle a student email validation link."""
    link = get_object_or_404(EmailValidationLink, token=token)
    school = get_object_or_404(School, slug=slug)
    if link.school != school:
        raise PermissionDenied("Invalid email validation link URL")

    # It's money time!
    link.consume()
    gift_card, claim_code = get_or_issue_gift_card(link.student, link.contest)

    return render(
        request,
        "verify_email.dhtml",
        {
            "school": school,
            "student": link.student,
            "gift_card": gift_card,
            "claim_code": claim_code,
        },
    )
