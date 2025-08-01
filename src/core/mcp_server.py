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

from src.clients.moodle_client_enhanced import EnhancedMoodleClient
from src.core.config import Config
from src.core.constants import ContentTypes, Defaults, Messages, ToolDescriptions
from src.core.content_formatter import ContentFormatter
from src.core.content_parser import ChatContentParser
from src.models.models import ChatContent, CourseStructure

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

        # Initialize Enhanced Moodle client if credentials are available
        if self.config.moodle_url and self.config.moodle_token:
            try:
                self.moodle_client = EnhancedMoodleClient(
                    base_url=self.config.moodle_url, token=self.config.moodle_token
                )
                logger.info("Enhanced Moodle client initialized with plugin support")
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
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
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
                    types.TextContent(
                        type="text", text=f"Error executing tool '{name}': {str(e)}"
                    )
                ]

    async def _create_course_from_chat(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
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
            logger.info(f"Creating course: {course_name}")
            course_id = await self.moodle_client.create_course(
                name=course_name,
                description=course_description,
                category_id=category_id,
            )
            logger.info(f"Course created with ID: {course_id}")

            # Since we created a new course, the name should match what was requested
            actual_course_name = course_name
            course_creation_success = True

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
                        # Create file resource for downloadable code (returns dict now)
                        file_result = await self.moodle_client.create_file_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=f"{item.title} - Code File",
                            content=item.content,
                            filename=f"{item.title.lower().replace(' ', '_')}.{item.language or 'txt'}",
                        )
                        if isinstance(file_result, dict) and file_result.get("success"):
                            created_activities.append(file_result)
                        else:
                            # Legacy support for old return format
                            created_activities.append(
                                {"success": True, "activity_id": file_result}
                            )

                        # Create page with syntax highlighted code
                        formatted_content = (
                            self.content_formatter.format_code_for_moodle(
                                code=item.content,
                                language=item.language,
                                title=item.title,
                                description=item.description or "",
                            )
                        )
                        page_result = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        if isinstance(page_result, dict):
                            created_activities.append(page_result)
                        else:
                            # Legacy support for old return format
                            created_activities.append(
                                {"success": True, "activity_id": page_result}
                            )

                    elif item.type == "topic":
                        # Create page for topic description
                        formatted_content = (
                            self.content_formatter.format_topic_for_moodle(
                                content=item.content,
                                title=item.title,
                                description=item.description or "",
                            )
                        )
                        page_result = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        if isinstance(page_result, dict):
                            created_activities.append(page_result)
                        else:
                            # Legacy support for old return format
                            created_activities.append(
                                {"success": True, "activity_id": page_result}
                            )

            # Get the course URL for easy access
            course_url = f"{self.moodle_client.base_url}/course/view.php?id={course_id}"

            # Calculate actual success counts
            successful_activities = sum(
                1
                for activity in created_activities
                if isinstance(activity, dict) and activity.get("success", False)
            )
            failed_activities = len(created_activities) - successful_activities

            # Generate detailed activity status
            activity_details = []
            for i, activity in enumerate(created_activities, 1):
                if isinstance(activity, dict):
                    status = "[OK]" if activity.get("success") else "[ERROR]"
                    method = activity.get("method", "unknown")
                    message = activity.get("message", "No details")
                    activity_details.append(
                        f"   {i}. {status} Method: {method} - {message}"
                    )
                else:
                    activity_details.append(
                        f"   {i}. [OK] Legacy format (assumed success)"
                    )

            summary = f"""
{'[OK]' if successful_activities > 0 else '[WARNING]'} Course structure created!

[CONTENT] Course Details:
- Course ID: {course_id}
- Course Name: {actual_course_name}
- Course URL: {course_url}
- Sections Created: {len(course_structure.sections)}
- Activities Attempted: {len(created_activities)}
- Activities Successful: {successful_activities}
- Activities Failed: {failed_activities}

 Content Summary:
- Code Examples: {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
- Topic Descriptions: {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}

[INFO] Activity Details:
{"".join(activity_details) if activity_details else "   No activities processed"}

[TARGET] Access Instructions:
1. Visit your Moodle site: {self.moodle_client.base_url}
2. Go to "My Courses" to see the course
3. Or access directly: {course_url}

[INFO] Course Structure:
{self._format_course_structure_summary(course_structure)}

[TIP] Notes:
- New course created successfully with proper structure
- Content storage limited by Moodle API permissions - see formatted content below
- Course sections created but content must be added manually

[INFO] **FORMATTED CONTENT FOR MANUAL ADDITION:**
Copy the content below into your Moodle course sections:

{self._format_content_for_manual_addition(course_structure)}
"""

            return [types.TextContent(type="text", text=summary)]

        except Exception as e:
            logger.error(f"Failed to create course: {e}")
            return [
                types.TextContent(
                    type="text", text=f"Failed to create course: {str(e)}"
                )
            ]

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
            return [
                types.TextContent(
                    type="text", text=f"Failed to preview content: {str(e)}"
                )
            ]

    async def _add_content_to_existing_course(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Add content to existing Moodle course"""
        if not self.moodle_client:
            return [
                types.TextContent(
                    type="text", text="Error: Moodle client not initialized."
                )
            ]

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
                        file_result = await self.moodle_client.create_file_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=f"{item.title} - Code File",
                            content=item.content,
                            filename=f"{item.title.lower().replace(' ', '_')}.{item.language or 'txt'}",
                        )
                        if isinstance(file_result, dict) and file_result.get("success"):
                            added_activities.append(file_result)
                        else:
                            # Legacy support for old return format
                            added_activities.append(
                                {"success": True, "activity_id": file_result}
                            )

                        formatted_content = (
                            self.content_formatter.format_code_for_moodle(
                                code=item.content,
                                language=item.language,
                                title=item.title,
                                description=item.description or "",
                            )
                        )
                        page_result = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        if isinstance(page_result, dict):
                            added_activities.append(page_result)
                        else:
                            # Legacy support for old return format
                            added_activities.append(
                                {"success": True, "activity_id": page_result}
                            )

                    elif item.type == "topic":
                        formatted_content = (
                            self.content_formatter.format_topic_for_moodle(
                                content=item.content,
                                title=item.title,
                                description=item.description or "",
                            )
                        )
                        page_result = await self.moodle_client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        if isinstance(page_result, dict):
                            added_activities.append(page_result)
                        else:
                            # Legacy support for old return format
                            added_activities.append(
                                {"success": True, "activity_id": page_result}
                            )

            # Calculate actual success counts
            successful_activities = sum(
                1
                for activity in added_activities
                if isinstance(activity, dict) and activity.get("success", False)
            )
            failed_activities = len(added_activities) - successful_activities

            # Generate detailed activity status
            activity_details = []
            for i, activity in enumerate(added_activities, 1):
                if isinstance(activity, dict):
                    status = "[OK]" if activity.get("success") else "[ERROR]"
                    method = activity.get("method", "unknown")
                    message = activity.get("message", "No details")
                    activity_details.append(
                        f"   {i}. {status} Method: {method} - {message}"
                    )
                else:
                    activity_details.append(
                        f"   {i}. [OK] Legacy format (assumed success)"
                    )

            summary = f"""
{'[OK]' if successful_activities > 0 else '[WARNING]'} Content added to existing course!

[CONTENT] Course Details:
- Course ID: {course_id}
- New Sections Added: {len(course_structure.sections)}
- Activities Attempted: {len(added_activities)}
- Activities Successful: {successful_activities}
- Activities Failed: {failed_activities}

 Added Content Summary:
- Code Examples: {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
- Topic Descriptions: {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}

[INFO] Activity Details:
{"".join(activity_details) if activity_details else "   No activities processed"}

[TIP] Note: Content is stored in section summaries due to Moodle 4.3 API limitations.
"""

            return [types.TextContent(type="text", text=summary)]

        except Exception as e:
            logger.error(f"Failed to add content to course: {e}")
            return [
                types.TextContent(
                    type="text", text=f"Failed to add content to course: {str(e)}"
                )
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
                item_type = "" if item.type == "topic" else ""
                summary_lines.append(f"   {i}.{j} {item_type} {item.title}")
        return "\n".join(summary_lines)

    def _format_course_structure_preview(self, structure: CourseStructure) -> str:
        """Format detailed course structure for preview"""
        preview_lines = []
        for section in structure.sections:
            preview_lines.append(f"\n[CONTENT] Section: {section.name}")
            preview_lines.append(f"   Description: {section.description}")

            for item in section.items:
                if item.type == "code":
                    preview_lines.append(f"    Code: {item.title}")
                    preview_lines.append(
                        f"      Language: {item.language or 'Unknown'}"
                    )
                    preview_lines.append(
                        f"      Lines: {len(item.content.splitlines())}"
                    )
                elif item.type == "topic":
                    preview_lines.append(f"    Topic: {item.title}")
                    preview_lines.append(
                        f"      Content length: {len(item.content)} characters"
                    )

                if item.description:
                    preview_lines.append(
                        f"      Description: {item.description[:100]}..."
                    )

        return "\n".join(preview_lines)

    def _format_content_for_manual_addition(self, structure: CourseStructure) -> str:
        """Format content in a way that's easy to copy-paste into Moodle sections"""
        content_lines = []

        for i, section in enumerate(structure.sections, 1):
            content_lines.append(f"\n{'='*60}")
            content_lines.append(f"SECTION {i}: {section.name.upper()}")
            content_lines.append(f"{'='*60}")
            content_lines.append(
                f"\n[INFO] **Instructions**: Copy the HTML content below into Moodle Section {i}"
            )
            content_lines.append(
                f"   1. Go to your course: http://localhost:8080/course/view.php"
            )
            content_lines.append(f"   2. Click 'Edit' mode")
            content_lines.append(f"   3. In Section {i}, click 'Edit section'")
            content_lines.append(
                f"   4. Paste the content below into the 'Summary' field"
            )
            content_lines.append(f"   5. Save changes")

            # Combine all items in this section into one formatted content block
            section_content = f"""
<div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px;">
<h2 style="color: #0d6efd; margin-bottom: 20px;">[CONTENT] {section.name}</h2>
"""

            for item in section.items:
                if item.type == "topic":
                    section_content += f"""
<div style="background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; border-radius: 4px;">
<h3 style="color: #155724; margin-bottom: 10px;"> {item.title}</h3>
<div style="line-height: 1.6;">
{item.content.replace(chr(10), '<br>')}
</div>
</div>
"""
                elif item.type == "code":
                    section_content += f"""
<div style="background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #6c757d; border-radius: 4px;">
<h3 style="color: #495057; margin-bottom: 10px;"> {item.title}</h3>
<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto;"><code>{item.content}</code></pre>
</div>
"""

            section_content += """
</div>
<div style="margin-top: 20px; padding: 10px; background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 4px;">
<small style="color: #0c5460;">
[TIP] <strong>Tip:</strong> This content was automatically generated from your chat.
You can edit it directly in Moodle to customize the formatting or add additional materials.
</small>
</div>
"""

            content_lines.append(f"\n **HTML Content for Section {i}:**")
            content_lines.append("```html")
            content_lines.append(section_content.strip())
            content_lines.append("```")
            content_lines.append(f"\n")

        return "\n".join(content_lines)


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
