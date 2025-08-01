"""
Enhanced MoodleClaude Integration
Advanced functionality for local_wsmanagesections and core_files_upload
"""

import json
import mimetypes
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests


@dataclass
class SectionConfig:
    """Configuration for creating/updating course sections.

    This dataclass encapsulates all the parameters needed to create or update
    a course section in Moodle through the local_wsmanagesections plugin.

    Attributes:
        name: Display name of the section
        summary: Optional HTML description/summary of the section
        visible: Whether the section is visible to students (default: True)
        availability_conditions: JSON-serializable availability/restriction conditions
        position: Specific position/order in the course (0-based index)
        format_options: Additional format-specific options for the section

    Example:
        >>> config = SectionConfig(
        ...     name="Introduction to Python",
        ...     summary="<p>Basic Python concepts and syntax</p>",
        ...     visible=True,
        ...     position=1
        ... )
    """

    name: str
    summary: Optional[str] = None
    visible: bool = True
    availability_conditions: Optional[Dict[str, Any]] = None
    position: Optional[int] = None
    format_options: Optional[Dict[str, Any]] = None


@dataclass
class FileUploadConfig:
    """Configuration for file uploads to Moodle.

    This dataclass contains all parameters needed to upload files to Moodle
    through the core_files_upload web service function.

    Attributes:
        filename: Name of the file including extension
        content: Raw bytes content of the file
        contextid: Moodle context ID where file should be stored
        component: Moodle component handling the file (default: "mod_resource")
        filearea: File area within the component (default: "content")
        itemid: Item ID for organizing files (default: 0)
        filepath: Virtual path within the file area (default: "/")
        author: Author attribution for the file (default: "Claude AI")
        license: License identifier for the file content
        userid: Specific user ID to associate with upload

    Example:
        >>> config = FileUploadConfig(
        ...     filename="example.pdf",
        ...     content=pdf_bytes,
        ...     contextid=12345,
        ...     author="Educational Content"
        ... )
    """

    filename: str
    content: bytes
    contextid: int
    component: str = "mod_resource"
    filearea: str = "content"
    itemid: int = 0
    filepath: str = "/"
    author: str = "Claude AI"
    license: Optional[str] = None
    userid: Optional[int] = None


