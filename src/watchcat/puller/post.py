from typing import Protocol, Collection
from datetime import datetime

class Post(Protocol):
    """A post pulled from a source.

    A post is a piece of content that can be pulled from a source, such as a research paper, blog post, or forum entry.
    """

    id: str
    title: str
    summary: str
    content: str
    url: str
    attachments: Collection[str]  # URLs to attachments or related resources
    published_date: datetime
    pulled_date: datetime
    source: str  # Identifier for the source from which the post was pulled
