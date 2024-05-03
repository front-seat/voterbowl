import htpy as h

from ..models import Contest, School
from .base_page import base_page
from .button import button
from .countdown import countdown
from .logo import school_logo

_STYLE = """
  me {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  me main {
    width: 100%;
    text-align: center;
    padding-bottom: 2rem;
    color: {color};
    background-color: {bg_color};
  }

  @media screen and (min-width: 768px) {
    me main {
      padding: 2rem 0;
    }
  }

  me main img {
    height: 150px;
    margin: 1.5rem 0;
  }

  me main p {
    font-weight: 378;
    font-size: 20px;
    line-height: 130%;
  }

  me main h2 {
    font-weight: 500;
    font-size: 36px;
    line-height: 120%;
    text-transform: uppercase;
  }

  me .faq {
    width: 100%;
    color: white;
    padding: 2rem 0;
  }

  me .button-holder {
    display: flex;
    justify-content: center;
    margin: 1.5rem 0;
  }

  me .faq {
    background-color: black;
  }
"""


def _style(color: str, bg_color: str) -> h.Element:
    return h.style[_STYLE.replace("{color}", color).replace("{bg_color}", bg_color)]


def _contest_info(
    school: School, current_contest: Contest | None, past_contest: Contest | None
) -> h.Node:
    if current_contest:
        return h.p[
            school.short_name,
            " students: check your registration status",
            f"for a 1 in { current_contest.in_n } chance",
            f"to win a ${current_contest.amount} Amazon gift card.",
        ]
    elif past_contest:
        return [
            h.p[
                school.short_name,
                f" students: the ${past_contest.amount} ",
                "giveaway" if past_contest.is_giveaway else "contest",
                " has ended.",
            ],
            h.p["But: it's always a good time to make sure you're ready to vote."],
        ]
    else:
        return [
            h.p[school.short_name, " students: there's no contest right now."],
            h.p["But: it's always a good time to make sure you're ready to vote."],
        ]


def school_page(
    school: School, current_contest: Contest | None, past_contest: Contest | None
) -> h.Element:
    """Render a school landing page."""
    return base_page(
        title=f"Voter Bowl x {school.name}", bg_color=school.logo.bg_color
    )[
        h.div[
            _style(bg_color=school.logo.bg_color, color=school.logo.bg_text_color),
            h.main[
                h.div(".container")[
                    countdown(current_contest) if current_contest else None,
                    school_logo(school),
                    h.h2["Welcome to the Voter Bowl"],
                    _contest_info(school, current_contest, past_contest),
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
