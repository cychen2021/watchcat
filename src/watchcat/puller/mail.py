from datetime import datetime
from typing import Sequence, override
from .post import Post
from phdkit import strip_indent


__all__ = ["Mail"]


class Mail(Post):
    def __init__(
        self,
        *,
        id: str,
        url: str,
        subject: str,
        body: str,
        attachments: Sequence[str],
        received_date: datetime,
        pulled_date: datetime | None = None,
        source: str,
    ) -> None:
        self.id = id
        self.url = url
        self.subject = subject
        self.body = body
        self._attachments = attachments
        self.published_date = received_date
        if pulled_date is None:
            self.pulled_date = datetime.now()
        else:
            self.pulled_date = pulled_date
        self.source = source

    @override
    def to_prompt(self) -> str:
        """Convert the mail content to a prompt for the language model."""
        return strip_indent(f"""
            |# {self.subject}
            |{self.body}
        """)

    @override
    def __repr__(self) -> str:
        """String representation of the mail object."""
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
    @override
    def attachments(self) -> Sequence[str]:
        """Return the list of attachment URLs."""
        return self._attachments

    @override
    def serializable_object(self) -> dict[str, str]:
        """Return a serializable representation of the mail content."""
        return {
            "id": self.id,
            "url": self.url,
            "subject": self.subject,
            "body": self.body,
            "attachments": ",".join(self.attachments),
            "received_date": self.published_date.isoformat(),
            "pulled_date": self.pulled_date.isoformat(),
            "source": self.source,
        }

    @override
    @classmethod
    def from_serializable_object(cls, obj: dict[str, str]) -> "Mail":
        """Populate the mail content from a serializable representation."""
        instance = cls(
            id=obj["id"],
            url=obj["url"],
            subject=obj["subject"],
            body=obj["body"],
            attachments=obj["attachments"].split(",") if obj["attachments"] else [],
            received_date=datetime.fromisoformat(obj["received_date"]),
            pulled_date=datetime.fromisoformat(obj["pulled_date"]),
            source=obj["source"],
        )
        return instance
