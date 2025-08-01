#!/usr/bin/env python3
"""
Unit tests for architectural pattern implementations
Tests dependency injection, observer pattern, command pattern, and repository pattern
"""

import asyncio
import json
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.command_system import (
    BaseCommand,
    CommandContext,
    CommandExecutor,
    CommandStatus,
    CreateCourseCommand,
)

# Import our architectural components
from src.core.dependency_injection import ServiceContainer, ServiceLifetime
from src.core.event_system import EventPublisher, LoggingObserver, MetricsObserver
from src.core.interfaces import (
    CommandResult,
    ICourseCreationService,
    IEventPublisher,
    ISessionCommand,
    ISessionObserver,
    ISessionRepository,
    SessionEvent,
    SessionEventType,
)
from src.core.repositories import InMemorySessionRepository, SQLiteSessionRepository
from src.core.services import CourseCreationService


class TestDependencyInjectionContainer:
    """Test the dependency injection container"""

    def setup_method(self):
        self.container = ServiceContainer()

    def test_register_and_resolve_singleton(self):
        """Test singleton service registration and resolution"""

        # Define interfaces and implementations
        class ITestService:
            def get_value(self) -> str:
                pass

        class TestService(ITestService):
            def __init__(self):
                self.value = "test_value"
                self.creation_count = getattr(TestService, "_creation_count", 0) + 1
                TestService._creation_count = self.creation_count

            def get_value(self) -> str:
                return f"{self.value}_{self.creation_count}"

        # Register as singleton
        self.container.register(ITestService, TestService, ServiceLifetime.SINGLETON)

        # Resolve multiple times
        service1 = self.container.resolve(ITestService)
        service2 = self.container.resolve(ITestService)

        # Should be the same instance
        assert service1 is service2
        assert service1.get_value() == "test_value_1"

    def test_register_and_resolve_transient(self):
        """Test transient service registration and resolution"""

        class ITestService:
            def get_id(self) -> int:
                pass

        class TestService(ITestService):
            def __init__(self):
                self.id = id(self)

            def get_id(self) -> int:
                return self.id

        # Register as transient
        self.container.register(ITestService, TestService, ServiceLifetime.TRANSIENT)

        # Resolve multiple times
        service1 = self.container.resolve(ITestService)
        service2 = self.container.resolve(ITestService)

        # Should be different instances
        assert service1 is not service2
        assert service1.get_id() != service2.get_id()

    def test_constructor_dependency_injection(self):
        """Test automatic constructor dependency injection"""

        class IDependency:
            def get_data(self) -> str:
                pass

        class Dependency(IDependency):
            def get_data(self) -> str:
                return "dependency_data"

        class IService:
            def process(self) -> str:
                pass

        class Service(IService):
            def __init__(self, dependency: IDependency):
                self.dependency = dependency

            def process(self) -> str:
                return f"processed_{self.dependency.get_data()}"

        # Register services
        self.container.register(IDependency, Dependency)
        self.container.register(IService, Service)

        # Resolve service with injected dependency
        service = self.container.resolve(IService)
        assert service.process() == "processed_dependency_data"

    def test_factory_registration(self):
        """Test factory method registration"""

        class ITestService:
            def get_config(self) -> str:
                pass

        class TestService(ITestService):
            def __init__(self, config: str):
                self.config = config

            def get_config(self) -> str:
                return self.config

        # Register with factory
        def create_test_service() -> ITestService:
            return TestService("factory_config")

        self.container.register_factory(ITestService, create_test_service)

        # Resolve
        service = self.container.resolve(ITestService)
        assert service.get_config() == "factory_config"

    def test_service_not_registered_error(self):
        """Test error when resolving non-registered service"""

        class IUnregisteredService:
            pass

        with pytest.raises(ValueError, match="Service .* is not registered"):
            self.container.resolve(IUnregisteredService)


