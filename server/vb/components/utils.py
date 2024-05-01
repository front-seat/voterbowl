import typing as t
from dataclasses import dataclass, field, replace

import htpy as h


@dataclass(frozen=True)
class with_children[C, **P, R]:
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


# Wrapped func that returns Element; children only
# <div class="card"><p>paragraph content</p></div>
print(card[h.p["paragraph content"]])

# Wrapped func that returns Element; children + kwargs
# <div class="card" data-foo="bar">content</div>
print(card(data_foo="bar")["content"])

# Wrapped func that returns Node; children only
# <ul><li>Neato</li><li>Burrito</li></ul>
print(h.ul[list_items["Neato", "Burrito"]])

# The odd duck that doesn't behave like an h.Element:
# with_children[card]
print(card)

# Another odd duck:
# with_children[card]
print(card())


if t.TYPE_CHECKING:
    # h.Element
    t.reveal_type(card["content"])

    # h.Node
    t.reveal_type(list_items["Neato", "Burrito"])

    # with_children[...]
    t.reveal_type(card)
