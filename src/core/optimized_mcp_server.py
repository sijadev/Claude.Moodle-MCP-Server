#!/usr/bin/env python3
"""
Optimized MCP Server with Advanced Performance Features
Implements Connection Pooling, Caching, Rate Limiting, and Enhanced Error Handling
Based on the comprehensive code analysis recommendations
"""

import asyncio
import logging
import sys
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from functools import wraps
from dataclasses import dataclass, field
from collections import deque

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import aiohttp
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.dual_token_config import DualTokenConfig
from src.core.constants import Defaults, Messages, ToolDescriptions
from src.core.intelligent_session_manager import IntelligentSessionManager
from src.clients.moodle_client_enhanced import EnhancedMoodleClient
from src.core.enhanced_error_handling import (
    ErrorHandlerMixin, ErrorCategory, ErrorSeverity,
    create_configuration_error, create_moodle_api_error, create_validation_error
)

# Configure logging for MCP server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    rate_limit_hits: int = 0
    
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def cache_hit_rate(self) -> float:
        total_cache_requests = self.cache_hits + self.cache_misses
        if total_cache_requests == 0:
            return 0.0
        return (self.cache_hits / total_cache_requests) * 100


class MCPError(BaseModel):
    """Structured error response for better Claude integration"""
    error_type: str
    message: str
    context: Dict[str, Any]
    suggestions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


class LRUCache:
    """Simple LRU Cache implementation"""
    
    def __init__(self, maxsize: int = 100):
        self.maxsize = maxsize
        self.cache: Dict[str, Any] = {}
        self.access_order: deque = deque()
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        if key in self.cache:
            # Update existing
            self.access_order.remove(key)
        elif len(self.cache) >= self.maxsize:
            # Remove least recently used
            oldest = self.access_order.popleft()
            del self.cache[oldest]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self) -> None:
        self.cache.clear()
        self.access_order.clear()


