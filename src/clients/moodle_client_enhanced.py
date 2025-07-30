"""
Enhanced Moodle API Client using custom MoodleClaude plugin
Provides full content creation capabilities with real activity storage
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

from src.core.constants import Defaults, Messages, ErrorCodes, ActivityTypes, MoodleWebServices, CourseFormats

logger = logging.getLogger(__name__)


class MoodleAPIError(Exception):
    """Custom exception for Moodle API errors"""

    def __init__(self, message: str, error_code: str = ErrorCodes.API_ERROR):
        super().__init__(message)
        self.error_code = error_code


class EnhancedMoodleClient:
    """Enhanced client for interacting with Moodle using custom MoodleClaude plugin"""

    def __init__(self, base_url: str, token: str):
        """
        Initialize Enhanced Moodle client

        Args:
            base_url: Moodle site URL (e.g., https://moodle.example.com)
            token: Moodle web service token
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.api_url = f"{self.base_url}{Defaults.WEBSERVICE_PATH}"
        self.session = None
        self.plugin_available = None  # Will be determined on first use

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
    
    def _flatten_params(self, params: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """
        Flatten nested parameters for Moodle API format
        
        Converts:
            {'sections': [{'name': 'test', 'activities': []}]}
        To:
            {'sections[0][name]': 'test', 'sections[0][activities]': []}
        """
        items = []
        
        if isinstance(params, dict):
            for k, v in params.items():
                new_key = f"{parent_key}[{k}]" if parent_key else k
                
                if isinstance(v, list):
                    for i, item in enumerate(v):
                        list_key = f"{new_key}[{i}]"
                        if isinstance(item, dict):
                            items.extend(self._flatten_params(item, list_key).items())
                        else:
                            items.append((list_key, item))
                    # Also add the empty array indicator if list is empty
                    if not v:
                        items.append((new_key, []))
                elif isinstance(v, dict):
                    items.extend(self._flatten_params(v, new_key).items())
                else:
                    items.append((new_key, v))
        
        return dict(items)

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
            # Functions that need parameter flattening for complex structures
            flatten_functions = [
                'local_moodleclaude_create_course_structure',
                'core_course_create_courses',  # Also used for courses array
            ]
            
            if function in flatten_functions:
                flattened_params = self._flatten_params(params)
                data.update(flattened_params)
            else:
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

    async def _check_plugin_availability(self) -> bool:
        """
        Check if the MoodleClaude plugin is available
        
        Returns:
            True if plugin functions are available
        """
        if self.plugin_available is not None:
            return self.plugin_available
            
        try:
            # Try to get site info to see available functions
            site_info = await self._call_api("core_webservice_get_site_info", {})
            if 'functions' in site_info:
                functions = [f.get('name', '') for f in site_info['functions']]
                self.plugin_available = 'local_moodleclaude_create_page_activity' in functions
                if self.plugin_available:
                    logger.info("✅ MoodleClaude plugin detected - using enhanced functionality")
                else:
                    logger.warning("⚠️ MoodleClaude plugin not found - falling back to limited functionality")
                return self.plugin_available
        except Exception as e:
            logger.warning(f"Could not check plugin availability: {e}")
            
        self.plugin_available = False
        return False

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
        Create a new course in Moodle with the given parameters
        
        This method creates an actual new course with proper sequential ID assignment.
        Implementation is the same as the original client.
        """
        logger.info(f"Creating new course: '{name}'")
        
        # Generate unique shortname if not provided
        if not shortname:
            timestamp = int(time.time())
            safe_name = "".join(c for c in name.lower()[:30] if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            shortname = f"{safe_name}_{timestamp}"
        
        # Prepare course creation parameters
        course_params = {
            'courses[0][fullname]': name,
            'courses[0][shortname]': shortname,
            'courses[0][categoryid]': category_id,
            'courses[0][summary]': description,
            'courses[0][summaryformat]': 1,  # HTML format
            'courses[0][format]': format,
            'courses[0][numsections]': numsections,
            'courses[0][visible]': 1,  # Make course visible
            'courses[0][startdate]': int(time.time()),  # Start today
        }
        
        # Add optional parameters
        if idnumber:
            course_params['courses[0][idnumber]'] = idnumber
        
        try:
            # Create the course using core_course_create_courses
            result = await self._call_api('core_course_create_courses', course_params)
            
            if not result or len(result) == 0:
                raise MoodleAPIError("Course creation returned no result")
            
            # Extract the new course ID
            new_course = result[0] if isinstance(result, list) else result
            course_id = new_course.get('id')
            
            if not course_id:
                raise MoodleAPIError("Course creation did not return a valid course ID")
            
            logger.info(f"✅ Successfully created new course '{name}' with ID: {course_id}")
            
            # Auto-enroll current user
            try:
                await self._enroll_user_in_course(course_id)
            except Exception as e:
                logger.warning(f"Could not auto-enroll user in course {course_id}: {e}")

            return course_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create course '{name}': {e}")
            raise MoodleAPIError(f"Failed to create course: {str(e)}")

    async def _enroll_user_in_course(self, course_id: int):
        """Enroll the current user in a course (same as original implementation)"""
        try:
            current_user = await self._get_current_user()
            if not current_user:
                logger.warning("Could not determine current user for enrollment")
                return
                
            user_id = current_user.get('userid')
            username = current_user.get('username', 'unknown')
            
            logger.info(f"Enrolling user {username} (ID: {user_id}) in course {course_id}")
            
            # Try self-enrollment
            enrol_methods = await self._call_api('core_enrol_get_course_enrolment_methods', {
                'courseid': course_id
            })
            
            for method in enrol_methods:
                if method.get('type') in ['self', 'manual'] and method.get('status') == 0:
                    try:
                        await self._call_api('enrol_self_enrol_user', {
                            'courseid': course_id,
                            'instanceid': method.get('id')
                        })
                        logger.info(f"Successfully enrolled user {username} in course {course_id}")
                        return
                    except Exception as e:
                        logger.debug(f"Self-enrollment failed: {e}")
                        continue
            
        except Exception as e:
            logger.warning(f"Failed to enroll user in course {course_id}: {e}")

    async def _get_current_user(self) -> Dict[str, Any]:
        """Get current user information from the token"""
        try:
            site_info = await self._call_api('core_webservice_get_site_info')
            return site_info
        except Exception as e:
            logger.warning(f"Could not get current user info: {e}")
            return {}

    async def create_section(self, course_id: int, name: str, description: str = "", position: int = 0) -> int:
        """
        Create or update a section in a course
        
        Uses WSManageSections plugin if available, falls back to existing sections
        """
        try:
            # Try WSManageSections first
            result = await self._call_api(MoodleWebServices.CREATE_SECTIONS, {
                "courseid": course_id,
                "position": position,
                "number": 1
            })
            
            if result and len(result) > 0:
                section_number = result[0].get('sectionnumber')
                logger.info(f"Created section {section_number} in course {course_id}")
                
                # Update section content if plugin is available
                if await self._check_plugin_availability():
                    await self.update_section_content(course_id, section_number, name, description)
                
                return section_number
            else:
                raise MoodleAPIError("Section creation returned no result")
                
        except Exception as e:
            logger.warning(f"Could not create section with WSManageSections: {e}")
            logger.info(f"Using existing sections")
            
            # Fallback: use existing sections
            return position if position > 0 else 1

    async def update_section_content(self, course_id: int, section_number: int, name: str, summary: str = "") -> bool:
        """
        Update section content using plugin if available
        
        Args:
            course_id: Course ID
            section_number: Section number
            name: Section name
            summary: Section summary
            
        Returns:
            True if successful, False if plugin not available
        """
        if not await self._check_plugin_availability():
            logger.info(f"📝 Section {section_number} content (plugin required for storage):")
            logger.info(f"   Name: '{name}'")
            logger.info(f"   Summary length: {len(summary)} characters")
            return False
            
        try:
            result = await self._call_api('local_moodleclaude_update_section_content', {
                'courseid': course_id,
                'section': section_number,
                'name': name,
                'summary': summary
            })
            
            if result.get('success'):
                logger.info(f"✅ Section {section_number} updated successfully")
                return True
            else:
                logger.warning(f"❌ Section update failed: {result.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating section {section_number}: {e}")
            return False

    async def create_page_activity(
        self, course_id: int, section_id: int, name: str, content: str
    ) -> Dict[str, Any]:
        """
        Create a Page activity using plugin if available
        
        Args:
            course_id: Course ID
            section_id: Section number (not database ID)
            name: Activity name
            content: HTML content for the page

        Returns:
            Dict with success status and details
        """
        logger.info(f"📄 Creating page activity '{name}' for course {course_id}, section {section_id}")
        
        if not await self._check_plugin_availability():
            # Fallback to old behavior
            logger.warning(f"❌ Plugin not available - cannot create real page activity")
            return {
                "success": False,
                "method": "plugin_required",
                "activity_id": None,
                "message": f"MoodleClaude plugin required for page activity creation"
            }
        
        try:
            result = await self._call_api('local_moodleclaude_create_page_activity', {
                'courseid': course_id,
                'section': section_id,
                'name': name,
                'content': content,
                'intro': f'Page activity created by MoodleClaude'
            })
            
            if result.get('success'):
                logger.info(f"✅ Page activity '{name}' created successfully")
                return {
                    "success": True,
                    "method": "plugin_api",
                    "activity_id": result.get('activityid'),
                    "cm_id": result.get('cmid'),
                    "message": result.get('message', 'Page activity created successfully')
                }
            else:
                logger.warning(f"❌ Page activity creation failed: {result.get('message')}")
                return {
                    "success": False,
                    "method": "plugin_api",
                    "activity_id": None,
                    "message": result.get('message', 'Page activity creation failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating page activity '{name}': {e}")
            return {
                "success": False,
                "method": "plugin_api",
                "activity_id": None,
                "message": f"Error: {str(e)}"
            }

    async def create_label_activity(
        self, course_id: int, section_id: int, content: str
    ) -> Dict[str, Any]:
        """
        Create a Label activity using plugin if available
        
        Args:
            course_id: Course ID
            section_id: Section number
            content: HTML content

        Returns:
            Dict with success status and details
        """
        logger.info(f"🏷️ Creating label activity for course {course_id}, section {section_id}")
        
        if not await self._check_plugin_availability():
            logger.warning(f"❌ Plugin not available - cannot create real label activity")
            return {
                "success": False,
                "method": "plugin_required",
                "activity_id": None,
                "message": f"MoodleClaude plugin required for label activity creation"
            }
        
        try:
            result = await self._call_api('local_moodleclaude_create_label_activity', {
                'courseid': course_id,
                'section': section_id,
                'content': content
            })
            
            if result.get('success'):
                logger.info(f"✅ Label activity created successfully")
                return {
                    "success": True,
                    "method": "plugin_api",
                    "activity_id": result.get('activityid'),
                    "cm_id": result.get('cmid'),
                    "message": result.get('message', 'Label activity created successfully')
                }
            else:
                logger.warning(f"❌ Label activity creation failed: {result.get('message')}")
                return {
                    "success": False,
                    "method": "plugin_api",
                    "activity_id": None,
                    "message": result.get('message', 'Label activity creation failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating label activity: {e}")
            return {
                "success": False,
                "method": "plugin_api",
                "activity_id": None,
                "message": f"Error: {str(e)}"
            }

    async def create_file_activity(
        self, course_id: int, section_id: int, name: str, content: str, filename: str
    ) -> Dict[str, Any]:
        """
        Create a File resource using plugin if available
        
        Args:
            course_id: Course ID
            section_id: Section number
            name: Resource name
            content: File content
            filename: File name

        Returns:
            Dict with success status and details
        """
        logger.info(f"📄 Creating file resource '{name}' ({filename}) for course {course_id}, section {section_id}")
        
        if not await self._check_plugin_availability():
            logger.warning(f"❌ Plugin not available - cannot create real file resource")
            return {
                "success": False,
                "method": "plugin_required",
                "activity_id": None,
                "message": f"MoodleClaude plugin required for file resource creation"
            }
        
        try:
            result = await self._call_api('local_moodleclaude_create_file_resource', {
                'courseid': course_id,
                'section': section_id,
                'name': name,
                'filename': filename,
                'content': content,
                'intro': f'File resource created by MoodleClaude'
            })
            
            if result.get('success'):
                logger.info(f"✅ File resource '{name}' created successfully")
                return {
                    "success": True,
                    "method": "plugin_api",
                    "activity_id": result.get('activityid'),
                    "cm_id": result.get('cmid'),
                    "file_id": result.get('fileid'),
                    "message": result.get('message', 'File resource created successfully')
                }
            else:
                logger.warning(f"❌ File resource creation failed: {result.get('message')}")
                return {
                    "success": False,
                    "method": "plugin_api",
                    "activity_id": None,
                    "message": result.get('message', 'File resource creation failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating file resource '{name}': {e}")
            return {
                "success": False,
                "method": "plugin_api",
                "activity_id": None,
                "message": f"Error: {str(e)}"
            }

    async def create_course_structure(self, course_id: int, sections_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create complete course structure using plugin if available
        
        Args:
            course_id: Course ID
            sections_data: List of section dictionaries with activities
            
        Returns:
            Dict with creation results
        """
        logger.info(f"🏗️ Creating course structure for course {course_id} with {len(sections_data)} sections")
        
        if not await self._check_plugin_availability():
            logger.warning(f"❌ Plugin not available - using individual API calls")
            # Fall back to individual calls
            return await self._create_structure_individually(course_id, sections_data)
        
        try:
            result = await self._call_api('local_moodleclaude_create_course_structure', {
                'courseid': course_id,
                'sections': sections_data
            })
            
            if result.get('success'):
                logger.info(f"✅ Course structure created successfully")
                return result
            else:
                logger.warning(f"❌ Course structure creation failed: {result.get('message')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Error creating course structure: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "sections": []
            }

    async def _create_structure_individually(self, course_id: int, sections_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fallback method to create structure using individual API calls
        """
        results = []
        section_num = 1
        
        for section_data in sections_data:
            section_result = {
                'sectionnumber': section_num,
                'sectionname': section_data['name'],
                'success': False,
                'activities': [],
                'message': ''
            }
            
            try:
                # Update section
                section_success = await self.update_section_content(
                    course_id, section_num, 
                    section_data['name'], 
                    section_data.get('summary', '')
                )
                
                if section_success:
                    section_result['success'] = True
                    section_result['message'] = 'Section updated successfully'
                    
                    # Create activities
                    for activity_data in section_data.get('activities', []):
                        activity_result = {
                            'type': activity_data['type'],
                            'name': activity_data['name'],
                            'success': False,
                            'message': '',
                            'activityid': 0
                        }
                        
                        try:
                            if activity_data['type'] == 'page':
                                result = await self.create_page_activity(
                                    course_id, section_num, 
                                    activity_data['name'], activity_data['content']
                                )
                            elif activity_data['type'] == 'label':
                                result = await self.create_label_activity(
                                    course_id, section_num, activity_data['content']
                                )
                            elif activity_data['type'] == 'file':
                                result = await self.create_file_activity(
                                    course_id, section_num, 
                                    activity_data['name'], activity_data['content'],
                                    activity_data.get('filename', activity_data['name'] + '.txt')
                                )
                            else:
                                result = {'success': False, 'message': f"Unknown activity type: {activity_data['type']}"}
                            
                            activity_result['success'] = result['success']
                            activity_result['message'] = result['message']
                            activity_result['activityid'] = result.get('activity_id', 0)
                            
                        except Exception as e:
                            activity_result['message'] = f"Activity creation failed: {str(e)}"
                        
                        section_result['activities'].append(activity_result)
                else:
                    section_result['message'] = 'Section update failed (plugin required)'
                    
            except Exception as e:
                section_result['message'] = f"Section creation failed: {str(e)}"
            
            results.append(section_result)
            section_num += 1
        
        return {
            'success': any(s['success'] for s in results),
            'message': 'Course structure creation completed (individual calls)',
            'sections': results
        }

    # Include all other methods from original client (get_courses, get_categories, etc.)
    async def get_courses(self) -> List[Dict[str, Any]]:
        """Get list of courses the user has access to"""
        try:
            result = await self._call_api(MoodleWebServices.GET_COURSES)
            if isinstance(result, list):
                return result
            return []
        except MoodleAPIError:
            logger.warning("Failed to retrieve courses")
            return []

    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get list of course categories"""
        try:
            result = await self._call_api(MoodleWebServices.GET_CATEGORIES)
            if isinstance(result, list):
                return result
            return []
        except MoodleAPIError:
            logger.warning("Failed to retrieve categories")
            return []

    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()