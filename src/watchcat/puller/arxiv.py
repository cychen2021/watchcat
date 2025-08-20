from typing import Sequence, override, Collection
from enum import Enum
import urllib.request
import urllib.parse
from xml.etree import ElementTree as ET
from datetime import datetime

from watchcat.puller.post import Post
from .source import Source, SourceKind, SourceFilter
from .arxiv_paper import ArxivPaper


class ArxivFilterKind(Enum):
    TITLE = "title"
    AUTHOR = "author"
    DATE = "date"
    ABSTRACT = "abstract"


class _CombinedFilter(SourceFilter):
    """Helper class for combining filters with AND/OR operations."""

    def __init__(self, left: SourceFilter, right: SourceFilter, operator: str) -> None:
        self.left = left
        self.right = right
        self.operator = operator

    def __call__(self, post: Post) -> bool:
        if self.operator == "AND":
            return self.left(post) and self.right(post)
        elif self.operator == "OR":
            return self.left(post) or self.right(post)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    def __and__(self, other: SourceFilter) -> SourceFilter:
        return _CombinedFilter(self, other, "AND")

    def __or__(self, other: SourceFilter) -> SourceFilter:
        return _CombinedFilter(self, other, "OR")

    def __invert__(self) -> SourceFilter:
        return _InvertedFilter(self)


class _InvertedFilter(SourceFilter):
    """Helper class for inverting filters."""

    def __init__(self, filter_obj: SourceFilter) -> None:
        self.filter_obj = filter_obj

    def __call__(self, post: Post) -> bool:
        return not self.filter_obj(post)

    def __and__(self, other: SourceFilter) -> SourceFilter:
        return _CombinedFilter(self, other, "AND")

    def __or__(self, other: SourceFilter) -> SourceFilter:
        return _CombinedFilter(self, other, "OR")

    def __invert__(self) -> SourceFilter:
        return self.filter_obj


class ArxivFilter(SourceFilter):
    def __init__(self, kind: ArxivFilterKind, **filter_args) -> None:
        self.kind = kind
        self.filter_args = filter_args

    def __call__(self, post: Post) -> bool:
        """Check if a post matches the filter criteria."""
        if not isinstance(post, ArxivPaper):
            return False

        if self.kind == ArxivFilterKind.TITLE:
            # For title filtering, we might need to extract title from URL or use a different approach
            # Since ArxivPaper doesn't have a title field, we'll check URL or source instead
            if "term" in self.filter_args:
                term = self.filter_args["term"].lower()
                # Check if term appears in URL, source, or abstract as a fallback
                return (
                    term in post.url.lower()
                    or term in post.source.lower()
                    or term in post.abstract.lower()
                )

        elif self.kind == ArxivFilterKind.AUTHOR:
            # ArxivPaper doesn't have authors field, so we'll search in abstract or source
            if "name" in self.filter_args:
                name = self.filter_args["name"].lower()
                return name in post.abstract.lower() or name in post.source.lower()

        elif self.kind == ArxivFilterKind.ABSTRACT:
            if "term" in self.filter_args:
                term = self.filter_args["term"].lower()
                return term in post.abstract.lower()

        elif self.kind == ArxivFilterKind.DATE:
            if "start" in self.filter_args and "end" in self.filter_args:
                start_date = self.filter_args["start"]
                end_date = self.filter_args["end"]
                return start_date <= post.__published_date <= end_date

        return False

    def __and__(self, other: SourceFilter) -> SourceFilter:
        """Combine two filters with a logical AND."""
        return _CombinedFilter(self, other, "AND")

    def __or__(self, other: SourceFilter) -> SourceFilter:
        """Combine two filters with a logical OR."""
        return _CombinedFilter(self, other, "OR")

    def __invert__(self) -> SourceFilter:
        """Invert the filter."""
        return _InvertedFilter(self)


