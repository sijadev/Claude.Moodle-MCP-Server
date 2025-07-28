"""
Enhanced Unit Tests for MoodleClaude Integration
Tests for local_wsmanagesections and core_files_upload functionality
"""

import json
import os

# Import the classes we're testing from the root directory
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from enhanced_moodle_claude import (
    EnhancedMoodleAPI,
    FileUploadConfig,
    MoodleClaudeIntegration,
    SectionConfig,
)


class TestSectionConfig(unittest.TestCase):
    """Test SectionConfig dataclass functionality"""

    def test_section_config_creation(self):
        """Test basic section config creation"""
        config = SectionConfig(name="Test Section", summary="Test summary", visible=True)

        self.assertEqual(config.name, "Test Section")
        self.assertEqual(config.summary, "Test summary")
        self.assertTrue(config.visible)
        self.assertIsNone(config.availability_conditions)
        self.assertIsNone(config.position)

    def test_section_config_with_availability(self):
        """Test section config with availability conditions"""
        availability = {"op": "&", "c": [{"type": "date", "d": ">=", "t": 1640995200}]}

        config = SectionConfig(
            name="Restricted Section", availability_conditions=availability, position=3
        )

        self.assertEqual(config.availability_conditions, availability)
        self.assertEqual(config.position, 3)


class TestFileUploadConfig(unittest.TestCase):
    """Test FileUploadConfig dataclass functionality"""

    def test_file_upload_config_creation(self):
        """Test basic file upload config creation"""
        content = b"Test file content"
        config = FileUploadConfig(filename="test.txt", content=content, contextid=123)

        self.assertEqual(config.filename, "test.txt")
        self.assertEqual(config.content, content)
        self.assertEqual(config.contextid, 123)
        self.assertEqual(config.component, "mod_resource")  # Default value
        self.assertEqual(config.author, "Claude AI")  # Default value

    def test_file_upload_config_custom_values(self):
        """Test file upload config with custom values"""
        config = FileUploadConfig(
            filename="custom.pdf",
            content=b"PDF content",
            contextid=456,
            component="mod_assign",
            filearea="submissions",
            author="Custom Author",
            license="cc-4.0",
        )

        self.assertEqual(config.component, "mod_assign")
        self.assertEqual(config.filearea, "submissions")
        self.assertEqual(config.author, "Custom Author")
        self.assertEqual(config.license, "cc-4.0")