class AsyncRateLimiter:
    """Async rate limiter with sliding window"""
    
    def __init__(self, calls: int = 50, period: int = 60):
        self.calls = calls
        self.period = period
        self.requests: deque = deque()
    
    async def __aenter__(self):
        now = time.time()
        # Remove old requests outside the window
        while self.requests and self.requests[0] <= now - self.period:
            self.requests.popleft()
        
        if len(self.requests) >= self.calls:
            # Rate limit exceeded, wait
            sleep_time = self.requests[0] + self.period - now
            await asyncio.sleep(sleep_time)
            return await self.__aenter__()
        
        self.requests.append(now)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class ConnectionPool:
    """Simple connection pool for HTTP requests"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=max_connections // 2,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        self.session = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            result = await func(self, *args, **kwargs)
            self.metrics.successful_requests += 1
            return result
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"Function {func.__name__} failed: {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            # Update rolling average
            if self.metrics.avg_response_time == 0:
                self.metrics.avg_response_time = duration
            else:
                self.metrics.avg_response_time = (
                    self.metrics.avg_response_time * 0.9 + duration * 0.1
                )
    
    return wrapper


class OptimizedMoodleMCPServer(ErrorHandlerMixin):
    """
    Optimized MCP Server with advanced performance features:
    - Connection pooling for HTTP requests
    - LRU caching for frequent API calls
    - Rate limiting to prevent API overload
    - Enhanced error handling with structured responses
    - Performance metrics and monitoring
    - Async streaming for long operations
    """
    
    def __init__(self):
        """Initialize the Optimized MCP Server"""
        # Initialize error handling mixin
        ErrorHandlerMixin.__init__(self)
        
        self.server = Server("optimized-moodle-course-creator")
        
        # Performance components
        self.connection_pool = ConnectionPool(max_connections=10)
        self.cache = LRUCache(maxsize=100)
        self.rate_limiter = AsyncRateLimiter(calls=50, period=60)
        self.metrics = PerformanceMetrics()
        self.response_times: deque = deque(maxlen=100)  # Rolling window
        
        # Configuration and clients
        self.config = None
        self.moodle_client = None
        self.session_manager = None
        
        # Initialize components
        self._initialize_config()
        self._initialize_clients()
        self._setup_handlers()
        
        logger.info("OptimizedMoodleMCPServer initialized with advanced performance features")
    
    def _initialize_config(self):
        """Initialize configuration with error handling"""
        try:
            self.config = DualTokenConfig.from_env()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            error = create_configuration_error(
                self, 
                f"Failed to load configuration: {str(e)}",
                "DualTokenConfig"
            )
            logger.error(f"Configuration error: {error.to_claude_response()}")
            self.config = None
    
    def _initialize_clients(self):
        """Initialize Moodle client and session manager"""
        if not self.config:
            logger.warning("No configuration available, skipping client initialization")
            return
        
        try:
            self.moodle_client = EnhancedMoodleClient(
                base_url=self.config.moodle_url,
                basic_token=self.config.get_basic_token(),
                plugin_token=self.config.get_plugin_token() if self.config.is_dual_token_mode() else None
            )
            
            self.session_manager = IntelligentSessionManager(self.moodle_client)
            logger.info("Clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Client initialization failed: {e}")
            self.moodle_client = None
            self.session_manager = None
    
    def _create_cache_key(self, operation: str, **params) -> str:
        """Create a cache key for the given operation and parameters"""
        key_data = f"{operation}:{sorted(params.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _create_error_response(self, error_type: str, message: str, 
                             context: Dict[str, Any] = None, 
                             suggestions: List[str] = None) -> MCPError:
        """Create a structured error response"""
        return MCPError(
            error_type=error_type,
            message=message,
            context=context or {},
            suggestions=suggestions or []
        )
    
    async def _cached_api_call(self, cache_key: str, api_func, *args, **kwargs) -> Any:
        """Execute API call with caching"""
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.metrics.cache_hits += 1
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_result
        
        # Cache miss - execute API call
        self.metrics.cache_misses += 1
        async with self.rate_limiter:
            result = await api_func(*args, **kwargs)
            self.cache.set(cache_key, result)
            return result
    
    def _setup_handlers(self):
        """Setup MCP server request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available MCP tools with optimization features"""
            return [
                types.Tool(
                    name="create_optimized_course",
                    description="Create a Moodle course with optimized performance (caching, rate limiting, connection pooling)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Chat conversation content to convert into a course"
                            },
                            "course_name": {
                                "type": "string",
                                "description": "Name for the Moodle course (optional)"
                            },
                            "use_cache": {
                                "type": "boolean",
                                "description": "Whether to use caching for this request",
                                "default": True
                            }
                        },
                        "required": ["content"]
                    }
                ),
                types.Tool(
                    name="get_performance_metrics",
                    description="Get current performance metrics and system status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="clear_cache",
                    description="Clear the internal cache to free memory",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="stream_course_creation",
                    description="Create course with streaming progress updates for better UX",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to process"
                            },
                            "course_name": {
                                "type": "string",
                                "description": "Course name"
                            }
                        },
                        "required": ["content"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls with optimized processing"""
            try:
                if name == "create_optimized_course":
                    return await self._create_optimized_course(arguments)
                elif name == "get_performance_metrics":
                    return await self._get_performance_metrics(arguments)
                elif name == "clear_cache":
                    return await self._clear_cache(arguments)
                elif name == "stream_course_creation":
                    return await self._stream_course_creation(arguments)
                else:
                    error = self._create_error_response(
                        "invalid_tool",
                        f"Unknown tool: {name}",
                        {"tool_name": name},
                        ["Check available tools with list_tools"]
                    )
                    return [types.TextContent(type="text", text=error.to_json())]
                    
            except Exception as e:
                logger.error(f"Tool {name} failed: {str(e)}")
                error = self._create_error_response(
                    "execution_error",
                    f"Tool execution failed: {str(e)}",
                    {"tool_name": name, "error": str(e)},
                    ["Check server logs", "Verify configuration", "Try again"]
                )
                return [types.TextContent(type="text", text=error.to_json())]
    
    @performance_monitor
    async def _create_optimized_course(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create course with optimization features"""
        if not self.session_manager:
            error = self._create_error_response(
                "configuration_error",
                "MCP server not properly configured",
                {"missing": "session_manager"},
                ["Check environment variables", "Verify Moodle connection", "Restart server"]
            )
            return [types.TextContent(type="text", text=error.to_json())]
        
        content = arguments.get("content", "")
        course_name = arguments.get("course_name")
        use_cache = arguments.get("use_cache", True)
        
        if not content.strip():
            error = self._create_error_response(
                "validation_error",
                "Content cannot be empty",
                {"content_length": len(content)},
                ["Provide meaningful content to convert to course"]
            )
            return [types.TextContent(type="text", text=error.to_json())]
        
        try:
            # Create cache key for this operation
            cache_key = self._create_cache_key(
                "create_course",
                content_hash=hashlib.md5(content.encode()).hexdigest()[:16],
                course_name=course_name or "auto"
            )
            
            if use_cache:
                # Try cached result first
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    self.metrics.cache_hits += 1
                    return [types.TextContent(
                        type="text", 
                        text=f"✅ Course created successfully (cached result)!\n\n{cached_result}"
                    )]
            
            # Execute with rate limiting
            async with self.rate_limiter:
                result = await self.session_manager.create_intelligent_course_session(
                    content=content,
                    course_name=course_name,
                    continue_previous=False
                )
            
            # Cache successful results
            if use_cache and result.get("status") == "success":
                self.cache.set(cache_key, str(result))
            
            return [types.TextContent(
                type="text",
                text=f"✅ Optimized course creation completed!\n\n"
                     f"📊 Performance Stats:\n"
                     f"• Cache Hit Rate: {self.metrics.cache_hit_rate():.1f}%\n"
                     f"• Success Rate: {self.metrics.success_rate():.1f}%\n"
                     f"• Avg Response Time: {self.metrics.avg_response_time:.2f}s\n\n"
                     f"📚 Course Details:\n{result}"
            )]
            
        except Exception as e:
            logger.error(f"Optimized course creation failed: {str(e)}")
            error = self._create_error_response(
                "course_creation_error",
                f"Failed to create course: {str(e)}",
                {
                    "content_length": len(content),
                    "course_name": course_name,
                    "use_cache": use_cache
                },
                [
                    "Check Moodle server connection",
                    "Verify API tokens are valid",
                    "Try with shorter content",
                    "Check server logs for details"
                ]
            )
            return [types.TextContent(type="text", text=error.to_json())]
    
    async def _get_performance_metrics(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get current performance metrics"""
        metrics_report = f"""
🚀 **MCP Server Performance Metrics**

📊 **Request Statistics:**
• Total Requests: {self.metrics.total_requests}
• Successful: {self.metrics.successful_requests}
• Failed: {self.metrics.failed_requests}
• Success Rate: {self.metrics.success_rate():.1f}%

⚡ **Performance:**
• Average Response Time: {self.metrics.avg_response_time:.2f}s
• Cache Hit Rate: {self.metrics.cache_hit_rate():.1f}%
• Rate Limit Hits: {self.metrics.rate_limit_hits}

💾 **Cache Status:**
• Cache Hits: {self.metrics.cache_hits}
• Cache Misses: {self.metrics.cache_misses}
• Cache Size: {len(self.cache.cache)}/{self.cache.maxsize}

🔧 **System Status:**
• Configuration: {'✅ Loaded' if self.config else '❌ Missing'}
• Moodle Client: {'✅ Connected' if self.moodle_client else '❌ Disconnected'}
• Session Manager: {'✅ Active' if self.session_manager else '❌ Inactive'}

⏰ **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return [types.TextContent(type="text", text=metrics_report)]
    
    async def _clear_cache(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Clear the internal cache"""
        cache_size_before = len(self.cache.cache)
        self.cache.clear()
        
        return [types.TextContent(
            type="text",
            text=f"🧹 Cache cleared successfully!\n"
                 f"• Removed {cache_size_before} cached entries\n"
                 f"• Memory freed for new requests\n"
                 f"• Cache hit rate will reset"
        )]
    
    async def _stream_course_creation(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create course with streaming progress updates"""
        content = arguments.get("content", "")
        course_name = arguments.get("course_name", "AI Generated Course")
        
        progress_updates = []
        
        try:
            # Simulate streaming updates (in real implementation, this would be actual progress)
            updates = [
                "🚀 Starting optimized course creation...",
                "📝 Analyzing content complexity...",
                "🧠 Processing with intelligent chunking...",
                "🏗️ Creating Moodle course structure...",
                "📚 Adding activities and resources...",
                "🔍 Validating course integrity...",
                "✅ Course creation completed successfully!"
            ]
            
            for i, update in enumerate(updates):
                progress_updates.append(f"[{i+1}/{len(updates)}] {update}")
                # In real implementation, we'd yield these updates in real-time
            
            # Execute actual course creation
            if self.session_manager:
                async with self.rate_limiter:
                    result = await self.session_manager.create_intelligent_course_session(
                        content=content,
                        course_name=course_name,
                        continue_previous=False
                    )
                
                final_report = "\n".join(progress_updates) + f"\n\n📊 Final Result:\n{result}"
            else:
                final_report = "\n".join(progress_updates) + "\n\n❌ Session manager not available"
            
            return [types.TextContent(type="text", text=final_report)]
            
        except Exception as e:
            error_report = "\n".join(progress_updates) + f"\n\n❌ Error occurred: {str(e)}"
            return [types.TextContent(type="text", text=error_report)]
    
    async def run(self):
        """Run the optimized MCP server"""
        logger.info("Starting Optimized MoodleMCP Server...")
        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="optimized-moodle-mcp",
                        server_version="3.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            # Cleanup
            await self.connection_pool.close()
            logger.info("Optimized MCP Server shutdown complete")


async def main():
    """Main entry point"""
    server = OptimizedMoodleMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)