class TestObserverPattern:
    """Test the observer pattern implementation"""

    def setup_method(self):
        self.event_publisher = EventPublisher()

    @pytest.mark.asyncio
    async def test_event_publishing_and_observation(self):
        """Test basic event publishing and observation"""
        received_events = []

        class TestObserver(ISessionObserver):
            async def on_session_event(self, event: SessionEvent) -> None:
                received_events.append(event)

        # Subscribe observer
        observer = TestObserver()
        self.event_publisher.subscribe(observer)

        # Publish event
        event = SessionEvent(
            SessionEventType.SESSION_CREATED, "test_session_123", {"test_data": "value"}
        )

        await self.event_publisher.publish(event)

        # Verify event was received
        assert len(received_events) == 1
        assert received_events[0].event_type == SessionEventType.SESSION_CREATED
        assert received_events[0].session_id == "test_session_123"
        assert received_events[0].data["test_data"] == "value"

    @pytest.mark.asyncio
    async def test_multiple_observers(self):
        """Test multiple observers receiving the same event"""
        observer1_events = []
        observer2_events = []

        class Observer1(ISessionObserver):
            async def on_session_event(self, event: SessionEvent) -> None:
                observer1_events.append(event)

        class Observer2(ISessionObserver):
            async def on_session_event(self, event: SessionEvent) -> None:
                observer2_events.append(event)

        # Subscribe observers
        self.event_publisher.subscribe(Observer1())
        self.event_publisher.subscribe(Observer2())

        # Publish event
        event = SessionEvent(SessionEventType.PROCESSING_STARTED, "session_456", {})
        await self.event_publisher.publish(event)

        # Both observers should receive the event
        assert len(observer1_events) == 1
        assert len(observer2_events) == 1
        assert observer1_events[0].session_id == "session_456"
        assert observer2_events[0].session_id == "session_456"

    @pytest.mark.asyncio
    async def test_metrics_observer(self):
        """Test the metrics observer functionality"""
        metrics_observer = MetricsObserver()
        self.event_publisher.subscribe(metrics_observer)

        # Publish various events
        events = [
            SessionEvent(SessionEventType.SESSION_CREATED, "session_1", {}),
            SessionEvent(SessionEventType.SESSION_CREATED, "session_2", {}),
            SessionEvent(
                SessionEventType.SESSION_COMPLETED,
                "session_1",
                {"processing_time": 5.5},
            ),
            SessionEvent(SessionEventType.SESSION_FAILED, "session_3", {}),
        ]

        for event in events:
            await self.event_publisher.publish(event)

        # Check metrics
        metrics = metrics_observer.get_metrics()
        assert metrics["total_events"] == 4
        assert metrics["sessions_created"] == 2
        assert metrics["sessions_completed"] == 1
        assert metrics["sessions_failed"] == 1
        assert metrics["success_rate"] == 50.0  # 1 completed out of 2 created
        assert 5.5 in metrics["processing_times"]

    def test_observer_count(self):
        """Test observer count tracking"""

        class TestObserver(ISessionObserver):
            async def on_session_event(self, event: SessionEvent) -> None:
                pass

        # Initially no observers
        observer_count = self.event_publisher.get_observer_count()
        assert observer_count["total_observers"] == 0

        # Add observers
        self.event_publisher.subscribe(TestObserver())
        self.event_publisher.subscribe(TestObserver())

        observer_count = self.event_publisher.get_observer_count()
        assert observer_count["total_observers"] == 2


