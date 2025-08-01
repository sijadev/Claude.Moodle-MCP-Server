"""
Adaptive Configuration System for Advanced MCP Server
Provides configurable limits, strategies, and adaptive learning parameters
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProcessingLimits:
    """Configurable processing limits that adapt based on performance"""

    # Content size limits
    max_char_length: int = 8000
    min_char_length: int = 100
    max_char_length_hard_limit: int = 20000

    # Structure limits
    max_sections: int = 15
    max_items_per_section: int = 20
    max_code_blocks: int = 30
    max_topics: int = 40

    # Processing limits
    max_chunks_per_session: int = 10
    max_retry_attempts: int = 3
    session_timeout_hours: int = 2

    # Adaptive learning parameters
    adaptation_sensitivity: float = 0.1  # How quickly to adapt (0.1 = 10% changes)
    confidence_threshold: float = 0.8  # When to trust learned limits
    min_data_points: int = 10  # Minimum data before adapting

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingLimits":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class StrategyConfig:
    """Configuration for processing strategies"""

    # Strategy selection thresholds
    single_pass_complexity_threshold: float = 0.3
    intelligent_chunk_complexity_threshold: float = 0.6
    progressive_build_complexity_threshold: float = 0.8

    # Strategy-specific parameters
    intelligent_chunk_overlap: int = 2  # Items to overlap between chunks
    progressive_build_min_sections: int = 3
    adaptive_retry_backoff_factor: float = 1.5

    # Strategy effectiveness tracking
    strategy_success_rates: Dict[str, float] = field(
        default_factory=lambda: {
            "single_pass": 0.9,
            "intelligent_chunk": 0.85,
            "progressive_build": 0.8,
            "adaptive_retry": 0.7,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategyConfig":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class MoodleIntegrationConfig:
    """Configuration for Moodle integration features"""

    # Connection settings
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    # Course creation settings
    default_course_format: str = "topics"
    default_category_id: int = 1
    auto_enroll_creator: bool = True

    # Content creation settings
    code_activity_type: str = "page"  # page, resource, label
    topic_activity_type: str = "page"
    enable_syntax_highlighting: bool = True

    # Validation settings
    validate_after_create: bool = True
    validation_timeout: int = 10
    require_validation_success: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoodleIntegrationConfig":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class UserExperienceConfig:
    """Configuration for user experience and messaging"""

    # Response style
    use_emojis: bool = True
    detailed_progress_updates: bool = True
    include_technical_details: bool = False

    # Continuation prompts
    continuation_messages: List[str] = field(
        default_factory=lambda: [
            "Great progress! Ready for the next section of content.",
            "Perfect! Please share the next part when you're ready.",
            "Excellent work! I'm ready to continue with more content.",
            "Nice! Let's keep building your course with the next section.",
        ]
    )

    # Error messages
    friendly_error_messages: bool = True
    provide_suggestions: bool = True
    include_session_recovery: bool = True

    # Analytics display
    show_processing_metrics: bool = True
    show_complexity_analysis: bool = True
    show_time_estimates: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserExperienceConfig":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class DatabaseConfig:
    """Configuration for database and persistence"""

    # Database settings
    db_path: str = "data/moodle_claude_sessions.db"
    backup_interval_hours: int = 6
    max_backups_to_keep: int = 10

    # Session management
    max_active_sessions: int = 100
    cleanup_interval_hours: int = 1
    session_retention_days: int = 7

    # Analytics and metrics
    enable_analytics: bool = True
    metrics_retention_days: int = 30
    enable_performance_monitoring: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatabaseConfig":
        """Create from dictionary"""
        return cls(**data)


class AdaptiveConfig:
    """
    Main configuration class that manages all aspects of the adaptive system
    Handles loading, saving, and runtime adaptation of configuration parameters
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize adaptive configuration

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path or self._get_default_config_path()

        # Initialize configuration components
        self.processing = ProcessingLimits()
        self.strategy = StrategyConfig()
        self.moodle = MoodleIntegrationConfig()
        self.user_experience = UserExperienceConfig()
        self.database = DatabaseConfig()

        # Runtime tracking
        self.adaptation_history: List[Dict[str, Any]] = []
        self.last_save_time: Optional[float] = None

        # Load configuration if exists
        self.load_config()

        logger.info(f"AdaptiveConfig initialized with config path: {self.config_path}")

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Use project root/config directory
        project_root = Path(__file__).parent.parent
        config_dir = project_root / "config"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "adaptive_settings.json")

    def load_config(self) -> bool:
        """
        Load configuration from file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.config_path):
                logger.info(
                    f"Config file not found at {self.config_path}, using defaults"
                )
                return False

            with open(self.config_path, "r") as f:
                config_data = json.load(f)

            # Load each configuration section
            if "processing" in config_data:
                self.processing = ProcessingLimits.from_dict(config_data["processing"])

            if "strategy" in config_data:
                self.strategy = StrategyConfig.from_dict(config_data["strategy"])

            if "moodle" in config_data:
                self.moodle = MoodleIntegrationConfig.from_dict(config_data["moodle"])

            if "user_experience" in config_data:
                self.user_experience = UserExperienceConfig.from_dict(
                    config_data["user_experience"]
                )

            if "database" in config_data:
                self.database = DatabaseConfig.from_dict(config_data["database"])

            if "adaptation_history" in config_data:
                self.adaptation_history = config_data["adaptation_history"]

            logger.info("Configuration loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False

    def save_config(self) -> bool:
        """
        Save current configuration to file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            config_data = {
                "processing": self.processing.to_dict(),
                "strategy": self.strategy.to_dict(),
                "moodle": self.moodle.to_dict(),
                "user_experience": self.user_experience.to_dict(),
                "database": self.database.to_dict(),
                "adaptation_history": self.adaptation_history[
                    -100:
                ],  # Keep last 100 entries
                "last_updated": self._get_current_timestamp(),
            }

            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=2)

            self.last_save_time = self._get_current_timestamp()
            logger.info("Configuration saved successfully")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

    def adapt_processing_limits(
        self, success_rate: float, avg_content_size: int, total_requests: int
    ) -> bool:
        """
        Adapt processing limits based on performance metrics

        Args:
            success_rate: Current success rate (0.0 to 1.0)
            avg_content_size: Average content size processed
            total_requests: Total number of requests processed

        Returns:
            True if limits were adapted, False otherwise
        """
        if total_requests < self.processing.min_data_points:
            return False

        try:
            original_limits = self.processing.to_dict()
            adaptation_made = False

            # Adapt character length limit based on success rate
            if (
                success_rate > 0.9
                and avg_content_size > self.processing.max_char_length
            ):
                # Increase limit if we're succeeding with larger content
                new_limit = min(
                    int(
                        self.processing.max_char_length
                        * (1 + self.processing.adaptation_sensitivity)
                    ),
                    self.processing.max_char_length_hard_limit,
                )
                if new_limit != self.processing.max_char_length:
                    self.processing.max_char_length = new_limit
                    adaptation_made = True

            elif success_rate < 0.7:
                # Decrease limit if we're failing frequently
                new_limit = max(
                    int(
                        self.processing.max_char_length
                        * (1 - self.processing.adaptation_sensitivity)
                    ),
                    self.processing.min_char_length,
                )
                if new_limit != self.processing.max_char_length:
                    self.processing.max_char_length = new_limit
                    adaptation_made = True

            # Adapt section limits based on success patterns
            if success_rate > 0.85:
                # Slightly increase section limits
                self.processing.max_sections = min(
                    int(self.processing.max_sections * 1.05), 25
                )
                adaptation_made = True
            elif success_rate < 0.6:
                # Decrease section limits
                self.processing.max_sections = max(
                    int(self.processing.max_sections * 0.95), 5
                )
                adaptation_made = True

            if adaptation_made:
                # Record adaptation
                self.adaptation_history.append(
                    {
                        "timestamp": self._get_current_timestamp(),
                        "trigger": "performance_metrics",
                        "success_rate": success_rate,
                        "avg_content_size": avg_content_size,
                        "total_requests": total_requests,
                        "original_limits": original_limits,
                        "new_limits": self.processing.to_dict(),
                    }
                )

                logger.info(
                    f"Processing limits adapted: char_limit={self.processing.max_char_length}, "
                    f"sections={self.processing.max_sections}"
                )

                # Auto-save if significant change
                self.save_config()

            return adaptation_made

        except Exception as e:
            logger.error(f"Error adapting processing limits: {e}")
            return False

    def adapt_strategy_effectiveness(self, strategy: str, success: bool) -> bool:
        """
        Update strategy effectiveness based on usage results

        Args:
            strategy: Strategy name that was used
            success: Whether the strategy was successful

        Returns:
            True if strategy rates were updated, False otherwise
        """
        try:
            if strategy not in self.strategy.strategy_success_rates:
                self.strategy.strategy_success_rates[strategy] = 0.8  # Default rate

            current_rate = self.strategy.strategy_success_rates[strategy]

            # Use exponential moving average to update success rate
            alpha = 0.1  # Learning rate
            new_rate = current_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha

            # Only update if change is significant
            if abs(new_rate - current_rate) > 0.01:
                self.strategy.strategy_success_rates[strategy] = new_rate

                self.adaptation_history.append(
                    {
                        "timestamp": self._get_current_timestamp(),
                        "trigger": "strategy_effectiveness",
                        "strategy": strategy,
                        "success": success,
                        "old_rate": current_rate,
                        "new_rate": new_rate,
                    }
                )

                logger.info(
                    f"Strategy effectiveness updated: {strategy} = {new_rate:.3f}"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Error adapting strategy effectiveness: {e}")
            return False

    def get_optimal_strategy_thresholds(self) -> Dict[str, float]:
        """
        Get optimal strategy selection thresholds based on learned effectiveness

        Returns:
            Dictionary of strategy thresholds
        """
        try:
            # Sort strategies by effectiveness
            sorted_strategies = sorted(
                self.strategy.strategy_success_rates.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            # Adjust thresholds based on relative effectiveness
            thresholds = {}

            # Most effective strategy gets lowest threshold
            if len(sorted_strategies) >= 1:
                best_strategy = sorted_strategies[0][0]
                if best_strategy == "single_pass":
                    thresholds["single_pass"] = 0.25
                elif best_strategy == "intelligent_chunk":
                    thresholds["single_pass"] = 0.2
                    thresholds["intelligent_chunk"] = 0.5
                else:
                    thresholds["single_pass"] = 0.15
                    thresholds["intelligent_chunk"] = 0.4
                    thresholds["progressive_build"] = 0.7

            # Fill in remaining thresholds with defaults
            return {
                "single_pass": thresholds.get(
                    "single_pass", self.strategy.single_pass_complexity_threshold
                ),
                "intelligent_chunk": thresholds.get(
                    "intelligent_chunk",
                    self.strategy.intelligent_chunk_complexity_threshold,
                ),
                "progressive_build": thresholds.get(
                    "progressive_build",
                    self.strategy.progressive_build_complexity_threshold,
                ),
            }

        except Exception as e:
            logger.error(f"Error calculating optimal thresholds: {e}")
            return {
                "single_pass": self.strategy.single_pass_complexity_threshold,
                "intelligent_chunk": self.strategy.intelligent_chunk_complexity_threshold,
                "progressive_build": self.strategy.progressive_build_complexity_threshold,
            }

    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration for debugging/monitoring

        Returns:
            Dictionary with configuration summary
        """
        return {
            "processing_limits": {
                "max_char_length": self.processing.max_char_length,
                "max_sections": self.processing.max_sections,
                "adaptation_sensitivity": self.processing.adaptation_sensitivity,
            },
            "strategy_effectiveness": self.strategy.strategy_success_rates.copy(),
            "moodle_integration": {
                "connection_timeout": self.moodle.connection_timeout,
                "validate_after_create": self.moodle.validate_after_create,
            },
            "user_experience": {
                "use_emojis": self.user_experience.use_emojis,
                "detailed_progress_updates": self.user_experience.detailed_progress_updates,
            },
            "database": {
                "db_path": self.database.db_path,
                "max_active_sessions": self.database.max_active_sessions,
            },
            "adaptation_stats": {
                "total_adaptations": len(self.adaptation_history),
                "last_adaptation": self.adaptation_history[-1]["timestamp"]
                if self.adaptation_history
                else None,
                "config_path": self.config_path,
                "last_save_time": self.last_save_time,
            },
        }

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values

        Returns:
            True if reset successfully, False otherwise
        """
        try:
            self.processing = ProcessingLimits()
            self.strategy = StrategyConfig()
            self.moodle = MoodleIntegrationConfig()
            self.user_experience = UserExperienceConfig()
            self.database = DatabaseConfig()
            self.adaptation_history = []

            logger.info("Configuration reset to defaults")
            return self.save_config()

        except Exception as e:
            logger.error(f"Error resetting configuration: {e}")
            return False

    def _get_current_timestamp(self) -> float:
        """Get current timestamp"""
        import time

        return time.time()

    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to a specific file

        Args:
            export_path: Path to export the configuration

        Returns:
            True if exported successfully, False otherwise
        """
        try:
            config_data = {
                "processing": self.processing.to_dict(),
                "strategy": self.strategy.to_dict(),
                "moodle": self.moodle.to_dict(),
                "user_experience": self.user_experience.to_dict(),
                "database": self.database.to_dict(),
                "adaptation_history": self.adaptation_history,
                "exported_at": self._get_current_timestamp(),
                "export_version": "2.0.0",
            }

            os.makedirs(os.path.dirname(export_path), exist_ok=True)

            with open(export_path, "w") as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Configuration exported to: {export_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False

    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from a specific file

        Args:
            import_path: Path to import the configuration from

        Returns:
            True if imported successfully, False otherwise
        """
        try:
            if not os.path.exists(import_path):
                logger.error(f"Import file not found: {import_path}")
                return False

            with open(import_path, "r") as f:
                config_data = json.load(f)

            # Validate import version if available
            if "export_version" in config_data:
                version = config_data["export_version"]
                logger.info(f"Importing configuration version: {version}")

            # Import each section
            if "processing" in config_data:
                self.processing = ProcessingLimits.from_dict(config_data["processing"])

            if "strategy" in config_data:
                self.strategy = StrategyConfig.from_dict(config_data["strategy"])

            if "moodle" in config_data:
                self.moodle = MoodleIntegrationConfig.from_dict(config_data["moodle"])

            if "user_experience" in config_data:
                self.user_experience = UserExperienceConfig.from_dict(
                    config_data["user_experience"]
                )

            if "database" in config_data:
                self.database = DatabaseConfig.from_dict(config_data["database"])

            if "adaptation_history" in config_data:
                self.adaptation_history = config_data["adaptation_history"]

            logger.info(f"Configuration imported from: {import_path}")
            return self.save_config()

        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False


# Global configuration instance
_global_config: Optional[AdaptiveConfig] = None


def get_adaptive_config(config_path: Optional[str] = None) -> AdaptiveConfig:
    """
    Get global adaptive configuration instance

    Args:
        config_path: Optional path to configuration file

    Returns:
        AdaptiveConfig instance
    """
    global _global_config

    if _global_config is None:
        _global_config = AdaptiveConfig(config_path)

    return _global_config


def reload_adaptive_config(config_path: Optional[str] = None) -> AdaptiveConfig:
    """
    Reload global adaptive configuration

    Args:
        config_path: Optional path to configuration file

    Returns:
        New AdaptiveConfig instance
    """
    global _global_config
    _global_config = AdaptiveConfig(config_path)
    return _global_config
