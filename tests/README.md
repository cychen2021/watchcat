# Watchcat Tests

This directory contains comprehensive unit tests and mock tests for the `watchcat` puller modules.

## Test Structure

### Test Files

- `test_source.py` - Tests for the base source module and enums
- `test_arxiv_paper.py` - Unit tests for the ArxivPaper class
- `test_mail.py` - Unit tests for the Mail class  
- `test_arxiv.py` - Unit and mock tests for the Arxiv source and filters
- `test_mailbox.py` - Unit and mock tests for the Mailbox source and filters

### Test Coverage

The test suite covers:

#### ArxivPaper (`test_arxiv_paper.py`)
- Object initialization with and without pulled date
- Property accessors (attachments, published_date, pulled_date)
- String representation methods (to_prompt, __repr__)
- Serialization/deserialization (serializable_object, from_serializable_object)
- Round-trip serialization integrity
- Multi-line abstract handling

#### Mail (`test_mail.py`)
- Object initialization with and without pulled date
- Empty and populated attachments handling
- String representation methods (to_prompt, __repr__)
- Serialization/deserialization with attachment handling
- Round-trip serialization integrity
- Multi-line body content handling

#### Source Enums (`test_source.py`)
- SourceKind enum values and members
- String representation of enum values

#### Arxiv Source (`test_arxiv.py`)
- **ArxivFilter Tests:**
  - Filter initialization and configuration
  - Title, abstract, author, and date filtering
  - Filter combinations (AND, OR, NOT operations)
  - Combined filter behavior and double inversion
  - Non-ArxivPaper object filtering
  
- **Arxiv Source Tests:**
  - Source initialization
  - Query construction for different filter types
  - Multiple filter combination in queries
  - API integration with mocked HTTP responses
  - Error handling (HTTP errors, malformed XML, missing fields)
  - PDF URL fallback when explicit links are missing
  - Default date range handling
  - Additional filter integration

#### Mailbox Source (`test_mailbox.py`)
- **MailFilter Tests:**
  - Filter initialization for different criteria
  - Subject, body, sender, date, and attachment filtering
  - Filter logical operations (AND, OR, NOT)
  - Non-Mail object filtering
  
- **Mailbox Source Tests:**
  - IMAP and POP3 initialization with various configurations
  - Default port selection based on protocol and SSL settings
  - Invalid protocol error handling
  - IMAP search criteria building from filters
  - Email parsing (simple and multipart messages)
  - Attachment extraction from multipart emails
  - Error handling during email parsing
  - IMAP and POP3 email fetching with mocked servers
  - Connection error handling
  - Protocol validation
  - Additional filter integration

## Mock Testing

The tests extensively use mocking to simulate:

- HTTP responses from ArXiv API
- IMAP/POP3 server interactions
- Email message parsing
- Network connectivity issues
- Malformed data handling

## Running Tests

### Run All Tests
```bash
uv run python -m pytest tests/puller/ -v
```

### Run Specific Test File
```bash
uv run python -m pytest tests/puller/test_arxiv.py -v
```

### Run Specific Test Case
```bash
uv run python -m pytest tests/puller/test_arxiv.py::TestArxiv::test_pull_with_filter_success -v
```

## Test Results

All tests pass successfully:
- **75 total tests**
- **100% pass rate**
- Coverage includes both unit tests and integration tests with mocked external dependencies

## Notes

- Tests use proper mocking to avoid actual network calls
- Email and HTTP response parsing is thoroughly tested
- Error conditions and edge cases are covered
- Filter combinations and logical operations are validated
- Serialization integrity is verified through round-trip tests
