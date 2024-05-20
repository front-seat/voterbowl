import htpy as h

from server.utils.components import css_vars, with_children


@with_children
def button(children: h.Node, href: str, bg_color: str, color: str) -> h.Element:
    """Render a button with the given background and text color."""
    return h.a(".button", href=href, style=css_vars(bg_color=bg_color, color=color))[
        children
    ]
