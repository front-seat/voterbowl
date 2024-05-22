"""Utilities for working with HTML-in-python components."""

import pathlib
import typing as t
from dataclasses import dataclass, field, replace

import htpy as h
import markdown
from htpy import _iter_children as _h_iter_children
from markupsafe import Markup


def _load_file(file_name: str | pathlib.Path) -> str:
    """Load a text file and return its contents."""
    with open(file_name, "r") as f:
        return f.read()


def _load_sibling_file(base_file_name: str | pathlib.Path, file_name: str) -> str:
    """Load a file in the same directory as the base file."""
    return _load_file(pathlib.Path(base_file_name).resolve().parent / file_name)


def svg(base_file_name: str | pathlib.Path, file_name: str) -> Markup:
    """Load an SVG file in the same directory as the base file."""
    return Markup(_load_sibling_file(base_file_name, file_name))


def markdown_html(base_file_name: str | pathlib.Path, file_name: str) -> Markup:
    """Load a markdown file in the same directory as the base file."""
    text = _load_sibling_file(base_file_name, file_name)
    return Markup(markdown.markdown(text))


def css_vars(**vars: str) -> str:
    """Generate CSS variables to inject into an inline style attribute."""
    return " ".join(f"--{k.replace('_', '-')}: {v};" for k, v in vars.items())


@dataclass(frozen=True)
class with_children[C, R: (h.Element, h.Node), **P]:
    """Wrap a function to make it look more like an htpy.Element."""

    _f: t.Callable[t.Concatenate[C, P], R]
    _args: tuple[t.Any, ...] = field(default_factory=tuple)
    _kwargs: t.Mapping[str, t.Any] = field(default_factory=dict)

    def __getitem__(self, children: C) -> R:
        """Render the component with the given children."""
        return self._f(children, *self._args, **self._kwargs)  # type: ignore

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> t.Self:
        """Return a new instance of the class with the given arguments."""
        return replace(self, _args=args, _kwargs=kwargs)

    def __str__(self) -> str:
        """Return the name of the function being wrapped."""
        # CONSIDER: alternatively, invoke the function here? If the function
        # provides a default value for its arguments, it'll work; otherwise,
        # it will blow up... which might be a good thing?
        return f"with_children[{self._f.__name__}]"


class Fragment:
    """
    A fragment of HTML with no explicit parent element.

    CONSIDER: this feels like it should perhaps be the base class from
    which htpy.Element inherits? It's a container for children, without
    an Element's tag/attributes. And htpy.Node should probably include
    this as well.
    """

    __slots__ = ("_children",)

    def __init__(self, children: h.Node) -> None:
        """Initialize the fragment with the given children."""
        self._children = children

    def __getitem__(self, children: h.Node) -> t.Self:
        """Return a new fragment with the given children."""
        return self.__class__(children)

    def __str__(self) -> Markup:
        """Return the fragment as a string."""
        return Markup("".join(str(x) for x in self))

    def __iter__(self):
        """Iterate over the children of the fragment."""
        # XXX I'm using a private method here, which is not ideal.
        yield from _h_iter_children(self._children)


fragment = Fragment(None)
