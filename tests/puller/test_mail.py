"""Unit tests for Mail class."""

from datetime import datetime
from watchcat.puller.mail import Mail


class TestMail:
    """Test cases for Mail class."""

    def test_mail_initialization(self):
        """Test Mail object initialization."""
        received_date = datetime(2023, 6, 15, 12, 30)
        pulled_date = datetime(2023, 6, 16, 10, 0)
        attachments = ["file1.pdf", "file2.txt"]
        
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is a test email body.",
            attachments=attachments,
            received_date=received_date,
            pulled_date=pulled_date,
            source="test@example.com",
        )
        
        assert mail.id == "msg_12345"
        assert mail.url == "mailbox://example.com/INBOX/12345"
        assert mail.subject == "Test Email"
        assert mail.body == "This is a test email body."
        assert mail.attachments == attachments
        assert mail.published_date == received_date
        assert mail.pulled_date == pulled_date
        assert mail.source == "test@example.com"

    def test_mail_auto_pulled_date(self):
        """Test Mail with auto-generated pulled date."""
        before_creation = datetime.now()
        
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is a test email body.",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )
        
        after_creation = datetime.now()
        
        # Check that pulled_date is between before and after creation time
        assert before_creation <= mail.pulled_date <= after_creation

    def test_empty_attachments(self):
        """Test Mail with empty attachments."""
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is a test email body.",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )
        
        assert mail.attachments == []

    def test_to_prompt(self):
        """Test to_prompt method returns formatted content."""
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email Subject",
            body="This is the email body content.",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )
        
        prompt = mail.to_prompt()
        assert "# Test Email Subject" in prompt
        assert "This is the email body content." in prompt

    def test_repr(self):
        """Test __repr__ method returns formatted string."""
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is a test email body.",
            attachments=["file1.pdf"],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )
        
        repr_str = repr(mail)
        assert "msg_12345" in repr_str
        assert "mailbox://example.com/INBOX/12345" in repr_str
        assert "# Test Email" in repr_str
        assert "This is a test email body." in repr_str
        assert "file1.pdf" in repr_str

    def test_serializable_object(self):
        """Test serializable_object method returns correct dict."""
        received_date = datetime(2023, 6, 15, 12, 30)
        pulled_date = datetime(2023, 6, 16, 10, 0)
        attachments = ["file1.pdf", "file2.txt"]
        
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is a test email body.",
            attachments=attachments,
            received_date=received_date,
            pulled_date=pulled_date,
            source="test@example.com",
        )
        
        serialized = mail.serializable_object()
        
        expected = {
            "id": "msg_12345",
            "url": "mailbox://example.com/INBOX/12345",
            "subject": "Test Email",
            "body": "This is a test email body.",
            "attachments": "file1.pdf,file2.txt",
            "received_date": "2023-06-15T12:30:00",
            "pulled_date": "2023-06-16T10:00:00",
            "source": "test@example.com",
        }
        
        assert serialized == expected

    def test_serializable_object_empty_attachments(self):
        """Test serializable_object method with empty attachments."""
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is a test email body.",
            attachments=[],
            received_date=datetime(2023, 6, 15, 12, 30),
            pulled_date=datetime(2023, 6, 16, 10, 0),
            source="test@example.com",
        )
        
        serialized = mail.serializable_object()
        assert serialized["attachments"] == ""

    def test_from_serializable_object(self):
        """Test from_serializable_object class method."""
        serialized_data = {
            "id": "msg_12345",
            "url": "mailbox://example.com/INBOX/12345",
            "subject": "Test Email",
            "body": "This is a test email body.",
            "attachments": "file1.pdf,file2.txt",
            "received_date": "2023-06-15T12:30:00",
            "pulled_date": "2023-06-16T10:00:00",
            "source": "test@example.com",
        }
        
        mail = Mail.from_serializable_object(serialized_data)
        
        assert mail.id == "msg_12345"
        assert mail.url == "mailbox://example.com/INBOX/12345"
        assert mail.subject == "Test Email"
        assert mail.body == "This is a test email body."
        assert mail.attachments == ["file1.pdf", "file2.txt"]
        assert mail.published_date == datetime(2023, 6, 15, 12, 30)
        assert mail.pulled_date == datetime(2023, 6, 16, 10, 0)
        assert mail.source == "test@example.com"

    def test_from_serializable_object_empty_attachments(self):
        """Test from_serializable_object with empty attachments."""
        serialized_data = {
            "id": "msg_12345",
            "url": "mailbox://example.com/INBOX/12345",
            "subject": "Test Email",
            "body": "This is a test email body.",
            "attachments": "",
            "received_date": "2023-06-15T12:30:00",
            "pulled_date": "2023-06-16T10:00:00",
            "source": "test@example.com",
        }
        
        mail = Mail.from_serializable_object(serialized_data)
        assert mail.attachments == []

    def test_serialization_roundtrip(self):
        """Test that serialization and deserialization is reversible."""
        original_mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is a test email body.",
            attachments=["file1.pdf", "file2.txt"],
            received_date=datetime(2023, 6, 15, 12, 30),
            pulled_date=datetime(2023, 6, 16, 10, 0),
            source="test@example.com",
        )
        
        # Serialize and then deserialize
        serialized = original_mail.serializable_object()
        restored_mail = Mail.from_serializable_object(serialized)
        
        # Check that all important attributes match
        assert restored_mail.id == original_mail.id
        assert restored_mail.url == original_mail.url
        assert restored_mail.subject == original_mail.subject
        assert restored_mail.body == original_mail.body
        assert restored_mail.attachments == original_mail.attachments
        assert restored_mail.published_date == original_mail.published_date
        assert restored_mail.pulled_date == original_mail.pulled_date
        assert restored_mail.source == original_mail.source

    def test_multiline_body(self):
        """Test Mail with multiline body."""
        mail = Mail(
            id="msg_12345",
            url="mailbox://example.com/INBOX/12345",
            subject="Test Email",
            body="This is line 1.\nThis is line 2.\nThis is line 3.",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )
        
        prompt = mail.to_prompt()
        assert "line 1" in prompt
        assert "line 2" in prompt
        assert "line 3" in prompt
