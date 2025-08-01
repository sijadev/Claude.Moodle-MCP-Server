#!/usr/bin/env python3
"""
Working MCP Server für Claude Desktop
====================================

Funktionsfähiger MCP Server ohne komplexe Dependencies.
Konzentriert sich auf die Core-Funktionalität ohne externe Config-Files.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import MCP components
try:
    import mcp.server.stdio
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
except ImportError as e:
    print(f"MCP library not available: {e}")
    print("Please install: pip install mcp")
    sys.exit(1)

# Import standard libraries for HTTP requests
try:
    import aiohttp
except ImportError:
    print("aiohttp not available, please install: pip install aiohttp")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("working_mcp_server")


# Server configuration from environment variables
class ServerConfig:
    """Server configuration from environment variables."""

    def __init__(self):
        self.moodle_url = os.environ.get("MOODLE_URL", "http://localhost:8080")
        # Try new token names first, fall back to old names
        self.moodle_token_basic = (
            os.environ.get("MOODLE_BASIC_TOKEN")
            or os.environ.get("MOODLE_TOKEN_BASIC")
            or os.environ.get("MOODLE_ADMIN_TOKEN", "")
        )
        self.moodle_token_enhanced = (
            os.environ.get("MOODLE_PLUGIN_TOKEN")
            or os.environ.get("MOODLE_TOKEN_ENHANCED")
            or os.environ.get("MOODLE_ADMIN_TOKEN", "")
        )
        self.moodle_username = os.environ.get(
            "MOODLE_USERNAME", os.environ.get("MOODLE_WS_USER", "admin")
        )
        self.server_name = os.environ.get("SERVER_NAME", "working-moodle-mcp")
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")

        # Set log level
        if self.log_level:
            level = getattr(logging, self.log_level.upper(), logging.INFO)
            logging.getLogger().setLevel(level)

        logger.info(f"Server Config: {self.server_name} -> {self.moodle_url}")


# Global config instance
config = ServerConfig()


class WorkingMoodleClient:
    """Simple Moodle client for MCP server."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def call_webservice(self, function: str, **params) -> Dict[str, Any]:
        """Call a Moodle web service function."""
        await self._ensure_session()

        url = f"{self.base_url}/webservice/rest/server.php"

        data = {
            "wstoken": self.token,
            "wsfunction": function,
            "moodlewsrestformat": "json",
            **params,
        }

        try:
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()

                    # Check for Moodle errors
                    if isinstance(result, dict) and "exception" in result:
                        raise Exception(
                            f"Moodle error: {result.get('message', 'Unknown error')}"
                        )

                    return result
                else:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")

        except Exception as e:
            logger.error(f"Webservice call failed: {function} - {str(e)}")
            raise

    async def create_courses(
        self, courses_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create courses using proper Moodle form-data format."""
        await self._ensure_session()

        url = f"{self.base_url}/webservice/rest/server.php"

        # Build form data with Moodle's array syntax
        data = {
            "wstoken": self.token,
            "wsfunction": "core_course_create_courses",
            "moodlewsrestformat": "json",
        }

        # Add courses data with proper array syntax
        for i, course in enumerate(courses_data):
            for key, value in course.items():
                data[f"courses[{i}][{key}]"] = value

        try:
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()

                    # Check for Moodle errors
                    if isinstance(result, dict) and "exception" in result:
                        raise Exception(
                            f"Moodle error: {result.get('message', 'Unknown error')}"
                        )

                    return result
                else:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")

        except Exception as e:
            logger.error(f"Course creation failed: {str(e)}")
            raise


# Global Moodle client instances
moodle_basic = None
moodle_enhanced = None


async def get_moodle_client(use_enhanced: bool = False) -> WorkingMoodleClient:
    """Get Moodle client instance."""
    global moodle_basic, moodle_enhanced

    if use_enhanced and config.moodle_token_enhanced:
        if moodle_enhanced is None:
            moodle_enhanced = WorkingMoodleClient(
                config.moodle_url, config.moodle_token_enhanced
            )
        return moodle_enhanced
    else:
        if moodle_basic is None:
            moodle_basic = WorkingMoodleClient(
                config.moodle_url, config.moodle_token_basic
            )
        return moodle_basic


# Create the MCP server
server = Server(config.server_name)


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_courses",
            description="Get list of courses from Moodle",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search term for course names (optional)",
                    }
                },
            },
        ),
        types.Tool(
            name="get_course_contents",
            description="Get contents of a specific course",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID of the course"}
                },
                "required": ["course_id"],
            },
        ),
        types.Tool(
            name="create_course",
            description="Create a new course in Moodle",
            inputSchema={
                "type": "object",
                "properties": {
                    "fullname": {
                        "type": "string",
                        "description": "Full name of the course",
                    },
                    "shortname": {
                        "type": "string",
                        "description": "Short name/code of the course",
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "Category ID (default: 1)",
                        "default": 1,
                    },
                },
                "required": ["fullname", "shortname"],
            },
        ),
        types.Tool(
            name="test_connection",
            description="Test connection to Moodle server",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="create_course_section",
            description="Create a new section in a course",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID of the course"},
                    "name": {"type": "string", "description": "Name of the section"},
                    "summary": {
                        "type": "string",
                        "description": "Summary/description of the section",
                    },
                    "section": {
                        "type": "integer",
                        "description": "Section number (optional)",
                    },
                },
                "required": ["course_id", "name"],
            },
        ),
        types.Tool(
            name="add_course_module",
            description="Add an activity/resource module to a course section",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID of the course"},
                    "section": {
                        "type": "integer",
                        "description": "Section number",
                        "default": 0,
                    },
                    "module_name": {
                        "type": "string",
                        "description": "Module type (forum, assign, quiz, resource, etc.)",
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the activity/resource",
                    },
                    "intro": {
                        "type": "string",
                        "description": "Introduction/description",
                    },
                    "visible": {
                        "type": "boolean",
                        "description": "Whether the module is visible",
                        "default": True,
                    },
                },
                "required": ["course_id", "module_name", "name"],
            },
        ),
        types.Tool(
            name="create_assignment",
            description="Create an assignment in a course",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID of the course"},
                    "section": {
                        "type": "integer",
                        "description": "Section number",
                        "default": 0,
                    },
                    "name": {"type": "string", "description": "Assignment name"},
                    "intro": {
                        "type": "string",
                        "description": "Assignment description",
                    },
                    "duedate": {
                        "type": "integer",
                        "description": "Due date timestamp (optional)",
                    },
                    "allowsubmissionsfromdate": {
                        "type": "integer",
                        "description": "Allow submissions from date timestamp (optional)",
                    },
                    "grade": {
                        "type": "integer",
                        "description": "Maximum grade",
                        "default": 100,
                    },
                },
                "required": ["course_id", "name", "intro"],
            },
        ),
        types.Tool(
            name="create_forum",
            description="Create a forum in a course",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID of the course"},
                    "section": {
                        "type": "integer",
                        "description": "Section number",
                        "default": 0,
                    },
                    "name": {"type": "string", "description": "Forum name"},
                    "intro": {"type": "string", "description": "Forum description"},
                    "type": {
                        "type": "string",
                        "description": "Forum type (news, single, qanda, general)",
                        "default": "general",
                    },
                },
                "required": ["course_id", "name", "intro"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "test_connection":
            return await handle_test_connection()
        elif name == "get_courses":
            return await handle_get_courses(arguments)
        elif name == "get_course_contents":
            return await handle_get_course_contents(arguments)
        elif name == "create_course":
            return await handle_create_course(arguments)
        elif name == "create_course_section":
            return await handle_create_course_section(arguments)
        elif name == "add_course_module":
            return await handle_add_course_module(arguments)
        elif name == "create_assignment":
            return await handle_create_assignment(arguments)
        elif name == "create_forum":
            return await handle_create_forum(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool call failed: {name} - {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_test_connection() -> List[types.TextContent]:
    """Test connection to Moodle."""
    try:
        client = await get_moodle_client()
        result = await client.call_webservice("core_webservice_get_site_info")

        site_name = result.get("sitename", "Unknown")
        version = result.get("release", "Unknown")

        return [
            types.TextContent(
                type="text",
                text=f"✅ Connected to Moodle successfully!\n"
                f"Site: {site_name}\n"
                f"Version: {version}\n"
                f"URL: {config.moodle_url}",
            )
        ]

    except Exception as e:
        return [types.TextContent(type="text", text=f"❌ Connection failed: {str(e)}")]


async def handle_get_courses(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Get list of courses."""
    try:
        client = await get_moodle_client()

        # Call Moodle webservice to get courses
        courses = await client.call_webservice("core_course_get_courses")

        if not courses:
            return [types.TextContent(type="text", text="No courses found.")]

        # Filter by search term if provided
        search_term = arguments.get("search", "").lower()
        if search_term:
            courses = [
                course
                for course in courses
                if search_term in course.get("fullname", "").lower()
                or search_term in course.get("shortname", "").lower()
            ]

        # Format results
        course_list = []
        for course in courses:
            course_info = (
                f"ID: {course.get('id', 'N/A')}\n"
                f"Name: {course.get('fullname', 'N/A')}\n"
                f"Short: {course.get('shortname', 'N/A')}\n"
                f"Category: {course.get('categoryname', 'N/A')}\n"
                f"Enrolled: {course.get('enrolledusercount', 0)} users\n"
            )
            course_list.append(course_info)

        result_text = f"Found {len(courses)} courses:\n\n" + "\n---\n".join(course_list)

        return [types.TextContent(type="text", text=result_text)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Failed to get courses: {str(e)}")]


async def handle_get_course_contents(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Get course contents."""
    try:
        course_id = arguments["course_id"]
        client = await get_moodle_client()

        contents = await client.call_webservice(
            "core_course_get_contents", courseid=course_id
        )

        if not contents:
            return [
                types.TextContent(
                    type="text", text=f"No contents found for course {course_id}."
                )
            ]

        # Format course structure
        sections = []
        for section in contents:
            section_info = f"Section {section.get('section', 'N/A')}: {section.get('name', 'Unnamed')}"

            modules = section.get("modules", [])
            if modules:
                module_list = []
                for module in modules:
                    mod_info = f"  - {module.get('modname', 'Unknown')}: {module.get('name', 'Unnamed')}"
                    module_list.append(mod_info)
                section_info += "\n" + "\n".join(module_list)
            else:
                section_info += "\n  (No activities)"

            sections.append(section_info)

        result_text = f"Course {course_id} Contents:\n\n" + "\n\n".join(sections)

        return [types.TextContent(type="text", text=result_text)]

    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"Failed to get course contents: {str(e)}"
            )
        ]


async def handle_create_course(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Create a new course."""
    try:
        fullname = arguments["fullname"]
        shortname = arguments["shortname"]
        category_id = arguments.get("category_id", 1)

        client = await get_moodle_client(
            use_enhanced=True
        )  # Use enhanced token for creation

        courses_data = [
            {
                "fullname": fullname,
                "shortname": shortname,
                "categoryid": category_id,
                "summary": f'Course created via MCP on {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            }
        ]

        result = await client.create_courses(courses_data)

        if result and len(result) > 0:
            new_course = result[0]
            course_id = new_course.get("id")

            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Course created successfully!\n"
                    f"ID: {course_id}\n"
                    f"Name: {fullname}\n"
                    f"Short: {shortname}\n"
                    f"URL: {config.moodle_url}/course/view.php?id={course_id}",
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text", text="❌ Course creation failed: No result returned"
                )
            ]

    except Exception as e:
        return [
            types.TextContent(type="text", text=f"❌ Failed to create course: {str(e)}")
        ]


async def handle_create_course_section(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Create a new section in a course."""
    try:
        course_id = arguments["course_id"]
        name = arguments["name"]
        summary = arguments.get("summary", "")
        section = arguments.get("section")

        client = await get_moodle_client(use_enhanced=True)

        # Create section using core_course_create_sections
        sections_data = [
            {
                "course": course_id,
                "name": name,
                "summary": summary,
                "summaryformat": 1,  # HTML format
            }
        ]

        if section is not None:
            sections_data[0]["section"] = section

        result = await client.call_webservice(
            "core_course_create_sections", sections=sections_data
        )

        if result and len(result) > 0:
            new_section = result[0]
            section_id = new_section.get("id")
            section_num = new_section.get("section")

            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Course section created successfully!\n"
                    f"Section ID: {section_id}\n"
                    f"Section Number: {section_num}\n"
                    f"Name: {name}\n"
                    f"Course ID: {course_id}",
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text", text="❌ Section creation failed: No result returned"
                )
            ]

    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"❌ Failed to create section: {str(e)}"
            )
        ]


async def handle_add_course_module(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Add a module to a course section."""
    try:
        course_id = arguments["course_id"]
        section = arguments.get("section", 0)
        module_name = arguments["module_name"]
        name = arguments["name"]
        intro = arguments.get("intro", "")
        visible = arguments.get("visible", True)

        client = await get_moodle_client(use_enhanced=True)

        # Create module using core_course_create_modules
        module_data = {
            "courseid": course_id,
            "section": section,
            "modulename": module_name,
            "name": name,
            "intro": intro,
            "introformat": 1,  # HTML format
            "visible": 1 if visible else 0,
        }

        result = await client.call_webservice(
            "core_course_create_modules", modules=[module_data]
        )

        if result and len(result) > 0:
            module_id = result[0].get("coursemodule")

            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Course module added successfully!\n"
                    f"Module ID: {module_id}\n"
                    f"Type: {module_name}\n"
                    f"Name: {name}\n"
                    f"Course ID: {course_id}\n"
                    f"Section: {section}",
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text", text="❌ Module creation failed: No result returned"
                )
            ]

    except Exception as e:
        return [
            types.TextContent(type="text", text=f"❌ Failed to add module: {str(e)}")
        ]


async def handle_create_assignment(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Create an assignment in a course."""
    try:
        course_id = arguments["course_id"]
        section = arguments.get("section", 0)
        name = arguments["name"]
        intro = arguments["intro"]
        duedate = arguments.get("duedate", 0)
        allowsubmissionsfromdate = arguments.get("allowsubmissionsfromdate", 0)
        grade = arguments.get("grade", 100)

        client = await get_moodle_client(use_enhanced=True)

        # Create assignment using mod_assign_save_assignment
        assignment_data = {
            "courseid": course_id,
            "section": section,
            "name": name,
            "intro": intro,
            "introformat": 1,  # HTML format
            "duedate": duedate,
            "allowsubmissionsfromdate": allowsubmissionsfromdate,
            "grade": grade,
            "visible": 1,
        }

        # Use generic module creation for assignments
        assignment_module = {
            "courseid": course_id,
            "section": section,
            "modulename": "assign",
            "name": name,
            "intro": intro,
            "introformat": 1,
            "visible": 1,
        }

        result = await client.call_webservice(
            "core_course_create_modules", modules=[assignment_module]
        )

        if result and len(result) > 0:
            module_id = result[0].get("coursemodule")

            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Assignment created successfully!\n"
                    f"Assignment ID: {module_id}\n"
                    f"Name: {name}\n"
                    f"Course ID: {course_id}\n"
                    f"Section: {section}\n"
                    f"Max Grade: {grade}",
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Assignment creation failed: No result returned",
                )
            ]

    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"❌ Failed to create assignment: {str(e)}"
            )
        ]


async def handle_create_forum(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Create a forum in a course."""
    try:
        course_id = arguments["course_id"]
        section = arguments.get("section", 0)
        name = arguments["name"]
        intro = arguments["intro"]
        forum_type = arguments.get("type", "general")

        client = await get_moodle_client(use_enhanced=True)

        # Create forum using generic module creation
        forum_module = {
            "courseid": course_id,
            "section": section,
            "modulename": "forum",
            "name": name,
            "intro": intro,
            "introformat": 1,
            "visible": 1,
        }

        result = await client.call_webservice(
            "core_course_create_modules", modules=[forum_module]
        )

        if result and len(result) > 0:
            module_id = result[0].get("coursemodule")

            return [
                types.TextContent(
                    type="text",
                    text=f"✅ Forum created successfully!\n"
                    f"Forum ID: {module_id}\n"
                    f"Name: {name}\n"
                    f"Type: {forum_type}\n"
                    f"Course ID: {course_id}\n"
                    f"Section: {section}",
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text", text="❌ Forum creation failed: No result returned"
                )
            ]

    except Exception as e:
        return [
            types.TextContent(type="text", text=f"❌ Failed to create forum: {str(e)}")
        ]


async def cleanup():
    """Cleanup function to close connections."""
    if moodle_basic:
        await moodle_basic.close()
    if moodle_enhanced:
        await moodle_enhanced.close()


async def main():
    """Main server function."""
    logger.info(f"Starting {config.server_name} MCP Server...")
    logger.info(f"Moodle URL: {config.moodle_url}")
    logger.info(f"Basic Token: {'✅' if config.moodle_token_basic else '❌'}")
    logger.info(f"Enhanced Token: {'✅' if config.moodle_token_enhanced else '❌'}")

    try:
        # Initialize MCP server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=config.server_name,
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        await cleanup()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)
