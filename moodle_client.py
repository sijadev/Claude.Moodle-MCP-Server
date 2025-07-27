"""
Moodle API Client for course and activity creation
Handles authentication and API interactions with Moodle
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import tempfile
import os

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
        self.base_url = base_url.rstrip('/')
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
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
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
                    if isinstance(result, dict) and 'exception' in result:
                        raise MoodleAPIError(f"Moodle API Error: {result.get('message', 'Unknown error')}")
                    
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
        shortname = name.lower().replace(' ', '_').replace('-', '_')
        # Ensure shortname is unique by adding timestamp if needed
        import time
        shortname = f"{shortname}_{int(time.time())}"
        
        params = {
            'courses[0][fullname]': name,
            'courses[0][shortname]': shortname,
            'courses[0][categoryid]': category_id,
            'courses[0][summary]': description,
            'courses[0][summaryformat]': 1,  # HTML format
            'courses[0][format]': 'topics',  # Course format
            'courses[0][visible]': 1,  # Visible
            'courses[0][numsections]': 0,  # Will add sections manually
        }
        
        result = await self._call_api('core_course_create_courses', params)
        
        if not result or not isinstance(result, list) or len(result) == 0:
            raise MoodleAPIError("Failed to create course: No course ID returned")
        
        course_id = result[0].get('id') if isinstance(result[0], dict) else None
        if not course_id:
            raise MoodleAPIError("Failed to create course: Invalid response format")
        
        logger.info(f"Created course '{name}' with ID: {course_id}")
        return course_id
    
    async def create_section(self, course_id: int, name: str, description: str = "") -> int:
        """
        Create a new section in a course
        
        Args:
            course_id: Course ID
            name: Section name
            description: Section description
            
        Returns:
            Created section ID
        """
        params = {
            'courseid': course_id,
            'sections[0][name]': name,
            'sections[0][summary]': description,
            'sections[0][summaryformat]': 1,  # HTML format
        }
        
        result = await self._call_api('core_course_create_sections', params)
        
        if not result or not isinstance(result, list) or len(result) == 0:
            raise MoodleAPIError("Failed to create section: No section ID returned")
        
        section_id = result[0].get('id') if isinstance(result[0], dict) else None
        if not section_id:
            raise MoodleAPIError("Failed to create section: Invalid response format")
        
        logger.info(f"Created section '{name}' with ID: {section_id}")
        return section_id
    
    async def create_page_activity(self, course_id: int, section_id: int, name: str, content: str) -> int:
        """
        Create a Page activity in Moodle
        
        Args:
            course_id: Course ID
            section_id: Section ID
            name: Activity name
            content: HTML content for the page
            
        Returns:
            Created activity ID
        """
        params = {
            'assignments[0][courseid]': course_id,
            'assignments[0][name]': name,
            'assignments[0][intro]': content,
            'assignments[0][introformat]': 1,  # HTML format
            'assignments[0][activity]': 'page',
            'assignments[0][section]': section_id,
            'assignments[0][visible]': 1,
            'assignments[0][completion]': 0,
        }
        
        # Use core_course_create_activities for page creation
        activity_params = {
            'activities[0][modulename]': 'page',
            'activities[0][courseid]': course_id,
            'activities[0][name]': name,
            'activities[0][intro]': f"<p>{name}</p>",
            'activities[0][introformat]': 1,
            'activities[0][section]': section_id,
            'activities[0][visible]': 1,
            'activities[0][content]': content,
            'activities[0][contentformat]': 1,
        }
        
        try:
            result = await self._call_api('core_course_create_activities', activity_params)
        except MoodleAPIError:
            # Fallback: try using mod_page_create_pages if available
            page_params = {
                'pages[0][course]': course_id,
                'pages[0][name]': name,
                'pages[0][intro]': f"<p>{name}</p>",
                'pages[0][introformat]': 1,
                'pages[0][content]': content,
                'pages[0][contentformat]': 1,
            }
            
            try:
                result = await self._call_api('mod_page_add_page', page_params)
            except MoodleAPIError:
                # Final fallback: create as a label
                return await self.create_label_activity(course_id, section_id, name, content)
        
        if not result or not isinstance(result, list) or len(result) == 0:
            # Fallback to label creation
            return await self.create_label_activity(course_id, section_id, name, content)
        
        activity_id = (result[0].get('id') or result[0].get('coursemodule')) if isinstance(result[0], dict) else None
        if not activity_id:
            # Fallback to label creation
            return await self.create_label_activity(course_id, section_id, name, content)
        
        logger.info(f"Created page activity '{name}' with ID: {activity_id}")
        return activity_id
    
    async def create_label_activity(self, course_id: int, section_id: int, name: str, content: str) -> int:
        """
        Create a Label activity as fallback
        
        Args:
            course_id: Course ID
            section_id: Section ID
            name: Activity name
            content: HTML content
            
        Returns:
            Created activity ID
        """
        full_content = f"<h3>{name}</h3>\n{content}"
        
        params = {
            'labels[0][course]': course_id,
            'labels[0][name]': name,
            'labels[0][intro]': full_content,
            'labels[0][introformat]': 1,
        }
        
        try:
            result = await self._call_api('mod_label_add_label', params)
        except MoodleAPIError:
            # If label creation also fails, try generic activity creation
            activity_params = {
                'activities[0][modulename]': 'label',
                'activities[0][courseid]': course_id,
                'activities[0][name]': name,
                'activities[0][intro]': full_content,
                'activities[0][introformat]': 1,
                'activities[0][section]': section_id,
                'activities[0][visible]': 1,
            }
            result = await self._call_api('core_course_create_activities', activity_params)
        
        if not result or not isinstance(result, list) or len(result) == 0:
            raise MoodleAPIError("Failed to create label activity")
        
        activity_id = (result[0].get('id') or result[0].get('coursemodule')) if isinstance(result[0], dict) else None
        if not activity_id:
            raise MoodleAPIError("Failed to create label activity: Invalid response format")
        
        logger.info(f"Created label activity '{name}' with ID: {activity_id}")
        return activity_id
    
    async def create_file_activity(self, course_id: int, section_id: int, name: str, 
                                  content: str, filename: str) -> int:
        """
        Create a File resource activity
        
        Args:
            course_id: Course ID
            section_id: Section ID
            name: Activity name
            content: File content
            filename: File name
            
        Returns:
            Created activity ID
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{filename.split(".")[-1]}', 
                                       delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Upload file first
            file_id = await self._upload_file(temp_file_path, filename)
            
            # Create resource activity
            params = {
                'resources[0][course]': course_id,
                'resources[0][name]': name,
                'resources[0][intro]': f"<p>Download: {filename}</p>",
                'resources[0][introformat]': 1,
                'resources[0][files][0]': file_id,
            }
            
            try:
                result = await self._call_api('mod_resource_add_resource', params)
            except MoodleAPIError:
                # Fallback: create as URL resource with content
                return await self._create_content_as_page(course_id, section_id, name, content, filename)
            
            if not result or not isinstance(result, list) or len(result) == 0:
                return await self._create_content_as_page(course_id, section_id, name, content, filename)
            
            activity_id = (result[0].get('id') or result[0].get('coursemodule')) if isinstance(result[0], dict) else None
            if not activity_id:
                return await self._create_content_as_page(course_id, section_id, name, content, filename)
            
            logger.info(f"Created file resource '{name}' with ID: {activity_id}")
            return activity_id
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
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
        
        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('token', self.token)
            data.add_field('filearea', 'draft')
            data.add_field('itemid', '0')
            data.add_field('file', f, filename=filename)
            
            if self.session:
                async with self.session.post(upload_url, data=data) as response:
                    if response.status != 200:
                        raise MoodleAPIError(f"File upload failed: HTTP {response.status}")
                    
                    result = await response.json()
                    
                    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                        return result[0].get('url', '')
                    
                    raise MoodleAPIError("File upload failed: Invalid response")
            else:
                raise MoodleAPIError("No session available for file upload")
    
    async def _create_content_as_page(self, course_id: int, section_id: int, 
                                    name: str, content: str, filename: str) -> int:
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
    
    async def get_courses(self) -> List[Dict[str, Any]]:
        """
        Get list of courses
        
        Returns:
            List of course information
        """
        result = await self._call_api('core_course_get_courses')
        return result if isinstance(result, list) else []
    
    async def get_course_sections(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get sections for a course
        
        Args:
            course_id: Course ID
            
        Returns:
            List of section information
        """
        params = {'courseid': course_id}
        result = await self._call_api('core_course_get_contents', params)
        return result if isinstance(result, list) else []
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
