import htpy as h
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse

from server.utils.components import style

from ..models import Contest, ContestEntry, School
from .base_page import base_page
from .countdown import countdown
from .logo import school_logo
from .utils import Fragment, fragment


def check_page(school: School, current_contest: Contest | None) -> h.Element:
    """Render a school-specific 'check voter registration' form page."""
    extra_head = [
        h.script(src="https://cdn.voteamerica.com/embed/tools.js", _async=True),
    ]
    return base_page(
        title=f"Voter Bowl x {school.name}",
        bg_color=school.logo.bg_color,
        extra_head=extra_head,
        show_faq=False,
        show_footer=False,
    )[
        h.check_page[
            h.div[
                style(
                    __file__,
                    "check_page.css",
                    main_color=school.logo.bg_text_color,
                    main_bg_color=school.logo.bg_color,
                ),
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
    ]


def fail_check_partial(
    school: School, first_name: str, last_name: str, current_contest: Contest | None
) -> Fragment:
    """Render a partial page for when the user's email is invalid."""
    return fragment[
        school_logo(school),
        h.fail_check(
            data_school_name=school.short_name,
            data_first_name=first_name,
            data_last_name=last_name,
        )[
            h.p[
                h.b["We could not use your email"],
                f". Please use your { school.short_name } student email.",
            ]
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
        contest = contest_entry.contest
        if contest.is_monetary:
            return [
                h.b["You win!"],
                f" We sent a ${contest_entry.amount_won} {contest.prize} to your school email. ",
                "(Check your spam folder.) ",
                h.br,
                h.br,
                "Your friends can also win. ",
                share_link,
            ]
        return [
            h.b["You win: "],
            f"{contest.prize_long}.",
            h.br,
            h.br,
            "Your friends can also win. ",
            share_link,
        ]

    if contest_entry:
        contest = contest_entry.contest
        if contest.is_no_prize:
            return [
                "Thanks for checking your voter registration. ",
                "Please register to vote if you haven't yet.",
                h.br,
                h.br,
                "Tell your friends! ",
                share_link,
            ]
        if contest.is_giveaway:
            raise RuntimeError(
                f"Giveaways should always have winners ({contest_entry.pk})"
            )
        if contest.is_dice_roll:
            # Works for both monetary and non-monetary dice rolls
            return [
                "Please register to vote if you haven't yet.",
                h.br,
                h.br,
                f"You didn't win a {contest.prize}. ",
                f"The last winner was {most_recent_winner.student.anonymized_name} {naturaltime(most_recent_winner.created_at)}. "
                if most_recent_winner
                else None,
                "Your friends can still win! ",
                share_link,
            ]
        if contest.is_single_winner:
            # We don't know if the user won or lost, so we don't say anything
            # more than 'we'll let you know'
            return [
                "Thanks! Please register to vote if you haven't yet.",
                h.br,
                h.br,
                f"You're entered into the ${contest.amount:,} drawing. We'll email you if you win."
                if contest.is_monetary
                else "You're entered into the drawing. We'll email you if you win.",
                h.br,
                h.br,
                "Your friends can also win! ",
                share_link,
            ]
        raise ValueError(f"Unknown contest kind: {contest.kind}")

    return [
        "Thanks for checking your voter registration.",
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
        h.finish_check(
            data_is_winner="true"
            if contest_entry and contest_entry.is_winner
            else "false"
        )[
            h.p[
                style(__file__, "finish_check_partial.css"),
                _finish_check_description(school, contest_entry, most_recent_winner),
            ]
        ],
    ]
