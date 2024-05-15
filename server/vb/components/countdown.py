import htpy as h

from server.utils.components import style

from ..models import Contest


def _describe_contest(contest: Contest) -> h.Node:
    """Render a description of the given contest."""
    if contest.is_no_prize:
        return h.p["Check your registration status soon:"]
    if contest.is_giveaway:
        if contest.is_monetary:
            return h.p[
                f"${contest.amount} {contest.prize_long}",
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
                f"${contest.amount} {contest.prize_long}",
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
                f"${contest.amount} {contest.prize_long}",
                h.br,
                "sweepstakes ends in:",
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
    return h.div[
        style(
            __file__,
            "countdown.css",
            number_color=logo.action_text_color,
            number_bg_color=logo.action_color,
            colon_color=logo.bg_text_color,
        ),
        _describe_contest(contest),
        h.big_countdown(data_end_at=contest.end_at.isoformat())[
            h.div(".countdown")[
                h.span(".number", data_number="h0"),
                h.span(".number", data_number="h1"),
                h.span(".colon")[":"],
                h.span(".number", data_number="m0"),
                h.span(".number", data_number="m1"),
                h.span(".colon")[":"],
                h.span(".number", data_number="s0"),
                h.span(".number", data_number="s1"),
            ]
        ],
    ]
