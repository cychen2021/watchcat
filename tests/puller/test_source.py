"""Unit tests for source module enums and protocols."""

from watchcat.puller.source import SourceKind


class TestSourceKind:
    """Test cases for SourceKind enum."""

    def test_source_kind_values(self):
        """Test SourceKind enum values."""
        assert SourceKind.ARXIV.value == "arxiv"
        assert SourceKind.MAIL.value == "mail"

    def test_source_kind_members(self):
        """Test SourceKind enum members."""
        assert SourceKind.ARXIV in SourceKind
        assert SourceKind.MAIL in SourceKind
        assert len(SourceKind) == 2

    def test_source_kind_string_representation(self):
        """Test string representation of SourceKind."""
        assert str(SourceKind.ARXIV) == "SourceKind.ARXIV"
        assert str(SourceKind.MAIL) == "SourceKind.MAIL"
