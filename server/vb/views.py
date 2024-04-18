from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import School


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


class VerifyForm(forms.Form):
    """Form for verifying a check."""

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()


@require_POST
@csrf_exempt  # CONSIDER: maybe use Django's CSRF protection even here?
def finish_check(request: HttpRequest, slug: str) -> HttpResponse:
    """Handle a check registration form submission."""
    school = get_object_or_404(School, slug=slug)
    current_contest = school.contests.current()
    if not current_contest:
        raise ValueError("No active contest TODO")
    form = VerifyForm(request.POST)
    if not form.is_valid():
        raise PermissionDenied("Invalid form")

    return render(
        request,
        "finish_check.dhtml",
        {
            "school": school,
            "current_contest": current_contest,
            "first_name": form.cleaned_data["first_name"],
            "last_name": form.cleaned_data["last_name"],
            "email": form.cleaned_data["email"],
        },
    )
