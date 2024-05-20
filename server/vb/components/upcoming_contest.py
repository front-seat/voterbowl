import htpy as h

from server.utils.components import css_vars

from ..models import Contest
from .logo import school_logo


def upcoming_contest(contest: Contest) -> h.Element:
    """Render an upcoming contest."""
    return h.div(
        ".upcoming-contest", style=css_vars(logo_bg_color=contest.school.logo.bg_color)
    )[
        h.div(".content")[
            school_logo(contest.school),
            h.p(".school")[contest.school.name],
        ],
    ]
