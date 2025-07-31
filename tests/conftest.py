"""
Pytest configuration and shared fixtures
"""

import os
import tempfile
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest


# Test fixtures
@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    return {
        "MOODLE_URL": "http://test-moodle.example.com",
        "MOODLE_TOKEN": "test_token_12345678901234567890123456789012",
        "MOODLE_USERNAME": "testuser",
        "SERVER_NAME": "test-moodle-server",
        "LOG_LEVEL": "DEBUG",
    }


@pytest.fixture
def sample_chat_content():
    """Sample chat content for testing"""
    return """
    User: Can you show me how to create a Python function?
    
    Assistant: Here's a simple Python function:
    
    ```python
    def greet(name):
        return f"Hello, {name}!"
    
    # Example usage
    result = greet("World")
    print(result)  # Output: Hello, World!
    ```
    
    This function takes a name parameter and returns a greeting string.
    
    User: What about error handling?
    
    Assistant: Here's the same function with error handling:
    
    ```python
    def safe_greet(name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not name.strip():
            raise ValueError("Name cannot be empty")
        return f"Hello, {name}!"
    
    # Example with error handling
    try:
        result = safe_greet("World")
        print(result)
    except (TypeError, ValueError) as e:
        print(f"Error: {e}")
    ```
    
    This version includes input validation and proper error handling.
    """


@pytest.fixture
def sample_course_structure():
    """Sample course structure for testing"""
    import sys
    import os
    
    # Add the src directory to the Python path for imports to work  
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(current_dir, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    try:
        from src.models.models import ContentItem, CourseStructure
    except ImportError:
        from models.models import ContentItem, CourseStructure

    items = [
        ContentItem(
            type="code",
            title="Basic Python Function",
            content='def greet(name):\n    return f"Hello, {name}!"',
            language="python",
            description="A simple greeting function",
        ),
        ContentItem(
            type="code",
            title="Error Handling Function",
            content='def safe_greet(name):\n    if not isinstance(name, str):\n        raise TypeError("Name must be a string")\n    return f"Hello, {name}!"',
            language="python",
            description="Function with error handling",
        ),
        ContentItem(
            type="topic",
            title="Function Basics",
            content="Functions are reusable blocks of code that perform specific tasks.",
            description="Introduction to Python functions",
        ),
    ]

    section = CourseStructure.Section(
        name="Python Functions", description="Learn about Python functions", items=items
    )

    return CourseStructure(sections=[section])


@pytest.fixture
def mock_moodle_responses():
    """Mock Moodle API responses"""
    return {
        "create_course": {"id": 123, "shortname": "test_course"},
        "create_section": {"id": 456},
        "create_page_activity": {"id": 789, "name": "Test Page"},
        "create_file_activity": {"id": 101112, "name": "Test File"},
        "get_courses": [
            {"id": 1, "fullname": "Test Course 1", "shortname": "test1"},
            {"id": 2, "fullname": "Test Course 2", "shortname": "test2"},
        ],
        "get_categories": [{"id": 1, "name": "General", "description": "General category"}],
    }


@pytest.fixture
def mock_moodle_client(mock_moodle_responses):
    """Mock Moodle client for testing"""
    client = AsyncMock()
    client.create_course.return_value = mock_moodle_responses["create_course"]["id"]
    client.create_section.return_value = mock_moodle_responses["create_section"]["id"]
    client.create_page_activity.return_value = mock_moodle_responses["create_page_activity"]
    client.create_file_activity.return_value = mock_moodle_responses["create_file_activity"]
    client.get_courses.return_value = mock_moodle_responses["get_courses"]
    client.get_categories.return_value = mock_moodle_responses["get_categories"]
    return client


@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("MOODLE_URL=http://test.example.com\n")
        f.write("MOODLE_TOKEN=test_token\n")
        f.write("MOODLE_USERNAME=testuser\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test"""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    return Mock()


# Test utilities
class MockResponse:
    """Mock HTTP response for testing"""

    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)

    async def json(self):
        return self.json_data

    async def text(self):
        return self.text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def create_mock_response(data: Dict[str, Any], status: int = 200) -> MockResponse:
    """Helper to create mock HTTP responses"""
    return MockResponse(data, status)
