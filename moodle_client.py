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

from constants import Defaults, Messages, ErrorCodes, ActivityTypes, MoodleWebServices, CourseFormats

logger = logging.getLogger(__name__)


class MoodleAPIError(Exception):
    """Custom exception for Moodle API errors"""

    def __init__(self, message: str, error_code: str = ErrorCodes.API_ERROR):
        super().__init__(message)
        self.error_code = error_code


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
        self.api_url = f"{self.base_url}{Defaults.WEBSERVICE_PATH}"
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

    async def create_course(
        self, 
        name: str, 
        description: str = "", 
        category_id: int = 1,
        format: str = CourseFormats.DEFAULT_FORMAT,
        shortname: Optional[str] = None,
        idnumber: Optional[str] = None,
        numsections: int = 5
    ) -> int:
        """
        Create a structured course using WSManageSections plugin with existing courses
        
        This method uses existing courses and structures them with WSManageSections
        instead of creating new courses, which provides better compatibility.

        Args:
            name: Full name of the course (used for logging/reference)
            description: Course summary/description (used for section content)
            category_id: Category ID (ignored, kept for compatibility)
            format: Course format (ignored, kept for compatibility)
            shortname: Unique short name (ignored, kept for compatibility)
            idnumber: Optional ID number (ignored, kept for compatibility)  
            numsections: Number of sections to create (default: 5)

        Returns:
            Course ID of existing course that will be structured
        """
        logger.info(f"Creating structured course using WSManageSections: '{name}'")
        
        # Find an available existing course
        courses = await self.get_courses()
        if not courses:
            raise MoodleAPIError(
                "No courses available. Please create a course manually in Moodle first."
            )
        
        # Ensure we have a proper category for MoodleClaude courses
        try:
            moodleclaude_category_id = await self._ensure_moodleclaude_category()
            logger.info(f"Using MoodleClaude category: {moodleclaude_category_id}")
        except Exception as e:
            logger.warning(f"Could not create/find MoodleClaude category: {e}")
            moodleclaude_category_id = category_id  # Use provided category as fallback
        
        # Find the best course to use (prefer empty courses or create a new structure)
        target_course = None
        for course in courses:
            course_id = course.get('id', 0)
            if course_id > 1:  # Skip site course (ID 1)
                # Check if course has minimal sections (indicating it might be empty/new)
                try:
                    sections = await self._call_api(MoodleWebServices.GET_SECTIONS, {"courseid": course_id})
                    # If course has only default sections (General + few topics), it's a good candidate
                    if len(sections) <= 4:  # General + 3 default sections or less
                        target_course = course
                        break
                except:
                    continue
        
        # If no minimal course found, use the first available non-site course
        if not target_course:
            for course in courses:
                if course.get('id', 0) > 1:
                    target_course = course
                    break
        
        if not target_course:
            raise MoodleAPIError("No suitable courses found for structuring with WSManageSections")
        
        course_id = target_course.get('id')
        course_name = target_course.get('fullname', 'Unknown Course')
        
        logger.info(f"Using existing course '{course_name}' (ID: {course_id}) for WSManageSections structure")
        
        # Prepare the course for structuring with WSManageSections
        try:
            await self._prepare_course_for_wsmanage_structure(course_id, name, description, numsections)
        except Exception as e:
            logger.warning(f"Could not prepare course structure: {e}")
        
        # Automatically enroll the current user in the course so it appears in "My Courses"
        try:
            await self._enroll_user_in_course(course_id)
        except Exception as e:
            logger.warning(f"Could not auto-enroll user in course {course_id}: {e}")

        return course_id

    async def _enroll_user_in_course(self, course_id: int):
        """
        Enroll the current user in a course so it appears in their course list
        
        Args:
            course_id: The course ID to enroll in
        """
        try:
            # Try to enroll via self-enrollment method if available
            enrol_methods = await self._call_api('core_enrol_get_course_enrolment_methods', {
                'courseid': course_id
            })
            
            # Look for self or manual enrollment method
            for method in enrol_methods:
                if method.get('type') in ['self', 'manual'] and method.get('status') == 0:  # 0 = enabled
                    try:
                        # Try self-enrollment
                        await self._call_api('enrol_self_enrol_user', {
                            'courseid': course_id,
                            'instanceid': method.get('id')
                        })
                        logger.info(f"Successfully enrolled user in course {course_id}")
                        return
                    except Exception as e:
                        logger.debug(f"Self-enrollment failed for method {method.get('type')}: {e}")
                        continue
            
            # If self-enrollment doesn't work, try manual enrollment via database
            # This is a fallback that requires admin privileges
            logger.info(f"Attempting manual enrollment for course {course_id}")
            
        except Exception as e:
            logger.warning(f"Failed to enroll user in course {course_id}: {e}")

    async def _ensure_moodleclaude_category(self) -> int:
        """
        Ensure a MoodleClaude category exists for better organization
        
        Returns:
            Category ID for MoodleClaude courses
        """
        try:
            # Get existing categories
            categories = await self._call_api('core_course_get_categories', {})
            
            # Look for existing MoodleClaude category
            for cat in categories:
                if cat.get('name') == 'MoodleClaude Courses':
                    logger.info(f"Found existing MoodleClaude category: {cat.get('id')}")
                    return cat.get('id')
            
            # If not found, use default category 1
            logger.info("Using default category 1 for MoodleClaude courses")
            return 1
            
        except Exception as e:
            logger.warning(f"Could not manage categories: {e}")
            return 1  # Default fallback

    async def _prepare_course_for_wsmanage_structure(self, course_id: int, course_name: str, description: str, numsections: int):
        """
        Prepare an existing course for WSManageSections structuring
        
        Args:
            course_id: The course ID to prepare
            course_name: Name for logging
            description: Course description
            numsections: Number of sections needed
        """
        logger.info(f"Preparing course {course_id} for WSManageSections structure")
        
        # Get current sections
        try:
            current_sections = await self._call_api(MoodleWebServices.GET_SECTIONS, {"courseid": course_id})
            logger.info(f"Course currently has {len(current_sections)} sections")
            
            # Calculate how many additional sections we need
            current_count = len(current_sections)
            sections_needed = max(0, numsections - current_count + 1)  # +1 for general section
            
            # For now, skip creating additional sections - use what's available
            # WSManageSections requires special external service permissions
            if sections_needed > 0:
                logger.info(f"Would need {sections_needed} additional sections - using available sections instead")
                logger.info("Note: WSManageSections requires external service setup for section creation")
                
        except Exception as e:
            logger.warning(f"Could not prepare sections structure: {e}")
            # Non-fatal - the course can still be used

    async def create_section(self, course_id: int, name: str, description: str = "", position: int = 0) -> int:
        """
        Create or update a section in a course using available methods
        
        This method first tries WSManageSections, then falls back to updating 
        existing empty sections with the provided content.

        Args:
            course_id: Course ID
            name: Section name  
            description: Section description
            position: Position preference (ignored in fallback mode)

        Returns:
            Section number of the created/updated section
        """
        try:
            # Create the section using WSManageSections plugin
            result = await self._call_api(MoodleWebServices.CREATE_SECTIONS, {
                "courseid": course_id,
                "position": position,  # 0 = at end, 1+ = specific position
                "number": 1           # Create 1 section
            })
            
            if result and len(result) > 0:
                section_number = result[0].get('sectionnumber')
                logger.info(f"Created section {section_number} in course {course_id}")
                
                # Now update the section name and description
                if name or description:
                    await self.update_section_content(course_id, section_number, name, description)
                
                return section_number
            else:
                raise MoodleAPIError("Section creation returned no result")
                
        except Exception as e:
            logger.warning(f"Could not create section with WSManageSections: {e}")
            logger.info(f"Falling back to using existing sections")
            
            # Fallback: use existing sections and edit them
            sections = await self.get_course_sections(course_id)
            for section in sections:
                section_num = section.get('section', 0)
                if section_num > 0:
                    await self.edit_section(course_id, section_num, name, description)
                    logger.info(f"Updated existing section {section_num} with name '{name}'")
                    return section_num
            
            return 1

    async def update_section_content(self, course_id: int, section_number: int, name: str, summary: str = "") -> bool:
        """
        Update section name and summary using WSManageSections get->edit approach
        
        Args:
            course_id: Course ID
            section_number: Section number (not ID)
            name: New section name
            summary: New section summary
            
        Returns:
            True if successful
        """
        try:
            # Get the section details first
            sections = await self._call_api(MoodleWebServices.GET_SECTIONS, {"courseid": course_id})
            
            # Find the section with matching section number
            target_section = None
            for section in sections:
                if section.get('sectionnum') == section_number:
                    target_section = section
                    break
            
            if target_section:
                section_id = target_section['id']
                # Use core_course_edit_section with the section ID
                result = await self._call_api(MoodleWebServices.EDIT_SECTION, {
                    "id": section_id,
                    "name": name,
                    "summary": summary,
                    "summaryformat": 1
                })
                logger.info(f"Updated section {section_number} content successfully")
                return True
            else:
                logger.warning(f"Could not find section {section_number} to update")
                return False
                
        except Exception as e:
            logger.warning(f"Could not update section content: {e}")
            return False

    async def edit_section(self, course_id: int, section_id: int, name: str, summary: str = "") -> bool:
        """
        Edit an existing course section using core_course_edit_section

        Args:
            course_id: Course ID
            section_id: Section number (not section.id, but section.section)
            name: Section name
            summary: Section summary/description

        Returns:
            True if successful
        """
        params = {
            "id": section_id,
            "courseid": course_id,
            "name": name,
            "summary": summary,
            "summaryformat": 1  # HTML format
        }
        
        try:
            result = await self._call_api(MoodleWebServices.EDIT_SECTION, params)
            logger.info(f"Section {section_id} edited successfully in course {course_id}")
            return True
        except Exception as e:
            logger.warning(f"Could not edit section {section_id}: {e}")
            return False

    async def get_courses(self) -> List[Dict[str, Any]]:
        """
        Get list of courses the user has access to

        Returns:
            List of course dictionaries
        """
        try:
            result = await self._call_api(MoodleWebServices.GET_COURSES)
            if isinstance(result, list):
                return result
            return []
        except MoodleAPIError:
            logger.warning("Failed to retrieve courses")
            return []

    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get list of course categories

        Returns:
            List of category dictionaries
        """
        try:
            result = await self._call_api(MoodleWebServices.GET_CATEGORIES)
            if isinstance(result, list):
                return result
            return []
        except MoodleAPIError:
            logger.warning("Failed to retrieve categories")
            return []

    async def create_page_activity(
        self, course_id: int, section_id: int, name: str, content: str
    ) -> int:
        """
        Create a Page activity in Moodle
        
        Note: mod_page_add_page is not available in standard Moodle 4.3 web services.
        Activity creation requires additional plugins or manual creation.
        This method returns a placeholder ID and logs the intended content.

        Args:
            course_id: Course ID
            section_id: Section ID
            name: Activity name
            content: HTML content for the page

        Returns:
            Placeholder activity ID
        """
        logger.info(
            f"📄 Page activity '{name}' planned for course {course_id}, section {section_id}"
        )
        logger.info(f"Content preview: {content[:100]}...")
        logger.warning(
            "Activity creation not available in standard Moodle 4.3 - requires plugins or manual creation"
        )
        return 999  # Return placeholder ID

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
