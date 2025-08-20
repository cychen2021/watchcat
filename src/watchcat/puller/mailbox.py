from typing import Sequence, override
from enum import Enum
import imaplib
import poplib
import email
import email.utils
from email.message import Message
from datetime import datetime, timedelta

from .source import Source, SourceKind, SourceFilter
from .mail import Mail
from .post import Post


class MailFilterKind(Enum):
    """Types of filters for mailbox content."""
    
    SUBJECT = "subject"
    SENDER = "sender"
    BODY = "body"
    DATE = "date"
    HAS_ATTACHMENT = "has_attachment"


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


class MailFilter(SourceFilter):
    """Filter for mail content based on various criteria."""

    def __init__(self, kind: MailFilterKind, **filter_args) -> None:
        self.kind = kind
        self.filter_args = filter_args

    def __call__(self, post: Post) -> bool:
        """Check if a post matches the filter criteria."""
        if not isinstance(post, Mail):
            return False

        if self.kind == MailFilterKind.SUBJECT:
            if "term" in self.filter_args:
                term = self.filter_args["term"].lower()
                return term in post.subject.lower()

        elif self.kind == MailFilterKind.SENDER:
            if "email" in self.filter_args:
                email_addr = self.filter_args["email"].lower()
                # For simplicity, we'll search in the source field
                # In a real implementation, you'd extract the sender from email headers
                return email_addr in post.source.lower()

        elif self.kind == MailFilterKind.BODY:
            if "term" in self.filter_args:
                term = self.filter_args["term"].lower()
                return term in post.body.lower()

        elif self.kind == MailFilterKind.DATE:
            if "start" in self.filter_args and "end" in self.filter_args:
                start_date = self.filter_args["start"]
                end_date = self.filter_args["end"]
                return start_date <= post.published_date <= end_date

        elif self.kind == MailFilterKind.HAS_ATTACHMENT:
            if "has_attachment" in self.filter_args:
                has_attachment = self.filter_args["has_attachment"]
                return bool(post.attachments) == has_attachment

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


