import typing as t
from dataclasses import dataclass, field, replace

import htpy as h
from htpy import _iter_children as _h_iter_children
from markupsafe import Markup

# FUTURE use PEP 695 syntax when mypy supports it
P = t.ParamSpec("P")
C = t.TypeVar("C")
R = t.TypeVar("R", h.Element, h.Node)


@dataclass(frozen=True)
class with_children(t.Generic[C, P, R]):
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
        # CONSIDER: alternatively, require that all wrapped functions
        # have a default value for the `children` argument, and invoke
        # the function here?
        return f"with_children[{self._f.__name__}]"


@with_children
def card(children: h.Node, data_foo: str | None = None) -> h.Element:
    """Render a card with the given children."""
    return h.div(".card", data_foo=data_foo)[children]


@with_children
def list_items(children: t.Iterable[str]) -> h.Node:
    """Render all children in list items."""
    return [h.li[child] for child in children]


class Fragment:
    """A fragment of HTML that can be rendered as a string."""

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
        yield from _h_iter_children(self._children)


fragment = Fragment(None)
