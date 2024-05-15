import htpy as h

from server.utils.components import style

from .utils import with_children


@with_children
def button(children: h.Node, href: str, bg_color: str, color: str) -> h.Element:
    """Render a button with the given background and text color."""
    return h.a(href=href)[
        style(__file__, "button.css", bg_color=bg_color, color=color), children
    ]
