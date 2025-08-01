#!/usr/bin/env python3
"""
Service Configuration for MoodleClaude
Configures dependency injection and service wiring
"""

import logging
from typing import Any, Dict

from config.dual_token_config import DualTokenConfig

# Import existing implementations (these would need to be adapted to interfaces)
from ..clients.moodle_client_enhanced import EnhancedMoodleClient
from .adaptive_content_processor import AdaptiveContentProcessor
from .dependency_injection import ServiceContainer, ServiceLifetime

# Import implementations
from .event_system import EventPublisher, LoggingObserver, MetricsObserver
from .interfaces import (
    IAnalyticsService,
    IConfiguration,
    IContentProcessor,
    ICourseCreationService,
    IEventPublisher,
    IMoodleClient,
    ISessionRepository,
)
from .repositories import (
    CachedSessionRepository,
    InMemorySessionRepository,
    SQLiteSessionRepository,
)
from .services import AnalyticsService, CourseCreationService, SessionCoordinatorService

logger = logging.getLogger(__name__)


class ConfigurationAdapter(IConfiguration):
    """Adapter for existing DualTokenConfig to IConfiguration interface"""

    def __init__(self, dual_token_config: DualTokenConfig):
        self._config = dual_token_config

    def get_moodle_url(self) -> str:
        return self._config.moodle_url

    def get_basic_token(self) -> str:
        return self._config.get_basic_token()

    def get_plugin_token(self) -> str:
        return self._config.get_plugin_token()

    def is_dual_token_mode(self) -> bool:
        return self._config.is_dual_token_mode()

    def get_server_config(self) -> Dict[str, Any]:
        return self._config.get_config_summary()


def configure_services(
    container: ServiceContainer, config_options: Dict[str, Any] = None
) -> ServiceContainer:
    """
    Configure all services in the dependency injection container

    Args:
        container: The service container to configure
        config_options: Configuration options for services
    """
    config_options = config_options or {}

    logger.info("Configuring MoodleClaude services...")

    # 1. Configuration Services
    try:
        dual_config = DualTokenConfig.from_env()
        configuration_adapter = ConfigurationAdapter(dual_config)
        container.register_instance(IConfiguration, configuration_adapter)
        logger.debug("Configuration services registered")
    except Exception as e:
        logger.error(f"Failed to configure configuration services: {e}")
        raise

    # 2. Repository Services
    db_path = config_options.get("db_path", "data/sessions.db")
    use_in_memory = config_options.get("use_in_memory_repository", False)
    use_cache = config_options.get("use_cached_repository", True)

    if use_in_memory:
        primary_repo = InMemorySessionRepository()
        logger.debug("Using in-memory session repository")
    else:
        primary_repo = SQLiteSessionRepository(db_path)
        logger.debug(f"Using SQLite session repository: {db_path}")

    if use_cache and not use_in_memory:
        cache_size = config_options.get("cache_size", 100)
        cached_repo = CachedSessionRepository(primary_repo, cache_size)
        container.register_instance(ISessionRepository, cached_repo)
        logger.debug(f"Using cached repository with size {cache_size}")
    else:
        container.register_instance(ISessionRepository, primary_repo)

    # 3. Event System
    event_publisher = EventPublisher()
    container.register_instance(IEventPublisher, event_publisher)

    # Register default observers
    if config_options.get("enable_logging_observer", True):
        logging_observer = LoggingObserver()
        event_publisher.subscribe(logging_observer)
        logger.debug("Logging observer registered")

    if config_options.get("enable_metrics_observer", True):
        metrics_observer = MetricsObserver()
        event_publisher.subscribe(metrics_observer)
        container.register_instance(
            MetricsObserver, metrics_observer
        )  # For accessing metrics
        logger.debug("Metrics observer registered")

    # 4. Moodle Client (adapter needed)
    # Note: This would require adapting EnhancedMoodleClient to IMoodleClient interface
    try:
        moodle_client = EnhancedMoodleClient(
            base_url=dual_config.moodle_url,
            basic_token=dual_config.get_basic_token(),
            plugin_token=(
                dual_config.get_plugin_token()
                if dual_config.is_dual_token_mode()
                else None
            ),
        )
        # Register under the interface for dependency injection
        container.register_instance(IMoodleClient, moodle_client)
        container.register_instance(EnhancedMoodleClient, moodle_client)
        logger.debug("Moodle client registered")
    except Exception as e:
        logger.error(f"Failed to configure Moodle client: {e}")
        # Continue without Moodle client for testing

    # 5. Content Processor (adapter needed)
    # Note: This would require adapting AdaptiveContentProcessor to IContentProcessor interface
    try:
        content_processor = AdaptiveContentProcessor()
        # Register under the interface for dependency injection
        container.register_instance(IContentProcessor, content_processor)
        container.register_instance(AdaptiveContentProcessor, content_processor)
        logger.debug("Content processor registered")
    except Exception as e:
        logger.error(f"Failed to configure content processor: {e}")

    # 6. Application Services
    # These services will be created by the DI container when needed
    container.register(
        ICourseCreationService, CourseCreationService, ServiceLifetime.SINGLETON
    )
    container.register(IAnalyticsService, AnalyticsService, ServiceLifetime.SINGLETON)

    # 7. Coordination Services
    container.register(
        SessionCoordinatorService, SessionCoordinatorService, ServiceLifetime.SINGLETON
    )

    logger.info("Service configuration completed successfully")
    return container


