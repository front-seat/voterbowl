import typing as t

import htpy as h

from ..models import Contest
from .base_page import base_page
from .logo import VOTER_BOWL_LOGO
from .ongoing_contest import ongoing_contest
from .upcoming_contest import upcoming_contest


def _ongoing_contests(contests: list[Contest]) -> h.Node:
    """Render a list of ongoing contests."""
    if contests:
        return h.div(".ongoing")[(ongoing_contest(contest) for contest in contests)]
    return None


def _upcoming_contests(contests: list[Contest]) -> h.Node:
    if contests:
        return [
            h.p(".coming-soon")["Coming Soon"],
            h.div(".upcoming")[(upcoming_contest(contest) for contest in contests)],
        ]
    return None


def home_page(
    ongoing_contests: t.Iterable[Contest],
    upcoming_contests: t.Iterable[Contest],
) -> h.Element:
    """Render the home page for voterbowl.org."""
    ongoing_contests = list(ongoing_contests)
    upcoming_contests = list(upcoming_contests)

    return base_page[
        h.div("#home-page")[
            h.main[
                h.div(".container")[
                    h.div(".center")[VOTER_BOWL_LOGO],
                    h.h2[
                        "College students win prizes by checking if they are registered to vote."
                    ],
                    _ongoing_contests(ongoing_contests),
                    _upcoming_contests(upcoming_contests),
                    h.p["There are no contests at this time. Check back later!"]
                    if not ongoing_contests and not upcoming_contests
                    else None,
                ]
            ],
        ]
    ]
