import htpy as h

from server.utils.components import style

from ..models import Contest


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
        h.p[
            f"${contest.amount} Amazon gift card",
            h.br,
            "giveaway " if contest.is_giveaway else "contest ",
            "ends in:",
        ],
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
