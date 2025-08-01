#!/usr/bin/env python3
"""
Dependency Injection Container for MoodleClaude
Implements IoC container for loose coupling and testability
"""

import asyncio
import inspect
import logging
from threading import Lock
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

from .interfaces import IServiceContainer

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceLifetime:
    """Service lifetime options"""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class ServiceDescriptor:
    """Describes how a service should be created and managed"""

    def __init__(
        self,
        interface_type: Type,
        implementation: Union[Type, Callable, Any],
        lifetime: str = ServiceLifetime.SINGLETON,
        factory: Optional[Callable] = None,
    ):
        self.interface_type = interface_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.factory = factory
        self.instance: Optional[Any] = None


class ServiceContainer(IServiceContainer):
    """
    Dependency Injection Container implementing IoC pattern

    Features:
    - Singleton, Transient, and Scoped lifetimes
    - Constructor injection
    - Factory methods
    - Async service resolution
    - Thread-safe operations
    """

    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        self._lock = Lock()
        self._scope_counter = 0

    def register(
        self,
        interface_type: Type[T],
        implementation: Union[Type[T], Callable[[], T], T],
        lifetime: str = ServiceLifetime.SINGLETON,
    ) -> "ServiceContainer":
        """
        Register a service implementation

        Args:
            interface_type: The interface or abstract base class
            implementation: The concrete implementation, factory, or instance
            lifetime: Service lifetime (singleton, transient, scoped)
        """
        with self._lock:
            if inspect.isclass(implementation):
                # Class-based registration
                descriptor = ServiceDescriptor(interface_type, implementation, lifetime)
            elif callable(implementation):
                # Factory-based registration
                descriptor = ServiceDescriptor(
                    interface_type, None, lifetime, implementation
                )
            else:
                # Instance-based registration (always singleton)
                descriptor = ServiceDescriptor(
                    interface_type, implementation, ServiceLifetime.SINGLETON
                )
                descriptor.instance = implementation

            self._services[interface_type] = descriptor
            logger.debug(
                f"Registered service: {interface_type.__name__} -> {implementation} ({lifetime})"
            )

        return self

    def register_singleton(
        self, interface_type: Type[T], implementation: Union[Type[T], Callable[[], T]]
    ) -> "ServiceContainer":
        """Register as singleton (default)"""
        return self.register(interface_type, implementation, ServiceLifetime.SINGLETON)

    def register_transient(
        self, interface_type: Type[T], implementation: Union[Type[T], Callable[[], T]]
    ) -> "ServiceContainer":
        """Register as transient (new instance each time)"""
        return self.register(interface_type, implementation, ServiceLifetime.TRANSIENT)

    def register_scoped(
        self, interface_type: Type[T], implementation: Union[Type[T], Callable[[], T]]
    ) -> "ServiceContainer":
        """Register as scoped (one instance per scope)"""
        return self.register(interface_type, implementation, ServiceLifetime.SCOPED)

    def register_instance(
        self, interface_type: Type[T], instance: T
    ) -> "ServiceContainer":
        """Register a specific instance"""
        return self.register(interface_type, instance, ServiceLifetime.SINGLETON)

    def register_factory(
        self,
        interface_type: Type[T],
        factory: Callable[[], T],
        lifetime: str = ServiceLifetime.SINGLETON,
    ) -> "ServiceContainer":
        """Register a factory method"""
        return self.register(interface_type, factory, lifetime)

    def resolve(self, interface_type: Type[T], scope_id: Optional[str] = None) -> T:
        """
        Resolve a service instance

        Args:
            interface_type: The interface to resolve
            scope_id: Optional scope identifier for scoped services
        """
        if not self.is_registered(interface_type):
            raise ValueError(f"Service {interface_type.__name__} is not registered")

        descriptor = self._services[interface_type]

        # Handle different lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            return self._resolve_singleton(descriptor)
        elif descriptor.lifetime == ServiceLifetime.TRANSIENT:
            return self._create_instance(descriptor)
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._resolve_scoped(descriptor, scope_id or "default")
        else:
            raise ValueError(f"Unknown service lifetime: {descriptor.lifetime}")

    async def resolve_async(
        self, interface_type: Type[T], scope_id: Optional[str] = None
    ) -> T:
        """Async version of resolve for services that require async initialization"""
        instance = self.resolve(interface_type, scope_id)

        # If instance has async initialization, call it
        if hasattr(instance, "__aenter__"):
            await instance.__aenter__()

        return instance

    def is_registered(self, interface_type: Type) -> bool:
        """Check if a service is registered"""
        return interface_type in self._services

    def create_scope(self) -> str:
        """Create a new scope for scoped services"""
        with self._lock:
            self._scope_counter += 1
            scope_id = f"scope_{self._scope_counter}"
            self._scoped_instances[scope_id] = {}
            return scope_id

    def dispose_scope(self, scope_id: str) -> None:
        """Dispose a scope and clean up scoped instances"""
        with self._lock:
            if scope_id in self._scoped_instances:
                # Dispose all scoped instances
                for instance in self._scoped_instances[scope_id].values():
                    if hasattr(instance, "dispose"):
                        try:
                            instance.dispose()
                        except Exception as e:
                            logger.error(f"Error disposing scoped instance: {e}")

                del self._scoped_instances[scope_id]

    def _resolve_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """Resolve singleton instance"""
        if descriptor.instance is None:
            with self._lock:
                if descriptor.instance is None:  # Double-check locking
                    descriptor.instance = self._create_instance(descriptor)

        return descriptor.instance

    def _resolve_scoped(self, descriptor: ServiceDescriptor, scope_id: str) -> Any:
        """Resolve scoped instance"""
        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}

        scoped_cache = self._scoped_instances[scope_id]

        if descriptor.interface_type not in scoped_cache:
            scoped_cache[descriptor.interface_type] = self._create_instance(descriptor)

        return scoped_cache[descriptor.interface_type]

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a new instance of the service"""
        try:
            if descriptor.factory:
                # Use factory method
                return descriptor.factory()
            elif descriptor.implementation:
                # Create instance using constructor injection
                return self._create_with_injection(descriptor.implementation)
            else:
                raise ValueError(
                    f"No factory or implementation for {descriptor.interface_type.__name__}"
                )

        except Exception as e:
            logger.error(
                f"Error creating instance for {descriptor.interface_type.__name__}: {e}"
            )
            raise

    def _create_with_injection(self, implementation_type: Type) -> Any:
        """Create instance with constructor dependency injection"""
        # Get constructor signature
        signature = inspect.signature(implementation_type.__init__)
        parameters = list(signature.parameters.values())[1:]  # Skip 'self'

        # Resolve dependencies
        args = []
        kwargs = {}

        for param in parameters:
            if param.annotation != inspect.Parameter.empty:
                # Try to resolve the dependency
                if self.is_registered(param.annotation):
                    dependency = self.resolve(param.annotation)
                    if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                        args.append(dependency)
                    else:
                        kwargs[param.name] = dependency
                elif param.default != inspect.Parameter.empty:
                    # Use default value
                    kwargs[param.name] = param.default
                else:
                    logger.warning(
                        f"Cannot resolve dependency {param.annotation} for {implementation_type.__name__}"
                    )

        return implementation_type(*args, **kwargs)

    def get_registered_services(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered services"""
        result = {}
        for interface_type, descriptor in self._services.items():
            result[interface_type.__name__] = {
                "interface": interface_type.__name__,
                "implementation": descriptor.implementation.__name__
                if hasattr(descriptor.implementation, "__name__")
                else str(descriptor.implementation),
                "lifetime": descriptor.lifetime,
                "has_instance": descriptor.instance is not None,
            }
        return result

    def clear(self) -> None:
        """Clear all registered services"""
        with self._lock:
            # Dispose all instances
            for descriptor in self._services.values():
                if descriptor.instance and hasattr(descriptor.instance, "dispose"):
                    try:
                        descriptor.instance.dispose()
                    except Exception as e:
                        logger.error(f"Error disposing instance: {e}")

            # Clear all scopes
            for scope_id in list(self._scoped_instances.keys()):
                self.dispose_scope(scope_id)

            self._services.clear()
            self._instances.clear()
            self._scoped_instances.clear()


