from datetime import datetime
from typing import Sequence, override
from .post import Post
from phdkit import strip_indent


__all__ = ["ArxivPaper"]


class ArxivPaper(Post):
    def __init__(
        self,
        *,
        id: str,
        url: str,
        paper_url: str,
        publish_date: datetime,
        title: str,
        abstract: str,
        pulled_date: datetime | None = None,
        source: str,
    ) -> None:
        self.id = id
        self.url = url
        self.paper_url = paper_url
        self.__published_date = publish_date
        if pulled_date is None:
            self.pull_date = datetime.now()
        else:
            self.pull_date = pulled_date
        self.source = source
        self.abstract = abstract
        self.title = title

    @override
    def to_prompt(self) -> str:
        return strip_indent(f"""
            |# {self.title}
            |{self.abstract}
        """)

    @override
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

    @override
    def serializable_object(self) -> dict[str, str]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "paper_url": self.paper_url,
            "publish_date": self.__published_date.isoformat(),
            "pull_date": self.pull_date.isoformat(),
            "source": self.source,
            "abstract": self.abstract,
        }

    @override
    @classmethod
    def from_serializable_object(cls, obj: dict[str, str]) -> "ArxivPaper":
        instance = cls(
            id=obj["id"],
            url=obj["url"],
            paper_url=obj["paper_url"],
            publish_date=datetime.fromisoformat(obj["publish_date"]),
            title=obj["title"],
            abstract=obj["abstract"],
            pulled_date=datetime.fromisoformat(obj["pull_date"]),
            source=obj["source"],
        )
        return instance
