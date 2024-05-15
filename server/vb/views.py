import logging

from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now as dj_now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .components.check_page import check_page, fail_check_partial, finish_check_partial
from .components.home_page import home_page
from .components.rules_page import rules_page
from .components.school_page import school_page
from .components.validate_email_page import validate_email_page
from .models import Contest, EmailValidationLink, School
from .ops import (
    enter_contest,
    get_or_create_student,
    get_or_issue_prize,
    process_contest_workflow,
)

logger = logging.getLogger(__name__)


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    """Render the voterbowl homepage."""
    ongoing_contests = Contest.objects.ongoing().order_by("end_at")
    upcoming_contests = Contest.objects.upcoming().order_by("start_at")
    return HttpResponse(home_page(ongoing_contests, upcoming_contests))


@require_GET
def rules(request: HttpRequest) -> HttpResponse:
    """Render the voterbowl rules page."""
    return HttpResponse(rules_page())


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
    school = School.objects.filter(slug=slug).first()
    if school is None:
        return redirect("vb:home", permanent=False)
    current_contest = school.contests.current()
    past_contest = school.contests.most_recent_past()
    return HttpResponse(school_page(school, current_contest, past_contest))


@require_GET
def check(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Render a school-specific 'check voter registration' form page.

    This does something useful whether or not the school has a current contest.
    """
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current()
    return HttpResponse(check_page(school, current_contest))


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
    # Use a consistent time so that contest entry is not skewed
    when = dj_now()
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current(when=when)
    form = FinishCheckForm(request.POST, school=school)
    if not form.is_valid():
        if not form.has_only_email_error():
            raise PermissionDenied("Invalid")
        return HttpResponse(
            fail_check_partial(
                school,
                form.cleaned_data["first_name"],
                form.cleaned_data["last_name"],
                current_contest,
            )
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
        contest_entry, _ = enter_contest(student, current_contest, when=when)

    # Send the student an email validation link to claim their prize
    # if they won. In no other cases do we send validation links.
    if contest_entry is not None:
        process_contest_workflow(student, email, contest_entry)

    most_recent_winner = None
    if current_contest is not None:
        most_recent_winner = current_contest.most_recent_winner()

    return HttpResponse(
        finish_check_partial(
            school,
            contest_entry,
            most_recent_winner,
        )
    )


@require_GET
def validate_email(request: HttpRequest, slug: str, token: str) -> HttpResponse:
    """
    View visited when a user clicks on a validation link in their email.

    When a student reaches this point, we know (a) the email address is valid,
    (b) it's valid for the school, and (c) the student has access to the email
    address.

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

    # Historically, we issued email validation links for everyone, regardless
    # of whether they were contest winners. This is no longer the case.
    # Here, we simply bail out if the student is not a contest winner.
    contest_entry = link.contest_entry
    if contest_entry is None or not contest_entry.is_winner:
        return redirect("vb:home", permanent=False)

    try:
        # See comment on ContestEntry that prizes *should* be in a separate
        # model that has a 1:1 relationship with ContestEntry. For now, prize
        # issuance is done in the same table.
        contest_entry, claim_code = get_or_issue_prize(contest_entry)
        error = False
    except Exception:
        contest_entry, claim_code, error = None, None, True

    return HttpResponse(validate_email_page(school, contest_entry, claim_code, error))
