from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Iterator
from .paper import ArxivPaper


class ArxivSortBy(Enum):
    RELEVANCE = "relevance"


@dataclass
class ArxivSearch:
    query: str
    max_results: int = 100
    sort_by: ArxivSortBy = ArxivSortBy.RELEVANCE
    ascending: bool = False


class ArxivClient:
    URL = "http://export.arxiv.org/api/query"

    def results(self, search: ArxivSearch) -> Iterator[ArxivPaper]:
        """Fetch papers from arXiv API based on search criteria."""

        params = {
            "search_query": search.query,
            "max_results": str(search.max_results),
            "sortBy": search.sort_by.value,
            "sortOrder": "ascending" if search.ascending else "descending",
        }

        query_string = urllib.parse.urlencode(params)
        url = f"{self.URL}?{query_string}"

        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")

        # Parse XML response
        root = ET.fromstring(content)

        # Define namespace
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):
            yield self._parse_entry(entry, ns)

    def _parse_entry(self, entry: ET.Element, ns: dict) -> ArxivPaper:
        """Parse a single arXiv entry into an ArxivPaper object."""

        # Extract basic information
        id_elem = entry.find("atom:id", ns)
        title_elem = entry.find("atom:title", ns)
        summary_elem = entry.find("atom:summary", ns)
        published_elem = entry.find("atom:published", ns)
        updated_elem = entry.find("atom:updated", ns)

        # Extract authors
        authors = []
        for author in entry.findall("atom:author", ns):
            name_elem = author.find("atom:name", ns)
            if name_elem is not None:
                assert name_elem.text is not None
                authors.append(name_elem.text.strip())

        # Extract categories
        categories = []
        for category in entry.findall("atom:category", ns):
            term = category.get("term")
            if term:
                categories.append(term)

        # Extract PDF URL
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.get("type") == "application/pdf":
                pdf_url = link.get("href", "")
                break
        assert (
            id_elem is not None and id_elem.text is not None
        ), f"{id_elem} is None or has no text"
        assert (
            title_elem is not None and title_elem.text is not None
        ), f"{title_elem} is None or has no text"
        assert (
            summary_elem is not None and summary_elem.text is not None
        ), f"{summary_elem} is None or has no text"
        assert (
            published_elem is not None and published_elem.text is not None
        ), f"{published_elem} is None or has no text"
        assert (
            updated_elem is not None and updated_elem.text is not None
        ), f"{updated_elem} is None or has no text"
        return ArxivPaper(
            id=id_elem.text.strip() if id_elem is not None else "",
            title=title_elem.text.strip() if title_elem is not None else "",
            abstract=summary_elem.text.strip() if summary_elem is not None else "",
            authors=authors,
            published=(
                datetime.fromisoformat(published_elem.text.replace("Z", "+00:00"))
                if published_elem is not None
                else datetime.min
            ),
            updated=(
                datetime.fromisoformat(updated_elem.text.replace("Z", "+00:00"))
                if updated_elem is not None
                else datetime.min
            ),
            categories=categories,
            pdf_url=pdf_url,
        )
