import datetime
import typing as t
from dataclasses import dataclass, field, replace
from math import floor

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


@dataclass(frozen=True)
class RemainingTime:
    """Render the remaining time until the given end time."""

    h0: int
    """The tens digit of the hours."""

    h1: int
    """The ones digit of the hours."""

    m0: int
    """The tens digit of the minutes."""

    m1: int
    """The ones digit of the minutes."""

    s0: int
    """The tens digit of the seconds."""

    s1: int
    """The ones digit of the seconds."""

    @property
    def ended(self) -> bool:
        """Return whether the remaining time has ended."""
        return self.h0 == self.h1 == self.m0 == self.m1 == self.s0 == self.s1 == 0


def remaining_time(
    end_at: datetime.datetime, when: datetime.datetime | None = None
) -> RemainingTime:
    """Render the remaining time until the given end time."""
    now = when or datetime.datetime.now(datetime.UTC)
    delta = end_at - now
    if delta.total_seconds() <= 0:
        return RemainingTime(0, 0, 0, 0, 0, 0)
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    hours, minutes, seconds = map(floor, (hours, minutes, seconds))
    return RemainingTime(
        h0=hours // 10,
        h1=hours % 10,
        m0=minutes // 10,
        m1=minutes % 10,
        s0=seconds // 10,
        s1=seconds % 10,
    )


def small_countdown_str(
    end_at: datetime.datetime, when: datetime.datetime | None = None
) -> str:
    """Render the remaining time until the given end time."""
    rt = remaining_time(end_at, when)
    if rt.ended:
        return "Just ended!"
    return f"Ends in {rt.h0}{rt.h1}:{rt.m0}{rt.m1}:{rt.s0}{rt.s1}"
