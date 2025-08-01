#!/usr/bin/env python3
"""
Refactored MCP Server using improved architecture patterns
Demonstrates the implementation of all architectural improvements
"""

import asyncio
import logging
import sys
import os
from typing import Any, Dict, List
import traceback

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.dependency_injection import ServiceContainer, get_container
from src.core.service_configuration import create_configured_container, PRODUCTION_CONFIG
from src.core.interfaces import (
    ICourseCreationService, IAnalyticsService, IEventPublisher, ISessionRepository
)
from src.core.event_system import MetricsObserver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class RefactoredMoodleMCPServer:
    """
    Refactored MCP Server demonstrating improved architecture
    
    Key Improvements:
    - Dependency Injection for loose coupling
    - Single Responsibility services
    - Observer pattern for events
    - Command pattern for operations
    - Repository pattern for data persistence
    - Proper error handling and monitoring
    """
    
    def __init__(self, config_options: Dict[str, Any] = None):
        """Initialize the refactored MCP server"""
        self.server = Server("refactored-moodle-course-creator")
        
        # Initialize service container with dependency injection
        config_options = config_options or PRODUCTION_CONFIG
        self.container = create_configured_container(config_options)
        
        # Resolve services through DI container
        self.course_creation_service = None
        self.analytics_service = None
        self.event_publisher = None
        self.session_repository = None
        
        try:
            self._initialize_services()
            self._setup_handlers()
            logger.info("Refactored MCP Server initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize refactored MCP server: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _initialize_services(self) -> None:
        """Initialize services through dependency injection"""
        try:
            # Resolve services from container
            if self.container.is_registered(ICourseCreationService):
                self.course_creation_service = self.container.resolve(ICourseCreationService)
                logger.debug("Course creation service resolved")
            
            if self.container.is_registered(IAnalyticsService):
                self.analytics_service = self.container.resolve(IAnalyticsService)
                logger.debug("Analytics service resolved")
            
            if self.container.is_registered(IEventPublisher):
                self.event_publisher = self.container.resolve(IEventPublisher)
                logger.debug("Event publisher resolved")
            
            if self.container.is_registered(ISessionRepository):
                self.session_repository = self.container.resolve(ISessionRepository)
                logger.debug("Session repository resolved")
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise
    
    def _setup_handlers(self) -> None:
        """Setup MCP server request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools with improved architecture"""
            tools = [
                types.Tool(
                    name="create_intelligent_course",
                    description="Create a Moodle course using improved architecture with dependency injection and event-driven processing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Chat conversation content to convert into a course"
                            },
                            "course_name": {
                                "type": "string",
                                "description": "Name for the Moodle course"
                            },
                            "course_description": {
                                "type": "string",
                                "description": "Description for the course (optional)",
                                "default": ""
                            },
                            "category_id": {
                                "type": "integer",
                                "description": "Moodle category ID (optional)",
                                "default": 1
                            }
                        },
                        "required": ["content", "course_name"]
                    }
                ),
                types.Tool(
                    name="continue_course_session",
                    description="Continue processing a course creation session with additional content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID to continue"
                            },
                            "additional_content": {
                                "type": "string",
                                "description": "Additional content to add to the session (optional)",
                                "default": ""
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                types.Tool(
                    name="validate_course",
                    description="Validate a created course using the new validation system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID to validate"
                            },
                            "course_id": {
                                "type": "integer",
                                "description": "Moodle course ID to validate (optional)"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                types.Tool(
                    name="get_session_status",
                    description="Get detailed session status with command history and event timeline",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID to check"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                types.Tool(
                    name="get_processing_analytics",
                    description="Get comprehensive processing analytics and system health metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "detailed": {
                                "type": "boolean",
                                "description": "Whether to include detailed analytics",
                                "default": False
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_system_health",
                    description="Get system health status and service availability",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls using service-oriented architecture"""
            try:
                logger.info(f"Executing refactored tool: {name}")
                
                if name == "create_intelligent_course":
                    return await self._create_intelligent_course(arguments)
                elif name == "continue_course_session":
                    return await self._continue_course_session(arguments)
                elif name == "validate_course":
                    return await self._validate_course(arguments)
                elif name == "get_session_status":
                    return await self._get_session_status(arguments)
                elif name == "get_processing_analytics":
                    return await self._get_processing_analytics(arguments)
                elif name == "get_system_health":
                    return await self._get_system_health(arguments)
                else:
                    return await self._handle_unknown_tool(name)
                    
            except Exception as e:
                logger.error(f"Tool execution failed for {name}: {e}")
                logger.error(traceback.format_exc())
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Tool Execution Failed**\n\n"
                         f"Tool: {name}\n"
                         f"Error: {str(e)}\n\n"
                         f"This error has been logged for investigation. "
                         f"Please try again or contact support if the problem persists."
                )]
    
    async def _create_intelligent_course(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create course using service-oriented architecture"""
        if not self.course_creation_service:
            return self._service_unavailable_response("Course Creation Service")
        
        content = arguments.get("content", "").strip()
        course_name = arguments.get("course_name", "").strip()
        
        if not content:
            return [types.TextContent(
                type="text",
                text="❌ **Content Required**\n\n"
                     "Please provide chat content to create a course from.\n\n"
                     "💡 **Tip:** Share your conversation content and I'll transform it into a structured Moodle course!"
            )]
        
        if not course_name:
            return [types.TextContent(
                type="text",
                text="❌ **Course Name Required**\n\n"
                     "Please provide a name for your course.\n\n"
                     "💡 **Example:** 'Advanced Python Programming' or 'Web Development Fundamentals'"
            )]
        
        try:
            # Prepare options
            options = {
                "description": arguments.get("course_description", ""),
                "category_id": arguments.get("category_id", 1),
                "user_id": "mcp_user"  # Could be extracted from context
            }
            
            # Create course using service
            result = await self.course_creation_service.create_course_from_content(
                content=content,
                course_name=course_name,
                options=options
            )
            
            # Format response based on result
            if result["success"]:
                response_parts = [
                    f"✅ **Course Creation Initiated Successfully!**\n\n",
                    f"**Course Name:** {course_name}\n",
                    f"**Session ID:** `{result['session_id']}`\n\n"
                ]
                
                if result.get("course_id"):
                    response_parts.extend([
                        f"**Course ID:** {result['course_id']}\n",
                        f"**Status:** Course created and available in Moodle\n\n"
                    ])
                else:
                    response_parts.append("**Status:** Processing initiated - course will be created shortly\n\n")
                
                response_parts.extend([
                    f"🎯 **What's Next:**\n",
                    f"- Your content is being processed using our improved architecture\n",
                    f"- Use `get_session_status` with session ID to track progress\n",
                    f"- Receive real-time updates through our event system\n\n",
                    f"💡 **New Features:**\n",
                    f"- Dependency injection for better reliability\n",
                    f"- Event-driven processing with detailed monitoring\n",
                    f"- Command pattern for operation tracking and undo support\n",
                    f"- Repository pattern for robust data persistence"
                ])
                
                return [types.TextContent(type="text", text="".join(response_parts))]
            
            else:
                error_message = result.get("message", "Unknown error occurred")
                errors = result.get("errors", [])
                
                response_parts = [
                    f"❌ **Course Creation Failed**\n\n",
                    f"**Session ID:** `{result.get('session_id', 'N/A')}`\n",
                    f"**Error:** {error_message}\n\n"
                ]
                
                if errors:
                    response_parts.extend([
                        f"**Detailed Errors:**\n"
                    ])
                    for error in errors:
                        response_parts.append(f"- {error}\n")
                    response_parts.append("\n")
                
                response_parts.extend([
                    f"🔧 **Troubleshooting:**\n",
                    f"- Check your content format and length\n",
                    f"- Verify Moodle connection settings\n",
                    f"- Use `get_system_health` to check service status\n",
                    f"- Try again with simplified content"
                ])
                
                return [types.TextContent(type="text", text="".join(response_parts))]
        
        except Exception as e:
            logger.error(f"Course creation failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Unexpected Error in Course Creation**\n\n"
                     f"An unexpected error occurred: {str(e)}\n\n"
                     f"This has been logged for investigation. Please try again or contact support."
            )]
    
    async def _continue_course_session(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Continue course session using service layer"""
        if not self.course_creation_service:
            return self._service_unavailable_response("Course Creation Service")
        
        session_id = arguments.get("session_id", "").strip()
        additional_content = arguments.get("additional_content", "")
        
        if not session_id:
            return [types.TextContent(
                type="text",
                text="❌ **Session ID Required**\n\n"
                     "Please provide the session ID from your previous course creation request."
            )]
        
        try:
            result = await self.course_creation_service.continue_course_creation(
                session_id=session_id,
                additional_content=additional_content
            )
            
            if result["success"]:
                return [types.TextContent(
                    type="text",
                    text=f"✅ **Session Continued Successfully**\n\n"
                         f"**Session ID:** `{session_id}`\n"
                         f"**Status:** {result.get('message', 'Processing continued')}\n\n"
                         f"Use `get_session_status` to monitor progress."
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Session Continuation Failed**\n\n"
                         f"**Session ID:** `{session_id}`\n"
                         f"**Error:** {result.get('message', 'Unknown error')}\n\n"
                         f"💡 The session may have expired or completed. Try creating a new course."
                )]
        
        except Exception as e:
            logger.error(f"Session continuation failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Session Continuation Error**\n\n"
                     f"Failed to continue session: {str(e)}"
            )]
    
    async def _validate_course(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Validate course using command pattern"""
        if not self.course_creation_service:
            return self._service_unavailable_response("Course Creation Service")
        
        session_id = arguments.get("session_id", "").strip()
        course_id = arguments.get("course_id")
        
        if not session_id:
            return [types.TextContent(
                type="text",
                text="❌ **Session ID Required**\n\n"
                     "Please provide the session ID to validate."
            )]
        
        try:
            result = await self.course_creation_service.validate_course(
                session_id=session_id,
                course_id=course_id
            )
            
            if result["success"]:
                validation_data = result.get("validation_data", {})
                
                response_parts = [
                    f"✅ **Course Validation Successful**\n\n",
                    f"**Session ID:** `{session_id}`\n"
                ]
                
                if validation_data.get("course_id"):
                    response_parts.extend([
                        f"**Course ID:** {validation_data['course_id']}\n",
                        f"**Expected Sections:** {validation_data.get('expected_sections', 'N/A')}\n",
                        f"**Actual Sections:** {validation_data.get('actual_sections', 'N/A')}\n",
                        f"**Validation Status:** {'✅ Passed' if validation_data.get('validation_passed') else '❌ Failed'}\n"
                    ])
                
                return [types.TextContent(type="text", text="".join(response_parts))]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Course Validation Failed**\n\n"
                         f"**Session ID:** `{session_id}`\n"
                         f"**Error:** {result.get('message', 'Validation failed')}"
                )]
        
        except Exception as e:
            logger.error(f"Course validation failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Validation Error**\n\n"
                     f"Failed to validate course: {str(e)}"
            )]
    
    async def _get_session_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get session status with command history"""
        if not self.course_creation_service:
            return self._service_unavailable_response("Course Creation Service")
        
        session_id = arguments.get("session_id", "").strip()
        
        if not session_id:
            return [types.TextContent(
                type="text",
                text="❌ **Session ID Required**\n\n"
                     "Please provide the session ID to check status."
            )]
        
        try:
            result = await self.course_creation_service.get_session_status(session_id)
            
            if result["success"]:
                session_data = result["session_data"]
                command_history = result.get("command_history", [])
                
                response_parts = [
                    f"📊 **Session Status Report**\n\n",
                    f"**Session ID:** `{session_id}`\n",
                    f"**Course Name:** {session_data['course_name']}\n",
                    f"**Current State:** {session_data['state'].title()}\n",
                    f"**Created:** {session_data['created_at']}\n"
                ]
                
                if session_data.get("updated_at"):
                    response_parts.append(f"**Last Updated:** {session_data['updated_at']}\n")
                
                if session_data.get("course_id"):
                    response_parts.append(f"**Course ID:** {session_data['course_id']}\n")
                
                # Progress information
                progress = session_data.get("progress", {})
                if progress:
                    response_parts.extend([
                        f"\n**📈 Progress:**\n",
                        f"- **Completion:** {progress.get('percentage', 0):.1f}%\n"
                    ])
                
                # Command history
                if command_history:
                    response_parts.extend([
                        f"\n**🔧 Command History:**\n"
                    ])
                    for cmd in command_history[-5:]:  # Show last 5 commands
                        status_emoji = "✅" if cmd.get("success") else "❌"
                        response_parts.append(
                            f"- {status_emoji} {cmd['command_type']} ({cmd['status']})\n"
                        )
                
                return [types.TextContent(type="text", text="".join(response_parts))]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Session Status Error**\n\n"
                         f"**Session ID:** `{session_id}`\n"
                         f"**Error:** {result.get('message', 'Session not found')}"
                )]
        
        except Exception as e:
            logger.error(f"Session status retrieval failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Status Retrieval Error**\n\n"
                     f"Failed to get session status: {str(e)}"
            )]
    
    async def _get_processing_analytics(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get processing analytics using analytics service"""
        if not self.analytics_service:
            return self._service_unavailable_response("Analytics Service")
        
        detailed = arguments.get("detailed", False)
        
        try:
            analytics = await self.analytics_service.get_processing_analytics(detailed)
            
            if "error" in analytics:
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Analytics Error**\n\n"
                         f"Failed to retrieve analytics: {analytics['error']}"
                )]
            
            overview = analytics.get("overview", {})
            states = analytics.get("sessions_by_state", {})
            
            response_parts = [
                f"📊 **Processing Analytics Dashboard**\n\n",
                f"**📈 Overall Performance:**\n",
                f"- **Total Sessions:** {overview.get('total_sessions', 0)}\n",
                f"- **Active Sessions:** {overview.get('active_sessions', 0)}\n",
                f"- **Recent Activity:** {overview.get('recent_activity', 0)} (24h)\n",
                f"- **Success Rate:** {overview.get('success_rate', 0):.1f}%\n\n",
                
                f"**📋 Sessions by State:**\n"
            ]
            
            for state, count in states.items():
                response_parts.append(f"- **{state.title()}:** {count}\n")
            
            response_parts.append(f"\n**⏰ Generated:** {analytics.get('timestamp', 'N/A')}")
            
            # Additional metrics for detailed view
            if detailed and "detailed_metrics" in analytics:
                detailed_metrics = analytics["detailed_metrics"]
                response_parts.extend([
                    f"\n\n**🔍 Detailed Metrics:**\n",
                    f"- **Timeline Analysis:** {detailed_metrics.get('creation_timeline', {})}\n",
                    f"- **State Distribution:** {detailed_metrics.get('states_distribution', {})}\n"
                ])
            
            return [types.TextContent(type="text", text="".join(response_parts))]
        
        except Exception as e:
            logger.error(f"Analytics retrieval failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Analytics Error**\n\n"
                     f"Failed to retrieve processing analytics: {str(e)}"
            )]
    
    async def _get_system_health(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get system health status"""
        if not self.analytics_service:
            return self._service_unavailable_response("Analytics Service")
        
        try:
            health = await self.analytics_service.get_system_health()
            
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌"
            }.get(health["status"], "❓")
            
            response_parts = [
                f"🏥 **System Health Report**\n\n",
                f"**Overall Status:** {status_emoji} {health['status'].title()}\n",
                f"**Active Sessions:** {health.get('active_sessions', 0)}\n",
                f"**Error Rate:** {health.get('error_rate', 0):.1%}\n",
                f"**Database:** {'✅ Accessible' if health.get('database_accessible') else '❌ Issues'}\n",
                f"**Timestamp:** {health.get('timestamp', 'N/A')}\n\n"
            ]
            
            # Service-specific health
            if self.container:
                service_count = len(self.container.get_registered_services())
                response_parts.extend([
                    f"**🔧 Service Container:**\n",
                    f"- **Registered Services:** {service_count}\n",
                    f"- **DI Container:** ✅ Active\n",
                    f"- **Event System:** {'✅ Active' if self.event_publisher else '❌ Inactive'}\n"
                ])
            
            # Recommendations
            if health["status"] != "healthy":
                response_parts.extend([
                    f"\n**💡 Recommendations:**\n",
                    f"- Check error logs for specific issues\n",
                    f"- Verify Moodle connection\n",
                    f"- Consider system restart if issues persist\n"
                ])
            
            return [types.TextContent(type="text", text="".join(response_parts))]
        
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Health Check Error**\n\n"
                     f"Failed to retrieve system health: {str(e)}\n\n"
                     f"This indicates a serious system issue. Please check logs and restart if necessary."
            )]
    
    async def _handle_unknown_tool(self, name: str) -> List[types.TextContent]:
        """Handle unknown tool requests"""
        return [types.TextContent(
            type="text",
            text=f"❌ **Unknown Tool: {name}**\n\n"
                 f"The requested tool is not available in this refactored server.\n\n"
                 f"**Available Tools:**\n"
                 f"- `create_intelligent_course` - Create courses with improved architecture\n"
                 f"- `continue_course_session` - Continue processing sessions\n"
                 f"- `validate_course` - Validate created courses\n"
                 f"- `get_session_status` - Get detailed session information\n"
                 f"- `get_processing_analytics` - Get system analytics\n"
                 f"- `get_system_health` - Check system health\n\n"
                 f"💡 **New Architecture Features:**\n"
                 f"- Dependency injection for better modularity\n"
                 f"- Event-driven processing with real-time monitoring\n"
                 f"- Command pattern for operation tracking\n"
                 f"- Repository pattern for reliable data persistence"
        )]
    
    def _service_unavailable_response(self, service_name: str) -> List[types.TextContent]:
        """Generate service unavailable response"""
        return [types.TextContent(
            type="text",
            text=f"❌ **Service Unavailable: {service_name}**\n\n"
                 f"The {service_name} is currently unavailable. This may be due to:\n\n"
                 f"- Configuration issues\n"
                 f"- Service initialization problems\n"
                 f"- Missing dependencies\n\n"
                 f"**Troubleshooting:**\n"
                 f"1. Check system health with `get_system_health`\n"
                 f"2. Verify configuration settings\n"
                 f"3. Restart the MCP server\n"
                 f"4. Check logs for detailed error information\n\n"
                 f"If the problem persists, please contact support."
        )]
    
    async def run(self):
        """Run the refactored MCP Server"""
        logger.info("Starting Refactored MoodleMCP Server with improved architecture...")
        
        try:
            # Initialize notification options
            init_options = InitializationOptions(
                server_name="refactored-moodle-course-creator",
                server_version="3.0.0",
                capabilities={}
            )
            
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream, 
                    write_stream, 
                    init_options
                )
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Cleanup services
            await self._cleanup_services()
            logger.info("Refactored MoodleMCP Server shutdown complete")
    
    async def _cleanup_services(self):
        """Cleanup services and resources"""
        try:
            # Cleanup event publisher
            if self.event_publisher and hasattr(self.event_publisher, 'shutdown'):
                self.event_publisher.shutdown()
            
            # Clear service container
            if self.container:
                self.container.clear()
            
            logger.debug("Service cleanup completed")
        
        except Exception as e:
            logger.error(f"Error during service cleanup: {e}")


async def main():
    """Main entry point for the Refactored MCP Server"""
    try:
        server = RefactoredMoodleMCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"Fatal error starting refactored MCP server: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())