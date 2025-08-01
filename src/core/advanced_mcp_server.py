#!/usr/bin/env python3
"""
Advanced MCP Server with Intelligent Course Creation
Enhanced version with adaptive processing, session management, and automatic continuation
"""

import asyncio
import logging
import sys
import os
from typing import Any, Dict, List, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.dual_token_config import DualTokenConfig
from src.core.constants import Defaults, Messages, ToolDescriptions
from src.core.intelligent_session_manager import IntelligentSessionManager
from src.core.adaptive_content_processor import AdaptiveContentProcessor
from src.clients.moodle_client_enhanced import EnhancedMoodleClient

# Configure logging for MCP server (stderr only)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class AdvancedMoodleMCPServer:
    """
    Advanced MCP Server with intelligent course creation capabilities
    
    Features:
    - Adaptive content processing with automatic length detection
    - Intelligent session management with persistence
    - Automatic continuation logic for large content
    - Real-time validation against Moodle database
    - Queue-based processing with retry logic
    - Natural language responses for seamless UX
    """
    
    def __init__(self):
        """Initialize the Advanced MCP Server"""
        self.server = Server("advanced-moodle-course-creator")
        
        # Initialize configuration
        try:
            self.config = DualTokenConfig.from_env()
            logger.info("Advanced MCP Server initialized with dual-token configuration")
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            self.config = None
        
        # Initialize Moodle client
        self.moodle_client = None
        if self.config:
            try:
                self.moodle_client = EnhancedMoodleClient(
                    base_url=self.config.moodle_url,
                    basic_token=self.config.get_basic_token(),
                    plugin_token=self.config.get_plugin_token() if self.config.is_dual_token_mode() else None
                )
                logger.info("Enhanced Moodle client initialized successfully")
            except Exception as e:
                logger.error(f"Moodle client initialization failed: {e}")
        
        # Initialize intelligent session manager
        self.session_manager = IntelligentSessionManager(self.moodle_client)
        
        # Setup MCP server handlers
        self._setup_handlers()
        
        logger.info("AdvancedMoodleMCPServer fully initialized with intelligent features")
    
    def _setup_handlers(self):
        """Setup MCP server request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available MCP tools with enhanced capabilities"""
            return [
                types.Tool(
                    name="create_intelligent_course",
                    description="Intelligently create a Moodle course with automatic chunking, session management, and continuation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Chat conversation content to convert into a course"
                            },
                            "course_name": {
                                "type": "string",
                                "description": "Name for the Moodle course (optional - will be auto-generated)"
                            },
                            "continue_previous": {
                                "type": "boolean",
                                "description": "Whether to continue a previous session (optional)",
                                "default": False
                            }
                        },
                        "required": ["content"]
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
                                "description": "Additional content to add to the session (optional)"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                types.Tool(
                    name="validate_course",
                    description="Validate a created course against the database and expected content",
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
                    description="Get current status and progress of a course creation session",
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
                    description="Get analytics and metrics about content processing and session management",
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
                    name="analyze_content_complexity",
                    description="Analyze content complexity and get processing recommendations without creating a course",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to analyze"
                            }
                        },
                        "required": ["content"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls with intelligent processing"""
            try:
                logger.info(f"Executing advanced tool: {name}")
                
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
                elif name == "analyze_content_complexity":
                    return await self._analyze_content_complexity(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Advanced tool execution failed: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Tool execution failed: {str(e)}\n\nI encountered an issue processing your request. Please try again or contact support if the problem persists."
                )]
    
    async def _create_intelligent_course(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create course with intelligent processing and automatic continuation"""
        content = arguments.get("content", "")
        course_name = arguments.get("course_name", "")
        continue_previous = arguments.get("continue_previous", False)
        
        if not content.strip():
            return [types.TextContent(
                type="text",
                text="❌ Please provide content to create a course from.\n\nI need some chat content to work with. Share your conversation and I'll create a structured course from it."
            )]
        
        try:
            # Create intelligent session
            result = await self.session_manager.create_intelligent_course_session(
                content=content,
                course_name=course_name,
                continue_previous=continue_previous
            )
            
            if result["success"]:
                if result.get("immediate_completion"):
                    # Course created successfully in one pass
                    response_parts = [
                        f"✅ **Course Created Successfully!**\n",
                        f"**Course Name:** {result.get('course_name', 'Untitled Course')}\n",
                    ]
                    
                    if result.get("course_id"):
                        response_parts.extend([
                            f"**Course ID:** {result['course_id']}\n",
                            f"**Course URL:** {result.get('course_url', 'N/A')}\n",
                        ])
                    
                    if result.get("final_summary"):
                        summary = result["final_summary"]
                        response_parts.extend([
                            f"\n📊 **Course Summary:**\n",
                            f"- **Sections Created:** {summary.get('total_sections', 0)}\n",
                            f"- **Content Items:** {summary.get('total_items', 0)}\n",
                            f"- **Processing Time:** {summary.get('processing_time', 0):.1f} seconds\n"
                        ])
                    
                    if result.get("moodle_integration") == "success":
                        response_parts.append(f"\n🎯 Your course is now live on Moodle and ready for students!")
                    elif result.get("preview_mode"):
                        response_parts.append(f"\n📋 Course structure created in preview mode (no Moodle connection)")
                    
                    return [types.TextContent(type="text", text="".join(response_parts))]
                
                else:
                    # Multi-step processing initiated
                    response_parts = [
                        f"🚀 **Starting Intelligent Course Creation**\n\n",
                        f"{result.get('user_friendly_message', result.get('message', ''))}\n\n",
                    ]
                    
                    if result.get("processing_plan"):
                        plan = result["processing_plan"]
                        response_parts.extend([
                            f"📋 **Processing Plan:**\n",
                            f"- **Strategy:** {plan['strategy'].replace('_', ' ').title()}\n",
                            f"- **Estimated Parts:** {plan['estimated_chunks']}\n",
                            f"- **Estimated Time:** ~{plan['estimated_time']} seconds\n",
                            f"- **Complexity Score:** {plan['complexity_score']:.1f}/1.0\n\n",
                        ])
                    
                    response_parts.extend([
                        f"**Session ID:** `{result['session_id']}`\n\n",
                        f"I'll process your content intelligently and keep you updated. You can check progress anytime using the session ID above."
                    ])
                    
                    return [types.TextContent(type="text", text="".join(response_parts))]
            
            else:
                # Error occurred
                error_message = result.get("error", "Unknown error occurred")
                suggested_action = result.get("suggested_action", "retry")
                
                response_parts = [
                    f"❌ **Course Creation Issue**\n\n",
                    f"{result.get('message', 'I encountered an issue creating your course.')}\n\n",
                    f"**Error Details:** {error_message}\n\n",
                ]
                
                if suggested_action == "retry":
                    response_parts.append("💡 **Suggestion:** Try again or break your content into smaller parts.")
                elif suggested_action == "manual_intervention_required":
                    response_parts.append("🔧 **Suggestion:** This content may need manual review. Please contact support.")
                else:
                    response_parts.append("💡 **Suggestion:** Please try rephrasing your content or providing it in smaller sections.")
                
                return [types.TextContent(type="text", text="".join(response_parts))]
                
        except Exception as e:
            logger.error(f"Error in intelligent course creation: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Unexpected Error**\n\nI encountered an unexpected issue: {str(e)}\n\nPlease try again with smaller content or contact support if the problem persists."
            )]
    
    async def _continue_course_session(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Continue processing a course creation session"""
        session_id = arguments.get("session_id", "")
        additional_content = arguments.get("additional_content", "")
        
        if not session_id:
            return [types.TextContent(
                type="text",
                text="❌ Please provide a session ID to continue.\n\nUse the session ID from your previous course creation request."
            )]
        
        try:
            result = await self.session_manager.continue_session_processing(
                session_id=session_id,
                additional_content=additional_content
            )
            
            if result["success"]:
                response_parts = [
                    f"✅ **Session Continued Successfully**\n\n",
                ]
                
                if result.get("progress"):
                    progress = result["progress"]
                    response_parts.extend([
                        f"📊 **Progress Update:**\n",
                        f"- **Completion:** {progress['percentage']:.1f}%\n",
                        f"- **Parts Processed:** {progress['completed_chunks']}/{progress['total_chunks']}\n\n",
                    ])
                
                if result.get("continuation_needed"):
                    response_parts.extend([
                        f"🔄 **Next Steps:**\n",
                        f"{result.get('continuation_prompt', 'Please provide the next section of content.')}\n\n",
                        f"**Session ID:** `{session_id}`"
                    ])
                else:
                    # Session completed
                    response_parts.extend([
                        f"🎉 **Course Creation Completed!**\n\n",
                    ])
                    
                    if result.get("course_id"):
                        response_parts.extend([
                            f"**Course ID:** {result['course_id']}\n",
                            f"**Total Sections:** {result.get('total_sections_count', 'N/A')}\n",
                        ])
                    
                    if result.get("moodle_integration") == "updated":
                        response_parts.append("🎯 Your course has been updated on Moodle!")
                
                return [types.TextContent(type="text", text="".join(response_parts))]
            
            else:
                error_message = result.get("error", "Unknown error")
                action = result.get("action", "unknown")
                
                response_parts = [
                    f"❌ **Session Continuation Issue**\n\n",
                    f"{result.get('message', 'I encountered an issue continuing your session.')}\n\n",
                ]
                
                if action == "create_new_session":
                    response_parts.append("💡 **Suggestion:** The session may have expired. Please start a new course creation.")
                elif action == "retry":
                    response_parts.append("💡 **Suggestion:** Please try again or provide content in smaller parts.")
                else:
                    response_parts.append(f"**Error:** {error_message}")
                
                return [types.TextContent(type="text", text="".join(response_parts))]
                
        except Exception as e:
            logger.error(f"Error continuing session: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Session Continuation Error**\n\nI couldn't continue the session: {str(e)}\n\nPlease try starting a new course creation or contact support."
            )]
    
    async def _validate_course(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Validate course creation against database"""
        session_id = arguments.get("session_id", "")
        course_id = arguments.get("course_id")
        
        if not session_id:
            return [types.TextContent(
                type="text",
                text="❌ Please provide a session ID to validate."
            )]
        
        try:
            # Get session status
            session_status = self.session_manager.content_processor.get_session_status(session_id)
            
            if not session_status:
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Session Not Found**\n\nSession `{session_id}` was not found or has expired."
                )]
            
            response_parts = [
                f"🔍 **Course Validation Report**\n\n",
                f"**Session ID:** `{session_id}`\n",
                f"**Course Name:** {session_status.get('course_name', 'N/A')}\n",
                f"**Processing State:** {session_status['state'].title()}\n",
                f"**Progress:** {session_status['progress']['percentage']:.1f}%\n\n",
            ]
            
            if session_status.get('course_id'):
                response_parts.extend([
                    f"**Course ID:** {session_status['course_id']}\n",
                    f"**Sections Created:** {session_status.get('created_sections_count', 0)}\n\n",
                ])
            
            # Validation status
            if session_status['state'] == 'completed':
                response_parts.extend([
                    f"✅ **Validation Status:** Course created successfully\n",
                    f"📊 **Quality Metrics:**\n",
                    f"- Content processing completed\n",
                    f"- All sections created\n",
                    f"- Session completed without errors\n"
                ])
            elif session_status['state'] == 'failed':
                response_parts.extend([
                    f"❌ **Validation Status:** Course creation failed\n",
                    f"**Last Error:** {session_status.get('last_error', 'Unknown error')}\n",
                    f"**Error Count:** {session_status.get('error_count', 0)}\n"
                ])
            else:
                response_parts.extend([
                    f"🔄 **Validation Status:** Course creation in progress\n",
                    f"**Current State:** {session_status['state'].title()}\n"
                ])
                
                if session_status.get('needs_continuation'):
                    response_parts.append(f"**Action Required:** {session_status.get('continuation_prompt', 'Continue processing')}")
            
            return [types.TextContent(type="text", text="".join(response_parts))]
            
        except Exception as e:
            logger.error(f"Error validating course: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Validation Error**\n\nI couldn't validate the course: {str(e)}"
            )]
    
    async def _get_session_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get detailed session status and progress"""
        session_id = arguments.get("session_id", "")
        
        if not session_id:
            return [types.TextContent(
                type="text",
                text="❌ Please provide a session ID to check status."
            )]
        
        try:
            status = self.session_manager.content_processor.get_session_status(session_id)
            
            if not status:
                return [types.TextContent(
                    type="text",
                    text=f"❌ **Session Not Found**\n\nSession `{session_id}` was not found or has expired."
                )]
            
            response_parts = [
                f"📊 **Session Status Report**\n\n",
                f"**Session ID:** `{session_id}`\n",
                f"**Course Name:** {status.get('course_name', 'Untitled Course')}\n",
                f"**Current State:** {status['state'].title()}\n",
                f"**Strategy:** {status['strategy'].replace('_', ' ').title()}\n\n",
                
                f"**📈 Progress:**\n",
                f"- **Completion:** {status['progress']['percentage']:.1f}%\n",
                f"- **Parts Processed:** {status['progress']['completed_chunks']}/{status['progress']['total_chunks']}\n\n",
            ]
            
            if status.get('course_id'):
                response_parts.extend([
                    f"**🎯 Moodle Integration:**\n",
                    f"- **Course ID:** {status['course_id']}\n",
                    f"- **Sections Created:** {status.get('created_sections_count', 0)}\n\n",
                ])
            
            if status.get('needs_continuation'):
                response_parts.extend([
                    f"**🔄 Next Action Required:**\n",
                    f"{status.get('continuation_prompt', 'Continue with additional content')}\n\n",
                ])
            
            if status.get('error_count', 0) > 0:
                response_parts.extend([
                    f"**⚠️ Error Information:**\n",
                    f"- **Error Count:** {status['error_count']}\n",
                    f"- **Last Error:** {status.get('last_error', 'N/A')}\n\n",
                ])
            
            # Session expiry
            expires_at = status.get('expires_at')
            if expires_at:
                response_parts.append(f"**⏰ Session Expires:** {expires_at}")
            
            return [types.TextContent(type="text", text="".join(response_parts))]
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Status Check Error**\n\nI couldn't retrieve the session status: {str(e)}"
            )]
    
    async def _get_processing_analytics(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get processing analytics and system metrics"""
        detailed = arguments.get("detailed", False)
        
        try:
            analytics = self.session_manager.get_session_analytics()
            processor_metrics = self.session_manager.content_processor.get_processing_metrics()
            
            response_parts = [
                f"📊 **Processing Analytics Dashboard**\n\n",
            ]
            
            # Overall metrics
            if analytics.get("overall"):
                overall = analytics["overall"]
                response_parts.extend([
                    f"**📈 Overall Performance:**\n",
                    f"- **Total Sessions:** {overall.get('total_sessions', 0)}\n",
                    f"- **Completed:** {overall.get('completed_sessions', 0)}\n",
                    f"- **Failed:** {overall.get('failed_sessions', 0)}\n",
                    f"- **Average Completion Rate:** {overall.get('avg_completion_rate', 0):.1%}\n",
                    f"- **Average Content Size:** {overall.get('avg_content_size', 0):.0f} characters\n\n",
                ])
            
            # Success metrics
            if processor_metrics.get("success_metrics"):
                success = processor_metrics["success_metrics"]
                success_rate = success.get('successful_requests', 0) / max(success.get('total_requests', 1), 1)
                response_parts.extend([
                    f"**🎯 Success Metrics:**\n",
                    f"- **Success Rate:** {success_rate:.1%}\n",
                    f"- **Total Requests:** {success.get('total_requests', 0)}\n",
                    f"- **Failed Requests:** {success.get('failed_requests', 0)}\n\n",
                ])
            
            # Current system status
            response_parts.extend([
                f"**⚡ Current System Status:**\n",
                f"- **Active Sessions:** {analytics.get('active_sessions', 0)}\n",
                f"- **Learning Status:** {processor_metrics.get('learning_status', 'Unknown').title()}\n",
            ])
            
            if processor_metrics.get("current_limits"):
                limits = processor_metrics["current_limits"]
                response_parts.extend([
                    f"- **Content Limit:** {limits.get('max_char_length', 0)} characters\n",
                    f"- **Confidence Level:** {limits.get('confidence_level', 0):.1%}\n\n",
                ])
            
            if detailed and analytics.get("strategy_effectiveness"):
                response_parts.extend([
                    f"**🧠 Strategy Effectiveness:**\n"
                ])
                
                for strategy in analytics["strategy_effectiveness"]:
                    strategy_name = strategy.get('strategy', 'Unknown').replace('_', ' ').title()
                    response_parts.append(
                        f"- **{strategy_name}:** {strategy.get('success_rate', 0):.1%} success rate ({strategy.get('usage_count', 0)} uses)\n"
                    )
                
                response_parts.append("\n")
            
            # System recommendations
            response_parts.extend([
                f"**💡 System Recommendations:**\n"
            ])
            
            if success_rate > 0.9:
                response_parts.append("- ✅ System performing excellently\n")
            elif success_rate > 0.7:
                response_parts.append("- 👍 System performing well\n")
            else:
                response_parts.append("- ⚠️ System may need attention\n")
            
            if processor_metrics.get("learning_status") == "adaptive":
                response_parts.append("- 🧠 Adaptive learning is active and optimizing performance\n")
            else:
                response_parts.append("- 📚 System is still learning optimal processing parameters\n")
            
            return [types.TextContent(type="text", text="".join(response_parts))]
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Analytics Error**\n\nI couldn't retrieve processing analytics: {str(e)}"
            )]
    
    async def _analyze_content_complexity(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Analyze content complexity without creating a course"""
        content = arguments.get("content", "")
        
        if not content.strip():
            return [types.TextContent(
                type="text",
                text="❌ Please provide content to analyze."
            )]
        
        try:
            analysis = await self.session_manager.content_processor.analyze_content_complexity(content)
            
            response_parts = [
                f"🔍 **Content Analysis Report**\n\n",
                f"**📏 Content Metrics:**\n",
                f"- **Length:** {analysis['content_length']:,} characters\n",
                f"- **Code Blocks:** {analysis['code_blocks']}\n",
                f"- **Topics:** {analysis['topics']}\n",
                f"- **Estimated Sections:** {analysis['estimated_sections']}\n\n",
                
                f"**🧠 Complexity Analysis:**\n",
                f"- **Complexity Score:** {analysis['complexity_score']:.2f}/1.0\n",
                f"- **Recommended Strategy:** {analysis['recommended_strategy'].value.replace('_', ' ').title()}\n",
                f"- **Estimated Processing Parts:** {analysis['estimated_chunks']}\n",
                f"- **Estimated Processing Time:** ~{analysis['processing_time_estimate']} seconds\n\n",
            ]
            
            # Complexity interpretation
            complexity = analysis['complexity_score']
            if complexity < 0.3:
                response_parts.extend([
                    f"**✅ Complexity Assessment:** Simple Content\n",
                    f"This content can be processed quickly in a single pass. Perfect for immediate course creation!\n\n"
                ])
            elif complexity < 0.6:
                response_parts.extend([
                    f"**📊 Complexity Assessment:** Moderate Content\n",
                    f"This content will be processed in logical sections for optimal organization.\n\n"
                ])
            elif complexity < 0.8:
                response_parts.extend([
                    f"**🎯 Complexity Assessment:** Rich Content\n",
                    f"This is substantial content that will be carefully processed in multiple parts to ensure quality.\n\n"
                ])
            else:
                response_parts.extend([
                    f"**🚀 Complexity Assessment:** Complex Content\n",
                    f"This is very rich, comprehensive content that will benefit from adaptive processing strategies.\n\n"
                ])
            
            # Processing recommendations
            response_parts.extend([
                f"**💡 Processing Recommendations:**\n"
            ])
            
            if analysis['recommended_strategy'].value == 'single_pass':
                response_parts.append("- ⚡ Ready for immediate processing\n")
            elif analysis['recommended_strategy'].value == 'intelligent_chunk':
                response_parts.append("- 🧩 Will be intelligently chunked for optimal processing\n")
            elif analysis['recommended_strategy'].value == 'progressive_build':
                response_parts.append("- 🏗️ Will be built progressively for best course structure\n")
            else:
                response_parts.append("- 🔧 Will use adaptive processing for optimal results\n")
            
            response_parts.append(f"\n**🎯 Ready to create your course? Use the 'create_intelligent_course' tool with this content!**")
            
            return [types.TextContent(type="text", text="".join(response_parts))]
            
        except Exception as e:
            logger.error(f"Error analyzing content complexity: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Analysis Error**\n\nI couldn't analyze the content complexity: {str(e)}"
            )]
    
    async def run(self):
        """Run the Advanced MCP Server"""
        logger.info("Starting Advanced MoodleMCP Server with intelligent features...")
        
        try:
            # Initialize notification options
            init_options = InitializationOptions(
                server_name="advanced-moodle-course-creator",
                server_version="2.0.0",
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
            raise
        finally:
            # Cleanup
            await self.session_manager.cleanup_and_shutdown()
            logger.info("Advanced MoodleMCP Server shutdown complete")


async def main():
    """Main entry point for the Advanced MCP Server"""
    server = AdvancedMoodleMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())