#!/usr/bin/env python3
"""
Debug version of MCP server with enhanced logging for Claude Desktop validation
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from config import Config
from constants import Defaults, Messages, ToolDescriptions, ContentTypes
from content_formatter import ContentFormatter
from content_parser import ChatContentParser
from models import ChatContent, CourseStructure
from moodle_client import MoodleClient

# Enhanced logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server_debug.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class DebugMoodleMCPServer:
    """Debug version of MCP Server with enhanced logging"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info("🔧 STARTING DEBUG MCP SERVER")
        logger.info("=" * 60)
        
        self.server = Server(Defaults.SERVER_NAME)
        self.content_parser = ChatContentParser()
        self.moodle_client = None
        self.content_formatter = ContentFormatter()
        self.config = Config()

        # Initialize Moodle client if credentials are available
        if self.config.moodle_url and self.config.moodle_token:
            try:
                self.moodle_client = MoodleClient(
                    base_url=self.config.moodle_url, token=self.config.moodle_token
                )
                logger.info(f"✅ Moodle client initialized: {self.config.moodle_url}")
            except Exception as e:
                logger.error(f"❌ Moodle client failed: {e}")
        else:
            logger.warning("⚠️  No Moodle credentials - running in preview mode")

        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers with debug logging"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            logger.info("📋 LIST_TOOLS called by Claude Desktop")
            tools = [
                types.Tool(
                    name="create_course_from_chat",
                    description="Create a Moodle course from chat content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_content": {
                                "type": "string",
                                "description": "The chat conversation content to convert",
                            },
                            "course_name": {
                                "type": "string",
                                "description": "Name for the course",
                            },
                            "course_description": {
                                "type": "string",
                                "description": "Course description",
                                "default": "",
                            },
                        },
                        "required": ["chat_content", "course_name"],
                    },
                ),
            ]
            logger.info(f"📋 Returning {len(tools)} tools to Claude Desktop")
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            logger.info("=" * 60)
            logger.info(f"🛠️  TOOL CALL: {name}")
            logger.info(f"📥 Arguments: {list(arguments.keys())}")
            logger.info("=" * 60)
            
            if name == "create_course_from_chat":
                return await self._debug_create_course_from_chat(arguments)
            else:
                logger.error(f"❌ Unknown tool: {name}")
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _debug_create_course_from_chat(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Debug version of create course from chat"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"🎓 COURSE CREATION START - {timestamp}")
        
        chat_content = arguments.get("chat_content", "")
        course_name = arguments.get("course_name", "")
        course_description = arguments.get("course_description", "")
        
        logger.info(f"📝 Chat content length: {len(chat_content)} characters")
        logger.info(f"🏷️  Course name: {course_name}")
        logger.info(f"📖 Course description: {course_description}")
        
        if not self.moodle_client:
            logger.error("❌ No Moodle client available")
            return [types.TextContent(
                type="text",
                text="❌ Error: Moodle client not initialized. Please check MOODLE_URL and MOODLE_TOKEN environment variables."
            )]

        try:
            # Step 1: Parse content
            logger.info("🔍 STEP 1: Parsing chat content...")
            parsed_content = self.content_parser.parse_chat(chat_content)
            logger.info(f"✅ Parsed {len(parsed_content.items)} items")
            
            for i, item in enumerate(parsed_content.items):
                logger.info(f"   Item {i+1}: {item.type} - {item.title}")
                if hasattr(item, 'language'):
                    logger.info(f"     Language: {item.language}")
                logger.info(f"     Content length: {len(item.content)} chars")

            # Step 2: Create course structure
            logger.info("🏗️  STEP 2: Creating course structure...")
            course_structure = self._organize_content(parsed_content)
            logger.info(f"✅ Course structure with {len(course_structure.sections)} sections")

            # Step 3: Create course in Moodle
            logger.info("🎓 STEP 3: Creating course in Moodle...")
            course_id = await self.moodle_client.create_course(
                name=course_name,
                description=course_description,
                category_id=1,
            )
            logger.info(f"✅ Course created with ID: {course_id}")

            # Step 4: Add content to course
            logger.info("📚 STEP 4: Adding content to course...")
            created_activities = []
            
            for section_idx, section in enumerate(course_structure.sections):
                logger.info(f"   Processing section {section_idx + 1}: {section.name}")
                
                try:
                    section_id = await self.moodle_client.create_section(
                        course_id=course_id,
                        name=section.name,
                        description=section.description or "",
                    )
                    logger.info(f"   ✅ Section created: {section_id}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Section creation failed: {e}")
                    section_id = section_idx + 1  # Use default section

                for item_idx, item in enumerate(section.items):
                    logger.info(f"     Processing item {item_idx + 1}: {item.title}")
                    
                    try:
                        if item.type == "code":
                            # Create page activity for code
                            formatted_content = self.content_formatter.format_code_for_moodle(
                                code=item.content,
                                language=getattr(item, 'language', 'text'),
                                title=item.title,
                                description=getattr(item, 'description', ''),
                            )
                            
                            activity_id = await self.moodle_client.create_page_activity(
                                course_id=course_id,
                                section_id=section_id,
                                name=item.title,
                                content=formatted_content,
                            )
                            logger.info(f"     ✅ Code page created: {activity_id}")
                            created_activities.append(activity_id)
                            
                        elif item.type == "topic":
                            # Create page activity for topic
                            formatted_content = self.content_formatter.format_topic_for_moodle(
                                content=item.content,
                                title=item.title,
                                description=getattr(item, 'description', ''),
                            )
                            
                            activity_id = await self.moodle_client.create_page_activity(
                                course_id=course_id,
                                section_id=section_id,
                                name=item.title,
                                content=formatted_content,
                            )
                            logger.info(f"     ✅ Topic page created: {activity_id}")
                            created_activities.append(activity_id)
                            
                    except Exception as e:
                        logger.warning(f"     ⚠️  Activity creation failed: {e}")

            # Step 5: Generate response
            course_url = f"{self.moodle_client.base_url}/course/view.php?id={course_id}"
            
            success_message = f"""
🎉 Course Created Successfully!

📚 Course Details:
• Course ID: {course_id}
• Course Name: {course_name}
• Course URL: {course_url}
• Sections: {len(course_structure.sections)}
• Activities: {len(created_activities)}

📊 Content Analysis:
• Code Items: {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
• Topic Items: {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}
• Total Items: {len(parsed_content.items)}

🔗 Access Your Course:
1. Visit: {course_url}
2. Or go to "My Courses" in Moodle dashboard

⏰ Created: {timestamp}
"""

            logger.info("🎉 COURSE CREATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
            return [types.TextContent(type="text", text=success_message)]

        except Exception as e:
            error_msg = f"❌ Course creation failed: {str(e)}"
            logger.error(error_msg)
            logger.error("=" * 60)
            
            import traceback
            traceback.print_exc()
            
            return [types.TextContent(type="text", text=error_msg)]

    def _organize_content(self, parsed_content: ChatContent) -> CourseStructure:
        """Organize parsed content into course structure"""
        from models import CourseStructure
        
        if not parsed_content.items:
            # Create a default section with basic info
            section = CourseStructure.Section(
                name="General Information",
                description="Course information and resources",
                items=[]
            )
            return CourseStructure(sections=[section])
        
        # Group items by topic or create sections based on content type
        sections = []
        current_section_items = []
        current_section_name = "Course Content"
        
        for item in parsed_content.items:
            current_section_items.append(item)
        
        if current_section_items:
            section = CourseStructure.Section(
                name=current_section_name,
                description="Course content and examples",
                items=current_section_items
            )
            sections.append(section)
        
        return CourseStructure(sections=sections)

    async def run(self):
        """Run the debug MCP server"""
        logger.info("🚀 Starting MCP server stdio loop...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=Defaults.SERVER_NAME,
                    server_version=Defaults.SERVER_VERSION,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    server = DebugMoodleMCPServer()
    asyncio.run(server.run())