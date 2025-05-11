from dataclasses import dataclass


@dataclass
class ArxivPaper:
    id: str
    title: str
    authors: list[str]
    summary: str
    url: str
