from typing import Protocol, Collection
from datetime import datetime
from abc import abstractmethod
from phdkit import unimplemented, strip_indent


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
    def __repr__(self) -> str:
        return strip_indent(f"""
            |<Post id={self.id}
            |      url={self.url}
            |      published_date={self.published_date}
            |      pulled_date={self.pulled_date}
            |      source={self.source}
            |      attachments={",".join(self.attachments)}>
            {self.to_prompt()}
            |</Post>
        """)

    def __str__(self) -> str:
        return self.to_prompt()

    @abstractmethod
    def to_prompt(self) -> str:
        """Convert the post content to a prompt for the language model."""
        return unimplemented()

    @abstractmethod
    def serializable_object(self) -> object:
        """Return a serializable representation of the post content.

        Typically, it will be a recursive dictionary/list/primitive object that can be easily
        serialized to JSON or similar formats. This method will be used for storing the post in a
        database or sending it over a network.
        """
        return unimplemented()

    @abstractmethod
    @classmethod
    def from_serializable_object(cls, obj: object) -> "Post":
        """Populate the post content from a serializable representation.

        This method will be used for loading the post from a database or receiving it over a network.
        """
        return unimplemented()