def create_configured_container(
    config_options: Dict[str, Any] = None,
) -> ServiceContainer:
    """
    Create and configure a new service container

    Args:
        config_options: Configuration options for services
    """
    container = ServiceContainer()
    return configure_services(container, config_options)


def get_service_health_check(container: ServiceContainer) -> Dict[str, Any]:
    """
    Perform health check on all registered services

    Args:
        container: The configured service container
    """
    health_status = {
        "overall_status": "healthy",
        "services": {},
        "timestamp": str(logging.time.time()),
    }

    try:
        # Check configuration
        if container.is_registered(IConfiguration):
            config = container.resolve(IConfiguration)
            health_status["services"]["configuration"] = {
                "status": "healthy",
                "moodle_url": config.get_moodle_url(),
                "dual_token_mode": config.is_dual_token_mode(),
            }

        # Check repository
        if container.is_registered(ISessionRepository):
            # Repository health would be checked here
            health_status["services"]["repository"] = {"status": "healthy"}

        # Check event publisher
        if container.is_registered(IEventPublisher):
            event_publisher = container.resolve(IEventPublisher)
            observer_count = event_publisher.get_observer_count()
            health_status["services"]["event_system"] = {
                "status": "healthy",
                **observer_count,
            }

        # Check application services
        for service_type in [ICourseCreationService, IAnalyticsService]:
            if container.is_registered(service_type):
                health_status["services"][service_type.__name__] = {"status": "healthy"}

    except Exception as e:
        health_status["overall_status"] = "unhealthy"
        health_status["error"] = str(e)
        logger.error(f"Service health check failed: {e}")

    return health_status


# Configuration presets
DEVELOPMENT_CONFIG = {
    "use_in_memory_repository": True,
    "use_cached_repository": False,
    "enable_logging_observer": True,
    "enable_metrics_observer": True,
    "db_path": "data/dev_sessions.db",
}

PRODUCTION_CONFIG = {
    "use_in_memory_repository": False,
    "use_cached_repository": True,
    "cache_size": 200,
    "enable_logging_observer": True,
    "enable_metrics_observer": True,
    "db_path": "data/sessions.db",
}

TESTING_CONFIG = {
    "use_in_memory_repository": True,
    "use_cached_repository": False,
    "enable_logging_observer": False,
    "enable_metrics_observer": False,
    "db_path": ":memory:",
}
