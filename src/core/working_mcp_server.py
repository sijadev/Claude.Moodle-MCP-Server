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
        types.Tool(
            name="diagnose_webservices",
            description="Diagnose available web service functions and configuration",
            inputSchema={"type": "object", "properties": {}},
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
        elif name == "diagnose_webservices":
            return await handle_diagnose_webservices(arguments)
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

        # Create empty section first using local_wsmanagesections plugin
        create_data = {
            "courseid": course_id,
            "number": 1,  # Create 1 section
        }

        if section is not None:
            create_data["position"] = section
        else:
            create_data["position"] = 0  # 0 means at the end

        # Step 1: Create empty section
        create_result = await client.call_webservice(
            "local_wsmanagesections_create_sections", **create_data
        )

        if not create_result or len(create_result) == 0:
            raise Exception("Failed to create section")

        # Step 2: Update the section with name and summary
        new_section_id = create_result[0].get("id")
        if new_section_id and (name or summary):
            update_data = {}
            if name:
                update_data["name"] = name
            if summary:
                update_data["summary"] = summary
                update_data["summaryformat"] = 1

            await client.call_webservice(
                "local_wsmanagesections_update_sections",
                sectionid=new_section_id,
                **update_data,
            )

        result = create_result

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

        # Try primary method: core_course_create_modules
        try:
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
                raise Exception("No result returned from core_course_create_modules")

        except Exception as primary_error:
            # Fallback: Add content to course summary or description
            logger.warning(f"Primary module creation failed: {primary_error}")

            # Get course info to append module info to description
            try:
                course_info = await client.call_webservice(
                    "core_course_get_courses", options={"ids": [course_id]}
                )

                if course_info and len(course_info) > 0:
                    current_summary = course_info[0].get("summary", "")

                    # Append module information to course summary as fallback
                    new_content = f"\n\n**{module_name.upper()}: {name}**\n{intro}\n(Section {section})"
                    updated_summary = current_summary + new_content

                    # Try to update course summary
                    update_result = await client.call_webservice(
                        "core_course_update_courses",
                        courses=[
                            {
                                "id": course_id,
                                "summary": updated_summary,
                                "summaryformat": 1,
                            }
                        ],
                    )

                    return [
                        types.TextContent(
                            type="text",
                            text=f"⚠️ Module creation via web service failed.\n"
                            f"📝 Added {module_name} '{name}' to course description as fallback.\n"
                            f"Course ID: {course_id}\n"
                            f"Section: {section}\n\n"
                            f"💡 To enable full module creation, configure:\n"
                            f"• Site Administration → Server → Web services → External services\n"
                            f"• Add 'core_course_create_modules' to your web service\n"
                            f"• Original error: {primary_error}",
                        )
                    ]

            except Exception as fallback_error:
                logger.error(f"Fallback method also failed: {fallback_error}")

            # If all methods fail, provide helpful error message
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Failed to add module: {primary_error}\n\n"
                    f"🔧 **SOLUTION REQUIRED:**\n"
                    f"1. Go to: Site Administration → Server → Web services → External services\n"
                    f"2. Find your MoodleClaude web service\n"
                    f"3. Add these functions:\n"
                    f"   • core_course_create_modules\n"
                    f"   • core_course_update_courses\n"
                    f"4. Save and try again\n\n"
                    f"Module details: {module_name} '{name}' in course {course_id}, section {section}",
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

        # Try primary method: core_course_create_modules with assignment module
        try:
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
                raise Exception("No result returned from core_course_create_modules")

        except Exception as primary_error:
            # Fallback: Add assignment info to course summary
            logger.warning(f"Primary assignment creation failed: {primary_error}")

            try:
                course_info = await client.call_webservice(
                    "core_course_get_courses", options={"ids": [course_id]}
                )

                if course_info and len(course_info) > 0:
                    current_summary = course_info[0].get("summary", "")

                    # Format assignment details for course summary
                    due_info = f" (Due: {duedate})" if duedate > 0 else ""
                    assignment_content = (
                        f"\n\n**ASSIGNMENT: {name}**{due_info}\n"
                        f"{intro}\n"
                        f"Max Grade: {grade} points\n"
                        f"Section: {section}"
                    )
                    updated_summary = current_summary + assignment_content

                    await client.call_webservice(
                        "core_course_update_courses",
                        courses=[
                            {
                                "id": course_id,
                                "summary": updated_summary,
                                "summaryformat": 1,
                            }
                        ],
                    )

                    return [
                        types.TextContent(
                            type="text",
                            text=f"⚠️ Assignment web service creation failed.\n"
                            f"📝 Added assignment '{name}' to course description as fallback.\n"
                            f"Course ID: {course_id}\n"
                            f"Section: {section}\n"
                            f"Max Grade: {grade}\n\n"
                            f"💡 To enable full assignment creation, configure:\n"
                            f"• Site Administration → Server → Web services → External services\n"
                            f"• Add 'core_course_create_modules' to your web service\n"
                            f"• Original error: {primary_error}",
                        )
                    ]

            except Exception as fallback_error:
                logger.error(f"Assignment fallback failed: {fallback_error}")

            # Final error message with solution
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Failed to create assignment: {primary_error}\n\n"
                    f"🔧 **SOLUTION REQUIRED:**\n"
                    f"1. Go to: Site Administration → Server → Web services → External services\n"
                    f"2. Find your MoodleClaude web service\n"
                    f"3. Add these functions:\n"
                    f"   • core_course_create_modules\n"
                    f"   • core_course_update_courses\n"
                    f"4. Save and try again\n\n"
                    f"Assignment: '{name}' in course {course_id}, section {section}, grade {grade}",
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

        # Try primary method: core_course_create_modules with forum module
        try:
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
                raise Exception("No result returned from core_course_create_modules")

        except Exception as primary_error:
            # Fallback: Add forum info to course summary
            logger.warning(f"Primary forum creation failed: {primary_error}")

            try:
                course_info = await client.call_webservice(
                    "core_course_get_courses", options={"ids": [course_id]}
                )

                if course_info and len(course_info) > 0:
                    current_summary = course_info[0].get("summary", "")

                    # Format forum details for course summary
                    forum_content = (
                        f"\n\n**FORUM: {name}** ({forum_type})\n"
                        f"{intro}\n"
                        f"Section: {section}"
                    )
                    updated_summary = current_summary + forum_content

                    await client.call_webservice(
                        "core_course_update_courses",
                        courses=[
                            {
                                "id": course_id,
                                "summary": updated_summary,
                                "summaryformat": 1,
                            }
                        ],
                    )

                    return [
                        types.TextContent(
                            type="text",
                            text=f"⚠️ Forum web service creation failed.\n"
                            f"📝 Added forum '{name}' to course description as fallback.\n"
                            f"Course ID: {course_id}\n"
                            f"Section: {section}\n"
                            f"Type: {forum_type}\n\n"
                            f"💡 To enable full forum creation, configure:\n"
                            f"• Site Administration → Server → Web services → External services\n"
                            f"• Add 'core_course_create_modules' to your web service\n"
                            f"• Original error: {primary_error}",
                        )
                    ]

            except Exception as fallback_error:
                logger.error(f"Forum fallback failed: {fallback_error}")

            # Final error message with solution
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Failed to create forum: {primary_error}\n\n"
                    f"🔧 **SOLUTION REQUIRED:**\n"
                    f"1. Go to: Site Administration → Server → Web services → External services\n"
                    f"2. Find your MoodleClaude web service\n"
                    f"3. Add these functions:\n"
                    f"   • core_course_create_modules\n"
                    f"   • core_course_update_courses\n"
                    f"4. Save and try again\n\n"
                    f"Forum: '{name}' ({forum_type}) in course {course_id}, section {section}",
                )
            ]

    except Exception as e:
        return [
            types.TextContent(type="text", text=f"❌ Failed to create forum: {str(e)}")
        ]


