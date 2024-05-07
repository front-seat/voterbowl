"""Utilities for working with HTML-in-python components."""

import json
import pathlib
import typing as t

import htpy as h
import markdown
from markupsafe import Markup
from pydantic.alias_generators import to_camel


def load_file(file_name: str | pathlib.Path) -> str:
    """Load a text file and return its contents."""
    with open(file_name, "r") as f:
        return f.read()


def load_sibling_file(base_file_name: str | pathlib.Path, file_name: str) -> str:
    """Load a file in the same directory as the base file."""
    return load_file(pathlib.Path(base_file_name).resolve().parent / file_name)


def _css_vars(selector: str, /, **vars: str) -> str:
    """Generate CSS variables to inject into a stylesheet."""
    as_css = "\n".join("  --{k.replace('_', '-')}: {v};" for k, v in vars.items())
    return f"{selector} {{\n{as_css}\n}}\n"


def style(base_file_name: str | pathlib.Path, file_name: str, **vars: str) -> h.Element:
    """
    Load a CSS file in the same directory as the base file.

    In addition to the file, you can pass in CSS variables to inject into the
    stylesheet.
    """
    text = load_sibling_file(base_file_name, file_name)
    if vars:
        text = _css_vars("me", **vars) + text
    return h.style[Markup(text)]


def js(
    base_file_name: str | pathlib.Path,
    file_name: str,
    *,
    surreal: bool = True,
    **props: t.Any,
) -> h.Element:
    """
    Load a JS file in the same directory as the base file.

    Return a script element.

    If `props` are provided, they are added to the script element
    as data-props JSON.

    The `surreal` flag, if True, causes us to wrap the provided javascript
    in an invocation wrapper. The javascript is expected to take
    two arguments: `self` and `props`.

    CONSIDER: this still feels awkward to me, and I bet there's a cleaner
    pattern -- our CSS pattern feels very clean to me, for instance.
    """
    text = load_sibling_file(base_file_name, file_name)
    element = h.script
    if props:
        as_camel = {to_camel(k): v for k, v in props.items()}
        as_json = json.dumps(as_camel)
        element = element(data_props=as_json)
    if surreal:
        text = f"({text})(me(), me('script').dataset.props && JSON.parse(me('script').dataset.props))"  # noqa: E501
    return element[Markup(text)]


def svg(base_file_name: str | pathlib.Path, file_name: str) -> Markup:
    """Load an SVG file in the same directory as the base file."""
    return Markup(load_sibling_file(base_file_name, file_name))


def markdown_html(base_file_name: str | pathlib.Path, file_name: str) -> Markup:
    """Load a markdown file in the same directory as the base file."""
    text = load_sibling_file(base_file_name, file_name)
    return Markup(markdown.markdown(text))