class TestCommandPattern:
    """Test the command pattern implementation"""

    def setup_method(self):
        self.command_executor = CommandExecutor()
        self.mock_moodle_client = Mock()

    @pytest.mark.asyncio
    async def test_basic_command_execution(self):
        """Test basic command execution"""

        class TestCommand(BaseCommand):
            def __init__(self, context: CommandContext):
                super().__init__(context)
                self.executed = False

            async def _execute_impl(
                self, session_data: Dict[str, Any]
            ) -> CommandResult:
                self.executed = True
                return CommandResult(
                    success=True,
                    message="Test command executed",
                    data={"result": "success"},
                )

        # Create and execute command
        context = CommandContext("test_session")
        command = TestCommand(context)

        result = await self.command_executor.execute_command(command, {})

        # Verify execution
        assert result.success is True
        assert result.message == "Test command executed"
        assert result.data["result"] == "success"
        assert command.executed is True
        assert command.status == CommandStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_command_failure_handling(self):
        """Test command failure handling"""

        class FailingCommand(BaseCommand):
            async def _execute_impl(
                self, session_data: Dict[str, Any]
            ) -> CommandResult:
                raise ValueError("Command execution failed")

        context = CommandContext("test_session")
        command = FailingCommand(context)

        result = await self.command_executor.execute_command(command, {})

        # Verify failure handling
        assert result.success is False
        assert "Command execution failed" in result.message
        assert command.status == CommandStatus.FAILED
        assert command.error is not None

    @pytest.mark.asyncio
    async def test_create_course_command(self):
        """Test the CreateCourseCommand specifically"""
        # Mock the Moodle client
        self.mock_moodle_client.create_course = AsyncMock(return_value=123)

        context = CommandContext("test_session")
        command = CreateCourseCommand(
            context, self.mock_moodle_client, "Test Course", "Test Description"
        )

        result = await self.command_executor.execute_command(command, {})

        # Verify command execution
        assert result.success is True
        assert result.data["course_id"] == 123
        assert result.data["course_name"] == "Test Course"
        self.mock_moodle_client.create_course.assert_called_once_with(
            name="Test Course", description="Test Description"
        )

    @pytest.mark.asyncio
    async def test_command_history(self):
        """Test command history tracking"""

        class TestCommand(BaseCommand):
            def __init__(self, context: CommandContext, name: str):
                super().__init__(context)
                self.name = name

            async def _execute_impl(
                self, session_data: Dict[str, Any]
            ) -> CommandResult:
                return CommandResult(success=True, message=f"{self.name} executed")

        context = CommandContext("test_session")

        # Execute multiple commands
        commands = [
            TestCommand(context, "Command1"),
            TestCommand(context, "Command2"),
            TestCommand(context, "Command3"),
        ]

        for command in commands:
            await self.command_executor.execute_command(command, {})

        # Check history
        history = self.command_executor.get_command_history("test_session")
        assert len(history) == 3
        assert all(cmd["success"] is True for cmd in history)
        assert history[0]["command_type"] == "TestCommand"

    def test_command_statistics(self):
        """Test command execution statistics"""
        # Initially no statistics
        stats = self.command_executor.get_statistics()
        assert stats["total_commands"] == 0
        assert stats["success_rate"] == 0


class TestRepositoryPattern:
    """Test the repository pattern implementation"""

    def setup_method(self):
        self.in_memory_repo = InMemorySessionRepository()

    @pytest.mark.asyncio
    async def test_in_memory_repository_save_and_get(self):
        """Test in-memory repository save and get operations"""
        session_data = {
            "session_id": "test_session_123",
            "course_name": "Test Course",
            "state": "created",
            "content": "Test content",
            "progress": {"percentage": 0},
        }

        # Save session
        await self.in_memory_repo.save(session_data)

        # Retrieve session
        retrieved = await self.in_memory_repo.get_by_id("test_session_123")

        assert retrieved is not None
        assert retrieved["session_id"] == "test_session_123"
        assert retrieved["course_name"] == "Test Course"
        assert retrieved["state"] == "created"

    @pytest.mark.asyncio
    async def test_repository_update_session_state(self):
        """Test session state updates"""
        session_data = {
            "session_id": "test_session_456",
            "course_name": "Test Course",
            "state": "created",
        }

        # Save initial session
        await self.in_memory_repo.save(session_data)

        # Update session state
        update_data = {"progress": {"percentage": 50}, "course_id": 789}
        updated = await self.in_memory_repo.update_session_state(
            "test_session_456", "processing", update_data
        )

        assert updated is True

        # Verify update
        retrieved = await self.in_memory_repo.get_by_id("test_session_456")
        assert retrieved["state"] == "processing"
        assert retrieved["progress"]["percentage"] == 50
        assert retrieved["course_id"] == 789

    @pytest.mark.asyncio
    async def test_repository_get_active_sessions(self):
        """Test getting active sessions"""
        # Save multiple sessions
        sessions = [
            {"session_id": "session_1", "course_name": "Course 1", "state": "created"},
            {
                "session_id": "session_2",
                "course_name": "Course 2",
                "state": "processing",
            },
            {
                "session_id": "session_3",
                "course_name": "Course 3",
                "state": "completed",
            },
        ]

        for session in sessions:
            await self.in_memory_repo.save(session)

        # Get active sessions
        active_sessions = await self.in_memory_repo.get_active_sessions()

        assert len(active_sessions) == 3
        session_ids = [s["session_id"] for s in active_sessions]
        assert "session_1" in session_ids
        assert "session_2" in session_ids
        assert "session_3" in session_ids

    @pytest.mark.asyncio
    async def test_repository_delete_session(self):
        """Test session deletion"""
        session_data = {
            "session_id": "test_session_delete",
            "course_name": "Delete Test",
            "state": "created",
        }

        # Save and verify
        await self.in_memory_repo.save(session_data)
        retrieved = await self.in_memory_repo.get_by_id("test_session_delete")
        assert retrieved is not None

        # Delete and verify
        deleted = await self.in_memory_repo.delete("test_session_delete")
        assert deleted is True

        retrieved = await self.in_memory_repo.get_by_id("test_session_delete")
        assert retrieved is None


