"""Unit and mock tests for Arxiv source class."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from urllib.error import URLError

from watchcat.puller.arxiv import Arxiv, ArxivFilter, ArxivFilterKind, _CombinedFilter, _InvertedFilter
from watchcat.puller.arxiv_paper import ArxivPaper
from watchcat.puller.source import SourceKind


class TestArxivFilter:
    """Test cases for ArxivFilter class."""

    def test_arxiv_filter_initialization(self):
        """Test ArxivFilter initialization."""
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="machine learning")
        assert filter_obj.kind == ArxivFilterKind.TITLE
        assert filter_obj.filter_args == {"term": "machine learning"}

    def test_title_filter(self):
        """Test title filtering."""
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="machine learning")
        
        # Create a test paper
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Machine Learning Paper",
            abstract="This paper discusses machine learning algorithms.",
            source="ArXiv: Machine Learning Paper",
        )
        
        # Should match because "machine learning" is in the abstract
        assert filter_obj(paper) is True
        
        # Test with non-matching content
        paper2 = ArxivPaper(
            id="2306.54321",
            url="http://arxiv.org/abs/2306.54321",
            paper_url="http://arxiv.org/pdf/2306.54321.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Physics Paper",
            abstract="This paper discusses quantum physics.",
            source="ArXiv: Physics Paper",
        )
        
        assert filter_obj(paper2) is False

    def test_abstract_filter(self):
        """Test abstract filtering."""
        filter_obj = ArxivFilter(ArxivFilterKind.ABSTRACT, term="quantum")
        
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Physics Paper",
            abstract="This paper discusses quantum mechanics.",
            source="ArXiv: Physics Paper",
        )
        
        assert filter_obj(paper) is True

    def test_author_filter(self):
        """Test author filtering."""
        filter_obj = ArxivFilter(ArxivFilterKind.AUTHOR, name="einstein")
        
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Physics Paper",
            abstract="By Einstein, this paper discusses relativity.",
            source="ArXiv: Physics Paper",
        )
        
        assert filter_obj(paper) is True

    def test_non_arxiv_paper_filter(self):
        """Test filter with non-ArxivPaper object."""
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="test")
        
        # Mock a different type of Post
        mock_post = Mock()
        mock_post.__class__ = Mock  # Not ArxivPaper
        
        assert filter_obj(mock_post) is False

    def test_filter_combinations(self):
        """Test filter combination with logical operators."""
        filter1 = ArxivFilter(ArxivFilterKind.TITLE, term="machine")
        filter2 = ArxivFilter(ArxivFilterKind.ABSTRACT, term="learning")
        
        # Test AND operation
        combined_and = filter1 & filter2
        assert isinstance(combined_and, _CombinedFilter)
        assert combined_and.operator == "AND"
        
        # Test OR operation
        combined_or = filter1 | filter2
        assert isinstance(combined_or, _CombinedFilter)
        assert combined_or.operator == "OR"
        
        # Test inversion
        inverted = ~filter1
        assert isinstance(inverted, _InvertedFilter)

    def test_combined_filter_and(self):
        """Test combined filter with AND operation."""
        filter1 = ArxivFilter(ArxivFilterKind.TITLE, term="machine")
        filter2 = ArxivFilter(ArxivFilterKind.ABSTRACT, term="learning")
        combined = filter1 & filter2
        
        # Create paper that matches both filters
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Machine Learning Paper",
            abstract="This paper discusses machine learning algorithms.",
            source="ArXiv: Machine Learning Paper",
        )
        
        assert combined(paper) is True
        
        # Create paper that matches only one filter
        paper2 = ArxivPaper(
            id="2306.54321",
            url="http://arxiv.org/abs/2306.54321",
            paper_url="http://arxiv.org/pdf/2306.54321.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Physics Paper",
            abstract="This paper discusses machine physics.",  # Only "machine", not "learning"
            source="ArXiv: Physics Paper",
        )
        
        assert combined(paper2) is False

    def test_combined_filter_or(self):
        """Test combined filter with OR operation."""
        filter1 = ArxivFilter(ArxivFilterKind.TITLE, term="machine")
        filter2 = ArxivFilter(ArxivFilterKind.ABSTRACT, term="quantum")
        combined = filter1 | filter2
        
        # Paper matching first filter
        paper1 = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Machine Learning Paper",
            abstract="This paper discusses machine learning.",
            source="ArXiv: Machine Learning Paper",
        )
        
        assert combined(paper1) is True
        
        # Paper matching second filter
        paper2 = ArxivPaper(
            id="2306.54321",
            url="http://arxiv.org/abs/2306.54321",
            paper_url="http://arxiv.org/pdf/2306.54321.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Physics Paper",
            abstract="This paper discusses quantum mechanics.",
            source="ArXiv: Physics Paper",
        )
        
        assert combined(paper2) is True
        
        # Paper matching neither filter
        paper3 = ArxivPaper(
            id="2306.99999",
            url="http://arxiv.org/abs/2306.99999",
            paper_url="http://arxiv.org/pdf/2306.99999.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Biology Paper",
            abstract="This paper discusses biology.",
            source="ArXiv: Biology Paper",
        )
        
        assert combined(paper3) is False

    def test_inverted_filter(self):
        """Test inverted filter."""
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="machine")
        inverted = ~filter_obj
        
        # Paper that would match the original filter
        paper1 = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Machine Learning Paper",
            abstract="This paper discusses machine learning.",
            source="ArXiv: Machine Learning Paper",
        )
        
        # Should not match inverted filter
        assert inverted(paper1) is False
        
        # Paper that wouldn't match the original filter
        paper2 = ArxivPaper(
            id="2306.54321",
            url="http://arxiv.org/abs/2306.54321",
            paper_url="http://arxiv.org/pdf/2306.54321.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Physics Paper",
            abstract="This paper discusses physics.",
            source="ArXiv: Physics Paper",
        )
        
        # Should match inverted filter
        assert inverted(paper2) is True

    def test_double_inversion(self):
        """Test double inversion returns original behavior."""
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="machine")
        double_inverted = ~~filter_obj
        
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="ML Paper",
            abstract="This paper discusses machine learning.",
            source="ArXiv: ML Paper",
        )
        
        # Double inversion should behave like original
        assert double_inverted(paper) == filter_obj(paper)


class TestArxiv:
    """Test cases for Arxiv source class."""

    def test_arxiv_initialization(self):
        """Test Arxiv source initialization."""
        arxiv = Arxiv(id="test_arxiv")
        assert arxiv.id == "test_arxiv"
        assert arxiv.kind == SourceKind.ARXIV

    def test_construct_query_title_filter(self):
        """Test query construction for title filter."""
        arxiv = Arxiv(id="test")
        filters = [ArxivFilter(ArxivFilterKind.TITLE, term="machine learning")]
        
        query = arxiv.construct_query(filters)
        assert query == 'ti:"machine learning"'

    def test_construct_query_author_filter(self):
        """Test query construction for author filter."""
        arxiv = Arxiv(id="test")
        filters = [ArxivFilter(ArxivFilterKind.AUTHOR, name="John Doe")]
        
        query = arxiv.construct_query(filters)
        assert query == 'au:"John Doe"'

    def test_construct_query_abstract_filter(self):
        """Test query construction for abstract filter."""
        arxiv = Arxiv(id="test")
        filters = [ArxivFilter(ArxivFilterKind.ABSTRACT, term="neural networks")]
        
        query = arxiv.construct_query(filters)
        assert query == 'abs:"neural networks"'

    def test_construct_query_date_filter(self):
        """Test query construction for date filter."""
        arxiv = Arxiv(id="test")
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        filters = [ArxivFilter(ArxivFilterKind.DATE, start=start_date, end=end_date)]
        
        query = arxiv.construct_query(filters)
        assert "submittedDate:[202301010000 TO 202312310000]" in query

    def test_construct_query_multiple_filters(self):
        """Test query construction with multiple filters."""
        arxiv = Arxiv(id="test")
        filters = [
            ArxivFilter(ArxivFilterKind.TITLE, term="machine learning"),
            ArxivFilter(ArxivFilterKind.AUTHOR, name="John Doe"),
        ]
        
        query = arxiv.construct_query(filters)
        assert 'ti:"machine learning"' in query
        assert 'au:"John Doe"' in query
        assert " AND " in query

    def test_construct_query_empty_filters(self):
        """Test query construction with empty filters."""
        arxiv = Arxiv(id="test")
        query = arxiv.construct_query([])
        assert query == ""

    def test_pull_no_filters_raises_error(self):
        """Test that pull raises error when no filters provided."""
        arxiv = Arxiv(id="test")
        
        with pytest.raises(ValueError, match="At least one filter is required"):
            arxiv.pull()

    @patch('watchcat.puller.arxiv.urllib.request.urlopen')
    def test_pull_with_filter_success(self, mock_urlopen):
        """Test successful pull with filter."""
        # Mock the XML response
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom" 
              xmlns:arxiv="http://arxiv.org/schemas/atom">
            <entry>
                <id>http://arxiv.org/abs/2306.12345v1</id>
                <title>Test Paper Title</title>
                <summary>This is a test abstract about machine learning.</summary>
                <published>2023-06-15T12:00:00Z</published>
                <link href="http://arxiv.org/pdf/2306.12345v1.pdf" title="pdf" type="application/pdf"/>
            </entry>
        </feed>'''
        
        mock_response = Mock()
        mock_response.read.return_value = mock_xml.encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response
        
        arxiv = Arxiv(id="test")
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="machine learning")
        
        papers = arxiv.pull(filter_obj)
        
        assert len(papers) == 1
        assert isinstance(papers[0], ArxivPaper)
        assert papers[0].id == "2306.12345v1"
        assert papers[0].title == "Test Paper Title"
        assert "machine learning" in papers[0].abstract

    @patch('watchcat.puller.arxiv.urllib.request.urlopen')
    def test_pull_with_http_error(self, mock_urlopen):
        """Test pull with HTTP error."""
        mock_urlopen.side_effect = URLError("Connection failed")
        
        arxiv = Arxiv(id="test")
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="test")
        
        papers = arxiv.pull(filter_obj)
        
        # Should return empty list on error
        assert papers == []

    @patch('watchcat.puller.arxiv.urllib.request.urlopen')
    def test_pull_with_malformed_xml(self, mock_urlopen):
        """Test pull with malformed XML response."""
        mock_response = Mock()
        mock_response.read.return_value = b"<invalid>xml</malformed>"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response
        
        arxiv = Arxiv(id="test")
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="test")
        
        papers = arxiv.pull(filter_obj)
        
        # Should return empty list on parsing error
        assert papers == []

    @patch('watchcat.puller.arxiv.urllib.request.urlopen')
    def test_pull_with_missing_fields(self, mock_urlopen):
        """Test pull with XML missing required fields."""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <!-- Missing required fields like id, title, etc. -->
                <summary>Incomplete entry</summary>
            </entry>
        </feed>'''
        
        mock_response = Mock()
        mock_response.read.return_value = mock_xml.encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response
        
        arxiv = Arxiv(id="test")
        filter_obj = ArxivFilter(ArxivFilterKind.TITLE, term="test")
        
        papers = arxiv.pull(filter_obj)
        
        # Should skip incomplete entries
        assert papers == []

    @patch('watchcat.puller.arxiv.urllib.request.urlopen')
    def test_pull_with_additional_filters(self, mock_urlopen):
        """Test pull with additional non-ArxivFilter filters."""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2306.12345v1</id>
                <title>Test Paper</title>
                <summary>This is a test abstract.</summary>
                <published>2023-06-15T12:00:00Z</published>
            </entry>
        </feed>'''
        
        mock_response = Mock()
        mock_response.read.return_value = mock_xml.encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response
        
        # Create a mock additional filter that rejects all papers
        mock_filter = Mock()
        mock_filter.return_value = False
        
        arxiv = Arxiv(id="test")
        arxiv_filter = ArxivFilter(ArxivFilterKind.TITLE, term="test")
        
        papers = arxiv.pull(arxiv_filter, mock_filter)
        
        # Should be empty because additional filter rejects all
        assert papers == []

    def test_fetch_papers_fallback_pdf_url(self):
        """Test PDF URL fallback when no explicit PDF link is found."""
        arxiv = Arxiv(id="test")
        
        # Mock XML without explicit PDF link
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2306.12345v1</id>
                <title>Test Paper</title>
                <summary>Test abstract</summary>
                <published>2023-06-15T12:00:00Z</published>
                <link href="http://arxiv.org/abs/2306.12345v1" type="text/html"/>
            </entry>
        </feed>'''
        
        with patch('watchcat.puller.arxiv.urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = mock_xml.encode('utf-8')
            mock_response.__enter__ = Mock(return_value=mock_response)
            mock_response.__exit__ = Mock(return_value=None)
            mock_urlopen.return_value = mock_response
            
            papers = arxiv._fetch_papers_from_arxiv("test query")
            
            assert len(papers) == 1
            assert papers[0].paper_url == "https://arxiv.org/pdf/2306.12345v1.pdf"

    @patch('watchcat.puller.arxiv.datetime')
    def test_pull_default_date_range(self, mock_datetime):
        """Test pull with default date range when no ArxivFilter provided."""
        # Mock current time
        mock_now = datetime(2023, 6, 15, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        arxiv = Arxiv(id="test")
        
        # Create a non-ArxivFilter
        mock_filter = Mock()
        mock_filter.return_value = True
        
        with patch('watchcat.puller.arxiv.urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = b'<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
            mock_response.__enter__ = Mock(return_value=mock_response)
            mock_response.__exit__ = Mock(return_value=None)
            mock_urlopen.return_value = mock_response
            
            # papers variable is used to trigger the API call and test the URL format
            arxiv.pull(mock_filter)
            
            # Check that the API was called with a date range query
            mock_urlopen.assert_called_once()
            url = mock_urlopen.call_args[0][0]
            assert "submittedDate" in url
