"""Configuration loader for the Watchcat workflow automaton."""

from typing import Dict, Any
from pathlib import Path
import tomllib

from ..exceptions import ConfigurationError


class ConfigurationLoader:
    """Handles loading and merging configuration from TOML files."""

    def __init__(self, config_path: str, env_path: str) -> None:
        """Initialize the configuration loader.

        Args:
            config_path: Path to the main configuration file (TOML format)
            env_path: Path to the environment configuration file (TOML format)
        """
        self.config_path = config_path
        self.env_path = env_path
        self._config_data: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from TOML files.

        Returns:
            Merged configuration data from config and environment files

        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            # Load main configuration file
            config_path = Path(self.config_path)
            if config_path.exists():
                with open(config_path, "rb") as f:
                    self._config_data = tomllib.load(f)
            else:
                raise ConfigurationError(f"Configuration file not found: {self.config_path}")

            # Load environment variables if available
            env_path = Path(self.env_path)
            if env_path.exists():
                with open(env_path, "rb") as f:
                    env_data = tomllib.load(f)
                    # Merge environment data with config
                    self._config_data.update(env_data)

            return self._config_data

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Failed to load configuration: {e}")

    @property
    def config_data(self) -> Dict[str, Any]:
        """Get the loaded configuration data.

        Returns:
            Configuration data dictionary
        """
        return self._config_data.copy()

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get a specific configuration section.

        Args:
            section_name: Name of the configuration section

        Returns:
            Configuration section data
        """
        return self._config_data.get(section_name, {})

    def get_setting(self, section_name: str, setting_name: str, default: Any = None) -> Any:
        """Get a specific setting from a configuration section.

        Args:
            section_name: Name of the configuration section
            setting_name: Name of the setting
            default: Default value if setting is not found

        Returns:
            Setting value or default
        """
        section = self.get_section(section_name)
        return section.get(setting_name, default)
