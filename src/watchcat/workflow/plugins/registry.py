"""Plugin registry for managing workflow plugins."""

from typing import List, Dict, Any, Optional

from phdkit.log import Logger

from ...puller.source import Source, SourceFilter
from ..exceptions import PluginError
from .factory import PluginFactory


class PluginRegistry:
    """Manages registration and discovery of workflow plugins."""

    def __init__(
        self, config_data: Dict[str, Any], logger: Optional[Logger] = None
    ) -> None:
        """Initialize the plugin registry.

        Args:
            config_data: Configuration data containing plugin definitions
            logger: Optional logger for plugin operations
        """
        self.config_data = config_data
        self.logger = logger
        self.factory = PluginFactory(logger)

        # Plugin registries
        self.sources: List[Source] = []
        self.processors: List[Any] = []
        self.notifiers: List[Any] = []

    def register_all_plugins(self) -> None:
        """Discover and register all available plugins.

        Raises:
            PluginError: If plugin registration fails critically
        """
        try:
            # Register sources from configuration
            self._register_sources()

            # Register processors from configuration
            self._register_processors()

            # Register notifiers from configuration
            self._register_notifiers()

            if self.logger:
                self.logger.info(
                    "Plugin Registration",
                    f"Registered {len(self.sources)} sources, "
                    f"{len(self.processors)} processors, "
                    f"{len(self.notifiers)} notifiers",
                )

        except Exception as e:
            error_msg = f"Plugin registration failed: {e}"
            if self.logger:
                self.logger.error("Plugin Registration Error", error_msg)
            raise PluginError(error_msg)

    def get_source_filters(self, source: Source) -> List[SourceFilter]:
        """Get configured filters for a specific source.

        Args:
            source: Source to get filters for

        Returns:
            List of configured filters for the source
        """
        try:
            # Get filters from configuration for this source
            sources_config = self.config_data.get("sources", {})
            source_config = sources_config.get(source.id, {})
            filters_config = source_config.get("filters", [])

            filters = []
            for filter_config in filters_config:
                try:
                    filter_instance = self.factory.create_filter(filter_config)
                    if filter_instance:
                        filters.append(filter_instance)
                except Exception as e:
                    if self.logger:
                        self.logger.error(
                            "Filter Creation Error",
                            f"Failed to create filter for source {source.id}: {e}",
                        )
                    continue

            return filters

        except Exception as e:
            if self.logger:
                self.logger.error(
                    "Filter Configuration Error",
                    f"Failed to get filters for source {source.id}: {e}",
                )
            return []

    def _register_sources(self) -> None:
        """Register data sources from configuration."""
        sources_config = self.config_data.get("sources", {})

        for source_id, source_config in sources_config.items():
            try:
                source_type = source_config.get("type")
                enabled = source_config.get("enabled", True)

                if not enabled:
                    continue

                # Dynamically import and instantiate source based on type
                source = self.factory.create_source(
                    source_id, source_type, source_config
                )
                if source:
                    self.sources.append(source)
                    if self.logger:
                        self.logger.info(
                            "Source Registration", f"Registered source: {source_id}"
                        )

            except Exception as e:
                if self.logger:
                    self.logger.error(
                        "Source Registration Error",
                        f"Failed to register source {source_id}: {e}",
                    )
                continue

    def _register_processors(self) -> None:
        """Register data processors from configuration."""
        processors_config = self.config_data.get("processors", {})

        for processor_id, processor_config in processors_config.items():
            try:
                processor_type = processor_config.get("type")
                enabled = processor_config.get("enabled", True)

                if not enabled:
                    continue

                # Dynamically import and instantiate processor based on type
                processor = self.factory.create_processor(
                    processor_id, processor_type, processor_config
                )
                if processor:
                    self.processors.append(processor)
                    if self.logger:
                        self.logger.info(
                            "Processor Registration",
                            f"Registered processor: {processor_id}",
                        )

            except Exception as e:
                if self.logger:
                    self.logger.error(
                        "Processor Registration Error",
                        f"Failed to register processor {processor_id}: {e}",
                    )
                continue

    def _register_notifiers(self) -> None:
        """Register notifiers from configuration."""
        notifiers_config = self.config_data.get("notifiers", {})

        for notifier_id, notifier_config in notifiers_config.items():
            try:
                notifier_type = notifier_config.get("type")
                enabled = notifier_config.get("enabled", True)

                if not enabled:
                    continue

                # Dynamically import and instantiate notifier based on type
                notifier = self.factory.create_notifier(
                    notifier_id, notifier_type, notifier_config
                )
                if notifier:
                    self.notifiers.append(notifier)
                    if self.logger:
                        self.logger.info(
                            "Notifier Registration",
                            f"Registered notifier: {notifier_id}",
                        )

            except Exception as e:
                if self.logger:
                    self.logger.error(
                        "Notifier Registration Error",
                        f"Failed to register notifier {notifier_id}: {e}",
                    )
                continue
