from enum import Enum
from typing import Protocol, Sequence
from abc import abstractmethod
from .post import Post
from ..util import unimplemented


class SourceKind(Enum):
    ARXIV = "arxiv"
    ZULIP = "zulip"
    MAIL = "mail"


class SourceFilter(Protocol):
    """A filter for posts pulled from a source."""

    @abstractmethod
    def __call__(self, post: Post) -> bool:
        """Check if a post matches the filter criteria."""
        unimplemented()

    @abstractmethod
    def __and__(self, other: "SourceFilter") -> "SourceFilter":
        """Combine two filters with a logical AND."""
        unimplemented()

    @abstractmethod
    def __or__(self, other: "SourceFilter") -> "SourceFilter":
        """Combine two filters with a logical OR."""
        unimplemented()

    @abstractmethod
    def __invert__(self) -> "SourceFilter":
        """Invert the filter."""
        unimplemented()


class Source(Protocol):
    """An information source that can be pulled.

    Note that any class that implements a source should be configurable.
    """

    id: str
    kind: SourceKind

    @abstractmethod
    def pull(self, *filters: SourceFilter) -> Sequence[Post]:
        """Pull posts from the source, optionally filtered by the provided filters.

        Returns a sequence of posts that match the filters, possibly ordered.
        """
        unimplemented()