async def handle_diagnose_webservices(
    arguments: Dict[str, Any],
) -> List[types.TextContent]:
    """Diagnose available web service functions and configuration."""
    try:
        client = await get_moodle_client(use_enhanced=True)

        # Get site info and available functions
        site_info = await client.call_webservice("core_webservice_get_site_info")

        # Extract available functions
        functions = site_info.get("functions", [])
        available_functions = [func.get("name", "") for func in functions]

        # Check for required functions
        required_functions = [
            "core_course_create_modules",
            "core_course_update_courses",
            "local_wsmanagesections_create_sections",
            "local_wsmanagesections_update_sections",
            "core_course_get_courses",
            "core_course_create_courses",
        ]

        # Check availability
        function_status = {}
        for func in required_functions:
            function_status[func] = (
                "✅ Available" if func in available_functions else "❌ Missing"
            )

        # Build diagnostic report
        report = f"🔍 **MOODLE WEB SERVICE DIAGNOSTIC REPORT**\n\n"
        report += f"**Site Information:**\n"
        report += f"• Site Name: {site_info.get('sitename', 'Unknown')}\n"
        report += f"• Version: {site_info.get('release', 'Unknown')}\n"
        report += f"• User: {site_info.get('username', 'Unknown')}\n"
        report += f"• Total Functions Available: {len(available_functions)}\n\n"

        report += f"**Required Function Status:**\n"
        for func, status in function_status.items():
            report += f"• {func}: {status}\n"

        # Count missing functions
        missing_functions = [
            func for func, status in function_status.items() if "Missing" in status
        ]

        if missing_functions:
            report += f"\n❌ **{len(missing_functions)} FUNCTIONS MISSING**\n\n"
            report += f"**🔧 CONFIGURATION REQUIRED:**\n"
            report += f"1. Go to: Site Administration → Server → Web services → External services\n"
            report += f"2. Find or create your MoodleClaude web service\n"
            report += f"3. Add these missing functions:\n"
            for func in missing_functions:
                report += f"   • {func}\n"
            report += f"4. Save configuration\n"
            report += f"5. Test again with this diagnostic tool\n\n"
        else:
            report += f"\n✅ **ALL REQUIRED FUNCTIONS AVAILABLE**\n"
            report += (
                f"Your Moodle installation is properly configured for MoodleClaude!\n\n"
            )

        # Add troubleshooting section
        report += f"**🛠️ TROUBLESHOOTING:**\n"
        report += f"• If functions are missing, check web service configuration\n"
        report += f"• Ensure your user has 'webservice/rest:use' capability\n"
        report += f"• For section management, install local_wsmanagesections plugin\n"
        report += f"• Test basic functions like 'get_courses' first\n"

        return [types.TextContent(type="text", text=report)]

    except Exception as e:
        error_report = f"❌ **DIAGNOSTIC FAILED**\n\n"
        error_report += f"Error: {str(e)}\n\n"
        error_report += f"**Possible Issues:**\n"
        error_report += f"• Web services not enabled\n"
        error_report += f"• Invalid token or credentials\n"
        error_report += f"• Network connectivity issues\n"
        error_report += f"• Moodle site not accessible\n\n"
        error_report += f"**Basic Checks:**\n"
        error_report += f"1. Verify MOODLE_URL is correct\n"
        error_report += f"2. Check MOODLE_TOKEN_ENHANCED is valid\n"
        error_report += f"3. Test 'test_connection' tool first\n"

        return [types.TextContent(type="text", text=error_report)]


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