class EnhancedMoodleAPI:
    """Enhanced Moodle API client with advanced section and file management.

    This class provides a high-level interface to Moodle Web Services with specialized
    methods for course section management and file uploads. It handles authentication,
    error handling, and provides convenient methods for complex operations.

    Attributes:
        base_url: Base URL of the Moodle installation (without trailing slash)
        token: Web service authentication token
        session: Persistent HTTP session for API requests

    Example:
        >>> api = EnhancedMoodleAPI("https://moodle.example.com", "your_token_here")
        >>> site_info = api.get_site_info()
        >>> print(site_info['sitename'])
    """

    def __init__(self, base_url: str, token: str):
        """Initialize the Enhanced Moodle API client.

        Args:
            base_url: Base URL of the Moodle installation
            token: Valid web service authentication token

        Raises:
            ValueError: If base_url or token are empty
        """
        if not base_url or not token:
            raise ValueError("base_url and token are required")

        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        self.session.timeout = 30

    def _make_request(self, wsfunction: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Moodle Web Service API.

        Args:
            wsfunction: Name of the Moodle web service function to call
            params: Dictionary of parameters to send with the request

        Returns:
            Dictionary containing the API response data

        Raises:
            requests.RequestException: For HTTP-related errors
            json.JSONDecodeError: If response is not valid JSON
            Exception: For Moodle API errors (contains error message)
        """
        url = f"{self.base_url}/webservice/rest/server.php"

        data = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
            **params,
        }

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            # Check for Moodle API errors
            if isinstance(result, dict):
                if "exception" in result:
                    error_msg = result.get("message", "Unknown Moodle error")
                    raise Exception(f"Moodle API Error: {error_msg}")
                elif "error" in result:
                    raise Exception(f"Moodle API Error: {result['error']}")

            return result

        except requests.RequestException as e:
            raise e
        except json.JSONDecodeError as e:
            raise e

    def get_site_info(self) -> Dict[str, Any]:
        """Get basic information about the Moodle site.

        Returns:
            Dictionary containing site information including sitename, username,
            firstname, lastname, functions, and other site metadata.

        Example:
            >>> info = api.get_site_info()
            >>> print(f"Site: {info['sitename']}, User: {info['username']}")
        """
        return self._make_request("core_webservice_get_site_info", {})

    def create_course_section(
        self, courseid: int, section_config: SectionConfig
    ) -> Dict[str, Any]:
        """Create a new course section with the specified configuration.

        Args:
            courseid: ID of the course where the section should be created
            section_config: SectionConfig object containing section parameters

        Returns:
            Dictionary containing the created section data including sectionid

        Raises:
            Exception: If the section creation fails or courseid is invalid

        Example:
            >>> config = SectionConfig(
            ...     name="Week 1: Introduction",
            ...     summary="<p>Course introduction and overview</p>",
            ...     position=1
            ... )
            >>> result = api.create_course_section(123, config)
            >>> print(f"Created section with ID: {result['sectionid']}")
        """
        params = {
            "courseid": courseid,
            "sectionname": section_config.name,
            "visible": 1 if section_config.visible else 0,
        }

        if section_config.summary:
            params["summary"] = section_config.summary

        if section_config.availability_conditions:
            params["availability"] = json.dumps(section_config.availability_conditions)

        if section_config.position is not None:
            params["sectionnumber"] = section_config.position

        return self._make_request("local_wsmanagesections_create_section", params)

    def update_section(self, sectionid: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing section"""
        params = {"sectionid": sectionid, **updates}
        return self._make_request("local_wsmanagesections_update_section", params)

    def delete_section(self, sectionid: int) -> Dict[str, Any]:
        """Delete a section"""
        params = {"sectionid": sectionid}
        return self._make_request("local_wsmanagesections_delete_section", params)

    def move_sections(self, section_moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Move multiple sections to new positions"""
        operations = []
        for move in section_moves:
            operations.append(
                {
                    "operation": "move",
                    "sectionid": move["sectionid"],
                    "targetposition": move["position"],
                }
            )
        return self.bulk_section_operations(operations)

    def bulk_section_operations(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform bulk operations on sections"""
        params = {"operations": operations}
        return self._make_request("local_wsmanagesections_bulk_operations", params)

    def duplicate_section(self, sectionid: int, target_courseid: int) -> Dict[str, Any]:
        """Duplicate a section to another course"""
        params = {"sectionid": sectionid, "targetcourseid": target_courseid}
        return self._make_request("local_wsmanagesections_duplicate_section", params)

    def upload_file(self, file_config: FileUploadConfig) -> Dict[str, Any]:
        """Upload a file to Moodle"""
        # Step 1: Upload file to draft area
        upload_url = f"{self.base_url}/webservice/upload.php"

        # Prepare file data
        files = {
            "file": (
                file_config.filename,
                file_config.content,
                mimetypes.guess_type(file_config.filename)[0]
                or "application/octet-stream",
            )
        }

        upload_data = {
            "token": self.token,
            "itemid": file_config.itemid,
            "component": file_config.component,
            "filearea": file_config.filearea,
            "contextid": file_config.contextid,
            "filepath": file_config.filepath,
        }

        # Upload file
        upload_response = self.session.post(upload_url, data=upload_data, files=files)
        upload_response.raise_for_status()
        upload_result = upload_response.json()

        if "error" in upload_result:
            raise Exception(f"File upload failed: {upload_result['error']}")

        # Step 2: Save file from draft area
        if upload_result and len(upload_result) > 0:
            itemid = upload_result[0]["itemid"]

            save_params = {
                "contextid": file_config.contextid,
                "component": file_config.component,
                "filearea": file_config.filearea,
                "itemid": itemid,
                "filepath": file_config.filepath,
                "filename": file_config.filename,
                "author": file_config.author,
            }

            if file_config.license:
                save_params["license"] = file_config.license

            save_result = self._make_request(
                "core_files_save_draft_area_files", save_params
            )
            return save_result

        return upload_result

    def create_file_resource(
        self,
        courseid: int,
        sectionnum: int,
        name: str,
        file_content: bytes,
        filename: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a file resource in a course section"""

        # Get site info to determine context
        site_info = self.get_site_info()

        # Upload file first
        file_config = FileUploadConfig(
            filename=filename,
            content=file_content,
            contextid=1,  # Will be updated with proper context
            component="mod_resource",
            filearea="content",
        )

        upload_result = self.upload_file(file_config)

        # Create module
        module_params = {
            "courseid": courseid,
            "modulename": "resource",
            "section": sectionnum,
            "name": name,
            "intro": description,
            "visible": 1,
            "files": (
                upload_result if isinstance(upload_result, list) else [upload_result]
            ),
        }

        return self._make_request(
            "core_course_create_modules", {"modules": [module_params]}
        )

    def create_url_resource(
        self, courseid: int, sectionnum: int, name: str, url: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a URL resource in a course section"""
        module_params = {
            "courseid": courseid,
            "modulename": "url",
            "section": sectionnum,
            "name": name,
            "intro": description,
            "visible": 1,
            "externalurl": url,
        }

        return self._make_request(
            "core_course_create_modules", {"modules": [module_params]}
        )

    def get_course_sections(self, courseid: int) -> List[Dict[str, Any]]:
        """Get all sections for a course"""
        params = {"courseid": courseid}
        return self._make_request("core_course_get_contents", params)

    def create_course(
        self,
        fullname: str,
        shortname: str,
        categoryid: int,
        summary: str = "",
        format: str = "topics",
    ) -> Dict[str, Any]:
        """Create a new course"""
        courses = [
            {
                "fullname": fullname,
                "shortname": shortname,
                "categoryid": categoryid,
                "summary": summary,
                "format": format,
            }
        ]

        result = self._make_request("core_course_create_courses", {"courses": courses})
        return result[0] if result else {}


class MoodleClaudeIntegration:
    """Integration layer between Claude and Moodle with enhanced functionality.

    This class provides high-level methods for converting Claude chat content
    into structured Moodle courses with sections, resources, and files. It combines
    the enhanced API functionality with intelligent content parsing capabilities.

    Attributes:
        api: EnhancedMoodleAPI instance for Moodle operations
        moodle_url: Base URL of the Moodle installation

    Example:
        >>> integration = MoodleClaudeIntegration(
        ...     "https://moodle.example.com",
        ...     "your_token_here"
        ... )
        >>> course_data = integration.create_structured_course_from_chat(
        ...     courseid=123,
        ...     chat_content="# Week 1\nIntroduction to Python..."
        ... )
    """

    def __init__(self, moodle_url: str, token: str):
        """Initialize the MoodleClaude integration.

        Args:
            moodle_url: Base URL of the Moodle installation
            token: Valid web service authentication token
        """
        self.api = EnhancedMoodleAPI(moodle_url, token)
        self.moodle_url = moodle_url

    def _parse_chat_for_sections(self, chat_content: str) -> List[Dict[str, Any]]:
        """Parse chat content to extract sections and resources"""
        sections = []
        current_section = {"title": "General", "content": "", "files": []}

        lines = chat_content.split("\n")

        for line in lines:
            line = line.strip()

            # Check for markdown headers
            if line.startswith("#"):
                # Save previous section if it has content
                if current_section["content"].strip() or current_section["files"]:
                    sections.append(current_section)

                # Start new section
                header_level = len(line.split()[0])  # Count # characters
                title = line.lstrip("#").strip()
                current_section = {
                    "title": title,
                    "content": "",
                    "files": [],
                    "level": header_level,
                }
            else:
                # Add line to current section content
                current_section["content"] += line + "\n"

                # Check for URLs/file references
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                urls = re.findall(url_pattern, line)

                for url in urls:
                    # Determine if it's likely a file
                    parsed_url = urlparse(url)
                    filename = Path(parsed_url.path).name

                    file_extensions = [
                        ".pdf",
                        ".doc",
                        ".docx",
                        ".ppt",
                        ".pptx",
                        ".txt",
                        ".zip",
                        ".mp4",
                        ".avi",
                    ]
                    is_file = any(
                        filename.lower().endswith(ext) for ext in file_extensions
                    )

                    current_section["files"].append(
                        {
                            "type": "url",
                            "url": url,
                            "name": filename if is_file else url,
                            "is_downloadable": is_file,
                        }
                    )

        # Add the last section
        if current_section["content"].strip() or current_section["files"]:
            sections.append(current_section)

        # If no sections were created, create a default one
        if not sections:
            sections.append({"title": "General", "content": chat_content, "files": []})

        return sections

    def create_structured_course_from_chat(
        self, chat_content: str, course_name: str, categoryid: int
    ) -> Dict[str, Any]:
        """Create a structured course from chat content with sections"""

        # Parse chat content into sections
        sections = self._parse_chat_for_sections(chat_content)

        # Create course
        shortname = re.sub(r"[^a-zA-Z0-9]", "", course_name.replace(" ", ""))[:50]
        course_result = self.api.create_course(
            fullname=course_name,
            shortname=shortname,
            categoryid=categoryid,
            summary=f"Course created from Claude conversation",
        )

        # Handle both dict and list responses (for testing compatibility)
        if isinstance(course_result, list) and len(course_result) > 0:
            courseid = course_result[0]["id"]
        elif isinstance(course_result, dict):
            courseid = course_result["id"]
        else:
            raise ValueError("Unexpected course creation response format")

        created_sections = []

        # Create sections
        for i, section_data in enumerate(sections):
            section_config = SectionConfig(
                name=section_data["title"],
                summary=(
                    section_data["content"][:500] + "..."
                    if len(section_data["content"]) > 500
                    else section_data["content"]
                ),
                visible=True,
                position=i + 1,
            )

            section_result = self.api.create_course_section(courseid, section_config)
            created_sections.append(
                {
                    "section_info": section_result,
                    "resources": section_data.get("files", []),
                }
            )

        return {
            "courseid": courseid,
            "course_url": f"{self.moodle_url}/course/view.php?id={courseid}",
            "sections": created_sections,
            "parsed_content": sections,
        }

    def add_resources_to_section(
        self, courseid: int, sectionnum: int, resources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add various types of resources to a course section"""
        results = []

        for resource in resources:
            try:
                if resource["type"] == "file":
                    # Handle file upload
                    file_path = Path(resource["path"])
                    if file_path.exists():
                        with open(file_path, "rb") as f:
                            file_content = f.read()

                        result = self.api.create_file_resource(
                            courseid=courseid,
                            sectionnum=sectionnum,
                            name=resource.get("name", file_path.name),
                            file_content=file_content,
                            filename=file_path.name,
                            description=resource.get("description", ""),
                        )
                        results.append(result)

                elif resource["type"] == "url":
                    # Handle URL resource
                    result = self.api.create_url_resource(
                        courseid=courseid,
                        sectionnum=sectionnum,
                        name=resource.get("name", resource["url"]),
                        url=resource["url"],
                        description=resource.get("description", ""),
                    )
                    results.append(result)

                elif resource["type"] == "content":
                    # Handle text content as file
                    content_bytes = resource["content"].encode("utf-8")
                    filename = resource.get("filename", "content.txt")

                    result = self.api.create_file_resource(
                        courseid=courseid,
                        sectionnum=sectionnum,
                        name=resource.get("name", filename),
                        file_content=content_bytes,
                        filename=filename,
                        description=resource.get("description", ""),
                    )
                    results.append(result)

            except Exception as e:
                print(f"Error adding resource {resource}: {e}")
                continue

        return results

    def bulk_update_course_structure(
        self, courseid: int, structure_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform bulk updates to course structure"""
        operations = []

        for update in structure_updates:
            if update["type"] == "move_section":
                operations.append(
                    {
                        "operation": "move",
                        "sectionid": update["sectionid"],
                        "targetposition": update["position"],
                    }
                )
            elif update["type"] == "update_section":
                operations.append(
                    {
                        "operation": "update",
                        "sectionid": update["sectionid"],
                        "data": update["data"],
                    }
                )
            elif update["type"] == "duplicate_section":
                operations.append(
                    {
                        "operation": "duplicate",
                        "sectionid": update["sectionid"],
                        "targetcourseid": update["target_courseid"],
                    }
                )
            elif update["type"] == "delete_section":
                operations.append(
                    {"operation": "delete", "sectionid": update["sectionid"]}
                )

        return self.api.bulk_section_operations(operations)

    def _create_file_resource_from_description(
        self, courseid: int, sectionnum: int, file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a file resource from a file description"""
        if file_info["type"] == "url":
            return self.api.create_url_resource(
                courseid=courseid,
                sectionnum=sectionnum,
                name=file_info.get("name", file_info["url"]),
                url=file_info["url"],
                description=file_info.get("description", ""),
            )
        elif file_info["type"] == "file":
            # Handle local file
            file_path = Path(file_info["path"])
            if file_path.exists():
                with open(file_path, "rb") as f:
                    content = f.read()

                return self.api.create_file_resource(
                    courseid=courseid,
                    sectionnum=sectionnum,
                    name=file_info.get("name", file_path.name),
                    file_content=content,
                    filename=file_path.name,
                    description=file_info.get("description", ""),
                )

        raise ValueError(f"Unsupported file type: {file_info['type']}")

    def export_course_structure(self, courseid: int) -> Dict[str, Any]:
        """Export course structure for analysis or backup"""
        sections = self.api.get_course_sections(courseid)

        structure = {
            "courseid": courseid,
            "sections": [],
            "total_sections": len(sections),
            "export_timestamp": __import__("datetime").datetime.now().isoformat(),
        }

        for section in sections:
            section_info = {
                "id": section.get("id"),
                "name": section.get("name"),
                "summary": section.get("summary"),
                "visible": section.get("visible"),
                "section_number": section.get("section"),
                "modules": [],
            }

            # Add module information
            for module in section.get("modules", []):
                module_info = {
                    "id": module.get("id"),
                    "name": module.get("name"),
                    "modname": module.get("modname"),
                    "url": module.get("url"),
                    "visible": module.get("visible"),
                }
                section_info["modules"].append(module_info)

            structure["sections"].append(section_info)

        return structure

    def import_course_structure(
        self, structure_data: Dict[str, Any], target_courseid: int
    ) -> Dict[str, Any]:
        """Import course structure from exported data"""
        results = {"imported_sections": [], "errors": []}

        for section_data in structure_data.get("sections", []):
            try:
                section_config = SectionConfig(
                    name=section_data["name"],
                    summary=section_data.get("summary", ""),
                    visible=section_data.get("visible", True),
                )

                section_result = self.api.create_course_section(
                    target_courseid, section_config
                )
                results["imported_sections"].append(section_result)

            except Exception as e:
                results["errors"].append(
                    {"section": section_data.get("name", "Unknown"), "error": str(e)}
                )

        return results


# Convenience functions for common operations
def create_course_from_conversation(
    moodle_url: str,
    token: str,
    conversation_text: str,
    course_name: str,
    category_id: int,
) -> Dict[str, Any]:
    """Convenience function to create a course from conversation text"""
    integration = MoodleClaudeIntegration(moodle_url, token)
    return integration.create_structured_course_from_chat(
        conversation_text, course_name, category_id
    )


def upload_files_to_course(
    moodle_url: str,
    token: str,
    courseid: int,
    file_list: List[str],
    section_number: int = 1,
) -> List[Dict[str, Any]]:
    """Convenience function to upload multiple files to a course section"""
    integration = MoodleClaudeIntegration(moodle_url, token)

    resources = []
    for file_path in file_list:
        path_obj = Path(file_path)
        resources.append(
            {
                "type": "file",
                "path": file_path,
                "name": path_obj.stem,
                "description": f"Uploaded file: {path_obj.name}",
            }
        )

    return integration.add_resources_to_section(courseid, section_number, resources)
