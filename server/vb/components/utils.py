import typing as t
from collections.abc import Callable
from dataclasses import dataclass

import htpy as h

P = t.ParamSpec("P")
R = t.TypeVar("R")
C = t.TypeVar("C")


@dataclass
class _ChildrenWrapper(t.Generic[C, R]):
    _component_func: t.Callable
    _args: t.Tuple[t.Any, ...]
    _kwargs: t.Dict[str, t.Any]

    def __getitem__(self, children: C) -> R:
        return self._component_func(children, *self._args, **self._kwargs)  # type: ignore


@dataclass
class _OuterChildrenWrapper(t.Generic[P, C, R]):
    _component_func: t.Callable

    def __getitem__(self, children: C) -> R:
        return self._component_func(children)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> _ChildrenWrapper[C, R]:
        return _ChildrenWrapper(self._component_func, args, kwargs)


def with_children(
    component_func: Callable[t.Concatenate[C, P], R],
) -> _OuterChildrenWrapper[P, C, R]:
    """Wrap a component function to allow for children to be passed in a more natural way."""
    return _OuterChildrenWrapper[P, C, R](component_func)


@with_children
def bs_button(children: h.Node, style: t.Literal["success", "danger"]) -> h.Element:
    """Render a Bootstrap button."""
    return h.button(class_=["btn", f"btn-{style}"])[children]


@with_children
def card(children: h.Node) -> h.Element:
    """Render only the children."""
    return h.div("card")[children]


print(bs_button(style="danger")["Delete my account"])
print(bs_button(style="success"))
print(card[h.p["This is a paragraph."]])
