import htpy as h

from server.utils.components import js, style

from ..models import Contest
from .button import button
from .logo import school_logo


def ongoing_contest(contest: Contest) -> h.Element:
    """Render an ongoing contest."""
    return h.div[
        style(
            __file__, "ongoing_contest.css", logo_bg_color=contest.school.logo.bg_color
        ),
        h.div(".content")[
            school_logo(contest.school),
            h.p(".school")[contest.school.name],
            h.p(".description")[
                "Check your voter registration status",
                None if contest.is_giveaway else f" for a 1 in {contest.in_n} chance",
                f" to win a ${contest.amount} Amazon gift card.",
            ],
            h.div(".button-holder")[
                button(
                    href=contest.school.relative_url, bg_color="black", color="white"
                )["Visit event"]
            ],
        ],
        h.div(".box")[
            js(__file__, "ongoing_contest.js", ends_at=contest.end_at.isoformat()),
            "Ends in ...",
        ],
    ]