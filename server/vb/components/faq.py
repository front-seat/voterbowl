import typing as t

import htpy as h

from server.utils.components import markdown_html, style

from ..models import School


def qa(q: str, a: t.Iterable[h.Node]) -> h.Element:
    """Render a question and answer."""
    return h.div(".qa")[
        h.h3[q],
        (h.p[aa] for aa in a),
    ]


def faq(school: School | None) -> h.Element:
    """Render the frequently asked questions."""
    # TODO HTPY
    # check_now: list[h.Node] = [
    #     "Check now to avoid any last minute issues before the election."
    # ]
    # if school is not None:
    #     check_now = [
    #         h.a(href=reverse("vb:check", args=[school.slug]))["Check now"],
    #         " to avoid any last minute issues before the election.",
    #     ]

    return h.div[
        style(__file__, "faq.css"),
        markdown_html(__file__, "faq.md"),
    ]
