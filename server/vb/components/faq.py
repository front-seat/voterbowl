import htpy as h

from server.utils.components import markdown_html

from ..models import School


def faq(school: School | None) -> h.Element:
    """Render the frequently asked questions."""
    return h.div("#faq")[markdown_html(__file__, "faq.md")]
