import htpy as h
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.templatetags.static import static
from django.urls import reverse

from server.utils.components import js, style

from ..models import Contest, ContestEntry, School
from .base_page import base_page
from .countdown import countdown
from .logo import school_logo
from .utils import Fragment, fragment


def check_page(school: School, current_contest: Contest | None) -> h.Element:
    """Render a school-specific 'check voter registration' form page."""
    extra_head = [
        h.script(src=static("js/fireworks.js")),
        h.script(src="https://cdn.voteamerica.com/embed/tools.js", _async=True),
    ]
    return base_page(
        title=f"Voter Bowl x {school.name}",
        bg_color=school.logo.bg_color,
        extra_head=extra_head,
        show_faq=False,
        show_footer=False,
    )[
        h.div[
            style(
                __file__,
                "check_page.css",
                main_color=school.logo.bg_text_color,
                main_bg_color=school.logo.bg_color,
            ),
            js(__file__, "check_page.js"),
            h.main[
                h.div(".container")[
                    h.div(".urgency")[
                        school_logo(school),
                        countdown(current_contest)
                        if current_contest
                        else h.div(".separate")[
                            h.p["Check your voter registration status below."]
                        ],
                    ]
                ],
                h.div(".fireworks"),
            ],
            h.div(".form")[
                h.div(".container")[
                    h.div(
                        ".voteamerica-embed",
                        data_subscriber="voterbowl",
                        data_tool="verify",
                        data_edition="college",
                    )
                ]
            ],
        ]
    ]


def fail_check_partial(
    school: School, first_name: str, last_name: str, current_contest: Contest | None
) -> Fragment:
    """Render a partial page for when the user's email is invalid."""
    return fragment[
        school_logo(school),
        h.p[
            js(
                __file__,
                "fail_check_partial.js",
                school_name=school.short_name,
                first_name=first_name,
                last_name=last_name,
            ),
            h.b["We could not use your email"],
            f". Please use your { school.short_name } student email.",
        ],
    ]


def _finish_check_description(
    school: School,
    contest_entry: ContestEntry | None,
    most_recent_winner: ContestEntry | None,
) -> h.Node:
    share_link: h.Node = [
        "Share this link: ",
        h.a(href=reverse("vb:school", args=[school.slug]))[
            settings.BASE_HOST, "/", school.slug
        ],
    ]

    if contest_entry and contest_entry.is_winner:
        return [
            h.b["You win!"],
            f" We sent a ${contest_entry.amount_won} gift card to your school email. ",
            "(Check your spam folder.) ",
            h.br,
            h.br,
            "Your friends can also win. ",
            share_link,
        ]

    if contest_entry:
        return [
            "Please register to vote if you haven't yet.",
            h.br,
            h.br,
            "You didn't win a gift card. ",
            f"The last winner was {most_recent_winner.student.anonymized_name} {naturaltime(most_recent_winner.created_at)} ago."
            if most_recent_winner
            else None,
            "Your friends can still win! ",
            share_link,
        ]

    return [
        "Thanks for checking your voter registraiton.",
        h.br,
        h.br,
        "Please register to vote if you haven't yet.",
    ]


def finish_check_partial(
    school: School,
    contest_entry: ContestEntry | None,
    most_recent_winner: ContestEntry | None,
) -> Fragment:
    """Render a partial page for when the user has finished the check."""
    return fragment[
        school_logo(school),
        h.p[
            style(__file__, "finish_check_partial.css"),
            js(
                __file__,
                "finish_check_partial.js",
                is_winner=contest_entry and contest_entry.is_winner,
            ),
            _finish_check_description(school, contest_entry, most_recent_winner),
        ],
    ]
