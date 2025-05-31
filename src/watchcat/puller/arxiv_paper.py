from datetime import datetime
from typing import Sequence, override
from .post import Post
from ..util import strip_indent


__all__ = ["ArxivPaper"]

class ArxivPaper(Post):
    def __init__(
        self,
        *,
        id: str,
        url: str,
        paper_url: str,
        publish_date: datetime,
        abstract: str,
        pull_date: datetime | None = None,
        source: str,
    ) -> None:
        self.id = id
        self.url = url
        self.paper_url = paper_url
        self.publish_date = publish_date
        if pull_date is None:
            self.pull_date = datetime.now()
        else:
            self.pull_date = pull_date
        self.source = source
        self.abstract = abstract

    @property
    @override
    def attachments(self) -> Sequence[str]:
        return [self.paper_url]

    def __str__(self) -> str:
        return strip_indent(
            f"""
            |ArxivPaper(
            |    id={self.id},
            |    url={self.url},
            |    paper_url={self.paper_url},
            |    publish_date={self.publish_date},
            |    pull_date={self.pull_date},
            |    source={self.source},
            |    abstract={self.abstract}
            |)
            |---
            |{self.abstract}
        """
        )

    @override
    def serializable_object(self) -> object:
        ...

    @override
    def from_serializable_object(self, obj: object) -> None:
        ...

    @override
    def summarize_embedding(self, compute_embedding) -> list[float]:
        ...