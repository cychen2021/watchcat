"""Integration tests for the complete puller workflow."""

from unittest.mock import Mock, patch
from datetime import datetime

from watchcat.puller.source import SourceKind
from watchcat.puller.arxiv import Arxiv, ArxivFilter, ArxivFilterKind
from watchcat.puller.mailbox import Mailbox, MailFilter, MailFilterKind
from watchcat.puller.arxiv_paper import ArxivPaper
from watchcat.puller.mail import Mail


class TestPullerIntegration:
    """Integration tests for the complete puller workflow."""

    def test_source_kind_consistency(self):
        """Test that source kinds are consistent across implementations."""
        arxiv = Arxiv(id="test_arxiv")
        mailbox = Mailbox(
            id="test_mailbox",
            server="mail.example.com",
            username="user",
            password="pass",
        )
        
        assert arxiv.kind == SourceKind.ARXIV
        assert mailbox.kind == SourceKind.MAIL
        assert SourceKind.ARXIV.value == "arxiv"
        assert SourceKind.MAIL.value == "mail"

    @patch('watchcat.puller.arxiv.urllib.request.urlopen')
    def test_arxiv_end_to_end_workflow(self, mock_urlopen):
        """Test complete ArXiv workflow from filter to parsed papers."""
        # Setup mock response
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2306.12345v1</id>
                <title>Machine Learning in Quantum Computing</title>
                <summary>This paper explores the intersection of machine learning and quantum computing.</summary>
                <published>2023-06-15T12:00:00Z</published>
                <link href="http://arxiv.org/pdf/2306.12345v1.pdf" title="pdf" type="application/pdf"/>
            </entry>
            <entry>
                <id>http://arxiv.org/abs/2306.54321v1</id>
                <title>Classical Algorithms</title>
                <summary>This paper discusses traditional algorithmic approaches.</summary>
                <published>2023-06-16T10:00:00Z</published>
                <link href="http://arxiv.org/pdf/2306.54321v1.pdf" title="pdf" type="application/pdf"/>
            </entry>
        </feed>'''
        
        mock_response = Mock()
        mock_response.read.return_value = mock_xml.encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response
        
        # Create source and filters
        arxiv = Arxiv(id="quantum_ml_source")
        ml_filter = ArxivFilter(ArxivFilterKind.TITLE, term="machine learning")
        quantum_filter = ArxivFilter(ArxivFilterKind.ABSTRACT, term="quantum")
        combined_filter = ml_filter & quantum_filter
        
        # Pull papers
        papers = arxiv.pull(combined_filter)
        
        # Verify results
        assert len(papers) == 1  # Only one paper matches both filters
        paper = papers[0]
        assert isinstance(paper, ArxivPaper)
        assert paper.id == "2306.12345v1"
        assert paper.title == "Machine Learning in Quantum Computing"
        assert "machine learning" in paper.abstract.lower()
        assert "quantum" in paper.abstract.lower()
        assert paper.paper_url == "http://arxiv.org/pdf/2306.12345v1.pdf"
        
        # Test serialization workflow
        serialized = paper.serializable_object()
        restored_paper = ArxivPaper.from_serializable_object(serialized)
        assert restored_paper.id == paper.id
        assert restored_paper.title == paper.title
        assert restored_paper.abstract == paper.abstract

    def test_filter_composition_complex(self):
        """Test complex filter compositions work correctly."""
        # Create complex filter: (title:ML OR abstract:AI) AND NOT author:Smith
        ml_title = ArxivFilter(ArxivFilterKind.TITLE, term="machine learning")
        ai_abstract = ArxivFilter(ArxivFilterKind.ABSTRACT, term="artificial intelligence")
        smith_author = ArxivFilter(ArxivFilterKind.AUTHOR, name="Smith")
        
        # Complex composition: (ML_title OR AI_abstract) AND NOT Smith_author
        complex_filter = (ml_title | ai_abstract) & (~smith_author)
        
        # Create test papers
        paper1 = ArxivPaper(
            id="1",
            url="http://arxiv.org/abs/1",
            paper_url="http://arxiv.org/pdf/1.pdf",
            publish_date=datetime.now(),
            title="Machine Learning Methods",
            abstract="Methods for ML research",
            source="Test",
        )
        
        paper2 = ArxivPaper(
            id="2",
            url="http://arxiv.org/abs/2",
            paper_url="http://arxiv.org/pdf/2.pdf",
            publish_date=datetime.now(),
            title="Physics Paper",
            abstract="Artificial intelligence in physics by Smith",
            source="Test",
        )
        
        paper3 = ArxivPaper(
            id="3",
            url="http://arxiv.org/abs/3",
            paper_url="http://arxiv.org/pdf/3.pdf",
            publish_date=datetime.now(),
            title="Biology Paper",
            abstract="Biology research without AI or ML",
            source="Test",
        )
        
        # Test the complex filter
        assert complex_filter(paper1) is True   # Has ML in title, no Smith
        assert complex_filter(paper2) is False  # Has AI but also Smith
        assert complex_filter(paper3) is False  # No ML or AI
        
    def test_mail_filter_composition(self):
        """Test mail filter compositions work correctly."""
        # Create filters
        urgent_subject = MailFilter(MailFilterKind.SUBJECT, term="urgent")
        boss_sender = MailFilter(MailFilterKind.SENDER, email="boss@company.com")
        has_attachment = MailFilter(MailFilterKind.HAS_ATTACHMENT, has_attachment=True)
        
        # Composition: urgent AND (from_boss OR has_attachment)
        complex_filter = urgent_subject & (boss_sender | has_attachment)
        
        # Test mails
        mail1 = Mail(
            id="1",
            url="mailbox://test/1",
            subject="Urgent: Review needed",
            body="Please review",
            attachments=["doc.pdf"],
            received_date=datetime.now(),
            source="colleague@company.com",
        )
        
        mail2 = Mail(
            id="2",
            url="mailbox://test/2",
            subject="Urgent: Meeting",
            body="Meeting tomorrow",
            attachments=[],
            received_date=datetime.now(),
            source="Mailbox (boss@company.com): Urgent: Meeting",
        )
        
        mail3 = Mail(
            id="3",
            url="mailbox://test/3",
            subject="Regular update",
            body="Weekly update",
            attachments=[],
            received_date=datetime.now(),
            source="colleague@company.com",
        )
        
        # Test the complex filter
        assert complex_filter(mail1) is True   # Urgent + has attachment
        assert complex_filter(mail2) is True   # Urgent + from boss
        assert complex_filter(mail3) is False  # Not urgent
        
    def test_post_protocol_compliance(self):
        """Test that both ArxivPaper and Mail properly implement Post protocol."""
        paper = ArxivPaper(
            id="test_paper",
            url="http://arxiv.org/abs/test",
            paper_url="http://arxiv.org/pdf/test.pdf",
            publish_date=datetime.now(),
            title="Test Paper",
            abstract="Test abstract",
            source="Test Source",
        )
        
        mail = Mail(
            id="test_mail",
            url="mailbox://test/mail",
            subject="Test Subject",
            body="Test body",
            attachments=["test.pdf"],
            received_date=datetime.now(),
            source="Test Sender",
        )
        
        # Both should have the same protocol interface
        for post in [paper, mail]:
            assert hasattr(post, 'id')
            assert hasattr(post, 'url') 
            assert hasattr(post, 'attachments')
            assert hasattr(post, 'published_date')
            assert hasattr(post, 'pulled_date')
            assert hasattr(post, 'source')
            assert callable(getattr(post, 'to_prompt'))
            assert callable(getattr(post, 'serializable_object'))
            assert hasattr(post.__class__, 'from_serializable_object')
            
            # Test methods work
            prompt = post.to_prompt()
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            
            serialized = post.serializable_object()
            assert isinstance(serialized, dict)
            
            # Test round-trip
            restored = post.__class__.from_serializable_object(serialized)
            assert restored.id == post.id
            assert restored.url == post.url
            assert restored.source == post.source

    def test_error_handling_robustness(self):
        """Test that error handling is robust across the system."""
        # Test ArxivPaper with minimal data
        minimal_paper = ArxivPaper(
            id="min",
            url="http://test.com",
            paper_url="http://test.pdf",
            publish_date=datetime.now(),
            title="",  # Empty title
            abstract="",  # Empty abstract
            source="",  # Empty source
        )
        
        # Should still work
        assert minimal_paper.to_prompt() is not None
        serialized = minimal_paper.serializable_object()
        restored = ArxivPaper.from_serializable_object(serialized)
        assert restored.id == minimal_paper.id
        
        # Test Mail with minimal data
        minimal_mail = Mail(
            id="min",
            url="mailbox://test",
            subject="",  # Empty subject
            body="",  # Empty body
            attachments=[],  # No attachments
            received_date=datetime.now(),
            source="",  # Empty source
        )
        
        # Should still work
        assert minimal_mail.to_prompt() is not None
        serialized = minimal_mail.serializable_object()
        restored = Mail.from_serializable_object(serialized)
        assert restored.id == minimal_mail.id
        
    def test_filter_type_safety(self):
        """Test that filters correctly handle wrong post types."""
        # ArXiv filter should reject Mail objects
        arxiv_filter = ArxivFilter(ArxivFilterKind.TITLE, term="test")
        mail = Mail(
            id="test",
            url="mailbox://test",
            subject="test paper title",
            body="test content",
            attachments=[],
            received_date=datetime.now(),
            source="test",
        )
        assert arxiv_filter(mail) is False
        
        # Mail filter should reject ArxivPaper objects  
        mail_filter = MailFilter(MailFilterKind.SUBJECT, term="test")
        paper = ArxivPaper(
            id="test",
            url="http://arxiv.org/abs/test",
            paper_url="http://arxiv.org/pdf/test.pdf",
            publish_date=datetime.now(),
            title="test subject line",
            abstract="test content",
            source="test",
        )
        assert mail_filter(paper) is False
