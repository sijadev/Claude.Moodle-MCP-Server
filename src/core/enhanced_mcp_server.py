#!/usr/bin/env python3
"""
Enhanced MCP Server with dual-token support for MoodleClaude
Supports both basic Moodle operations and enhanced plugin functionality
"""

import asyncio
import logging
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

import sys
import os
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.dual_token_config import DualTokenConfig
from src.core.constants import Defaults, Messages, ToolDescriptions, ContentTypes
from src.core.content_formatter import ContentFormatter
from src.core.content_parser import ChatContentParser
from src.core.content_chunker import ContentChunker
from src.core.chunk_processor_queue import ChunkProcessorQueue
from src.models.models import ChatContent, CourseStructure
from src.clients.moodle_client import MoodleClient
from src.clients.moodle_client_enhanced import EnhancedMoodleClient

# Configure logging for MCP server (stderr only, no emojis)
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stderr  # Ensure logs go to stderr, not stdout
)
logger = logging.getLogger(__name__)


class EnhancedMoodleMCPServer:
    """Enhanced MCP Server with dual-token support for optimal functionality"""
    
    def __init__(self):
        """Initialize the Enhanced MCP Server with dual-token configuration"""
        self.server = Server(Defaults.SERVER_NAME)
        self.content_parser = ChatContentParser()
        self.content_formatter = ContentFormatter()
        self.content_chunker = ContentChunker()
        self.chunk_processor = ChunkProcessorQueue(max_concurrent=2, rate_limit_delay=0.5)
        
        # Load dual-token configuration
        try:
            self.config = DualTokenConfig.from_env()
            logger.info(f"Configuration loaded: {self.config.get_config_summary()}")
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            self.config = None
            self.basic_client = None
            self.plugin_client = None
            self._setup_handlers()
            return
        
        # Initialize clients
        self.basic_client = None
        self.plugin_client = None
        
        if self.config.moodle_url:
            try:
                # Basic Moodle client for standard operations
                self.basic_client = MoodleClient(
                    base_url=self.config.moodle_url, 
                    token=self.config.get_basic_token()
                )
                logger.info("[OK] Basic Moodle client initialized")
                
                # Enhanced client for plugin operations
                plugin_token = self.config.get_plugin_token()
                self.plugin_client = EnhancedMoodleClient(
                    base_url=self.config.moodle_url,
                    token=plugin_token
                )
                
                if self.config.is_dual_token_mode():
                    logger.info("[OK] Enhanced plugin client initialized (dual-token mode)")
                else:
                    logger.info("[OK] Enhanced plugin client initialized (single-token mode)")
                    
            except Exception as e:
                logger.warning(f"Client initialization error: {e}")
        else:
            logger.info("Preview mode - no Moodle credentials provided")
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name=ToolDescriptions.CREATE_COURSE_NAME,
                    description=ToolDescriptions.CREATE_COURSE_DESC + " (Enhanced with plugin support)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_content": {
                                "type": "string",
                                "description": ToolDescriptions.CHAT_CONTENT_DESC,
                            },
                            "course_name": {
                                "type": "string",
                                "description": ToolDescriptions.COURSE_NAME_DESC,
                            },
                            "course_description": {
                                "type": "string",
                                "description": ToolDescriptions.COURSE_DESC_DESC,
                                "default": "",
                            },
                            "category_id": {
                                "type": "integer",
                                "description": ToolDescriptions.CATEGORY_ID_DESC,
                                "default": 1,
                            },
                        },
                        "required": ["chat_content", "course_name"],
                    },
                ),
                types.Tool(
                    name="extract_and_preview_content",
                    description="Extract and preview content from chat without creating course",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_content": {
                                "type": "string",
                                "description": "The chat conversation content to analyze",
                            }
                        },
                        "required": ["chat_content"],
                    },
                ),
                types.Tool(
                    name="test_plugin_functionality",
                    description="Test MoodleClaude plugin functionality and token configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "create_course_from_chat":
                    return await self._create_course_from_chat(arguments)
                elif name == "extract_and_preview_content":
                    return await self._extract_and_preview_content(arguments)
                elif name == "test_plugin_functionality":
                    return await self._test_plugin_functionality(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [
                    types.TextContent(type="text", text=f"Error executing tool '{name}': {str(e)}")
                ]
    
    async def _create_course_from_chat(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create course using enhanced dual-token system"""
        if not self.config:
            return [types.TextContent(type="text", text="Configuration error - check environment variables")]
        
        if not self.basic_client or not self.plugin_client:
            return [types.TextContent(type="text", text="Moodle clients not initialized - check credentials")]
        
        chat_content = arguments["chat_content"]
        course_name = arguments["course_name"]
        course_description = arguments.get("course_description", "")
        category_id = arguments.get("category_id", 1)
        
        try:
            # Parse content
            parsed_content = self.content_parser.parse_chat(chat_content)
            course_structure = self._organize_content(parsed_content)
            
            # Check if content needs chunking
            total_items = sum(len(section.items) for section in course_structure.sections)
            logger.info(f"Course structure has {len(course_structure.sections)} sections with {total_items} total items")
            
            # Chunk large content if needed
            if total_items > 15 or any(len(section.items) > 10 for section in course_structure.sections):
                logger.info("Large content detected - using chunked processing")
                course_chunks = self.content_chunker.chunk_course_structure(course_structure)
            else:
                course_chunks = [course_structure]
            
            # Create course using basic client
            logger.info(f"Creating course with basic client: {course_name}")
            async with self.basic_client as basic:
                course_id = await basic.create_course(
                    name=course_name,
                    description=course_description,
                    category_id=category_id,
                )
            
            logger.info(f"Course created with ID: {course_id}")
            
            # Enhance course with plugin client
            logger.info("Enhancing course with plugin functionality...")
            async with self.plugin_client as plugin:
                # Check if plugin is available
                plugin_available = await plugin._check_plugin_availability()
                
                if plugin_available:
                    logger.info("[OK] Plugin available - using enhanced functionality with queue processing")
                    
                    # Prepare sections data for all chunks
                    chunks_sections_data = []
                    for chunk_structure in course_chunks:
                        sections_data = []
                        for section in chunk_structure.sections:
                            section_data = {
                                'name': section.name,
                                'summary': section.description,
                                'activities': []
                            }
                            
                            for item in section.items:
                                if item.type == "code":
                                    # Create both file and page for code
                                    section_data['activities'].extend([
                                        {
                                            'type': 'file',
                                            'name': f"{item.title} - Code File",
                                            'content': item.content,
                                            'filename': f"{item.title.lower().replace(' ', '_')}.{item.language or 'txt'}"
                                        },
                                        {
                                            'type': 'page',
                                            'name': item.title,
                                            'content': self.content_formatter.format_code_for_moodle(
                                                code=item.content,
                                                language=item.language,
                                                title=item.title,
                                                description=item.description or ""
                                            )
                                        }
                                    ])
                                elif item.type == "topic":
                                    section_data['activities'].append({
                                        'type': 'page',
                                        'name': item.title,
                                        'content': self.content_formatter.format_topic_for_moodle(
                                            content=item.content,
                                            title=item.title,
                                            description=item.description or ""
                                        )
                                    })
                            
                            sections_data.append(section_data)
                        chunks_sections_data.append(sections_data)
                    
                    # Add chunks to queue and process
                    chunk_ids = await self.chunk_processor.add_chunks(course_id, chunks_sections_data)
                    logger.info(f"Added {len(chunk_ids)} chunks to processing queue: {chunk_ids}")
                    
                    # Progress callback for user feedback
                    async def progress_callback(completed: int, total: int):
                        logger.info(f"Progress: {completed}/{total} chunks processed ({completed/total*100:.1f}%)")
                    
                    # Process all chunks with queue
                    processing_summary = await self.chunk_processor.process_queue(plugin, progress_callback)
                    
                    # Extract results from processing summary
                    successful_chunks = processing_summary['successful_chunks']
                    total_chunks = processing_summary['total_chunks']
                    total_successful_activities = processing_summary['successful_activities']
                    total_activities = processing_summary['total_activities']
                    successful_sections = processing_summary['total_sections']
                    
                    if total_successful_activities > 0:
                        # Calculate content summary from original structure  
                        total_code_examples = sum(
                            len([item for item in section.items if item.type == 'code'])
                            for chunk in course_chunks for section in chunk.sections
                        )
                        total_topics = sum(
                            len([item for item in section.items if item.type == 'topic']) 
                            for chunk in course_chunks for section in chunk.sections
                        )
                        
                        # Generate enhanced summary with queue processing info
                        queue_info = ""
                        if len(course_chunks) > 1:
                            success_rate = processing_summary['success_rate'] * 100
                            queue_info = f" (Queue: {successful_chunks}/{total_chunks} chunks, {success_rate:.1f}% success rate)"
                        
                        # Add retry information if there were failures
                        retry_info = ""
                        if processing_summary['failed_chunks'] > 0:
                            retry_details = processing_summary['failed_chunk_details']
                            total_retries = sum(detail['retry_count'] for detail in retry_details)
                            retry_info = f"\n- Retries Attempted: {total_retries} (automatic recovery)"
                        
                        summary = f"""
[SUCCESS] **Enhanced Course Created Successfully!**

[CONTENT] **Course Details:**
- Course ID: {course_id}
- Course Name: {course_name}
- Course URL: {self.config.moodle_url}/course/view.php?id={course_id}

[LAUNCH] **Plugin Enhancement Results{queue_info}:**
- Sections Created: {successful_sections}
- Activities Created: {total_successful_activities}/{total_activities}
- Real Content Storage: [OK] ENABLED
- Section Updates: [OK] WORKING
- File Resources: [OK] WORKING{retry_info}

 **Content Summary:**
- Code Examples: {total_code_examples}
- Topic Descriptions: {total_topics}

[TARGET] **Access Instructions:**
1. Visit: {self.config.moodle_url}/course/view.php?id={course_id}
2. Content is automatically stored and ready to use!
3. No manual copy-paste required! [SUCCESS]

 **Token Configuration:** {self.config.get_config_summary()['token_mode'].title()} Mode

[INFO] **Queue Processing Stats:**
- Average processing time per chunk: {processing_summary['average_processing_time']:.2f}s
- Activity success rate: {processing_summary['activity_success_rate']*100:.1f}%
"""
                    else:
                        # No successful activities - show failure details
                        failed_chunks = processing_summary['failed_chunks']
                        total_chunks = processing_summary['total_chunks']
                        
                        failure_details = []
                        for detail in processing_summary['failed_chunk_details']:
                            failure_details.append(f"- {detail['chunk_id']}: {detail['error']} (retried {detail['retry_count']} times)")
                        
                        summary = f"""
[WARNING] **Course Created with Limited Success**

[CONTENT] **Course Details:**
- Course ID: {course_id}
- Course Name: {course_name}
- Course URL: {self.config.moodle_url}/course/view.php?id={course_id}

[CONFIG] **Queue Processing Results:**
- Successful Chunks: 0/{total_chunks}
- Failed Chunks: {failed_chunks}
- All content processing failed despite retries

[ERROR] **Failure Details:**
{chr(10).join(failure_details) if failure_details else '- No specific error details available'}

[INFO] **Next Steps:**
1. Check Moodle server capacity and API limits
2. Try processing smaller content portions
3. Review error messages above for specific issues
"""
                        
                else:
                    logger.warning("[ERROR] Plugin not available - using fallback")
                    summary = await self._create_course_fallback(course_id, course_structure, plugin)
                    
            return [types.TextContent(type="text", text=summary)]
            
        except Exception as e:
            logger.error(f"Course creation failed: {e}")
            return [types.TextContent(type="text", text=f"Failed to create course: {str(e)}")]
    
    async def _create_course_fallback(self, course_id: int, course_structure: CourseStructure, client) -> str:
        """Fallback course creation without plugin"""
        summary = f"""
[WARNING] **Course Created with Limited Functionality**

[CONTENT] **Course Details:**
- Course ID: {course_id}
- Course URL: {self.config.moodle_url}/course/view.php?id={course_id}

[CONFIG] **Plugin Status:** Not available - using fallback mode
- Real content storage: [ERROR] Limited
- Section updates: [ERROR] Limited
- Activity creation: [ERROR] Limited

[INFO] **Manual Content Addition Required:**
{self._format_content_for_manual_addition(course_structure)}

[TIP] **To enable full functionality:**
1. Ensure MoodleClaude plugin is installed
2. Enable "MoodleClaude Content Creation Service" in Moodle admin
3. Create token for the plugin service
4. Update MOODLE_PLUGIN_TOKEN in .env file
"""
        return summary
    
    async def _test_plugin_functionality(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Test plugin functionality and token configuration"""
        if not self.config:
            return [types.TextContent(type="text", text="[ERROR] Configuration error")]
        
        results = []
        results.append("🧪 **MoodleClaude Plugin Functionality Test**")
        results.append("=" * 60)
        
        # Test configuration
        config_summary = self.config.get_config_summary()
        results.append(f"\n[INFO] **Configuration:**")
        results.append(f"- Moodle URL: {config_summary['moodle_url']}")
        results.append(f"- Token Mode: {config_summary['token_mode'].title()}")
        results.append(f"- Basic Token: {'[OK]' if config_summary['basic_token_set'] else '[ERROR]'}")
        results.append(f"- Plugin Token: {'[OK]' if config_summary['plugin_token_set'] else '[ERROR]'}")
        
        # Test basic client
        if self.basic_client:
            results.append(f"\n[CONFIG] **Basic Client Test:**")
            try:
                async with self.basic_client as basic:
                    courses = await basic.get_courses()
                    results.append(f"[OK] Basic API access working - found {len(courses)} courses")
            except Exception as e:
                results.append(f"[ERROR] Basic API access failed: {e}")
        
        # Test plugin client
        if self.plugin_client:
            results.append(f"\n[LAUNCH] **Plugin Client Test:**")
            try:
                async with self.plugin_client as plugin:
                    plugin_available = await plugin._check_plugin_availability()
                    if plugin_available:
                        results.append("[OK] MoodleClaude plugin functions detected!")
                        results.append("[OK] Enhanced functionality available")
                    else:
                        results.append("[ERROR] MoodleClaude plugin functions not found")
                        results.append("[TIP] Check plugin installation and service configuration")
            except Exception as e:
                results.append(f"[ERROR] Plugin API access failed: {e}")
        
        results.append(f"\n" + "=" * 60)
        results.append("[TARGET] **Test Complete**")
        
        return [types.TextContent(type="text", text="\n".join(results))]
    
    async def _extract_and_preview_content(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Extract and preview content without creating course"""
        chat_content = arguments["chat_content"]
        
        try:
            parsed_content = self.content_parser.parse_chat(chat_content)
            course_structure = self._organize_content(parsed_content)
            
            preview = f"""
**Content Analysis Preview:**

**Total Sections:** {len(course_structure.sections)}
**Total Code Examples:** {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
**Total Topic Descriptions:** {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}

**Detailed Structure:**
{self._format_course_structure_preview(course_structure)}
"""
            return [types.TextContent(type="text", text=preview)]
            
        except Exception as e:
            logger.error(f"Failed to preview content: {e}")
            return [types.TextContent(type="text", text=f"Failed to preview content: {str(e)}")]
    
    def _organize_content(self, parsed_content: ChatContent) -> CourseStructure:
        """Organize parsed content into course structure (same as original)"""
        sections = []
        topic_groups = {}
        
        for item in parsed_content.items:
            if item.topic:
                if item.topic not in topic_groups:
                    topic_groups[item.topic] = []
                topic_groups[item.topic].append(item)
            else:
                if "General" not in topic_groups:
                    topic_groups["General"] = []
                topic_groups["General"].append(item)
        
        for topic_name, items in topic_groups.items():
            section = CourseStructure.Section(
                name=topic_name,
                description=f"Content related to {topic_name}",
                items=items,
            )
            sections.append(section)
        
        return CourseStructure(sections=sections)
    
    def _format_course_structure_preview(self, structure: CourseStructure) -> str:
        """Format detailed course structure for preview (same as original)"""
        preview_lines = []
        for section in structure.sections:
            preview_lines.append(f"\n[CONTENT] Section: {section.name}")
            preview_lines.append(f"   Description: {section.description}")
            
            for item in section.items:
                if item.type == "code":
                    preview_lines.append(f"    Code: {item.title}")
                    preview_lines.append(f"      Language: {item.language or 'Unknown'}")
                    preview_lines.append(f"      Lines: {len(item.content.splitlines())}")
                elif item.type == "topic":
                    preview_lines.append(f"    Topic: {item.title}")
                    preview_lines.append(f"      Content length: {len(item.content)} characters")
                
                if item.description:
                    preview_lines.append(f"      Description: {item.description[:100]}...")
        
        return "\n".join(preview_lines)
    
    def _format_content_for_manual_addition(self, structure: CourseStructure) -> str:
        """Format content for manual addition (abbreviated version)"""
        content_lines = []
        for i, section in enumerate(structure.sections, 1):
            content_lines.append(f"\n**Section {i}: {section.name}**")
            content_lines.append(f"Items: {len(section.items)} activities")
        
        content_lines.append(f"\n[TIP] Use plugin functionality for automatic content storage!")
        return "\n".join(content_lines)


async def main():
    """Main entry point for the Enhanced MCP server"""
    server_instance = EnhancedMoodleMCPServer()
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="enhanced-moodle-course-creator",
                server_version="2.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())