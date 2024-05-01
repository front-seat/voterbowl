import typing as t

import htpy as h

from ..models import Contest
from .base import base_page
from .logo import voter_bowl_logo


def _ongoing_contest(ongoing_contest: Contest) -> h.Node:
    pass


def _ongoing_contests(contests: list[Contest]) -> h.Node:
    """Render a list of ongoing contests."""
    if contests:
        return h.div[(_ongoing_contest(contest) for contest in contests)]
    return None


def _upcoming_contests(upcoming_contests: t.Iterable[Contest]) -> h.Node:
    pass


def home_page(
    ongoing_contests: t.Iterable[Contest],
    upcoming_contests: t.Iterable[Contest],
) -> h.Element:
    """Render the home page for voterbowl.org."""
    ongoing_contests = list(ongoing_contests)
    upcoming_contests = list(upcoming_contests)
    return base_page(
        [
            h.div[
                h.main[
                    h.div("container")[
                        h.div("center")[voter_bowl_logo()],
                        h.h2[
                            "College students win prizes by checking if they are registered to vote."
                        ],
                    ]
                ]
            ]
        ]
    )
