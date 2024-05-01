import typing as t

import htpy as h
from markupsafe import Markup

from ..models import Contest, School
from .base import base_page
from .logo import VOTER_BOWL_LOGO


def _logo_img(school: School) -> h.Element:
    return h.div(".logo")[
        h.img(
            src=school.logo.url,
            alt=f"{school.short_name} {school.mascot} logo",
        )
    ]


_COUNTDOWN_JS = Markup("""
(function(self) {
    function countdown(self) {
        // compute the deadline
        const deadline = new Date(self.dataset.endAt);
        const deadlineTime = deadline.getTime();

        /** Update the countdown. */
        function updateCountdown() {
            const now = new Date().getTime();
            const diff = deadlineTime - now;

            if (diff <= 0) {
                clearInterval(interval);
                self.innerText = "Just ended!";
                return;
            }

            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            const h0digit = Math.floor(hours / 10);
            const h1digit = hours % 10;
            const m0digit = Math.floor(minutes / 10);
            const m1digit = minutes % 10;
            const s0digit = Math.floor(seconds / 10);
            const s1digit = seconds % 10;

            const endsIn = `Ends in ${h0digit}${h1digit}:${m0digit}${m1digit}:${s0digit}${s1digit}`;
            self.innerText = endsIn;
        }

        updateCountdown();
        const interval = setInterval(updateCountdown, 1000);
    }

    onloadAdd(() => countdown(self));
})(me());
""")


def _ongoing_style(logo_bg_color: str) -> str:
    return """
me {
  border: 3px solid black;
  color: black;
  font-weight: 400;
  font-size: 18px;
  line-height: 140%;
  padding-left: 1em;
  padding-right: 1em;
  position: relative;
}

me .content {
  display: flex;
  flex-direction: column;
}

me .logo {
  border-radius: 100%;
  border: 2px solid black;
  background-color: {logo_bg_color};
  overflow: hidden;
  width: 60px;
  height: 60px;
  margin: 1.5em auto 1em auto;
}

me .logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

me .school {
  margin: 0;
  font-weight: 500;
  font-size: 24px;
  line-height: 100%;
  display: flex;
  justify-content: center;
}

me .description {
  margin-bottom: 0;
}

me .button-holder {
  width: 100%;
}

me .button-holder a {
  width: 100%;
}

/* A centered box at the top of the card */
me .box {
  position: absolute;
  top: -1em;
  left: 50%;
  transform: translateX(-50%);
  border: 3px solid black;
  background-color: #cdff64;
  font-weight: 600;
  line-height: 100%;
  letter-spacing: 4%;
  min-width: 30%;
  padding: 0.25rem;
  text-transform: uppercase;
}
""".replace("{logo_bg_color}", logo_bg_color)


def _ongoing_contest(contest: Contest) -> h.Element:
    return h.div[
        h.style[_ongoing_style(contest.school.logo.bg_color)],
        h.div(".content")[
            _logo_img(contest.school),
            h.p(".school")[contest.school.name],
            h.p(".description")[
                "Check your voter registration status",
                None if contest.is_giveaway else f" for a 1 in {contest.in_n} chance",
                f" to win a ${contest.amount} Amazon gift card.",
            ],
            h.div(".button-holder")["TODO"],
        ],
        h.div(".box", data_end_at=contest.end_at.isoformat())[
            h.script[_COUNTDOWN_JS], "Ends in ..."
        ],
    ]


def _ongoing_contests(contests: list[Contest]) -> h.Node:
    """Render a list of ongoing contests."""
    if contests:
        return h.div(".ongoing")[(_ongoing_contest(contest) for contest in contests)]
    return None


def _upcoming_style(logo_bg_color: str) -> str:
    return """
me {
  border: 3px solid black;
  padding: 1rem;
  color: black;
  font-size: 18px;
  font-weight: 440;
  font-variation-settings: "wght" 440;
  line-height: 1;
}

me .content {
  display: flex;
  align-items: center;
  gap: 1em;
}

me .logo {
  border-radius: 100%;
  border: 2px solid black;
  background-color: {logo_bg_color};
  overflow: hidden;
  width: 36px;
  height: 36px;
}

me .logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

me p {
  margin: 0;
}
""".replace("{logo_bg_color}", logo_bg_color)


def _upcoming_contest(contest: Contest) -> h.Element:
    return h.div[
        h.style[_upcoming_style(contest.school.logo.bg_color)],
        h.div(".content")[
            _logo_img(contest.school),
            h.p(".school")[contest.school.name],
        ],
    ]


def _upcoming_contests(contests: list[Contest]) -> h.Node:
    if contests:
        return [
            h.p(".coming-soon")["Coming Soon"],
            h.div(".upcoming")[(_upcoming_contest(contest) for contest in contests)],
        ]
    return None


_STYLE = """
me {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: #cdff64;
    color: black;
}

me main {
    width: 100%;
    text-align: center;
    padding: 2rem 0;
}

me main svg {
    width: 104px;
    margin: 1.5rem 0;
}

@media screen and (min-width: 768px) {
    me main svg {
        width: 112px;
    }
}

me main p {
    font-weight: 378;
    font-size: 20px;
    line-height: 130%;
}

me main h2 {
    font-weight: 500;
    font-size: 28px;
    line-height: 140%;
}

@media screen and (min-width: 768px) {
    me main h2 {
        font-size: 32px;
    }
}

me .button-holder {
    display: flex;
    justify-content: center;
    margin: 1.5rem 0;
}

me .ongoing {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 2rem;
    margin: 2rem 0;
}

me .upcoming {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.5rem;
    margin: 0.5rem 0;
}

me .coming-soon {
    text-transform: uppercase;
    font-weight: bold;
    font-size: 20px;
    line-height: 130%;
    display: flex;
    justify-content: center;
    margin: 1.5rem 0;
}
"""


def home_page(
    ongoing_contests: t.Iterable[Contest],
    upcoming_contests: t.Iterable[Contest],
) -> h.Element:
    """Render the home page for voterbowl.org."""
    ongoing_contests = list(ongoing_contests)
    upcoming_contests = list(upcoming_contests)

    return base_page[
        h.div[
            h.style[_STYLE],
            h.main[
                h.div(".container")[
                    h.div(".center")[VOTER_BOWL_LOGO],
                    h.h2[
                        "College students win prizes by checking if they are registered to vote."
                    ],
                    _ongoing_contests(ongoing_contests),
                    _upcoming_contests(upcoming_contests),
                    h.p["There are no contests at this time. Check back later!"]
                    if not ongoing_contests and not upcoming_contests
                    else None,
                ]
            ],
        ]
    ]
