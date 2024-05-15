import htpy as h

from server.utils.components import style

from ..models import Contest, School
from .base_page import base_page
from .button import button
from .countdown import countdown
from .logo import school_logo


def _no_current_prize_contest(school: School) -> h.Node:
    return h.p[
        school.short_name,
        " ",
        "students: check your voter registration now to avoid ",
        "last-minute issues before the election.",
    ]


def _current_contest_info(school: School, contest: Contest) -> h.Node:
    if contest.is_no_prize:
        return _no_current_prize_contest(school)
    if contest.is_giveaway:
        if contest.is_monetary:
            return h.p[
                school.short_name,
                " ",
                "students: check your voter registration ",
                f"to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return h.p[
            school.short_name,
            " ",
            "students: check your voter registration ",
            f"for a {contest.prize_long}.",
        ]
    if contest.is_dice_roll:
        if contest.is_monetary:
            return h.p[
                school.short_name,
                " ",
                "students: check your voter registration ",
                f"for a 1 in {contest.in_n} chance ",
                f"to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return h.p[
            school.short_name,
            " ",
            "students: check your voter registration ",
            f"for a 1 in {contest.in_n} chance",
            f"at {contest.prize_long}.",
        ]
    if contest.is_single_winner:
        if contest.is_monetary:
            return h.p[
                school.short_name,
                " ",
                "students: check your voter registration ",
                f"for a chance to win a ${contest.amount:,} {contest.prize_long}.",
            ]
        return h.p[
            school.short_name,
            " ",
            "students: check your voter registration ",
            f"for a chance to win {contest.prize_long}.",
        ]
    raise ValueError(f"Unknown contest kind: {contest.kind}")


def _contest_info(school: School, current_contest: Contest | None) -> h.Node:
    if current_contest:
        return _current_contest_info(school, current_contest)
    else:
        return _no_current_prize_contest(school)


def school_page(school: School, current_contest: Contest | None) -> h.Element:
    """Render a school landing page."""
    return base_page(
        title=f"Voter Bowl x {school.name}", bg_color=school.logo.bg_color
    )[
        h.div[
            style(
                __file__,
                "school_page.css",
                bg_color=school.logo.bg_color,
                color=school.logo.bg_text_color,
            ),
            h.main[
                h.div(".container")[
                    countdown(current_contest)
                    if current_contest and not current_contest.is_no_prize
                    else None,
                    school_logo(school),
                    h.h2["Welcome to the Voter Bowl"],
                    _contest_info(school, current_contest),
                    h.div(".button-holder")[
                        button(
                            href="./check/",
                            bg_color=school.logo.action_color,
                            color=school.logo.action_text_color,
                        )["Check my voter status"]
                    ],
                ]
            ],
        ]
    ]
