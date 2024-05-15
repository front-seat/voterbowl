import htpy as h

from server.utils.components import markdown_html, style

from .base_page import base_page


def rules_page() -> h.Element:
    """Render the rules page."""
    return base_page(title="Voter Bowl Rules", bg_color="white", show_faq=False)[
        h.div(".container")[
            style(__file__, "rules_page.css"),
            markdown_html(__file__, "rules.md"),
        ]
    ]