class Arxiv(Source):
    kind: SourceKind = SourceKind.ARXIV
    API_ENDPOINT = "http://export.arxiv.org/api/query"

    def construct_query(self, filters: Collection[ArxivFilter]) -> str:
        """Construct an ArXiv API search query from a collection of filters.

        Args:
            filters: Collection of ArxivFilter objects to combine into a query

        Returns:
            A string that can be used as the search_query parameter for the ArXiv API
        """
        if not filters:
            return ""

        query_parts = []

        for filter_obj in filters:
            if filter_obj.kind == ArxivFilterKind.TITLE:
                # Title search: ti:search_term
                if "term" in filter_obj.filter_args:
                    term = filter_obj.filter_args["term"]
                    query_parts.append(f'ti:"{term}"')

            elif filter_obj.kind == ArxivFilterKind.AUTHOR:
                # Author search: au:author_name
                if "name" in filter_obj.filter_args:
                    name = filter_obj.filter_args["name"]
                    query_parts.append(f'au:"{name}"')

            elif filter_obj.kind == ArxivFilterKind.ABSTRACT:
                # Abstract search: abs:search_term
                if "term" in filter_obj.filter_args:
                    term = filter_obj.filter_args["term"]
                    query_parts.append(f'abs:"{term}"')

            elif filter_obj.kind == ArxivFilterKind.DATE:
                # Date range search: submittedDate:[start TO end]
                if (
                    "start" in filter_obj.filter_args
                    and "end" in filter_obj.filter_args
                ):
                    start_date = filter_obj.filter_args["start"]
                    end_date = filter_obj.filter_args["end"]
                    # Ensure dates are in YYYYMMDDTTTT format
                    if hasattr(start_date, "strftime"):
                        start_date = start_date.strftime("%Y%m%d%H%M")
                    if hasattr(end_date, "strftime"):
                        end_date = end_date.strftime("%Y%m%d%H%M")
                    query_parts.append(f"submittedDate:[{start_date} TO {end_date}]")

        # Combine all query parts with AND
        if len(query_parts) == 1:
            return query_parts[0]
        elif len(query_parts) > 1:
            return " AND ".join(f"({part})" for part in query_parts)
        else:
            return ""

    def __init__(self, id: str) -> None:
        self.id = id

    @override
    def pull(self, *filters: SourceFilter) -> Sequence[ArxivPaper]:
        if not filters:
            raise ValueError(
                "At least one filter is required to pull posts from Arxiv, or otherwise there will be too many papers."
            )

        # Separate ArxivFilter objects from other filters
        arxiv_filters = [f for f in filters if isinstance(f, ArxivFilter)]
        other_filters = [f for f in filters if not isinstance(f, ArxivFilter)]

        # Construct query string for ArXiv API
        query = self.construct_query(arxiv_filters)
        if not query:
            # If no arxiv filters provided, we still need some constraint
            # For safety, we'll limit to recent papers
            from datetime import timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # Last week by default
            query = f"submittedDate:[{start_date.strftime('%Y%m%d%H%M')} TO {end_date.strftime('%Y%m%d%H%M')}]"

        # Make request to ArXiv API
        papers = self._fetch_papers_from_arxiv(query)

        # Apply additional filters that aren't ArxivFilter
        if other_filters:
            filtered_papers = []
            for paper in papers:
                if all(filter_obj(paper) for filter_obj in other_filters):
                    filtered_papers.append(paper)
            papers = filtered_papers

        return papers

    def _fetch_papers_from_arxiv(
        self, query: str, max_results: int = 100
    ) -> list[ArxivPaper]:
        """Fetch papers from ArXiv API and parse them into ArxivPaper objects."""
        # Construct the full API URL
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        url = f"{self.API_ENDPOINT}?{urllib.parse.urlencode(params)}"

        try:
            # Make the HTTP request
            with urllib.request.urlopen(url) as response:
                xml_content = response.read().decode("utf-8")

            # Parse the XML response
            root = ET.fromstring(xml_content)

            # Define XML namespaces
            namespaces = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }

            papers = []
            entries = root.findall("atom:entry", namespaces)

            for entry in entries:
                try:
                    # Extract paper information with null checks
                    paper_id_elem = entry.find("atom:id", namespaces)
                    if paper_id_elem is None or paper_id_elem.text is None:
                        continue
                    paper_id = paper_id_elem.text

                    # Get the ArXiv ID from the URL
                    arxiv_id = paper_id.split("/")[-1]

                    title_elem = entry.find("atom:title", namespaces)
                    if title_elem is None or title_elem.text is None:
                        continue
                    title = title_elem.text.strip()

                    abstract_elem = entry.find("atom:summary", namespaces)
                    if abstract_elem is None or abstract_elem.text is None:
                        continue
                    abstract = abstract_elem.text.strip()

                    # Parse publish date
                    published_elem = entry.find("atom:published", namespaces)
                    if published_elem is None or published_elem.text is None:
                        continue
                    published_str = published_elem.text
                    publish_date = datetime.fromisoformat(
                        published_str.replace("Z", "+00:00")
                    )

                    # Get PDF URL
                    links = entry.findall("atom:link", namespaces)
                    pdf_url = None
                    for link in links:
                        if link.get("title") == "pdf":
                            pdf_url = link.get("href")
                            break

                    if not pdf_url:
                        # Fallback: construct PDF URL from ArXiv ID
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                    # Create ArxivPaper object
                    paper = ArxivPaper(
                        id=arxiv_id,
                        url=paper_id,
                        paper_url=pdf_url,
                        publish_date=publish_date,
                        title=title,
                        abstract=abstract,
                        source=f"ArXiv: {title}",
                    )

                    papers.append(paper)

                except Exception:
                    # Skip papers that fail to parse
                    continue

            return papers

        except Exception:
            # If API request fails, return empty list
            # In a production system, you might want to log this error
            return []
