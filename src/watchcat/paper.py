from dataclasses import dataclass
from datetime import datetime
from typing import Sequence


@dataclass
class ArxivPaper:
    id: str
    title: str
    abstract: str
    authors: Sequence[str]
    published: datetime
    updated: datetime
    categories: Sequence[str]
    pdf_url: str

    @property
    def arxiv_id(self) -> str:
        """Extract the arXiv ID from the full ID URL."""
        return self.id.split("/")[-1]
