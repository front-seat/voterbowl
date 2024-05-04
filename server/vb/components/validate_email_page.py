import htpy as h
from django.conf import settings
from django.urls import reverse
from markupsafe import Markup

from ..models import ContestEntry, School
from .base_page import base_page
from .logo import school_logo

_STYLE = """
me {
	width: 100%;
	display: flex;
	flex-direction: column;
	align-items: center;
}

me a {
	color: {main_color};
	text-decoration: underline;
	transition: opacity 0.2s;
}

me a:hover {
	opacity: 0.7;
	transition: opacity 0.2s;
}

me main {
	width: 100%;
	text-align: center;
	padding: 2rem 0;
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
	background-color: black;
	padding: 2rem 0;
}

me .button-holder {
	display: flex;
	justify-content: center;
	margin: 1.5rem 0;
}

me main {
	color: {main_color};
	background-color: {main_bg_color};
}

me main h2 {
	display: flex;
	justify-content: center;
	align-items: center;
}

me main .hidden {
	display: none;
}

me main .code {
	font-size: 0.75em;
}

me main .clipboard,
me main .copied {
	margin-left: 0.2em;
	margin-top: 0.05em;
	width: 0.75em;
}

me main .clipboard {
	opacity: 0.5;
	cursor: pointer;
	transition: opacity 0.2s;
}

me main .clipboard:hover {
	opacity: 1;
	transition: opacity 0.2s;
}

me main .copied {
	opacity: 0.5;
}

@media screen and (min-width: 768px) {

	me main .clipboard,
	me main .copied {
		margin-left: 0.2em;
		margin-top: 0.2em;
		width: 1em;
	}


	me main .code {
		font-size: 1em;
	}
}
"""


_CLIPBOARD_SVG = Markup("""
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 7.5V6.108c0-1.135.845-2.098 1.976-2.192.373-.03.748-.057 1.123-.08M15.75 18H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08M15.75 18.75v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5A3.375 3.375 0 0 0 6.375 7.5H5.25m11.9-3.664A2.251 2.251 0 0 0 15 2.25h-1.5a2.251 2.251 0 0 0-2.15 1.586m5.8 0c.065.21.1.433.1.664v.75h-6V4.5c0-.231.035-.454.1-.664M6.75 7.5H4.875c-.621 0-1.125.504-1.125 1.125v12c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V16.5a9 9 0 0 0-9-9Z" />
</svg>
""")

_CLIPBOARD_CHECK_SVG = Markup("""
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M11.35 3.836c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m8.9-4.414c.376.023.75.05 1.124.08 1.131.094 1.976 1.057 1.976 2.192V16.5A2.25 2.25 0 0 1 18 18.75h-2.25m-7.5-10.5H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V18.75m-7.5-10.5h6.375c.621 0 1.125.504 1.125 1.125v9.375m-8.25-3 1.5 1.5 3-3.75" />
</svg>
""")


def _style(main_color: str, main_bg_color: str) -> h.Element:
    return h.style[
        _STYLE.replace("{main_color}", main_color).replace(
            "{main_bg_color}", main_bg_color
        )
    ]


_SCRIPT = h.script[
    Markup("""
(function(self) {
    onloadAdd(() => {
        const clipboard = self.querySelector(".clipboard");
        const copied = self.querySelector(".copied");
        const code = self.querySelector(".code");
        if (!clipboard || !copied || !code) {
            return;
        }
        clipboard.addEventListener("click", () => {
            navigator.clipboard.writeText(code.innerText);
            // hide the `clipboard` span; show the `copied` span
            // do this by adding `hidden` class to `clipboard` and
            // removing it from `copied`
            clipboard.classList.add("hidden");
            copied.classList.remove("hidden");
        });
    });
})(me());
""")
]


def _congrats(contest_entry: ContestEntry, claim_code: str) -> h.Node:
    return [
        h.p[f"Congrats! You won a ${contest_entry.amount_won} gift card!"],
        h.h2[
            h.span(".code")[claim_code],
            h.span(".clipboard", title="Copy to clipboard")[_CLIPBOARD_SVG],
            h.span(".copied hidden", title="Copied!")[_CLIPBOARD_CHECK_SVG],
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
            _style(
                main_color=school.logo.bg_text_color, main_bg_color=school.logo.bg_color
            ),
            h.main[
                _SCRIPT,
                h.div(".container")[
                    school_logo(school),
                    _congrats(contest_entry, claim_code)
                    if contest_entry and claim_code
                    else _sorry(),
                ],
            ],
        ],
    ]
