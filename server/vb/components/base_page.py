import htpy as h
from django.templatetags.static import static
from markupsafe import Markup

from server.utils.components import css_vars, with_children

from .faq import faq
from .footer import footer


def _gtag_scripts() -> h.Node:
    """Render the Google Analytics scripts."""
    return [
        h.script(
            src="https://www.googletagmanager.com/gtag/js?id=G-RDV3WS6HTE",
            _async=True,
        ),
        h.script[
            Markup("""
                window.dataLayer = window.dataLayer || [];

                function gtag() {
                    dataLayer.push(arguments);
                }
                gtag('js', new Date());
                gtag('config', 'G-RDV3WS6HTE');
            """)
        ],
    ]


@with_children
def base_page(
    children: h.Node = None,
    *,
    extra_head: h.Node | None = None,
    title: str = "VoterBowl",
    bg_color: str = "#cdff64",
    show_faq: bool = True,
    show_footer: bool = True,
) -> h.Element:
    """Render the generic structure for all pages on voterbowl.org."""
    return h.html(lang="en", style=css_vars(bg_color=bg_color))[
        h.head[
            _gtag_scripts(),
            h.title[title],
            h.meta(name="description", content="VoterBowl: online voting competitions"),
            h.meta(name="keywords", content="voting, competition, online"),
            h.meta(charset="utf-8"),
            h.meta(http_equiv="X-UA-Compatible", content="IE=edge"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            h.meta(name="format-detection", content="telephone=no"),
            h.link(rel="stylesheet", href=static("css/voterbowl.css")),
            h.script(src=static("js/voterbowl.mjs"), type="module"),
            extra_head,
        ],
        h.body[
            children,
            h.div("#faq")[h.div(".container")[faq(school=None)]] if show_faq else None,
            footer() if show_footer else None,
        ],
    ]
