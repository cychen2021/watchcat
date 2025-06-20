from typing import Sequence, override, Collection
from enum import Enum

from watchcat.puller.post import Post
from .source import Source, SourceKind, SourceFilter
from .arxiv_paper import ArxivPaper

class ArxivFilterKind(Enum):
    TITLE = "title"
    AUTHOR = "author"
    DATE = "date"
    ABSTRACT = "abstract"

class ArxivFilter(SourceFilter):
    def __init__(self, kind: ArxivFilterKind, **filter_args) -> None:
        self.kind = kind
        self.filter_args = filter_args



class Arxiv(Source):
    kind: SourceKind = SourceKind.ARXIV
    API_ENDPOINT = "http://export.arxiv.org/api/query"

    def construct_query(self, filters: Collection[ArxivFilter]) -> str:
        ...

    def __init__(self, id: str) -> None:
        self.id = id

    @override
    def pull(self, *filters: SourceFilter) -> Sequence[ArxivPaper]:
        if not filters:
            raise ValueError(
                "At least one filter is required to pull posts from Arxiv, or otherwise there will be too many papers."
            )
        ...
        return []