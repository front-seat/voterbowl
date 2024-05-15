import htpy as h
from django.conf import settings
from django.urls import reverse

from server.utils.components import style, svg

from ..models import ContestEntry, School
from .base_page import base_page
from .logo import school_logo


def _congrats(contest_entry: ContestEntry, claim_code: str) -> h.Node:
    return [
        h.p[f"Congrats! You won a ${contest_entry.amount_won} gift card!"],
        h.h2[
            h.span(".code")[claim_code],
            h.span(".clipboard", title="Copy to clipboard")[
                svg(__file__, "clipboard.svg")
            ],
            h.span(".copied hidden", title="Copied!")[
                svg(__file__, "clipboard_check.svg")
            ],
        ],
        h.p[
            "To use your gift card, copy the code above and paste it into ",
            h.a(href="https://www.amazon.com/gc/redeem", target="_blank")["Amazon.com"],
            ".",
        ],
        h.p[
            "Tell your friends so they can also win! Share this link: ",
            h.a(
                href=reverse(
                    "vb:school", kwargs={"slug": contest_entry.contest.school.slug}
                )
            )[settings.BASE_HOST, "/", contest_entry.contest.school.slug],
        ],
    ]


def _sorry() -> h.Node:
    return [
        h.p["Sorry, ", h.b["there was an error"], ". Please try again later."],
        h.p[
            "If you continue to have issues, please contact us at ",
            h.a(href="mailto:info@voterbowl.org")["info@voterbowl.org"],
            ".",
        ],
    ]


def validate_email_page(
    school: School,
    contest_entry: ContestEntry | None,
    claim_code: str | None,
    error: bool,
) -> h.Element:
    """Render the page that a user sees after clicking on a validation link in their email."""
    return base_page(
        title=f"Voter Bowl x {school.short_name}", bg_color=school.logo.bg_color
    )[
        h.div[
            style(
                __file__,
                "validate_email_page.css",
                main_color=school.logo.bg_text_color,
                main_bg_color=school.logo.bg_color,
            ),
            h.main[
                h.gift_code[
                    h.div(".container")[
                        school_logo(school),
                        _congrats(contest_entry, claim_code)
                        if contest_entry and claim_code
                        else _sorry(),
                    ],
                ]
            ],
        ],
    ]
