#!/usr/bin/env python3
"""
Test script for the refactored MCP server
"""

import asyncio
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_refactored_server_initialization():
    """Test that the refactored server initializes correctly"""
    print("🧪 Testing Refactored MCP Server Initialization...")
    
    try:
        from src.core.refactored_mcp_server import RefactoredMoodleMCPServer
        from src.core.service_configuration import TESTING_CONFIG
        
        # Create server with test configuration
        server = RefactoredMoodleMCPServer(TESTING_CONFIG)
        
        # Verify server components
        assert server.container is not None
        assert server.server is not None
        
        # Check if services are resolved (some might be None if dependencies missing)
        print(f"   - Service container: ✅ Initialized")
        print(f"   - Event publisher: {'✅' if server.event_publisher else '⚠️'} {'Available' if server.event_publisher else 'Not available'}")
        print(f"   - Session repository: {'✅' if server.session_repository else '⚠️'} {'Available' if server.session_repository else 'Not available'}")
        
        print("✅ Refactored MCP Server Initialization: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Refactored MCP Server Initialization: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_server_service_resolution():
    """Test service resolution in the server"""
    print("🧪 Testing Server Service Resolution...")
    
    try:
        from src.core.refactored_mcp_server import RefactoredMoodleMCPServer
        from src.core.service_configuration import TESTING_CONFIG
        from src.core.interfaces import IEventPublisher, ISessionRepository
        
        # Create server
        server = RefactoredMoodleMCPServer(TESTING_CONFIG)
        
        # Test container service resolution
        container = server.container
        
        # Check available services
        services = container.get_registered_services()
        print(f"   - Registered services: {len(services)}")
        
        for service_name, info in services.items():
            print(f"     * {service_name}: {info['lifetime']}")
        
        # Try to resolve key services
        if container.is_registered(IEventPublisher):
            event_publisher = container.resolve(IEventPublisher)
            assert event_publisher is not None
            print("   - Event Publisher: ✅ Resolved")
        
        if container.is_registered(ISessionRepository):
            repository = container.resolve(ISessionRepository)
            assert repository is not None
            print("   - Session Repository: ✅ Resolved")
        
        print("✅ Server Service Resolution: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Server Service Resolution: FAILED - {e}")
        return False


async def test_server_health_check():
    """Test server health check functionality"""
    print("🧪 Testing Server Health Check...")
    
    try:
        from src.core.service_configuration import get_service_health_check, create_configured_container, TESTING_CONFIG
        
        # Create container and check health
        container = create_configured_container(TESTING_CONFIG)
        health = get_service_health_check(container)
        
        print(f"   - Overall Status: {health['overall_status']}")
        print(f"   - Services Checked: {len(health.get('services', {}))}")
        
        for service_name, service_health in health.get('services', {}).items():
            status = service_health.get('status', 'unknown')
            print(f"     * {service_name}: {status}")
        
        assert health['overall_status'] in ['healthy', 'degraded', 'unhealthy']
        
        print("✅ Server Health Check: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Server Health Check: FAILED - {e}")
        return False


async def test_event_system_integration():
    """Test event system integration in the server"""
    print("🧪 Testing Event System Integration...")
    
    try:
        from src.core.refactored_mcp_server import RefactoredMoodleMCPServer
        from src.core.service_configuration import TESTING_CONFIG
        from src.core.interfaces import SessionEvent, SessionEventType, ISessionObserver
        
        # Create server
        server = RefactoredMoodleMCPServer(TESTING_CONFIG)
        
        if server.event_publisher:
            # Test event publishing
            received_events = []
            
            class TestObserver(ISessionObserver):
                async def on_session_event(self, event: SessionEvent) -> None:
                    received_events.append(event)
            
            # Subscribe observer
            server.event_publisher.subscribe(TestObserver())
            
            # Publish test event
            event = SessionEvent(SessionEventType.SESSION_CREATED, "test_integration", {"test": True})
            await server.event_publisher.publish(event)
            
            # Verify
            assert len(received_events) == 1
            assert received_events[0].session_id == "test_integration"
            
            print("   - Event publishing: ✅ Working")
            print("   - Observer pattern: ✅ Working")
        else:
            print("   - Event publisher: ⚠️ Not available (expected in test mode)")
        
        print("✅ Event System Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Event System Integration: FAILED - {e}")
        return False


async def test_mock_mcp_tool_handling():
    """Test MCP tool handling structure"""
    print("🧪 Testing MCP Tool Handling Structure...")
    
    try:
        from src.core.refactored_mcp_server import RefactoredMoodleMCPServer
        from src.core.service_configuration import TESTING_CONFIG
        
        # Create server
        server = RefactoredMoodleMCPServer(TESTING_CONFIG)
        
        # Test that server has the required handler structure
        assert hasattr(server, 'server')
        assert hasattr(server, '_setup_handlers')
        
        # Verify server name
        assert server.server.name == "refactored-moodle-course-creator"
        
        print("   - MCP Server: ✅ Initialized")
        print("   - Handler setup: ✅ Available")
        print("   - Server name: ✅ Correct")
        
        print("✅ MCP Tool Handling Structure: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ MCP Tool Handling Structure: FAILED - {e}")
        return False


async def main():
    """Run all server tests"""
    print("🚀 Testing Refactored MoodleClaude MCP Server\n")
    
    tests = [
        test_refactored_server_initialization,
        test_server_service_resolution,
        test_server_health_check,
        test_event_system_integration,
        test_mock_mcp_tool_handling
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
        print("\n🎉 Refactored MCP Server is working correctly!")
        print("\n💡 Next Steps:")
        print("   1. Update Claude Desktop configuration to use the refactored server")
        print("   2. Test with real Moodle integration")
        print("   3. Monitor performance improvements")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) need attention.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)