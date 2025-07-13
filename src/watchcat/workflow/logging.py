"""Logging utilities for the Watchcat workflow."""

from typing import Optional
from datetime import datetime, UTC

from phdkit.log import Logger, LogLevel, LogOutput


class WorkflowLogger:
    """Wrapper for workflow logging operations."""

    def __init__(self, develop_mode: bool = True) -> None:
        """Initialize the workflow logger.

        Args:
            develop_mode: Whether to run in development mode (affects logging)
        """
        self.develop_mode = develop_mode
        self.logger: Optional[Logger] = None

    def setup_logging(self) -> Logger:
        """Initialize logging infrastructure.

        Returns:
            Configured Logger instance
        """
        self.logger = Logger("watchcat.automaton")

        if self.develop_mode:
            self.logger.add_output(LogOutput.stderr(level=LogLevel.DEBUG))
        else:
            self.logger.add_output(LogOutput.stderr(level=LogLevel.INFO))

            # Add file logging in production
            timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
            log_path = f"watchcat_{timestamp}.jsonl"
            self.logger.add_output(
                LogOutput.file(log_path, level=LogLevel.DEBUG, format="jsonl")
            )

        return self.logger

    def log_info(self, header: str, message: str) -> None:
        """Log an info message if logger is available."""
        if self.logger:
            self.logger.info(header, message)

    def log_error(self, header: str, message: str) -> None:
        """Log an error message if logger is available."""
        if self.logger:
            self.logger.error(header, message)

    def log_warning(self, header: str, message: str) -> None:
        """Log a warning message if logger is available."""
        if self.logger:
            self.logger.warning(header, message)

    def log_critical(self, header: str, message: str) -> None:
        """Log a critical message if logger is available."""
        if self.logger:
            self.logger.critical(header, message)
