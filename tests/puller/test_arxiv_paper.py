"""Unit tests for ArxivPaper class."""

from datetime import datetime
from watchcat.puller.arxiv_paper import ArxivPaper


class TestArxivPaper:
    """Test cases for ArxivPaper class."""

    def test_arxiv_paper_initialization(self):
        """Test ArxivPaper object initialization."""
        test_date = datetime(2023, 6, 15, 12, 30)
        pulled_date = datetime(2023, 6, 16, 10, 0)

        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=test_date,
            title="Test Paper",
            abstract="This is a test abstract.",
            pulled_date=pulled_date,
            source="ArXiv: Test Paper",
        )

        assert paper.id == "2306.12345"
        assert paper.url == "http://arxiv.org/abs/2306.12345"
        assert paper.paper_url == "http://arxiv.org/pdf/2306.12345.pdf"
        assert paper.published_date == test_date
        assert paper.pulled_date == pulled_date
        assert paper.title == "Test Paper"
        assert paper.abstract == "This is a test abstract."
        assert paper.source == "ArXiv: Test Paper"

    def test_arxiv_paper_auto_pulled_date(self):
        """Test ArxivPaper with auto-generated pulled date."""
        before_creation = datetime.now()

        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Test Paper",
            abstract="This is a test abstract.",
            source="ArXiv: Test Paper",
        )

        after_creation = datetime.now()

        # Check that pulled_date is between before and after creation time
        assert before_creation <= paper.pulled_date <= after_creation

    def test_attachments_property(self):
        """Test that attachments property returns paper URL."""
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Test Paper",
            abstract="This is a test abstract.",
            source="ArXiv: Test Paper",
        )

        assert paper.attachments == ["http://arxiv.org/pdf/2306.12345.pdf"]

    def test_to_prompt(self):
        """Test to_prompt method returns formatted content."""
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Test Paper",
            abstract="This is a test abstract.",
            source="ArXiv: Test Paper",
        )

        prompt = paper.to_prompt()
        assert "# Test Paper" in prompt
        assert "This is a test abstract." in prompt

    def test_repr(self):
        """Test __repr__ method returns formatted string."""
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Test Paper",
            abstract="This is a test abstract.",
            source="ArXiv: Test Paper",
        )

        repr_str = repr(paper)
        assert "2306.12345" in repr_str
        assert "http://arxiv.org/abs/2306.12345" in repr_str
        assert "# Test Paper" in repr_str
        assert "This is a test abstract." in repr_str

    def test_serializable_object(self):
        """Test serializable_object method returns correct dict."""
        test_date = datetime(2023, 6, 15, 12, 30)
        pulled_date = datetime(2023, 6, 16, 10, 0)

        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=test_date,
            title="Test Paper",
            abstract="This is a test abstract.",
            pulled_date=pulled_date,
            source="ArXiv: Test Paper",
        )

        serialized = paper.serializable_object()

        expected = {
            "id": "2306.12345",
            "url": "http://arxiv.org/abs/2306.12345",
            "title": "Test Paper",
            "paper_url": "http://arxiv.org/pdf/2306.12345.pdf",
            "publish_date": "2023-06-15T12:30:00",
            "pull_date": "2023-06-16T10:00:00",
            "source": "ArXiv: Test Paper",
            "abstract": "This is a test abstract.",
        }

        assert serialized == expected

    def test_from_serializable_object(self):
        """Test from_serializable_object class method."""
        serialized_data = {
            "id": "2306.12345",
            "url": "http://arxiv.org/abs/2306.12345",
            "title": "Test Paper",
            "paper_url": "http://arxiv.org/pdf/2306.12345.pdf",
            "publish_date": "2023-06-15T12:30:00",
            "pull_date": "2023-06-16T10:00:00",
            "source": "ArXiv: Test Paper",
            "abstract": "This is a test abstract.",
        }

        paper = ArxivPaper.from_serializable_object(serialized_data)

        assert paper.id == "2306.12345"
        assert paper.url == "http://arxiv.org/abs/2306.12345"
        assert paper.title == "Test Paper"
        assert paper.paper_url == "http://arxiv.org/pdf/2306.12345.pdf"
        assert paper.published_date == datetime(2023, 6, 15, 12, 30)
        assert paper.pulled_date == datetime(2023, 6, 16, 10, 0)
        assert paper.source == "ArXiv: Test Paper"
        assert paper.abstract == "This is a test abstract."

    def test_serialization_roundtrip(self):
        """Test that serialization and deserialization is reversible."""
        original_paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15, 12, 30),
            title="Test Paper",
            abstract="This is a test abstract.",
            pulled_date=datetime(2023, 6, 16, 10, 0),
            source="ArXiv: Test Paper",
        )

        # Serialize and then deserialize
        serialized = original_paper.serializable_object()
        restored_paper = ArxivPaper.from_serializable_object(serialized)

        # Check that all important attributes match
        assert restored_paper.id == original_paper.id
        assert restored_paper.url == original_paper.url
        assert restored_paper.title == original_paper.title
        assert restored_paper.paper_url == original_paper.paper_url
        assert restored_paper.published_date == original_paper.published_date
        assert restored_paper.pulled_date == original_paper.pulled_date
        assert restored_paper.source == original_paper.source
        assert restored_paper.abstract == original_paper.abstract
        assert restored_paper.attachments == original_paper.attachments

    def test_multiline_abstract(self):
        """Test ArxivPaper with multiline abstract."""
        paper = ArxivPaper(
            id="2306.12345",
            url="http://arxiv.org/abs/2306.12345",
            paper_url="http://arxiv.org/pdf/2306.12345.pdf",
            publish_date=datetime(2023, 6, 15),
            title="Test Paper",
            abstract="This is the first line.\nThis is the second line.\nThis is the third line.",
            source="ArXiv: Test Paper",
        )

        prompt = paper.to_prompt()
        assert "first line" in prompt
        assert "second line" in prompt
        assert "third line" in prompt
