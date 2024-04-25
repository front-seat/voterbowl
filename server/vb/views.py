import logging

from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import EmailValidationLink, School
from .ops import (
    enter_contest,
    get_or_create_student,
    get_or_issue_prize,
    send_validation_link_email,
)

logger = logging.getLogger(__name__)


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    """Render the voterbowl homepage."""
    # return render(request, "home.dhtml")
    return redirect("/mga/", permanent=False)


@require_GET
def rules(request: HttpRequest) -> HttpResponse:
    """Render the voterbowl rules page."""
    return render(request, "rules.dhtml")


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

    # Enter the student into the contest if there is one and they aren't
    # already entered. (Otherwise, get their existing entry.)
    contest_entry = None
    if current_contest is not None:
        contest_entry, _ = enter_contest(student, current_contest)

    # Send the student an email validation link.
    #
    # In the case where (a) there's no contest, or (b) there's a contest
    # but the student didn't win, this is a simple validation link. In theory,
    # this is unnecessary if the given email has already been validated,
    # but we send it anyway for consistency.
    #
    # In the case where the student *won* a contest, this link is used
    # to claim their prize. We need to ensure the student has current access
    # to the email address before we issue the prize (aka deduct money from
    # our account).
    send_validation_link_email(student, email, contest_entry)

    return render(
        request,
        "finish_check.dhtml",
        {
            "school": school,
            "current_contest": current_contest,
            "contest_entry": contest_entry,
            "email": email,
        },
    )


@require_GET
def validate_email(request: HttpRequest, slug: str, token: str) -> HttpResponse:
    """
    View visited when a user clicks on a validation link in their email.

    When a student reaches this point, we know (a) the email address is valid,
    (b) it's valid for the school, and (c) the student has access to the email
    address.

    This is our opportunity to check the student's contest entries and issue
    any outstanding prizes. A student visiting this link may have entered zero
    or more contests.

    It's possible the user has clicked this validation link before. Behavior
    must be idempotent.
    """
    link = get_object_or_404(EmailValidationLink, token=token)
    school = get_object_or_404(School, slug=slug)
    if link.student.school != school:
        raise PermissionDenied("Invalid email validation link URL")

    # This email address is validated. As a result, the student is also
    # validated.
    link.consume()

    # Issue a prize, if appropriate
    contest_entry, claim_code, error = None, None, False
    if link.contest_entry is not None:
        try:
            contest_entry, claim_code = get_or_issue_prize(link.contest_entry)
        except Exception:
            error = True

    return render(
        request,
        "verify_email.dhtml",
        {
            "BASE_URL": settings.BASE_URL,
            "school": school,
            "student": link.student,
            "contest_entry": contest_entry,
            "claim_code": claim_code,
            "error": error,
        },
    )
