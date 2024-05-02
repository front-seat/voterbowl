import htpy as h

from .utils import with_children

_STYLE = """
me {
  cursor: pointer;
  transition: opacity 0.2s ease-in-out;
  text-transform: uppercase;
  text-decoration: none;
  font-weight: 600;
  font-size: 18px;
  line-height: 100%;
  border: none;
  text-align: center;
  letter-spacing: 0.05em;
  padding: 20px 24px;
  background-color: {bg_color};
  color: {color};
}

me:hover {
  opacity: 0.7;
  transition: opacity 0.2s ease-in-out;
}
"""


def _style(bg_color: str, color: str) -> h.Element:
    return h.style[_STYLE.replace("{bg_color}", bg_color).replace("{color}", color)]


@with_children
def button(children: h.Node, href: str, bg_color: str, color: str) -> h.Element:
    """Render a button with the given background and text color."""
    return h.a(href=href)[_style(bg_color, color), children]
