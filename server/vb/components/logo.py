import htpy as h

from server.utils.components import style, svg

from ..models import Logo, School

VOTER_BOWL_LOGO = svg(__file__, "voter_bowl_logo.svg")


def school_logo(school: School) -> h.Element:
    """Render a school's logo as an image element."""
    return h.div(".logo")[
        h.img(
            src=school.logo.url,
            alt=f"{school.short_name} {school.mascot} logo",
        )
    ]


def logo_specimen(logo: Logo) -> h.Element:
    """Render a school's logo as a specimen for our admin views."""
    return h.div[
        style(
            __file__,
            "logo_specimen.css",
            logo_bg_color=logo.bg_color,
            logo_bg_text_color=logo.bg_text_color,
            logo_action_color=logo.action_color,
            logo_action_text_color=logo.action_text_color,
        ),
        h.div(".bubble")[h.img(src=logo.url, alt="logo")],
        h.div(".bg")["text"],
        h.div(".action")["action"],
    ]
