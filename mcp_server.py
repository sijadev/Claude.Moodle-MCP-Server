#!/usr/bin/env python3
"""
MCP Server for Moodle Course Creation from Claude Chats
Extracts code examples and topic descriptions to create organized Moodle courses
"""

import asyncio
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoodleMCPServer:
    """MCP Server for Moodle Course Creation from Claude Chat Content.
    
    This server provides MCP (Model Context Protocol) tools for converting Claude
    chat conversations into structured Moodle courses. It handles content parsing,
    formatting, and integration with Moodle web services.
    
    Attributes:
        server: MCP Server instance for handling tool requests
        content_parser: Parser for extracting educational content from chats
        moodle_client: Client for Moodle API operations (None if no credentials)
        content_formatter: Formatter for creating Moodle-compatible content
        config: Configuration object with environment settings
        
    Example:
        The server is typically started from command line:
        $ python mcp_server.py
        
        Or used programmatically:
        >>> server = MoodleMCPServer()
        >>> await server.run()
    """
    
    def __init__(self):
        """Initialize the Moodle MCP Server with all required components."""
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
                logger.info(Messages.MOODLE_CLIENT_SUCCESS)
            except Exception as e:
                logger.warning(Messages.MOODLE_CLIENT_FAILED.format(error=e))
        else:
            logger.info(Messages.PREVIEW_MODE)

        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name=ToolDescriptions.CREATE_COURSE_NAME,
                    description=ToolDescriptions.CREATE_COURSE_DESC,
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
                    name="add_content_to_existing_course",
                    description="Add new content to an existing Moodle course",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "integer",
                                "description": "Existing Moodle course ID",
                            },
                            "chat_content": {
                                "type": "string",
                                "description": "New chat content to add",
                            },
                        },
                        "required": ["course_id", "chat_content"],
                    },
                ),
            ]

        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="moodle://courses",
                    name="Moodle Courses",
                    description="Available courses in Moodle",
                    mimeType="application/json",
                ),
                types.Resource(
                    uri="moodle://categories",
                    name="Course Categories",
                    description="Available course categories",
                    mimeType="application/json",
                ),
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            if not self.moodle_client:
                return '{"error": "Moodle client not initialized"}'

            try:
                if uri == "moodle://courses":
                    courses = await self.moodle_client.get_courses()
                    return str(courses)
                elif uri == "moodle://categories":
                    categories = await self.moodle_client.get_categories()
                    return str(categories)
                else:
                    return '{"error": "Unknown resource URI"}'
            except Exception as e:
                return f'{{"error": "Failed to read resource: {str(e)}"}}'

        @self.server.list_prompts()
        async def handle_list_prompts() -> List[types.Prompt]:
            """List available prompts"""
            return [
                types.Prompt(
                    name="course-structure-template",
                    description="Template for organizing course content",
                    arguments=[
                        types.PromptArgument(
                            name="topic",
                            description="Main topic for the course",
                            required=True,
                        ),
                        types.PromptArgument(
                            name="difficulty",
                            description="Course difficulty level",
                            required=False,
                        ),
                    ],
                ),
                types.Prompt(
                    name="code-example-template",
                    description="Template for formatting code examples",
                    arguments=[
                        types.PromptArgument(
                            name="language",
                            description="Programming language",
                            required=True,
                        ),
                        types.PromptArgument(
                            name="context",
                            description="Context or use case",
                            required=False,
                        ),
                    ],
                ),
            ]

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Dict[str, str] | None = None
        ) -> types.GetPromptResult:
            """Get prompt content"""
            args = arguments or {}

            if name == "course-structure-template":
                topic = args.get("topic", "General Topic")
                difficulty = args.get("difficulty", "Beginner")

                content = f"""# {topic} Course Structure

## Course Information
- **Topic**: {topic}
- **Difficulty**: {difficulty}
- **Format**: Interactive learning with code examples

## Suggested Structure:
1. **Introduction Section**
   - Overview of {topic}
   - Prerequisites
   - Learning objectives

2. **Core Concepts**
   - Fundamental principles
   - Key terminology
   - Basic examples

3. **Practical Examples** 
   - Hands-on coding exercises
   - Real-world applications
   - Best practices

4. **Advanced Topics** (if applicable)
   - Complex scenarios
   - Optimization techniques
   - Integration patterns

5. **Assessment & Resources**
   - Practice exercises
   - Additional reading
   - Reference materials
"""

                return types.GetPromptResult(
                    description=f"Course structure template for {topic}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text=content),
                        )
                    ],
                )

            elif name == "code-example-template":
                language = args.get("language", "python")
                context = args.get("context", "basic example")

                content = f"""# {language.title()} Code Example Template

## Context: {context}

### Code Structure:
```{language}
# TODO: Add your {language} code here
# This example demonstrates: {context}

# 1. Setup/Imports
# 2. Main logic
# 3. Example usage
# 4. Expected output
```

### Documentation:
- **Purpose**: Explain what this code does
- **Key Concepts**: List main concepts demonstrated
- **Usage**: How to run/implement this code
- **Extensions**: Possible modifications or improvements

### Learning Objectives:
- Understand core {language} concepts
- Apply {context} in practical scenarios
- Develop problem-solving skills
"""

                return types.GetPromptResult(
                    description=f"Code example template for {language}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text=content),
                        )
                    ],
                )

            else:
                raise ValueError(f"Unknown prompt: {name}")

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "create_course_from_chat":
                    return await self._create_course_from_chat(arguments)
                elif name == "extract_and_preview_content":
                    return await self._extract_and_preview_content(arguments)
                elif name == "add_content_to_existing_course":
                    return await self._add_content_to_existing_course(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [
                    types.TextContent(type="text", text=f"Error executing tool '{name}': {str(e)}")
                ]

    async def _create_course_from_chat(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create a new Moodle course from chat content"""
        if not self.moodle_client:
            return [
                types.TextContent(
                    type="text",
                    text="""Error: Moodle client not initialized. 

To create actual Moodle courses, you need to set these environment variables:
- MOODLE_URL: Your Moodle site URL (e.g., https://moodle.example.com)
- MOODLE_TOKEN: Your Moodle web service token

For now, you can use 'extract_and_preview_content' to see what would be created.""",
                )
            ]

        chat_content = arguments["chat_content"]
        course_name = arguments["course_name"]
        course_description = arguments.get("course_description", "")
        category_id = arguments.get("category_id", 1)

        try:
            # Parse chat content
            parsed_content = self.content_parser.parse_chat(chat_content)

            # Create course structure
            course_structure = self._organize_content(parsed_content)

            # Create course in Moodle
            course_id = await self.moodle_client.create_course(
                name=course_name,
                description=course_description,
                category_id=category_id,
            )

            # Create sections and activities
            created_activities = []
            for section in course_structure.sections:
                section_id = await self.moodle_client.create_section(
                    course_id=course_id,
                    name=section.name,
                    description=section.description,
                )

                for item in section.items:
                    if item.type == "code":
                        # Create file resource for downloadable code
                        file_activity = await self.moodle_client.create_file_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=f"{item.title} - Code File",
                            content=item.content,
                            filename=f"{item.title.lower().replace(' ', '_')}.{item.language or 'txt'}",
                        )
                        created_activities.append(file_activity)

                        # Create page with syntax highlighted code
                        formatted_content = self.content_formatter.format_code_for_moodle(
                            code=item.content,
                            language=item.language,
                            title=item.title,
                            description=item.description or "",
                        )
                        page_activity = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        created_activities.append(page_activity)

                    elif item.type == "topic":
                        # Create page for topic description
                        formatted_content = self.content_formatter.format_topic_for_moodle(
                            content=item.content,
                            title=item.title,
                            description=item.description or "",
                        )
                        page_activity = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        created_activities.append(page_activity)

            summary = f"""
Course created successfully!

Course ID: {course_id}
Course Name: {course_name}
Sections Created: {len(course_structure.sections)}
Activities Created: {len(created_activities)}

Content Summary:
- Code Examples: {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
- Topic Descriptions: {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}

Course Structure:
{self._format_course_structure_summary(course_structure)}
"""

            return [types.TextContent(type="text", text=summary)]

        except Exception as e:
            logger.error(f"Failed to create course: {e}")
            return [types.TextContent(type="text", text=f"Failed to create course: {str(e)}")]

    async def _extract_and_preview_content(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Extract and preview content without creating course"""
        chat_content = arguments["chat_content"]

        try:
            # Parse chat content
            parsed_content = self.content_parser.parse_chat(chat_content)

            # Create course structure
            course_structure = self._organize_content(parsed_content)

            # Format preview
            preview = f"""
Content Analysis Preview:

Total Sections: {len(course_structure.sections)}
Total Code Examples: {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
Total Topic Descriptions: {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}

Detailed Structure:
{self._format_course_structure_preview(course_structure)}
"""

            return [types.TextContent(type="text", text=preview)]

        except Exception as e:
            logger.error(f"Failed to preview content: {e}")
            return [types.TextContent(type="text", text=f"Failed to preview content: {str(e)}")]

    async def _add_content_to_existing_course(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Add content to existing Moodle course"""
        if not self.moodle_client:
            return [types.TextContent(type="text", text="Error: Moodle client not initialized.")]

        course_id = arguments["course_id"]
        chat_content = arguments["chat_content"]

        try:
            # Parse new content
            parsed_content = self.content_parser.parse_chat(chat_content)
            course_structure = self._organize_content(parsed_content)

            # Add new sections and activities
            added_activities = []
            for section in course_structure.sections:
                section_id = await self.moodle_client.create_section(
                    course_id=course_id,
                    name=section.name,
                    description=section.description,
                )

                for item in section.items:
                    if item.type == "code":
                        # Create activities for code
                        file_activity = await self.moodle_client.create_file_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=f"{item.title} - Code File",
                            content=item.content,
                            filename=f"{item.title.lower().replace(' ', '_')}.{item.language or 'txt'}",
                        )
                        added_activities.append(file_activity)

                        formatted_content = self.content_formatter.format_code_for_moodle(
                            code=item.content,
                            language=item.language,
                            title=item.title,
                            description=item.description or "",
                        )
                        page_activity = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        added_activities.append(page_activity)

                    elif item.type == "topic":
                        formatted_content = self.content_formatter.format_topic_for_moodle(
                            content=item.content,
                            title=item.title,
                            description=item.description or "",
                        )
                        page_activity = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        added_activities.append(page_activity)

            summary = f"""
Content added to existing course successfully!

Course ID: {course_id}
New Sections Added: {len(course_structure.sections)}
New Activities Added: {len(added_activities)}

Added Content Summary:
- Code Examples: {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
- Topic Descriptions: {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}
"""

            return [types.TextContent(type="text", text=summary)]

        except Exception as e:
            logger.error(f"Failed to add content to course: {e}")
            return [
                types.TextContent(type="text", text=f"Failed to add content to course: {str(e)}")
            ]

    def _organize_content(self, parsed_content: ChatContent) -> CourseStructure:
        """Organize parsed content into course structure"""
        sections = []

        # Group content by topics
        topic_groups = {}

        for item in parsed_content.items:
            if item.topic:
                if item.topic not in topic_groups:
                    topic_groups[item.topic] = []
                topic_groups[item.topic].append(item)
            else:
                # Create a general section for items without specific topics
                if "General" not in topic_groups:
                    topic_groups["General"] = []
                topic_groups["General"].append(item)

        # Create sections from topic groups
        for topic_name, items in topic_groups.items():
            section = CourseStructure.Section(
                name=topic_name,
                description=f"Content related to {topic_name}",
                items=items,
            )
            sections.append(section)

        return CourseStructure(sections=sections)

    def _format_course_structure_summary(self, structure: CourseStructure) -> str:
        """Format course structure for summary display"""
        summary_lines = []
        for i, section in enumerate(structure.sections, 1):
            summary_lines.append(f"{i}. {section.name} ({len(section.items)} items)")
            for j, item in enumerate(section.items, 1):
                item_type = "📝" if item.type == "topic" else "💻"
                summary_lines.append(f"   {i}.{j} {item_type} {item.title}")
        return "\n".join(summary_lines)

    def _format_course_structure_preview(self, structure: CourseStructure) -> str:
        """Format detailed course structure for preview"""
        preview_lines = []
        for section in structure.sections:
            preview_lines.append(f"\n📚 Section: {section.name}")
            preview_lines.append(f"   Description: {section.description}")

            for item in section.items:
                if item.type == "code":
                    preview_lines.append(f"   💻 Code: {item.title}")
                    preview_lines.append(f"      Language: {item.language or 'Unknown'}")
                    preview_lines.append(f"      Lines: {len(item.content.splitlines())}")
                elif item.type == "topic":
                    preview_lines.append(f"   📝 Topic: {item.title}")
                    preview_lines.append(f"      Content length: {len(item.content)} characters")

                if item.description:
                    preview_lines.append(f"      Description: {item.description[:100]}...")

        return "\n".join(preview_lines)


async def main():
    """Main entry point for the MCP server"""
    server_instance = MoodleMCPServer()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="moodle-course-creator",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
