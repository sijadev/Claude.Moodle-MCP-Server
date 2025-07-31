#!/usr/bin/env python3
"""
Simple MCP Server for testing Claude Desktop integration
This is a minimal server to ensure basic connectivity works
"""

import asyncio
import logging
import sys
import os
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class SimpleMoodleMCPServer:
    """Simple MCP server for testing connectivity"""
    
    def __init__(self):
        self.server = Server("simple-moodle-test")
        self._setup_handlers()
        logger.info("Simple MCP Server initialized successfully")
    
    def _setup_handlers(self):
        """Setup basic MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="test_connection",
                    description="Test MCP server connection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Test message",
                                "default": "Hello from MCP!"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            logger.info(f"Tool called: {name}")
            
            if name == "test_connection":
                message = arguments.get("message", "Hello from MCP!")
                return [types.TextContent(
                    type="text",
                    text=f"✅ **MCP Connection Test Successful!**\n\n"
                         f"Server: Simple Moodle MCP Server\n"
                         f"Message: {message}\n"
                         f"Status: Connected and working\n\n"
                         f"🎉 The refactored architecture server is ready!"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}"
                )]
    
    async def run(self):
        """Run the simple MCP server"""
        logger.info("Starting Simple MCP Server...")
        
        try:
            init_options = InitializationOptions(
                server_name="simple-moodle-test",
                server_version="1.0.0",
                capabilities={}
            )
            
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, init_options)
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            logger.info("Simple MCP Server shutdown complete")


async def main():
    """Main entry point"""
    try:
        server = SimpleMoodleMCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())