class TestServiceLayer:
    """Test the service layer implementation"""

    def setup_method(self):
        # Create mocks for dependencies
        self.mock_content_processor = Mock()
        self.mock_moodle_client = Mock()
        self.mock_session_repository = Mock()
        self.mock_event_publisher = Mock()

        # Create service with mocked dependencies
        self.course_service = CourseCreationService(
            content_processor=self.mock_content_processor,
            moodle_client=self.mock_moodle_client,
            session_repository=self.mock_session_repository,
            event_publisher=self.mock_event_publisher,
        )

    @pytest.mark.asyncio
    async def test_service_dependency_injection(self):
        """Test that service properly uses injected dependencies"""
        # Setup mocks
        self.mock_content_processor.analyze_content_complexity = AsyncMock(
            return_value={
                "complexity_score": 0.5,
                "recommended_strategy": "single_pass",
            }
        )

        self.mock_session_repository.save = AsyncMock()
        self.mock_event_publisher.publish = AsyncMock()

        # This test verifies that the service uses the injected dependencies
        # In a real scenario, we'd call a service method and verify mock calls
        assert self.course_service.content_processor is self.mock_content_processor
        assert self.course_service.moodle_client is self.mock_moodle_client
        assert self.course_service.session_repository is self.mock_session_repository
        assert self.course_service.event_publisher is self.mock_event_publisher


class TestIntegratedArchitecture:
    """Integration tests for the complete architectural solution"""

    @pytest.mark.asyncio
    async def test_full_dependency_injection_workflow(self):
        """Test complete workflow using dependency injection"""
        container = ServiceContainer()

        # Register services
        container.register(
            ISessionRepository, InMemorySessionRepository, ServiceLifetime.SINGLETON
        )
        container.register(IEventPublisher, EventPublisher, ServiceLifetime.SINGLETON)

        # Resolve services
        repository = container.resolve(ISessionRepository)
        event_publisher = container.resolve(IEventPublisher)

        # Verify they work together
        assert repository is not None
        assert event_publisher is not None

        # Test repository functionality
        session_data = {"session_id": "integration_test", "state": "created"}
        await repository.save(session_data)

        retrieved = await repository.get_by_id("integration_test")
        assert retrieved["session_id"] == "integration_test"

        # Test event system
        received_events = []

        class TestObserver(ISessionObserver):
            async def on_session_event(self, event: SessionEvent) -> None:
                received_events.append(event)

        event_publisher.subscribe(TestObserver())

        event = SessionEvent(SessionEventType.SESSION_CREATED, "integration_test", {})
        await event_publisher.publish(event)

        assert len(received_events) == 1
        assert received_events[0].session_id == "integration_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
