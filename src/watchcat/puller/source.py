from enum import Enum
from typing import Protocol, Sequence, Collection
from .post import Post


class SourceKind(Enum):
    ARXIV = "arxiv"
    ZULIP = "zulip"
    MAIL = "mail"


class SourceFilter(Protocol):
    """A filter for posts pulled from a source."""

    def __call__(self, post: Post) -> bool:
        """Check if a post matches the filter criteria."""
        ...

    def __and__(self, other: "SourceFilter") -> "SourceFilter":
        """Combine two filters with a logical AND."""
        ...

    def __or__(self, other: "SourceFilter") -> "SourceFilter":
        """Combine two filters with a logical OR."""
        ...

    def __invert__(self) -> "SourceFilter":
        """Invert the filter."""
        ...


class Source(Protocol):
    """An information source that can be pulled.

    Note that any class that implements a source should be configurable.
    """

    id: str
    kind: SourceKind

    def pull(self, *filters: SourceFilter) -> Sequence[Post]: ...
