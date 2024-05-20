import datetime

import htpy as h

from server.utils.components import css_vars

from ..models import Contest
from .button import button
from .countdown import remaining_time
from .logo import school_logo


def _format_countdown_str(
    end_at: datetime.datetime, when: datetime.datetime | None = None
) -> str:
    """Format the remaining time until the given end time."""
    rt = remaining_time(end_at, when)
    if rt.ended:
        return "Just ended!"
    return f"Ends in {rt.h0}{rt.h1}:{rt.m0}{rt.m1}:{rt.s0}{rt.s1}"


def _ongoing_description(contest: Contest) -> list[str]:
    """Render a description of the given contest."""
    if contest.is_no_prize:
        school = contest.school
        if school.mascot and school.percent_voted_2020:
            return [
                f"Join the {school.percent_voted_2020}% of the {school.mascot} who voted in the 2020 presidential election."
            ]
        return [
            "Check your voter registration now to avoid last-minute issues before the election."
        ]
    if contest.is_giveaway:
        if contest.is_monetary:
            return [
                "Check your voter registration ",
                f"to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return ["Check your voter registration ", f"for {contest.prize_long}."]
    if contest.is_dice_roll:
        if contest.is_monetary:
            return [
                "Check your voter registration ",
                f"for a 1 in {contest.in_n} chance "
                f"to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return [
            "Check your voter registration ",
            f"for a 1 in {contest.in_n} chance to at {contest.prize_long}.",
        ]
    if contest.is_single_winner:
        if contest.is_monetary:
            return [
                "Check your voter registration ",
                f"for a chance to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return [
            "Check your voter registration ",
            f"for a chance to win {contest.prize_long}.",
        ]
    raise ValueError(f"Unknown contest kind: {contest.kind}")


def ongoing_contest(contest: Contest) -> h.Element:
    """Render an ongoing contest."""
    return h.div(
        ".ongoing-contest", style=css_vars(logo_bg_color=contest.school.logo.bg_color)
    )[
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
            h.div(".box countdown")[_format_countdown_str(contest.end_at)]
        ],
    ]
