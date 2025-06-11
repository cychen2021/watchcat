from typing import override
from .source import Source, SourceKind, SourceFilter
from .arxiv_paper import ArxivPaper

class Arxiv(Source):
    kind: SourceKind = SourceKind.ARXIV

    def __init__(self) -> None:
        ...
