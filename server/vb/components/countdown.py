import datetime
from dataclasses import dataclass
from math import floor

import htpy as h

from server.utils.components import css_vars

from ..models import Contest

# -----------------------------------------------------------------------------
# Generic Countdown Utils
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RemainingTime:
    """Render the remaining time until the given end time."""

    h0: int
    """The tens digit of the hours."""

    h1: int
    """The ones digit of the hours."""

    m0: int
    """The tens digit of the minutes."""

    m1: int
    """The ones digit of the minutes."""

    s0: int
    """The tens digit of the seconds."""

    s1: int
    """The ones digit of the seconds."""

    @property
    def ended(self) -> bool:
        """Return whether the remaining time has ended."""
        return self.h0 == self.h1 == self.m0 == self.m1 == self.s0 == self.s1 == 0


def remaining_time(
    end_at: datetime.datetime, when: datetime.datetime | None = None
) -> RemainingTime:
    """Render the remaining time until the given end time."""
    now = when or datetime.datetime.now(datetime.UTC)
    delta = end_at - now
    if delta.total_seconds() <= 0:
        return RemainingTime(0, 0, 0, 0, 0, 0)
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    hours, minutes, seconds = map(floor, (hours, minutes, seconds))
    return RemainingTime(
        h0=hours // 10,
        h1=hours % 10,
        m0=minutes // 10,
        m1=minutes % 10,
        s0=seconds // 10,
        s1=seconds % 10,
    )


# -----------------------------------------------------------------------------
# Big Countdown Area
# -----------------------------------------------------------------------------


def _describe_contest(contest: Contest) -> h.Node:
    """Render a description of the given contest."""
    if contest.is_no_prize:
        return h.p["Check your voter registration soon:"]
    if contest.is_giveaway:
        if contest.is_monetary:
            return h.p[
                f"${contest.amount:,} {contest.prize_long}",
                h.br,
                "giveaway ends in:",
            ]
        return h.p[
            contest.prize_long,
            h.br,
            "ends in:",
        ]
    if contest.is_dice_roll:
        if contest.is_monetary:
            return h.p[
                f"${contest.amount:,} {contest.prize_long}",
                h.br,
                "contest ends in:",
            ]
        return h.p[
            contest.prize_long,
            h.br,
            "ends in:",
        ]
    if contest.is_single_winner:
        if contest.is_monetary:
            return h.p[
                f"${contest.amount:,} {contest.prize_long}",
                h.br,
                "drawing ends in:",
            ]
        return h.p[
            contest.prize_long,
            h.br,
            "ends in:",
        ]
    raise ValueError(f"Unknown contest kind: {contest.kind}")


def countdown(contest: Contest) -> h.Element:
    """Render a countdown timer for the given contest."""
    logo = contest.school.logo
    remaining = remaining_time(contest.end_at)
    return h.big_countdown(
        data_end_at=contest.end_at.isoformat(),
        style=css_vars(
            number_color=logo.action_text_color,
            number_bg_color=logo.action_color,
            colon_color=logo.bg_text_color,
        ),
    )[
        _describe_contest(contest),
        h.div(".countdown")[
            h.span(".number", data_number="h0")[f"{remaining.h0}"],
            h.span(".number", data_number="h1")[f"{remaining.h1}"],
            h.span(".colon")[":"],
            h.span(".number", data_number="m0")[f"{remaining.m0}"],
            h.span(".number", data_number="m1")[f"{remaining.m1}"],
            h.span(".colon")[":"],
            h.span(".number", data_number="s0")[f"{remaining.s0}"],
            h.span(".number", data_number="s1")[f"{remaining.s1}"],
        ],
    ]
