# Watchcat Puller Test Suite

This directory contains comprehensive unit tests and mock tests for the `watchcat` puller modules.

## Test Coverage

### 82 Total Tests Across 6 Test Files

#### 1. `test_arxiv_paper.py` (9 tests)

- **Purpose**: Unit tests for the `ArxivPaper` class
- **Coverage**:
  - Initialization and auto-generated pulled dates
  - Post protocol implementation (attachments, to_prompt, serialization)
  - String representation and object comparison
  - Serialization roundtrip integrity
  - Multiline abstract handling

#### 2. `test_mail.py` (11 tests)

- **Purpose**: Unit tests for the `Mail` class
- **Coverage**:
  - Email-specific functionality and properties
  - Empty and populated attachment handling
  - Post protocol compliance for email content
  - Serialization with attachment comma-separation
  - Multiline body content handling

#### 3. `test_source.py` (3 tests)

- **Purpose**: Unit tests for source enumeration types
- **Coverage**:
  - `SourceKind` enumeration values and members
  - String representation consistency
  - Type safety and enum behavior

#### 4. `test_arxiv.py` (25 tests)

- **Purpose**: Comprehensive testing of `Arxiv` source and `ArxivFilter` classes
- **Coverage**:
  - Filter initialization and validation
  - Complex filter combinations (AND, OR, NOT operations)
  - Query construction for ArXiv API
  - HTTP response mocking and XML parsing
  - Error handling for network failures and malformed data
  - Date range filtering and default behavior
  - Fallback URL generation

#### 5. `test_mailbox.py` (27 tests)

- **Purpose**: Full testing of `Mailbox` source and `MailFilter` classes
- **Coverage**:
  - IMAP and POP3 protocol support
  - Email server connection mocking
  - Filter types (subject, body, sender, date, attachment)
  - IMAP search criteria building
  - Email parsing (simple and multipart messages)
  - Connection error handling and protocol validation
  - SSL/non-SSL configuration testing

#### 6. `test_integration.py` (7 tests)

- **Purpose**: End-to-end workflow and integration testing
- **Coverage**:
  - Cross-module compatibility verification
  - Complex filter composition across different sources
  - Post protocol compliance validation
  - Error handling robustness testing
  - Type safety verification

## Mock Strategies

### External Dependencies Mocked

- **HTTP Requests**: `urllib.request.urlopen` for ArXiv API calls
- **Email Servers**: `imaplib.IMAP4_SSL`, `poplib.POP3_SSL` for mailbox connections
- **System Time**: `datetime.now()` for consistent test execution
- **Network Errors**: Connection timeouts and server failures

### Mock Patterns Used

- Context managers for proper resource cleanup
- Response objects with realistic data structures
- Error injection for robustness testing
- Protocol-specific behavior simulation

## Running Tests

### All Tests

```bash
uv run pytest tests/puller/ -v
```

### Specific Test File
```bash
uv run pytest tests/puller/test_arxiv.py -v
```

### With Coverage
```bash
uv run pytest tests/puller/ --cov=src/watchcat/puller
```

## Test Data

### ArXiv Test Data

- Sample XML responses mimicking ArXiv API structure
- Various paper metadata including titles, abstracts, authors
- Date ranges and publication information

```bash
uv run pytest tests/puller/ --cov=src/watchcat/puller
```

### Email Test Data:

- RFC 2822 compliant email messages
- Multipart MIME structures
- Various attachment types and encodings
- IMAP/POP3 protocol responses

## Key Testing Achievements

1. **Complete Mock Coverage**: All external dependencies properly mocked
2. **Protocol Compliance**: Verified Post protocol implementation across all classes
3. **Error Resilience**: Comprehensive error handling and recovery testing
4. **Filter Logic**: Complex boolean filter combinations thoroughly tested
5. **Serialization Integrity**: Roundtrip serialization validation for data persistence
6. **Integration Validation**: End-to-end workflow verification

## Bug Fixes During Testing

1. **ArxivPaper Constructor**: Fixed parameter naming issue (removed double underscores)
2. **ArxivFilter Logic**: Corrected title filtering to use actual title field
3. **Mock Setup**: Fixed context manager implementation for HTTP mocking
4. **Test Data Alignment**: Ensured test data matches filter expectations

## Maintenance Notes

- Tests are designed to be deterministic and independent
- Mock data should be updated if API structures change
- Filter tests include edge cases and boundary conditions
- Integration tests verify cross-module compatibility