class TestEnhancedMoodleAPI(unittest.TestCase):
    """Test EnhancedMoodleAPI functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.api = EnhancedMoodleAPI("http://test.moodle.com", "test_token")
        self.mock_session = Mock()
        self.api.session = self.mock_session

    def test_api_initialization(self):
        """Test API initialization"""
        api = EnhancedMoodleAPI("http://test.moodle.com/", "token123")
        self.assertEqual(api.base_url, "http://test.moodle.com")
        self.assertEqual(api.token, "token123")

    @patch("requests.Session")
    def test_make_request_success(self, mock_session_class):
        """Test successful API request"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "id": 123}
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        api = EnhancedMoodleAPI("http://test.moodle.com", "test_token")
        result = api._make_request("test_function", {"param": "value"})

        self.assertEqual(result, {"success": True, "id": 123})
        mock_session.post.assert_called_once()

        # Check the called parameters
        call_args = mock_session.post.call_args
        self.assertIn("wstoken", call_args[1]["data"])
        self.assertIn("wsfunction", call_args[1]["data"])
        self.assertEqual(call_args[1]["data"]["wsfunction"], "test_function")

    def test_make_request_error(self):
        """Test API request with Moodle error response"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "exception": "moodle_exception",
            "message": "Test error message",
        }
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.api._make_request("test_function", {})

        self.assertIn("Test error message", str(context.exception))

    def test_create_course_section(self):
        """Test creating a course section"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": 456, "section": 1}
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        section_config = SectionConfig(
            name="Test Section", summary="Test summary", visible=True, position=1
        )

        result = self.api.create_course_section(123, section_config)

        self.assertEqual(result["id"], 456)
        self.mock_session.post.assert_called_once()

        # Verify the request parameters
        call_args = self.mock_session.post.call_args[1]["data"]
        self.assertEqual(call_args["courseid"], 123)
        self.assertEqual(call_args["sectionname"], "Test Section")
        self.assertEqual(call_args["summary"], "Test summary")

    def test_create_section_with_availability(self):
        """Test creating section with availability conditions"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": 789}
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        availability = {"op": "&", "c": [{"type": "date"}]}
        section_config = SectionConfig(
            name="Restricted Section", availability_conditions=availability
        )

        result = self.api.create_course_section(123, section_config)

        call_args = self.mock_session.post.call_args[1]["data"]
        self.assertEqual(call_args["availability"], json.dumps(availability))

    def test_update_section(self):
        """Test updating a section"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        updates = {"name": "Updated Name", "summary": "Updated summary"}
        result = self.api.update_section(456, updates)

        self.assertTrue(result["success"])
        call_args = self.mock_session.post.call_args[1]["data"]
        self.assertEqual(call_args["sectionid"], 456)
        self.assertEqual(call_args["name"], "Updated Name")

    def test_bulk_section_operations(self):
        """Test bulk section operations"""
        mock_response = Mock()
        mock_response.json.return_value = {"operations_completed": 2}
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        operations = [
            {"operation": "move", "sectionid": 1, "targetposition": 2},
            {"operation": "update", "sectionid": 2, "data": {"name": "New Name"}},
        ]

        result = self.api.bulk_section_operations(operations)

        self.assertEqual(result["operations_completed"], 2)
        call_args = self.mock_session.post.call_args[1]["data"]
        self.assertEqual(call_args["operations"], operations)

    def test_move_sections(self):
        """Test moving multiple sections"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        section_moves = [{"sectionid": 1, "position": 3}, {"sectionid": 2, "position": 1}]

        result = self.api.move_sections(section_moves)

        self.assertTrue(result["success"])
        # Verify bulk_section_operations was called with correct parameters
        call_args = self.mock_session.post.call_args[1]["data"]
        operations = call_args["operations"]
        self.assertEqual(len(operations), 2)
        self.assertEqual(operations[0]["operation"], "move")

    def test_duplicate_section(self):
        """Test duplicating a section"""
        mock_response = Mock()
        mock_response.json.return_value = {"new_section_id": 999}
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        result = self.api.duplicate_section(456, 789)

        self.assertEqual(result["new_section_id"], 999)
        call_args = self.mock_session.post.call_args[1]["data"]
        self.assertEqual(call_args["sectionid"], 456)
        self.assertEqual(call_args["targetcourseid"], 789)

    @patch("mimetypes.guess_type")
    def test_upload_file(self, mock_guess_type):
        """Test file upload functionality"""
        mock_guess_type.return_value = ("text/plain", None)

        # Mock upload response
        upload_response = Mock()
        upload_response.json.return_value = [{"itemid": 12345}]
        upload_response.raise_for_status.return_value = None

        # Mock save draft response
        save_response = Mock()
        save_response.json.return_value = {"success": True}
        save_response.raise_for_status.return_value = None

        # Configure session to return different responses for different calls
        self.mock_session.post.side_effect = [upload_response, save_response]

        file_config = FileUploadConfig(filename="test.txt", content=b"Test content", contextid=123)

        result = self.api.upload_file(file_config)

        self.assertTrue(result["success"])
        self.assertEqual(self.mock_session.post.call_count, 2)

    def test_upload_file_error(self):
        """Test file upload error handling"""
        upload_response = Mock()
        upload_response.json.return_value = {"error": "Upload failed"}
        upload_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = upload_response

        file_config = FileUploadConfig(filename="test.txt", content=b"Test content", contextid=123)

        with self.assertRaises(Exception) as context:
            self.api.upload_file(file_config)

        self.assertIn("Upload failed", str(context.exception))

    def test_create_file_resource(self):
        """Test creating a file resource"""
        # Mock get_site_info response
        site_info_response = Mock()
        site_info_response.json.return_value = {"siteid": 1}
        site_info_response.raise_for_status.return_value = None

        # Mock upload responses
        upload_response = Mock()
        upload_response.json.return_value = [{"itemid": 12345}]
        upload_response.raise_for_status.return_value = None

        save_response = Mock()
        save_response.json.return_value = {"success": True}
        save_response.raise_for_status.return_value = None

        # Mock create module response
        module_response = Mock()
        module_response.json.return_value = {"cmid": 789}
        module_response.raise_for_status.return_value = None

        self.mock_session.post.side_effect = [
            site_info_response,  # get_site_info
            upload_response,  # file upload
            save_response,  # save draft
            module_response,  # create module
        ]

        result = self.api.create_file_resource(
            courseid=123,
            sectionnum=1,
            name="Test Resource",
            file_content=b"Test content",
            filename="test.txt",
        )

        self.assertEqual(result["cmid"], 789)
        self.assertEqual(self.mock_session.post.call_count, 4)


class TestMoodleClaudeIntegration(unittest.TestCase):
    """Test MoodleClaudeIntegration functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.integration = MoodleClaudeIntegration("http://test.moodle.com", "test_token")
        self.mock_api = Mock()
        self.integration.api = self.mock_api

    def test_integration_initialization(self):
        """Test integration initialization"""
        integration = MoodleClaudeIntegration("http://test.moodle.com", "token123")
        self.assertEqual(integration.api.base_url, "http://test.moodle.com")
        self.assertEqual(integration.api.token, "token123")

    def test_parse_chat_for_sections_simple(self):
        """Test parsing simple chat content"""
        chat_content = "This is just simple text without headers."

        sections = self.integration._parse_chat_for_sections(chat_content)

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["title"], "General")
        self.assertIn("simple text", sections[0]["content"])

    def test_parse_chat_for_sections_with_headers(self):
        """Test parsing chat content with markdown headers"""
        chat_content = """
        # Introduction
        This is the introduction section.
        
        ## Chapter 1
        This is chapter 1 content.
        
        ### Subsection
        This is a subsection.
        
        # Conclusion
        Final thoughts.
        """

        sections = self.integration._parse_chat_for_sections(chat_content)

        self.assertEqual(len(sections), 4)
        self.assertEqual(sections[0]["title"], "Introduction")
        self.assertEqual(sections[1]["title"], "Chapter 1")
        self.assertEqual(sections[2]["title"], "Subsection")
        self.assertEqual(sections[3]["title"], "Conclusion")

    def test_parse_chat_for_sections_with_files(self):
        """Test parsing chat content with file references"""
        chat_content = """
        # Resources
        Here are some resources:
        - https://example.com/document.pdf
        - Check out this presentation: https://slides.com/presentation.ppt
        """

        sections = self.integration._parse_chat_for_sections(chat_content)

        self.assertEqual(len(sections), 1)
        self.assertEqual(len(sections[0]["files"]), 2)
        self.assertEqual(sections[0]["files"][0]["type"], "url")
        self.assertIn("document.pdf", sections[0]["files"][0]["url"])

    def test_create_structured_course_from_chat(self):
        """Test creating structured course from chat content"""
        # Mock API responses
        self.mock_api.create_course.return_value = {"id": 123}
        self.mock_api.create_course_section.side_effect = [
            {"id": 1},  # create section 1
            {"id": 2},  # create section 2
        ]

        chat_content = """
        # Introduction
        Welcome to the course.
        
        # Main Content
        This is the main content.
        """

        result = self.integration.create_structured_course_from_chat(chat_content, "Test Course", 1)

        self.assertEqual(result["courseid"], 123)
        self.assertEqual(len(result["sections"]), 2)
        self.assertIn("course/view.php?id=123", result["course_url"])

        # Verify create_course_section was called
        self.assertEqual(self.mock_api.create_course_section.call_count, 2)

    def test_bulk_update_course_structure(self):
        """Test bulk updating course structure"""
        self.mock_api.bulk_section_operations.return_value = {"success": True}

        structure_updates = [
            {"type": "move_section", "sectionid": 1, "position": 2},
            {"type": "update_section", "sectionid": 2, "data": {"name": "New Name"}},
            {"type": "duplicate_section", "sectionid": 3, "target_courseid": 456},
        ]

        result = self.integration.bulk_update_course_structure(123, structure_updates)

        self.assertTrue(result["success"])
        self.mock_api.bulk_section_operations.assert_called_once()

        # Verify operations were properly formatted
        call_args = self.mock_api.bulk_section_operations.call_args[0][0]
        self.assertEqual(len(call_args), 3)
        self.assertEqual(call_args[0]["operation"], "move")
        self.assertEqual(call_args[1]["operation"], "update")
        self.assertEqual(call_args[2]["operation"], "duplicate")

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"file content")
    def test_add_resources_to_section_file(self, mock_file, mock_exists):
        """Test adding file resources to a section"""
        mock_exists.return_value = True
        self.mock_api.create_file_resource.return_value = {"cmid": 456}

        resources = [
            {
                "type": "file",
                "path": "/path/to/test.pdf",
                "name": "Test PDF",
                "description": "A test PDF file",
            }
        ]

        results = self.integration.add_resources_to_section(123, 1, resources)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["cmid"], 456)
        self.mock_api.create_file_resource.assert_called_once()

        # Verify file was opened and read
        mock_file.assert_called_once()

    def test_add_resources_to_section_url(self):
        """Test adding URL resources to a section"""
        self.mock_api.create_url_resource.return_value = {"cmid": 789}

        resources = [
            {
                "type": "url",
                "url": "https://example.com",
                "name": "Example Website",
                "description": "An example website",
            }
        ]

        results = self.integration.add_resources_to_section(123, 1, resources)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["cmid"], 789)
        self.mock_api.create_url_resource.assert_called_once()

        # Verify correct parameters were passed
        call_args = self.mock_api.create_url_resource.call_args
        self.assertEqual(call_args[1]["name"], "Example Website")
        self.assertEqual(call_args[1]["url"], "https://example.com")

    @patch("pathlib.Path.exists")
    def test_add_resources_file_not_exists(self, mock_exists):
        """Test handling of non-existent files"""
        mock_exists.return_value = False

        resources = [{"type": "file", "path": "/nonexistent/file.pdf", "name": "Missing File"}]

        results = self.integration.add_resources_to_section(123, 1, resources)

        # Should return empty list since file doesn't exist
        self.assertEqual(len(results), 0)
        self.mock_api.create_file_resource.assert_not_called()

    def test_create_file_resource_from_description_url(self):
        """Test creating file resource from URL description"""
        self.mock_api.create_url_resource.return_value = {"cmid": 999}

        file_info = {
            "type": "url",
            "url": "https://example.com/resource.pdf",
            "name": "PDF Resource",
        }

        result = self.integration._create_file_resource_from_description(123, 1, file_info)

        self.assertEqual(result["cmid"], 999)
        self.mock_api.create_url_resource.assert_called_once()


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.integration = MoodleClaudeIntegration("http://test.moodle.com", "test_token")
        self.mock_api = Mock()
        self.integration.api = self.mock_api

    def test_complete_course_creation_workflow(self):
        """Test complete workflow of course creation with sections and resources"""
        # Mock API responses for the complete workflow
        self.mock_api.create_course.return_value = {"id": 123}
        self.mock_api.create_course_section.side_effect = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.mock_api.create_url_resource.return_value = {"cmid": 456}

        # Complex chat content with multiple sections and resources
        chat_content = """
        # Course Introduction
        Welcome to our comprehensive course on Python programming.
        
        ## Getting Started
        Before we begin, make sure you have Python installed.
        Resource: https://python.org/downloads/python-installer.exe
        
        # Advanced Topics
        Now let's dive into advanced concepts.
        """

        # Create course from chat
        course_result = self.integration.create_structured_course_from_chat(
            chat_content, "Complete Python Course", 1
        )

        # Add additional resources
        resources = [
            {
                "type": "url",
                "url": "https://docs.python.org",
                "name": "Python Documentation",
                "description": "Official Python documentation",
            }
        ]

        resource_results = self.integration.add_resources_to_section(
            course_result["courseid"], 1, resources
        )

        # Perform bulk operations
        bulk_updates = [
            {"type": "move_section", "sectionid": 1, "position": 2},
            {"type": "update_section", "sectionid": 2, "data": {"name": "Updated Section"}},
        ]

        self.mock_api.bulk_section_operations.return_value = {"success": True}
        bulk_result = self.integration.bulk_update_course_structure(
            course_result["courseid"], bulk_updates
        )

        # Verify all operations completed successfully
        self.assertEqual(course_result["courseid"], 123)
        self.assertEqual(len(course_result["sections"]), 3)  # Including introduction
        self.assertEqual(len(resource_results), 1)
        self.assertTrue(bulk_result["success"])

        # Verify API calls were made in correct order
        self.mock_api.create_course_section.assert_called()
        self.mock_api.bulk_section_operations.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.api = EnhancedMoodleAPI("http://test.moodle.com", "test_token")
        self.mock_session = Mock()
        self.api.session = self.mock_session

    def test_network_error_handling(self):
        """Test handling of network errors"""
        self.mock_session.post.side_effect = requests.ConnectionError("Network error")

        with self.assertRaises(requests.ConnectionError):
            self.api._make_request("test_function", {})

    def test_http_error_handling(self):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        self.mock_session.post.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.api._make_request("test_function", {})

    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        with self.assertRaises(json.JSONDecodeError):
            self.api._make_request("test_function", {})

    def test_moodle_exception_response(self):
        """Test handling of Moodle exception responses"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "exception": "invalid_parameter_exception",
            "message": "Invalid course ID",
            "debuginfo": "Course with ID 999 does not exist",
        }
        mock_response.raise_for_status.return_value = None
        self.mock_session.post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.api._make_request("test_function", {})

        self.assertIn("Invalid course ID", str(context.exception))


class TestPerformance(unittest.TestCase):
    """Test performance-related scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.integration = MoodleClaudeIntegration("http://test.moodle.com", "test_token")
        self.mock_api = Mock()
        self.integration.api = self.mock_api

    def test_bulk_operations_efficiency(self):
        """Test that bulk operations are more efficient than individual calls"""
        # Simulate bulk operations
        bulk_operations = [
            {"type": "move_section", "sectionid": i, "position": i + 1} for i in range(10)
        ]

        self.mock_api.bulk_section_operations.return_value = {"success": True}

        # Perform bulk update
        result = self.integration.bulk_update_course_structure(123, bulk_operations)

        # Should make only one API call for all operations
        self.mock_api.bulk_section_operations.assert_called_once()
        self.assertTrue(result["success"])

    def test_large_content_parsing(self):
        """Test parsing of large chat content"""
        # Generate large content with many sections
        sections_content = []
        for i in range(100):
            sections_content.append(f"# Section {i}\nContent for section {i}")

        large_content = "\n\n".join(sections_content)

        # Should handle large content without issues
        sections = self.integration._parse_chat_for_sections(large_content)

        self.assertEqual(len(sections), 100)
        self.assertEqual(sections[0]["title"], "Section 0")
        self.assertEqual(sections[99]["title"], "Section 99")


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestSectionConfig,
        TestFileUploadConfig,
        TestEnhancedMoodleAPI,
        TestMoodleClaudeIntegration,
        TestIntegrationScenarios,
        TestErrorHandling,
        TestPerformance,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )
    print(f"{'='*50}")

    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    exit(exit_code)