# Global container instance
_container: Optional[ServiceContainer] = None
_container_lock = Lock()


def get_container() -> ServiceContainer:
    """Get the global service container instance"""
    global _container
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = ServiceContainer()
    return _container


def configure_services() -> ServiceContainer:
    """Configure the default services (to be called at startup)"""
    container = get_container()

    # Configuration services will be registered here
    # This is where we'll register all our implementations

    logger.info("Service container configured")
    return container


# Decorator for automatic service registration
def service(interface_type: Type[T], lifetime: str = ServiceLifetime.SINGLETON):
    """
    Decorator for automatic service registration

    Usage:
        @service(IMyService)
        class MyService(IMyService):
            pass
    """

    def decorator(implementation_class: Type[T]) -> Type[T]:
        container = get_container()
        container.register(interface_type, implementation_class, lifetime)
        return implementation_class

    return decorator


# Context manager for scoped services
class ServiceScope:
    """Context manager for scoped service lifetime"""

    def __init__(self, container: ServiceContainer):
        self.container = container
        self.scope_id: Optional[str] = None

    def __enter__(self) -> str:
        self.scope_id = self.container.create_scope()
        return self.scope_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.scope_id:
            self.container.dispose_scope(self.scope_id)

    async def __aenter__(self) -> str:
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__exit__(exc_type, exc_val, exc_tb)