class Mailbox(Source):
    """A mailbox source that can pull emails from IMAP or POP3 servers."""
    
    kind: SourceKind = SourceKind.MAIL

    def __init__(
        self,
        id: str,
        server: str,
        username: str,
        password: str,
        protocol: str = "imap",
        port: int | None = None,
        use_ssl: bool = True,
        folder: str = "INBOX",
    ) -> None:
        """Initialize a mailbox source.

        Args:
            id: Unique identifier for this mailbox
            server: Mail server hostname
            username: Username for authentication
            password: Password for authentication
            protocol: Mail protocol to use ("imap" or "pop3")
            port: Port number (defaults to standard ports for protocol/SSL combination)
            use_ssl: Whether to use SSL/TLS encryption
            folder: Folder to read from (IMAP only, defaults to "INBOX")
        """
        self.id = id
        self.server = server
        self.username = username
        self.password = password
        self.protocol = protocol.lower()
        self.use_ssl = use_ssl
        self.folder = folder

        # Set default ports if not specified
        if port is None:
            if self.protocol == "imap":
                self.port = 993 if use_ssl else 143
            elif self.protocol == "pop3":
                self.port = 995 if use_ssl else 110
            else:
                raise ValueError(f"Unsupported protocol: {protocol}")
        else:
            self.port = port

    @override
    def pull(self, *filters: SourceFilter) -> Sequence[Mail]:
        """Pull emails from the mailbox.

        Args:
            *filters: Optional filters to apply to the pulled emails

        Returns:
            A sequence of Mail objects that match the filters
        """
        # Separate MailFilter objects from other filters
        mail_filters = [f for f in filters if isinstance(f, MailFilter)]
        other_filters = [f for f in filters if not isinstance(f, MailFilter)]

        # Fetch emails from the server
        if self.protocol == "imap":
            emails = self._fetch_emails_imap(mail_filters)
        elif self.protocol == "pop3":
            emails = self._fetch_emails_pop3(mail_filters)
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

        # Apply additional filters that aren't MailFilter
        if other_filters:
            filtered_emails = []
            for email_msg in emails:
                if all(filter_obj(email_msg) for filter_obj in other_filters):
                    filtered_emails.append(email_msg)
            emails = filtered_emails

        return emails

    def _fetch_emails_imap(self, filters: list[MailFilter]) -> list[Mail]:
        """Fetch emails using IMAP protocol."""
        emails = []

        try:
            # Connect to IMAP server
            if self.use_ssl:
                mail_server = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                mail_server = imaplib.IMAP4(self.server, self.port)

            # Login
            mail_server.login(self.username, self.password)

            # Select folder
            mail_server.select(self.folder)

            # Build search criteria from filters
            search_criteria = self._build_imap_search_criteria(filters)

            # Search for emails
            status, message_ids = mail_server.search(None, search_criteria)
            if status != "OK":
                return emails

            # Process each email
            for message_id in message_ids[0].split():
                try:
                    # Fetch email
                    status, msg_data = mail_server.fetch(message_id, "(RFC822)")
                    if status != "OK" or not msg_data or not msg_data[0] or len(msg_data[0]) < 2:
                        continue

                    # Parse email
                    raw_email = msg_data[0][1]
                    if isinstance(raw_email, bytes):
                        email_msg = email.message_from_bytes(raw_email)
                    else:
                        email_msg = email.message_from_string(str(raw_email))
                    mail_obj = self._parse_email_to_mail(email_msg, message_id.decode())
                    if mail_obj:
                        emails.append(mail_obj)

                except Exception:
                    # Skip emails that fail to parse
                    continue

            # Close connection
            mail_server.close()
            mail_server.logout()

        except Exception:
            # If connection fails, return empty list
            # In a production system, you might want to log this error
            pass

        return emails

    def _fetch_emails_pop3(self, filters: list[MailFilter]) -> list[Mail]:
        """Fetch emails using POP3 protocol."""
        emails = []

        try:
            # Connect to POP3 server
            if self.use_ssl:
                mail_server = poplib.POP3_SSL(self.server, self.port)
            else:
                mail_server = poplib.POP3(self.server, self.port)

            # Login
            mail_server.user(self.username)
            mail_server.pass_(self.password)

            # Get number of messages
            num_messages = len(mail_server.list()[1])

            # Process each email (POP3 doesn't support server-side filtering)
            for i in range(1, min(num_messages + 1, 101)):  # Limit to 100 emails
                try:
                    # Retrieve email
                    raw_email = b"\r\n".join(mail_server.retr(i)[1])
                    email_msg = email.message_from_bytes(raw_email)
                    
                    mail_obj = self._parse_email_to_mail(email_msg, str(i))
                    if mail_obj:
                        emails.append(mail_obj)

                except Exception:
                    # Skip emails that fail to parse
                    continue

            # Close connection
            mail_server.quit()

        except Exception:
            # If connection fails, return empty list
            # In a production system, you might want to log this error
            pass

        return emails

    def _build_imap_search_criteria(self, filters: list[MailFilter]) -> str:
        """Build IMAP search criteria from MailFilter objects."""
        if not filters:
            # Default: get emails from last 30 days
            since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
            return f"SINCE {since_date}"

        criteria_parts = []

        for filter_obj in filters:
            if filter_obj.kind == MailFilterKind.SUBJECT:
                if "term" in filter_obj.filter_args:
                    term = filter_obj.filter_args["term"]
                    criteria_parts.append(f'SUBJECT "{term}"')

            elif filter_obj.kind == MailFilterKind.SENDER:
                if "email" in filter_obj.filter_args:
                    email_addr = filter_obj.filter_args["email"]
                    criteria_parts.append(f'FROM "{email_addr}"')

            elif filter_obj.kind == MailFilterKind.BODY:
                if "term" in filter_obj.filter_args:
                    term = filter_obj.filter_args["term"]
                    criteria_parts.append(f'BODY "{term}"')

            elif filter_obj.kind == MailFilterKind.DATE:
                if "start" in filter_obj.filter_args:
                    start_date = filter_obj.filter_args["start"]
                    if hasattr(start_date, "strftime"):
                        since_date = start_date.strftime("%d-%b-%Y")
                        criteria_parts.append(f"SINCE {since_date}")
                if "end" in filter_obj.filter_args:
                    end_date = filter_obj.filter_args["end"]
                    if hasattr(end_date, "strftime"):
                        before_date = end_date.strftime("%d-%b-%Y")
                        criteria_parts.append(f"BEFORE {before_date}")

        # Combine criteria with parentheses for multiple conditions
        if len(criteria_parts) == 1:
            return criteria_parts[0]
        elif len(criteria_parts) > 1:
            return "(" + " ".join(criteria_parts) + ")"
        else:
            # Fallback to recent emails
            since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
            return f"SINCE {since_date}"

    def _parse_email_to_mail(self, email_msg: Message, msg_id: str) -> Mail | None:
        """Parse an email message into a Mail object."""
        try:
            # Extract basic information
            subject = email_msg.get("Subject", "No Subject")
            sender = email_msg.get("From", "Unknown Sender")
            date_str = email_msg.get("Date", "")

            # Parse date
            if date_str:
                try:
                    # This is a simplified date parsing - you might want to use
                    # email.utils.parsedate_to_datetime for more robust parsing
                    received_date = email.utils.parsedate_to_datetime(date_str)
                except Exception:
                    received_date = datetime.now()
            else:
                received_date = datetime.now()

            # Extract body
            body = ""
            attachments = []

            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            if isinstance(payload, bytes):
                                body += payload.decode("utf-8", errors="ignore")
                            else:
                                body += str(payload)
                    elif part.get_filename():
                        # This is an attachment
                        filename = part.get_filename()
                        if filename:
                            attachments.append(filename)
            else:
                # Simple email
                payload = email_msg.get_payload(decode=True)
                if payload:
                    if isinstance(payload, bytes):
                        body = payload.decode("utf-8", errors="ignore")
                    else:
                        body = str(payload)

            # Create URL (simplified - in real implementation you might want a proper URL)
            url = f"mailbox://{self.server}/{self.folder}/{msg_id}"

            return Mail(
                id=msg_id,
                url=url,
                subject=subject,
                body=body.strip(),
                attachments=attachments,
                received_date=received_date,
                source=f"Mailbox ({sender}): {subject}",
            )

        except Exception:
            # Return None if parsing fails
            return None
