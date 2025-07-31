#!/usr/bin/env python3
"""
Simple test script to validate architectural patterns
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_dependency_injection():
    """Test basic dependency injection functionality"""
    print("🧪 Testing Dependency Injection...")
    
    try:
        from src.core.dependency_injection import ServiceContainer, ServiceLifetime
        
        # Create container
        container = ServiceContainer()
        
        # Define test interface and implementation
        class ITestService:
            def get_message(self) -> str:
                pass
        
        class TestService(ITestService):
            def get_message(self) -> str:
                return "Hello from DI Container!"
        
        # Register and resolve
        container.register(ITestService, TestService, ServiceLifetime.SINGLETON)
        service = container.resolve(ITestService)
        
        message = service.get_message()
        assert message == "Hello from DI Container!"
        
        print("✅ Dependency Injection: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Dependency Injection: FAILED - {e}")
        return False


async def test_observer_pattern():
    """Test basic observer pattern functionality"""
    print("🧪 Testing Observer Pattern...")
    
    try:
        from src.core.event_system import EventPublisher
        from src.core.interfaces import ISessionObserver, SessionEvent, SessionEventType
        
        # Create event publisher
        publisher = EventPublisher()
        
        # Create test observer
        received_events = []
        
        class TestObserver(ISessionObserver):
            async def on_session_event(self, event: SessionEvent) -> None:
                received_events.append(event)
        
        # Subscribe and publish
        observer = TestObserver()
        publisher.subscribe(observer)
        
        event = SessionEvent(SessionEventType.SESSION_CREATED, "test_session", {"test": "data"})
        await publisher.publish(event)
        
        # Verify
        assert len(received_events) == 1
        assert received_events[0].session_id == "test_session"
        
        print("✅ Observer Pattern: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Observer Pattern: FAILED - {e}")
        return False


async def test_repository_pattern():
    """Test basic repository pattern functionality"""
    print("🧪 Testing Repository Pattern...")
    
    try:
        from src.core.repositories import InMemorySessionRepository
        
        # Create repository
        repo = InMemorySessionRepository()
        
        # Test data
        session_data = {
            "session_id": "test_123",
            "course_name": "Test Course",
            "state": "created"
        }
        
        # Save and retrieve
        await repo.save(session_data)
        retrieved = await repo.get_by_id("test_123")
        
        # Verify
        assert retrieved is not None
        assert retrieved["session_id"] == "test_123"
        assert retrieved["course_name"] == "Test Course"
        
        print("✅ Repository Pattern: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Repository Pattern: FAILED - {e}")
        return False


async def test_command_pattern():
    """Test basic command pattern functionality"""
    print("🧪 Testing Command Pattern...")
    
    try:
        from src.core.command_system import BaseCommand, CommandExecutor, CommandContext, CommandResult
        
        # Create test command
        class TestCommand(BaseCommand):
            def __init__(self, context: CommandContext, value: str):
                super().__init__(context)
                self.value = value
                self.executed = False
            
            async def _execute_impl(self, session_data):
                self.executed = True
                return CommandResult(
                    success=True,
                    message=f"Command processed: {self.value}",
                    data={"processed_value": self.value}
                )
        
        # Execute command
        executor = CommandExecutor()
        context = CommandContext("test_session")
        command = TestCommand(context, "test_value")
        
        result = await executor.execute_command(command, {})
        
        # Verify
        assert result.success is True
        assert command.executed is True
        assert result.data["processed_value"] == "test_value"
        
        print("✅ Command Pattern: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Command Pattern: FAILED - {e}")
        return False


async def test_service_configuration():
    """Test service configuration"""
    print("🧪 Testing Service Configuration...")
    
    try:
        from src.core.service_configuration import create_configured_container, TESTING_CONFIG
        
        # Create configured container
        container = create_configured_container(TESTING_CONFIG)
        
        # Verify some services are registered
        services = container.get_registered_services()
        assert len(services) > 0
        
        print(f"✅ Service Configuration: PASSED ({len(services)} services registered)")
        return True
        
    except Exception as e:
        print(f"❌ Service Configuration: FAILED - {e}")
        return False


async def main():
    """Run all pattern tests"""
    print("🚀 Testing MoodleClaude Architectural Patterns\n")
    
    tests = [
        test_dependency_injection,
        test_observer_pattern,
        test_repository_pattern,
        test_command_pattern,
        test_service_configuration
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All architectural patterns are working correctly!")
        return True
    else:
        print(f"\n⚠️  {total - passed} pattern(s) need attention.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)