import htpy as h
from markupsafe import Markup

from ..models import Contest

_STYLE = """
me {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding-bottom: 0.5rem;
}

me p {
    text-transform: uppercase;
}

me .countdown {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    font-weight: 500;
    font-family: var(--font-mono);
    gap: 4px;
    height: 34px !important;
}

me .countdown span {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 27px;
}

me .countdown span.number {
    color: {number_color};
    background-color: {number_bg_color};
}

me .countdown span.colon {
    color: {colon_color};
    background-color: transparent;
}
"""


_SCRIPT = h.script[
    Markup("""
(function() {
    /**
        * Countdown to a deadline.
        * 
        * @param {HTMLElement} self element containing the countdown.
        * @returns {void}
        */
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
                numbers.forEach(number => number.textContent = '0');
                return;
            }

            // get the number elements
            const h0 = self.querySelector('[data-number=h0]');
            const h1 = self.querySelector('[data-number=h1]');
            const m0 = self.querySelector('[data-number=m0]');
            const m1 = self.querySelector('[data-number=m1]');
            const s0 = self.querySelector('[data-number=s0]');
            const s1 = self.querySelector('[data-number=s1]');
            const numbers = [h0, h1, m0, m1, s0, s1];

            if (numbers.some(number => !number)) {
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

            numbers[0].innerText = h0digit.toString();
            numbers[1].innerText = h1digit.toString();
            numbers[2].innerText = m0digit.toString();
            numbers[3].innerText = m1digit.toString();
            numbers[4].innerText = s0digit.toString();
            numbers[5].innerText = s1digit.toString();
        }

        updateCountdown();
        const interval = setInterval(updateCountdown, 1000);
    }

    const self = me();
    onloadAdd(() => countdown(self));
})();
""")
]


def _style(number_color: str, number_bg_color: str, colon_color: str) -> h.Element:
    return h.style[
        _STYLE.replace("{number_color}", number_color)
        .replace("{number_bg_color}", number_bg_color)
        .replace("{colon_color}", colon_color)
    ]


def countdown(contest: Contest) -> h.Element:
    """Render a countdown timer for the given contest."""
    logo = contest.school.logo
    return h.div[
        _style(
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
        h.div(".countdown", data_end_at=contest.end_at.isoformat())[
            _SCRIPT,
            h.span(".number", data_number="h0"),
            h.span(".number", data_number="h1"),
            h.span(".colon")[":"],
            h.span(".number", data_number="m0"),
            h.span(".number", data_number="m1"),
            h.span(".colon")[":"],
            h.span(".number", data_number="s0"),
            h.span(".number", data_number="s1"),
        ],
    ]
