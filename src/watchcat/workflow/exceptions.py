"""Exceptions for the Watchcat workflow automaton."""


class AutomatonError(Exception):
    """Base exception for automaton-related errors."""
    
    pass


class ConfigurationError(AutomatonError):
    """Raised when configuration is invalid or missing."""
    
    pass


class CheckpointError(AutomatonError):
    """Raised when checkpoint operations fail."""
    
    pass


class PluginError(AutomatonError):
    """Raised when plugin registration or execution fails."""
    
    pass


class DataProcessingError(AutomatonError):
    """Raised when data processing operations fail."""
    
    pass


class NotificationError(AutomatonError):
    """Raised when notification operations fail."""
    
    pass
