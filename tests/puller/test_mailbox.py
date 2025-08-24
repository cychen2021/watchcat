"""Unit and mock tests for Mailbox source class."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from watchcat.puller.mailbox import (
    Mailbox,
    MailFilter,
    MailFilterKind,
    _CombinedFilter,
    _InvertedFilter,
)
from watchcat.puller.mail import Mail
from watchcat.puller.source import SourceKind


class TestMailFilter:
    """Test cases for MailFilter class."""

    def test_mail_filter_initialization(self):
        """Test MailFilter initialization."""
        filter_obj = MailFilter(MailFilterKind.SUBJECT, term="urgent")
        assert filter_obj.kind == MailFilterKind.SUBJECT
        assert filter_obj.filter_args == {"term": "urgent"}

    def test_subject_filter(self):
        """Test subject filtering."""
        filter_obj = MailFilter(MailFilterKind.SUBJECT, term="urgent")

        mail = Mail(
            id="msg_123",
            url="mailbox://test.com/INBOX/123",
            subject="Urgent: Please review",
            body="This is urgent.",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )

        assert filter_obj(mail) is True

        # Test non-matching subject
        mail2 = Mail(
            id="msg_124",
            url="mailbox://test.com/INBOX/124",
            subject="Regular email",
            body="This is not urgent.",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )

        assert filter_obj(mail2) is False

    def test_body_filter(self):
        """Test body filtering."""
        filter_obj = MailFilter(MailFilterKind.BODY, term="meeting")

        mail = Mail(
            id="msg_123",
            url="mailbox://test.com/INBOX/123",
            subject="Schedule",
            body="Let's schedule a meeting for tomorrow.",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )

        assert filter_obj(mail) is True

    def test_sender_filter(self):
        """Test sender filtering."""
        filter_obj = MailFilter(MailFilterKind.SENDER, email="boss@company.com")

        mail = Mail(
            id="msg_123",
            url="mailbox://test.com/INBOX/123",
            subject="Important",
            body="From your boss",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="Mailbox (boss@company.com): Important",
        )

        assert filter_obj(mail) is True

    def test_date_filter(self):
        """Test date filtering."""
        start_date = datetime(2023, 6, 1)
        end_date = datetime(2023, 6, 30)
        filter_obj = MailFilter(MailFilterKind.DATE, start=start_date, end=end_date)

        # Mail within date range
        mail1 = Mail(
            id="msg_123",
            url="mailbox://test.com/INBOX/123",
            subject="June email",
            body="From June",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )

        assert filter_obj(mail1) is True

        # Mail outside date range
        mail2 = Mail(
            id="msg_124",
            url="mailbox://test.com/INBOX/124",
            subject="July email",
            body="From July",
            attachments=[],
            received_date=datetime(2023, 7, 15),
            source="test@example.com",
        )

        assert filter_obj(mail2) is False

    def test_attachment_filter(self):
        """Test attachment filtering."""
        filter_obj = MailFilter(MailFilterKind.HAS_ATTACHMENT, has_attachment=True)

        # Mail with attachments
        mail1 = Mail(
            id="msg_123",
            url="mailbox://test.com/INBOX/123",
            subject="With attachment",
            body="See attached file",
            attachments=["document.pdf"],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )

        assert filter_obj(mail1) is True

        # Mail without attachments
        mail2 = Mail(
            id="msg_124",
            url="mailbox://test.com/INBOX/124",
            subject="No attachment",
            body="Just text",
            attachments=[],
            received_date=datetime(2023, 6, 15),
            source="test@example.com",
        )

        assert filter_obj(mail2) is False

    def test_non_mail_object_filter(self):
        """Test filter with non-Mail object."""
        filter_obj = MailFilter(MailFilterKind.SUBJECT, term="test")

        # Mock a different type of Post
        mock_post = Mock()
        mock_post.__class__ = Mock  # Not Mail

        assert filter_obj(mock_post) is False

    def test_filter_combinations(self):
        """Test filter combination with logical operators."""
        filter1 = MailFilter(MailFilterKind.SUBJECT, term="urgent")
        filter2 = MailFilter(MailFilterKind.BODY, term="meeting")

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


class TestMailbox:
    """Test cases for Mailbox source class."""

    def test_mailbox_initialization_defaults(self):
        """Test Mailbox initialization with default values."""
        mailbox = Mailbox(
            id="test_mailbox",
            server="mail.example.com",
            username="user@example.com",
            password="password123",
        )

        assert mailbox.id == "test_mailbox"
        assert mailbox.server == "mail.example.com"
        assert mailbox.username == "user@example.com"
        assert mailbox.password == "password123"
        assert mailbox.protocol == "imap"
        assert mailbox.port == 993  # Default IMAP SSL port
        assert mailbox.use_ssl is True
        assert mailbox.folder == "INBOX"
        assert mailbox.kind == SourceKind.MAIL

    def test_mailbox_initialization_custom_values(self):
        """Test Mailbox initialization with custom values."""
        mailbox = Mailbox(
            id="test_mailbox",
            server="mail.example.com",
            username="user@example.com",
            password="password123",
            protocol="pop3",
            port=995,
            use_ssl=True,
            folder="Sent",
        )

        assert mailbox.protocol == "pop3"
        assert mailbox.port == 995
        assert mailbox.folder == "Sent"

    def test_mailbox_initialization_pop3_no_ssl(self):
        """Test Mailbox initialization with POP3 and no SSL."""
        mailbox = Mailbox(
            id="test_mailbox",
            server="mail.example.com",
            username="user@example.com",
            password="password123",
            protocol="pop3",
            use_ssl=False,
        )

        assert mailbox.port == 110  # Default POP3 non-SSL port

    def test_mailbox_initialization_imap_no_ssl(self):
        """Test Mailbox initialization with IMAP and no SSL."""
        mailbox = Mailbox(
            id="test_mailbox",
            server="mail.example.com",
            username="user@example.com",
            password="password123",
            protocol="imap",
            use_ssl=False,
        )

        assert mailbox.port == 143  # Default IMAP non-SSL port

    def test_mailbox_initialization_invalid_protocol(self):
        """Test Mailbox initialization with invalid protocol."""
        with pytest.raises(ValueError, match="Unsupported protocol"):
            Mailbox(
                id="test_mailbox",
                server="mail.example.com",
                username="user@example.com",
                password="password123",
                protocol="invalid",
            )

    def test_build_imap_search_criteria_no_filters(self):
        """Test IMAP search criteria building with no filters."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        criteria = mailbox._build_imap_search_criteria([])
        # Should include a default date range
        assert "SINCE" in criteria

    def test_build_imap_search_criteria_subject_filter(self):
        """Test IMAP search criteria for subject filter."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        filters = [MailFilter(MailFilterKind.SUBJECT, term="urgent")]
        criteria = mailbox._build_imap_search_criteria(filters)
        assert 'SUBJECT "urgent"' in criteria

    def test_build_imap_search_criteria_sender_filter(self):
        """Test IMAP search criteria for sender filter."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        filters = [MailFilter(MailFilterKind.SENDER, email="boss@company.com")]
        criteria = mailbox._build_imap_search_criteria(filters)
        assert 'FROM "boss@company.com"' in criteria

    def test_build_imap_search_criteria_date_filter(self):
        """Test IMAP search criteria for date filter."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        start_date = datetime(2023, 6, 1)
        end_date = datetime(2023, 6, 30)
        filters = [MailFilter(MailFilterKind.DATE, start=start_date, end=end_date)]
        criteria = mailbox._build_imap_search_criteria(filters)
        assert "SINCE 01-Jun-2023" in criteria
        assert "BEFORE 30-Jun-2023" in criteria

    def test_build_imap_search_criteria_multiple_filters(self):
        """Test IMAP search criteria with multiple filters."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        filters = [
            MailFilter(MailFilterKind.SUBJECT, term="urgent"),
            MailFilter(MailFilterKind.SENDER, email="boss@company.com"),
        ]
        criteria = mailbox._build_imap_search_criteria(filters)
        assert 'SUBJECT "urgent"' in criteria
        assert 'FROM "boss@company.com"' in criteria

    def test_parse_email_to_mail_simple(self):
        """Test parsing a simple email to Mail object."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        # Create a mock email message
        mock_email = Mock()
        mock_email.get.side_effect = lambda field, default=None: {
            "Subject": "Test Subject",
            "From": "sender@example.com",
            "Date": "Thu, 15 Jun 2023 12:00:00 +0000",
        }.get(field, default)
        mock_email.is_multipart.return_value = False
        mock_email.get_payload.return_value = b"Test email body"

        with patch(
            "watchcat.puller.mailbox.email.utils.parsedate_to_datetime"
        ) as mock_parse_date:
            mock_parse_date.return_value = datetime(2023, 6, 15, 12, 0, 0)

            mail = mailbox._parse_email(mock_email, "123")

            assert mail is not None
            assert mail.id == "123"
            assert mail.subject == "Test Subject"
            assert mail.body == "Test email body"
            assert mail.published_date == datetime(2023, 6, 15, 12, 0, 0)

    def test_parse_email_to_mail_multipart(self):
        """Test parsing a multipart email to Mail object."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        # Create mock email parts
        text_part = Mock()
        text_part.get_content_type.return_value = "text/plain"
        text_part.get_payload.return_value = b"Email body text"
        text_part.get_filename.return_value = None

        attachment_part = Mock()
        attachment_part.get_content_type.return_value = "application/pdf"
        attachment_part.get_payload.return_value = b"PDF content"
        attachment_part.get_filename.return_value = "document.pdf"

        mock_email = Mock()
        mock_email.get.side_effect = lambda field, default=None: {
            "Subject": "Test Subject",
            "From": "sender@example.com",
            "Date": "Thu, 15 Jun 2023 12:00:00 +0000",
        }.get(field, default)
        mock_email.is_multipart.return_value = True
        mock_email.walk.return_value = [text_part, attachment_part]

        with patch(
            "watchcat.puller.mailbox.email.utils.parsedate_to_datetime"
        ) as mock_parse_date:
            mock_parse_date.return_value = datetime(2023, 6, 15, 12, 0, 0)

            mail = mailbox._parse_email(mock_email, "123")

            assert mail is not None
            assert mail.body == "Email body text"
            assert "document.pdf" in mail.attachments

    def test_parse_email_to_mail_parsing_error(self):
        """Test email parsing with error handling."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        # Create mock email that will cause an exception
        mock_email = Mock()
        mock_email.get.side_effect = Exception("Parsing error")

        mail = mailbox._parse_email(mock_email, "123")
        assert mail is None

    @patch("watchcat.puller.mailbox.imaplib.IMAP4_SSL")
    def test_fetch_emails_imap_success(self, mock_imap_class):
        """Test successful IMAP email fetching."""
        # Setup mock IMAP server
        mock_server = Mock()
        mock_server.login.return_value = None
        mock_server.select.return_value = None
        mock_server.search.return_value = ("OK", [b"1 2"])
        mock_server.fetch.return_value = (
            "OK",
            [(None, b"Return-Path: <test@example.com>\r\nSubject: Test\r\n\r\nBody")],
        )
        mock_server.close.return_value = None
        mock_server.logout.return_value = None
        mock_imap_class.return_value = mock_server

        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        # Mock email parsing
        with patch.object(mailbox, "_parse_email") as mock_parse:
            mock_mail = Mock(spec=Mail)
            mock_parse.return_value = mock_mail

            emails = mailbox._fetch_emails_imap([])

            assert len(emails) == 2  # Two message IDs returned
            mock_server.login.assert_called_once_with("user", "pass")
            mock_server.select.assert_called_once_with("INBOX")

    @patch("watchcat.puller.mailbox.imaplib.IMAP4_SSL")
    def test_fetch_emails_imap_connection_error(self, mock_imap_class):
        """Test IMAP email fetching with connection error."""
        mock_imap_class.side_effect = Exception("Connection failed")

        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        emails = mailbox._fetch_emails_imap([])
        assert emails == []

    @patch("watchcat.puller.mailbox.poplib.POP3_SSL")
    def test_fetch_emails_pop3_success(self, mock_pop3_class):
        """Test successful POP3 email fetching."""
        # Setup mock POP3 server
        mock_server = Mock()
        mock_server.user.return_value = None
        mock_server.pass_.return_value = None
        mock_server.list.return_value = (None, [b"1", b"2"])  # Two messages
        mock_server.retr.return_value = (None, [b"Subject: Test", b"", b"Body"])
        mock_server.quit.return_value = None
        mock_pop3_class.return_value = mock_server

        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
            protocol="pop3",
        )

        # Mock email parsing
        with patch.object(mailbox, "_parse_email") as mock_parse:
            mock_mail = Mock(spec=Mail)
            mock_parse.return_value = mock_mail

            emails = mailbox._fetch_emails_pop3([])

            assert len(emails) == 2
            mock_server.user.assert_called_once_with("user")
            mock_server.pass_.assert_called_once_with("pass")

    @patch("watchcat.puller.mailbox.poplib.POP3_SSL")
    def test_fetch_emails_pop3_connection_error(self, mock_pop3_class):
        """Test POP3 email fetching with connection error."""
        mock_pop3_class.side_effect = Exception("Connection failed")

        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
            protocol="pop3",
        )

        emails = mailbox._fetch_emails_pop3([])
        assert emails == []

    def test_pull_unsupported_protocol(self):
        """Test pull with unsupported protocol."""
        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )
        mailbox.protocol = "unsupported"  # Manually set invalid protocol

        with pytest.raises(ValueError, match="Unsupported protocol"):
            mailbox.pull()

    @patch("watchcat.puller.mailbox.imaplib.IMAP4_SSL")
    def test_pull_with_additional_filters(self, mock_imap_class):
        """Test pull with additional non-MailFilter filters."""
        # Setup mock IMAP server
        mock_server = Mock()
        mock_server.login.return_value = None
        mock_server.select.return_value = None
        mock_server.search.return_value = ("OK", [b"1"])
        mock_server.fetch.return_value = ("OK", [(None, b"Subject: Test\r\n\r\nBody")])
        mock_server.close.return_value = None
        mock_server.logout.return_value = None
        mock_imap_class.return_value = mock_server

        mailbox = Mailbox(
            id="test",
            server="mail.example.com",
            username="user",
            password="pass",
        )

        # Create a mock additional filter that rejects all emails
        mock_filter = Mock()
        mock_filter.return_value = False

        with patch.object(mailbox, "_parse_email") as mock_parse:
            mock_mail = Mock(spec=Mail)
            mock_parse.return_value = mock_mail

            emails = mailbox.pull(mock_filter)

            # Should be empty because additional filter rejects all
            assert emails == []
