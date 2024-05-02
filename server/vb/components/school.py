import htpy as h

from ..models import Contest, School


def school_page(
    school: School, current_contest: Contest | None, past_contest: Contest | None
) -> h.Element:
    """Render a school landing page."""
    return h.div
