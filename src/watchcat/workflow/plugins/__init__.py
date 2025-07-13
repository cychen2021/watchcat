"""Plugin system for the Watchcat workflow."""

from .registry import PluginRegistry
from .factory import PluginFactory

__all__ = ["PluginRegistry", "PluginFactory"]
