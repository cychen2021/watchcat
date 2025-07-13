"""Simplified Automaton demonstrating the refactored architecture."""

from typing import Optional, Dict, Any, List
from datetime import datetime, UTC

from phdkit.log import Logger

from ..datastore import Database
from ..puller.post import Post
from .state import State
from .exceptions import AutomatonError
from .config import ConfigurationLoader
from .checkpoint import CheckpointManager
from .plugins import PluginRegistry
from .logging import WorkflowLogger


class Automaton:
    """Refactored finite state machine for orchestrating the Watchcat workflow.

    This is a demonstration of the new modular architecture where responsibilities
    are separated into focused components:
    - ConfigurationLoader: Handles TOML config loading
    - WorkflowLogger: Manages logging setup and operations
    - CheckpointManager: Handles workflow state persistence
    - PluginRegistry: Manages plugin discovery and registration
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        env_path: Optional[str] = None,
        develop_mode: bool = True
    ) -> None:
        """Initialize the automaton with configuration paths."""
        self.state: State = State.INIT
        self.config_path = config_path or "watchcat.config.toml"
        self.env_path = env_path or "watchcat.env.toml"
        self.develop_mode = develop_mode

        # Core components - initialized during INIT state
        self.workflow_logger = WorkflowLogger(develop_mode)
        self.logger: Optional[Logger] = None
        self.datastore: Optional[Database] = None
        self.config_loader: Optional[ConfigurationLoader] = None
        self.checkpoint_manager: Optional[CheckpointManager] = None
        self.plugin_registry: Optional[PluginRegistry] = None
        self.config_data: Dict[str, Any] = {}

        # Workflow data
        self.pulled_posts: List[Post] = []
        self.processed_insights: List[Any] = []
        self.user_model: Dict[str, Any] = {}
        self.notifications_sent: List[Dict[str, Any]] = []

        # Error handling
        self.last_error: Optional[Exception] = None
        self.retry_count: int = 0
        self.max_retries: int = 3

    def run(self) -> None:
        """Run the automaton until completion."""
        try:
            while self.state is not State.DONE:
                self.workflow_logger.log_info("State Transition", f"Transitioning to state: {self.state.value}")

                if self.state is State.INIT:
                    self._initialize()
                elif self.state is State.PULLING:
                    self._pull_data()
                elif self.state is State.SUMMARIZING:
                    self._summarize()
                elif self.state is State.EVALUATING:
                    self._evaluate_model()
                elif self.state is State.FEEDBACK:
                    self._handle_feedback()
                else:
                    raise AutomatonError(f"Unsupported state: {self.state}")

                # Save checkpoint after each state transition
                if self.checkpoint_manager:
                    self.checkpoint_manager.save_checkpoint(
                        self.state,
                        self.retry_count,
                        self.user_model,
                        self.pulled_posts,
                        self.processed_insights,
                        self.notifications_sent
                    )

        except Exception as e:
            self.last_error = e
            self.workflow_logger.log_error("Workflow Error", f"Workflow failed in state {self.state.value}: {e}")
            self._handle_error(e)
            raise

    def _initialize(self) -> None:
        """Initialize all components using the new modular architecture."""
        # Load configuration using ConfigurationLoader
        self.config_loader = ConfigurationLoader(self.config_path, self.env_path)
        self.config_data = self.config_loader.load()

        # Setup logging using WorkflowLogger
        self.logger = self.workflow_logger.setup_logging()
        self.workflow_logger.log_info("Initialization", "Initializing Watchcat workflow")

        # Initialize datastore
        self._initialize_datastore()

        # Initialize checkpoint manager
        if self.datastore:
            self.checkpoint_manager = CheckpointManager(self.datastore, self.logger)

        # Restore from checkpoint if available
        if self.checkpoint_manager:
            checkpoint_data = self.checkpoint_manager.restore_checkpoint()
            if checkpoint_data:
                self.state = State(checkpoint_data.get("state", State.INIT.value))
                self.retry_count = checkpoint_data.get("retry_count", 0)
                self.user_model = checkpoint_data.get("user_model", {})
                self.pulled_posts = checkpoint_data.get("pulled_posts", [])
                self.processed_insights = checkpoint_data.get("processed_insights", [])
                self.notifications_sent = checkpoint_data.get("notifications_sent", [])

        # Initialize and register plugins using PluginRegistry
        self.plugin_registry = PluginRegistry(self.config_data, self.logger)
        self.plugin_registry.register_all_plugins()

        self.workflow_logger.log_info("Initialization", "Initialization complete")
        self.state = State.PULLING

    def _pull_data(self) -> None:
        """Execute data pulling using the plugin registry."""
        self.workflow_logger.log_info("Data Pulling", "Starting data pulling phase")
        self.pulled_posts = []

        if not self.plugin_registry:
            self.workflow_logger.log_error("Data Pulling", "Plugin registry not initialized")
            self.state = State.SUMMARIZING
            return

        for source in self.plugin_registry.sources:
            try:
                self.workflow_logger.log_info("Source Processing", f"Pulling data from source: {source.id}")

                # Apply configured filters using plugin registry
                filters = self.plugin_registry.get_source_filters(source)
                posts = source.pull(*filters)

                # Process and store posts
                for post in posts:
                    self._store_post(post)
                    self.pulled_posts.append(post)

                self.workflow_logger.log_info("Source Complete", f"Pulled {len(posts)} posts from {source.id}")

            except Exception as e:
                self.workflow_logger.log_error("Source Error", f"Failed to pull from source {source.id}: {e}")
                continue

        self.workflow_logger.log_info("Data Pulling", f"Data pulling complete. Total posts: {len(self.pulled_posts)}")
        self.state = State.SUMMARIZING

    def _summarize(self) -> None:
        """Run processing pipeline using registered processors."""
        self.workflow_logger.log_info("Processing Pipeline", "Starting processing pipeline")
        self.processed_insights = []

        for post in self.pulled_posts:
            try:
                insight = self._process_post_with_plugins(post)
                if insight:
                    self.processed_insights.append(insight)
                    self._store_insight(insight)
            except Exception as e:
                self.workflow_logger.log_error("Post Processing Error", f"Failed to process post {post.id}: {e}")
                continue

        self.workflow_logger.log_info("Processing Pipeline", f"Processing complete. Generated {len(self.processed_insights)} insights")
        self.state = State.EVALUATING

    def _evaluate_model(self) -> None:
        """Update the user model based on processed insights."""
        self.workflow_logger.log_info("User Model", "Evaluating and updating user model")
        
        # Basic user model update (placeholder implementation)
        if "metrics" not in self.user_model:
            self.user_model["metrics"] = {"total_insights_generated": 0, "last_update": None}
        
        self.user_model["metrics"]["total_insights_generated"] += len(self.processed_insights)
        self.user_model["metrics"]["last_update"] = datetime.now(UTC).isoformat()
        
        self.workflow_logger.log_info("User Model", "User model update complete")
        self.state = State.FEEDBACK

    def _handle_feedback(self) -> None:
        """Handle feedback loop and notifications."""
        self.workflow_logger.log_info("Feedback Processing", "Processing feedback and notifications")
        
        # Basic notification handling (placeholder implementation)
        notifications = []
        if len(self.processed_insights) > 0:
            notifications.append({
                "type": "info",
                "message": f"Processed {len(self.processed_insights)} insights",
                "channels": ["log"]
            })

        for notification in notifications:
            self._send_basic_notification(notification)
            self.notifications_sent.append(notification)

        self.workflow_logger.log_info("Feedback Processing", f"Feedback processing complete. Sent {len(self.notifications_sent)} notifications")
        self.state = State.DONE

    def _initialize_datastore(self) -> None:
        """Initialize the datastore connection."""
        from ..datastore.sqlite3_db import SQLite3DB
        
        db_path = self.config_data.get("datastore", {}).get("path", "watchcat.db")
        self.datastore = SQLite3DB(db_path)
        self.datastore.open()

    def _process_post_with_plugins(self, post: Post) -> Optional[Dict[str, Any]]:
        """Process a post using registered plugins."""
        insight = {
            "post_id": post.id,
            "source": post.source,
            "processed_date": datetime.now(UTC).isoformat(),
            "relevance_score": 0.5,  # Default score
            "metadata": {}
        }

        # Process through registered processors
        if self.plugin_registry:
            for processor in self.plugin_registry.processors:
                try:
                    # Plugin processing would happen here
                    # For now, just record that it was processed
                    insight["metadata"][f"processor_{type(processor).__name__}"] = {
                        "processed": True,
                        "timestamp": datetime.now(UTC).isoformat()
                    }
                except Exception as e:
                    self.workflow_logger.log_error("Processor Error", f"Processor failed for post {post.id}: {e}")
                    continue

        return insight

    def _store_post(self, post: Post) -> None:
        """Store post in the datastore (placeholder implementation)."""
        self.workflow_logger.log_info("Post Storage", f"Stored post: {post.id}")

    def _store_insight(self, insight: Dict[str, Any]) -> None:
        """Store processed insight in the datastore (placeholder implementation)."""
        self.workflow_logger.log_info("Insight Storage", f"Stored insight for post: {insight['post_id']}")

    def _send_basic_notification(self, notification: Dict[str, Any]) -> None:
        """Send a basic notification (placeholder implementation)."""
        message = notification.get("message", "")
        self.workflow_logger.log_info("Notification", f"Sent notification: {message}")

    def _handle_error(self, error: Exception) -> None:
        """Handle workflow errors with retry logic."""
        self.retry_count += 1

        if self.retry_count <= self.max_retries:
            self.workflow_logger.log_warning("Error Recovery", f"Retrying after error (attempt {self.retry_count}/{self.max_retries})")
        else:
            self.workflow_logger.log_critical("Error Recovery", "Max retries exceeded, workflow terminated")
            self.state = State.DONE
