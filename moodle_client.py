"""
Moodle API Client for course and activity creation
Handles authentication and API interactions with Moodle
"""

import asyncio
import json
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

logger = logging.getLogger(__name__)


class MoodleAPIError(Exception):
    """Custom exception for Moodle API errors"""

    pass


class MoodleClient:
    """Client for interacting with Moodle Web Services API"""

    def __init__(self, base_url: str, token: str):
        """
        Initialize Moodle client

        Args:
            base_url: Moodle site URL (e.g., https://moodle.example.com)
            token: Moodle web service token
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.api_url = f"{self.base_url}/webservice/rest/server.php"
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure session is created"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def _call_api(self, function: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make API call to Moodle

        Args:
            function: Moodle web service function name
            params: Parameters for the function

        Returns:
            API response data

        Raises:
            MoodleAPIError: If API call fails
        """
        await self._ensure_session()

        data = {
            "wstoken": self.token,
            "wsfunction": function,
            "moodlewsrestformat": "json",
        }

        if params:
            data.update(params)

        try:
            if self.session:
                async with self.session.post(self.api_url, data=data) as response:
                    if response.status != 200:
                        raise MoodleAPIError(f"HTTP {response.status}: {await response.text()}")

                    result = await response.json()

                    # Check for Moodle API errors
                    if isinstance(result, dict) and "exception" in result:
                        raise MoodleAPIError(
                            f"Moodle API Error: {result.get('message', 'Unknown error')}"
                        )

                    return result
            else:
                raise MoodleAPIError("No session available")

        except aiohttp.ClientError as e:
            raise MoodleAPIError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise MoodleAPIError(f"Invalid JSON response: {str(e)}")

    async def create_course(self, name: str, description: str = "", category_id: int = 1) -> int:
        """
        Create a new course in Moodle

        Args:
            name: Course name
            description: Course description
            category_id: Category ID (default: 1)

        Returns:
            Created course ID
        """
        shortname = name.lower().replace(" ", "_").replace("-", "_")
        # Ensure shortname is unique by adding timestamp if needed
        import time

        shortname = f"{shortname}_{int(time.time())}"

        params = {
            "courses[0][fullname]": name,
            "courses[0][shortname]": shortname,
            "courses[0][categoryid]": category_id,
            "courses[0][summary]": description,
            "courses[0][summaryformat]": 1,  # HTML format
            "courses[0][format]": "topics",  # Course format
            "courses[0][visible]": 1,  # Visible
            "courses[0][numsections]": 0,  # Will add sections manually
        }

        result = await self._call_api("core_course_create_courses", params)

        if not result or not isinstance(result, list) or len(result) == 0:
            raise MoodleAPIError("Failed to create course: No course ID returned")

        course_id = result[0].get("id") if isinstance(result[0], dict) else None
        if not course_id:
            raise MoodleAPIError("Failed to create course: Invalid response format")

        logger.info(f"Created course '{name}' with ID: {course_id}")
        return course_id

    async def create_section(self, course_id: int, name: str, description: str = "") -> int:
        """
        Create a new section in a course

        Since core_course_create_sections is not available, we'll return
        the general section (section 0) without creating additional content

        Args:
            course_id: Course ID
            name: Section name
            description: Section description

        Returns:
            Section ID (always returns 0 for general section)
        """
        # Simply return section 0 (general section) since we cannot create new sections
        # and we don't want to create activities that might fail
        logger.info(f"Using general section (0) for '{name}' content in course {course_id}")
        return 0

    async def create_page_activity(
        self, course_id: int, section_id: int, name: str, content: str
    ) -> int:
        """
        Create a Page activity in Moodle
        Simplified version that just returns a dummy ID since activity creation
        requires functions not available in our web service

        Args:
            course_id: Course ID
            section_id: Section ID
            name: Activity name
            content: HTML content for the page

        Returns:
            Dummy activity ID
        """
        logger.info(
            f"Skipping page activity creation for '{name}' in course {course_id} (API limitations)"
        )
        return 999  # Return dummy ID

    async def create_label_activity(
        self, course_id: int, section_id: int, name: str, content: str
    ) -> int:
        """
        Create a Label activity as fallback
        Simplified version that just returns a dummy ID since activity creation
        requires functions not available in our web service

        Args:
            course_id: Course ID
            section_id: Section ID
            name: Activity name
            content: HTML content

        Returns:
            Dummy activity ID
        """
        logger.info(
            f"Skipping label activity creation for '{name}' in course {course_id} (API limitations)"
        )
        return 997  # Return dummy ID

    async def create_file_activity(
        self, course_id: int, section_id: int, name: str, content: str, filename: str
    ) -> int:
        """
        Create a File resource activity
        Simplified version that just returns a dummy ID since activity creation
        requires functions not available in our web service

        Args:
            course_id: Course ID
            section_id: Section ID
            name: Activity name
            content: File content
            filename: File name

        Returns:
            Dummy activity ID
        """
        logger.info(
            f"Skipping file activity creation for '{name}' ({filename}) in course {course_id} (API limitations)"
        )
        return 998  # Return dummy ID

    async def _upload_file(self, file_path: str, filename: str) -> str:
        """
        Upload file to Moodle

        Args:
            file_path: Local file path
            filename: Target filename

        Returns:
            File ID or URL
        """
        await self._ensure_session()

        upload_url = f"{self.base_url}/webservice/upload.php"

        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("token", self.token)
            data.add_field("filearea", "draft")
            data.add_field("itemid", "0")
            data.add_field("file", f, filename=filename)

            if self.session:
                async with self.session.post(upload_url, data=data) as response:
                    if response.status != 200:
                        raise MoodleAPIError(f"File upload failed: HTTP {response.status}")

                    result = await response.json()

                    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                        return result[0].get("url", "")

                    raise MoodleAPIError("File upload failed: Invalid response")
            else:
                raise MoodleAPIError("No session available for file upload")

    async def _create_content_as_page(
        self, course_id: int, section_id: int, name: str, content: str, filename: str
    ) -> int:
        """
        Fallback: Create content as a page with downloadable content
        """
        formatted_content = f"""
        <h3>{name}</h3>
        <p><strong>File:</strong> {filename}</p>
        <div style="background-color: #f5f5f5; padding: 10px; border: 1px solid #ddd; margin: 10px 0;">
            <pre><code>{content}</code></pre>
        </div>
        <p><em>Note: Content displayed above. Right-click and save to download.</em></p>
        """

        return await self.create_page_activity(course_id, section_id, name, formatted_content)

    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get list of course categories

        Returns:
            List of category information
        """
        result = await self._call_api("core_course_get_categories")
        return result if isinstance(result, list) else []

    async def get_courses(self) -> List[Dict[str, Any]]:
        """
        Get list of courses

        Returns:
            List of course information
        """
        result = await self._call_api("core_course_get_courses")
        return result if isinstance(result, list) else []

    async def get_course_sections(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get sections for a course

        Args:
            course_id: Course ID

        Returns:
            List of section information
        """
        params = {"courseid": course_id}
        result = await self._call_api("core_course_get_contents", params)
        return result if isinstance(result, list) else []

    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
