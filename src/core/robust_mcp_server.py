#!/usr/bin/env python3
"""
Robust MCP Server that gracefully handles missing dependencies
This server will start even if Moodle is not available
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class RobustMoodleMCPServer:
    """
    Robust MCP Server that starts even with missing dependencies
    """
    
    def __init__(self):
        """Initialize the robust MCP server"""
        self.server = Server("robust-moodle-course-creator")
        self.services_available = {}
        
        try:
            self._initialize_services()
            self._setup_handlers()
            logger.info("Robust MCP Server initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize robust MCP server: {e}")
            logger.error(traceback.format_exc())
            # Don't re-raise - continue with limited functionality
    
    def _initialize_services(self):
        """Initialize services with graceful fallback"""
        
        # Try to initialize dependency injection
        try:
            from src.core.service_configuration import create_configured_container, TESTING_CONFIG
            from src.core.interfaces import ICourseCreationService, IAnalyticsService
            
            # Use testing config to avoid external dependencies
            self.container = create_configured_container(TESTING_CONFIG)
            
            # Try to resolve services
            try:
                if self.container.is_registered(ICourseCreationService):
                    self.course_creation_service = self.container.resolve(ICourseCreationService)
                    self.services_available["course_creation"] = True
                    logger.info("Course creation service available")
            except Exception as e:
                logger.warning(f"Course creation service not available: {e}")
                self.services_available["course_creation"] = False
            
            try:
                if self.container.is_registered(IAnalyticsService):
                    self.analytics_service = self.container.resolve(IAnalyticsService)
                    self.services_available["analytics"] = True
                    logger.info("Analytics service available")
            except Exception as e:
                logger.warning(f"Analytics service not available: {e}")
                self.services_available["analytics"] = False
                
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            # Continue with basic functionality only
            self.services_available = {"course_creation": False, "analytics": False}
    
    def _setup_handlers(self):
        """Setup MCP handlers with graceful degradation"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools based on service availability"""
            tools = [
                types.Tool(
                    name="test_connection",
                    description="Test MCP server connection and service status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "detailed": {
                                "type": "boolean",
                                "description": "Show detailed service information",
                                "default": False
                            }
                        }
                    }
                )
            ]
            
            # Add course creation tool if service is available
            if self.services_available.get("course_creation", False):
                tools.append(types.Tool(
                    name="create_intelligent_course",
                    description="Create a Moodle course using improved architecture",
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
                            }
                        },
                        "required": ["content", "course_name"]
                    }
                ))
            
            # Add analytics tool if service is available
            if self.services_available.get("analytics", False):
                tools.append(types.Tool(
                    name="get_system_health",
                    description="Get system health status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ))
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls with graceful error handling"""
            try:
                logger.info(f"Executing tool: {name}")
                
                if name == "test_connection":
                    return await self._test_connection(arguments)
                elif name == "create_intelligent_course":
                    return await self._create_course(arguments)
                elif name == "get_system_health":
                    return await self._get_system_health(arguments)
                else:
                    return await self._handle_unknown_tool(name)
                    
            except Exception as e:
                logger.error(f"Tool execution failed for {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Tool Execution Error**\\n\\n"
                         f"Tool: {name}\\n"
                         f"Error: {str(e)}\\n\\n"
                         f"The server is running but encountered an error with this tool."
                )]
    
    async def _test_connection(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Test connection and show service status"""
        detailed = arguments.get("detailed", False)
        
        response_parts = [
            "✅ **MCP Connection Test Successful!**\\n\\n",
            "**Server:** Robust Moodle MCP Server\\n",
            "**Version:** 3.0.0 (Refactored Architecture)\\n",
            "**Status:** Connected and operational\\n\\n"
        ]
        
        # Service availability
        response_parts.append("**🔧 Service Status:**\\n")
        for service_name, available in self.services_available.items():
            status = "✅ Available" if available else "❌ Unavailable"
            response_parts.append(f"- **{service_name.replace('_', ' ').title()}:** {status}\\n")
        
        if detailed and hasattr(self, 'container'):
            try:
                services = self.container.get_registered_services()
                response_parts.extend([
                    f"\\n**📊 Detailed Service Info:**\\n",
                    f"- **Registered Services:** {len(services)}\\n"
                ])
                for service_name, info in list(services.items())[:5]:  # Show first 5
                    response_parts.append(f"  * {service_name}: {info.get('lifetime', 'unknown')}\\n")
            except Exception as e:
                response_parts.append(f"\\n**⚠️ Container Status:** Error accessing ({str(e)})\\n")
        
        response_parts.extend([
            "\\n**🚀 Architecture Features:**\\n",
            "- Dependency injection with graceful fallback\\n",
            "- Service-oriented architecture\\n",
            "- Robust error handling\\n",
            "- Event-driven processing (when available)\\n\\n",
            "💡 **Note:** Some features may be limited if external services (like Moodle) are unavailable."
        ])
        
        return [types.TextContent(type="text", text="".join(response_parts))]
    
    async def _create_course(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create course if service is available"""
        if not self.services_available.get("course_creation", False):
            return [types.TextContent(
                type="text",
                text="❌ **Course Creation Service Unavailable**\\n\\n"
                     "The course creation service is currently not available. This may be due to:\\n\\n"
                     "- Moodle server not running\\n"
                     "- Configuration issues\\n"
                     "- Missing dependencies\\n\\n"
                     "**💡 Troubleshooting:**\\n"
                     "1. Check if Moodle is running on localhost:8080\\n"
                     "2. Verify environment variables are set\\n"
                     "3. Use `test_connection` with detailed=true for more info"
            )]
        
        try:
            content = arguments.get("content", "").strip()
            course_name = arguments.get("course_name", "").strip()
            
            if not content or not course_name:
                return [types.TextContent(
                    type="text",
                    text="❌ **Missing Required Parameters**\\n\\n"
                         "Please provide both `content` and `course_name` parameters."
                )]
            
            # Delegate to service if available
            result = await self.course_creation_service.create_course_from_content(
                content=content,
                course_name=course_name,
                options={}
            )
            
            if result["success"]:
                return [types.TextContent(
                    type="text",
                    text=f"✅ **Course Creation Initiated**\\n\\n"
                         f"**Course Name:** {course_name}\\n"
                         f"**Session ID:** `{result['session_id']}`\\n\\n"
                         f"Course creation is in progress with the new architecture!"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Course Creation Failed**\\n\\n"
                         f"Error: {result.get('message', 'Unknown error')}"
                )]
                
        except Exception as e:
            logger.error(f"Course creation error: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Course Creation Error**\\n\\n"
                     f"An error occurred: {str(e)}"
            )]
    
    async def _get_system_health(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get system health if service is available"""
        if not self.services_available.get("analytics", False):
            return [types.TextContent(
                type="text",
                text="❌ **Analytics Service Unavailable**\\n\\n"
                     "System health monitoring is not available at this time."
            )]
        
        try:
            health = await self.analytics_service.get_system_health()
            
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️", 
                "unhealthy": "❌"
            }.get(health.get("status", "unknown"), "❓")
            
            return [types.TextContent(
                type="text",
                text=f"🏥 **System Health Report**\\n\\n"
                     f"**Overall Status:** {status_emoji} {health.get('status', 'Unknown').title()}\\n"
                     f"**Timestamp:** {health.get('timestamp', 'N/A')}\\n\\n"
                     f"Detailed health information available through analytics service."
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ **Health Check Error**\\n\\n"
                     f"Failed to retrieve system health: {str(e)}"
            )]
    
    async def _handle_unknown_tool(self, name: str) -> List[types.TextContent]:
        """Handle unknown tool requests"""
        available_tools = ["test_connection"]
        if self.services_available.get("course_creation", False):
            available_tools.append("create_intelligent_course")
        if self.services_available.get("analytics", False):
            available_tools.append("get_system_health")
        
        return [types.TextContent(
            type="text",
            text=f"❌ **Unknown Tool: {name}**\\n\\n"
                 f"**Available Tools:**\\n" +
                 "\\n".join(f"- `{tool}`" for tool in available_tools) +
                 f"\\n\\n💡 Tool availability depends on service status. "
                 f"Use `test_connection` to check what's available."
        )]
    
    async def run(self):
        """Run the robust MCP server"""
        logger.info("Starting Robust MoodleMCP Server...")
        
        try:
            init_options = InitializationOptions(
                server_name="robust-moodle-course-creator",
                server_version="3.0.0",
                capabilities={}
            )
            
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, init_options)
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            logger.info("Robust MoodleMCP Server shutdown complete")


async def main():
    """Main entry point"""
    try:
        server = RobustMoodleMCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"Fatal error starting robust MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())