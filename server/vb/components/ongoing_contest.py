import htpy as h

from server.utils.components import style

from ..models import Contest
from .button import button
from .logo import school_logo


def _ongoing_description(contest: Contest) -> list[str]:
    """Render a description of the given contest."""
    if contest.is_no_prize:
        return ["Check your voter registration status soon!"]
    if contest.is_giveaway:
        if contest.is_monetary:
            return [
                "Check your voter registration status ",
                f"to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return ["Check your voter registration status ", f"for {contest.prize_long}."]
    if contest.is_dice_roll:
        if contest.is_monetary:
            return [
                "Check your voter registration status ",
                f"for a 1 in {contest.in_n} chance "
                f"to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return [
            "Check your voter registration status ",
            f"for a 1 in {contest.in_n} chance to at {contest.prize_long}.",
        ]
    if contest.is_single_winner:
        if contest.is_monetary:
            return [
                "Check your voter registration status ",
                f"for a chance to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return [
            "Check your voter registration status ",
            f"for a chance to win {contest.prize_long}.",
        ]
    raise ValueError(f"Unknown contest kind: {contest.kind}")


def ongoing_contest(contest: Contest) -> h.Element:
    """Render an ongoing contest."""
    return h.div[
        style(
            __file__, "ongoing_contest.css", logo_bg_color=contest.school.logo.bg_color
        ),
        h.div(".content")[
            school_logo(contest.school),
            h.p(".school")[contest.school.name],
            h.p(".description")[*_ongoing_description(contest)],
            h.div(".button-holder")[
                button(
                    href=contest.school.relative_url, bg_color="black", color="white"
                )["Visit event"]
            ],
        ],
        h.small_countdown(data_end_at=contest.end_at.isoformat())[
            h.div(".box countdown")[""]
        ],
    ]
