from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import School


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    """Render the voterbowl homepage."""
    return render(request, "home.dhtml")


@require_GET
def school(request: HttpRequest, slug: str) -> HttpResponse:
    """Render a school page."""
    school = get_object_or_404(School, slug=slug)
    return render(request, "school.dhtml", {"school": school})
