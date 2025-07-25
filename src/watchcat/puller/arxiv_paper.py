from datetime import datetime
from typing import Sequence, override
from .post import Post
from phdkit import strip_indent, protect_indent


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
        __pulled_date: datetime | None = None,
        source: str,
    ) -> None:
        self.id = id
        self.url = url
        self.paper_url = paper_url
        self.__published_date = publish_date
        if __pulled_date is None:
            self.pull_date = datetime.now()
        else:
            self.pull_date = __pulled_date
        self.source = source
        self.abstract = abstract

    @property
    def published_date(self) -> datetime:
        """Alias for publish_date to match Post protocol."""
        return self.__published_date

    @property
    def pulled_date(self) -> datetime:
        """Alias for pull_date to match Post protocol."""
        return self.pull_date

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
            |    publish_date={self.__published_date},
            |    pull_date={self.pull_date},
            |    source={self.source},
            |    abstract={protect_indent(self.abstract)}
            |)
            |---
            |{self.abstract}""",
            keep_trailing_ws=True,
        )

    @override
    def serializable_object(self) -> dict[str, str]:
        return {
            "id": self.id,
            "url": self.url,
            "paper_url": self.paper_url,
            "publish_date": self.__published_date.isoformat(),
            "pull_date": self.pull_date.isoformat(),
            "source": self.source,
            "abstract": self.abstract,
        }

    @override
    def from_serializable_object(self, obj: dict[str, str]) -> None:
        self.id = obj["id"]
        self.url = obj["url"]
        self.paper_url = obj["paper_url"]
        self.__published_date = datetime.fromisoformat(obj["publish_date"])
        self.pull_date = datetime.fromisoformat(obj["pull_date"])
        self.source = obj["source"]
        self.abstract = obj["abstract"]

    @override
    def summarize_embedding(self, compute_embedding) -> list[float]:
        return compute_embedding(self.abstract)
