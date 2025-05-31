from typing import Protocol, Collection, Callable
from datetime import datetime
from abc import abstractmethod
from ..util import unimplemented


__all__ = ["Post"]


class Post(Protocol):
    """A post pulled from a source.

    A post is a piece of content that can be pulled from a source, such as a research paper, blog post, or forum entry.
    """

    id: str
    url: str
    attachments: Collection[str]  # URLs to attachments or related resources
    published_date: datetime
    pulled_date: datetime
    source: str  # Identifier for the source from which the post was pulled

    @abstractmethod
    def __str__(self) -> str:
        unimplemented()

    @abstractmethod
    def serializable_object(self) -> object:
        """Return a serializable representation of the post content.

        Typically, it will be a recursive dictionary/list/primitive structure that can be easily
        serialized to JSON or similar formats. This method will be used for storing the post in a
        database or sending it over a network.
        """
        unimplemented()

    @abstractmethod
    def from_serializable_object(self, obj: object) -> None:
        """Populate the post content from a serializable representation.

        This method will be used for loading the post from a database or receiving it over a network.
        """
        unimplemented()

    @abstractmethod
    def summarize_embedding(
        self, compute_embedding: Callable[..., list[float]]
    ) -> list[float]:
        """Generate an embedding that summarizes the post content using the provided embedding function."""
        unimplemented()
