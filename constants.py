"""
Constants and configuration values for MoodleClaude
Centralizes hard-coded strings, URLs, and configuration defaults
"""

from dataclasses import dataclass


class Defaults:
    """Default configuration values"""
    
    # Server defaults
    MOODLE_URL = "http://localhost:8080"
    MOODLE_PORT = 8080
    MOODLE_ADMIN_USER = "admin"
    MOODLE_TOKEN = ""
    
    # Server configuration
    SERVER_NAME = "moodle-course-creator"
    SERVER_VERSION = "1.0.0"
    LOG_LEVEL = "INFO"
    
    # Content processing limits
    MAX_CODE_LENGTH = 10000
    MAX_TOPIC_LENGTH = 5000
    MIN_CODE_LINES = 3
    MIN_TOPIC_WORDS = 10
    MAX_SECTIONS = 50
    MAX_ITEMS_PER_SECTION = 100
    
    # API endpoints
    WEBSERVICE_PATH = "/webservice/rest/server.php"
    ADMIN_PATH = "/admin"
    LOGIN_PATH = "/login/index.php"


class Messages:
    """User-facing messages and log strings"""
    
    # Initialization messages
    MOODLE_CLIENT_SUCCESS = "Moodle client initialized successfully"
    MOODLE_CLIENT_FAILED = "Moodle client initialization failed: {error}"
    PREVIEW_MODE = "Running in preview mode - no Moodle credentials provided"
    
    # Operation messages
    PARSING_STARTED = "Starting chat content parsing"
    PARSING_COMPLETED = "Parsed {count} content items from chat"
    COURSE_CREATED = "Created course '{name}' with ID: {course_id}"
    COURSE_CREATION_FAILED = "Failed to create course: {error}"
    
    # Tool execution messages
    TOOL_EXECUTION_FAILED = "Tool execution failed: {error}"
    CONTENT_PREVIEW_FAILED = "Failed to preview content: {error}"
    CONTENT_ADD_FAILED = "Failed to add content to course: {error}"
    
    # API error messages
    API_ERROR = "Moodle API error"
    CONNECTION_ERROR = "Failed to connect to Moodle server"
    AUTHENTICATION_ERROR = "Authentication failed - check token"
    PERMISSION_ERROR = "Permission denied - check user permissions"
    
    # Validation messages
    INVALID_CONTENT_TYPE = "Invalid content type: {type}"
    EMPTY_CONTENT = "Content cannot be empty"
    INVALID_URL = "Invalid Moodle URL: {url}"
    MISSING_CREDENTIALS = "Missing Moodle credentials"


class ToolDescriptions:
    """MCP tool descriptions and schemas"""
    
    CREATE_COURSE_NAME = "create_course_from_chat"
    CREATE_COURSE_DESC = "Extract content from Claude chat and create a Moodle course"
    
    PREVIEW_CONTENT_NAME = "extract_and_preview_content"
    PREVIEW_CONTENT_DESC = "Extract and preview content from chat without creating course"
    
    ADD_CONTENT_NAME = "add_content_to_course"
    ADD_CONTENT_DESC = "Add extracted content to an existing Moodle course"
    
    # Schema descriptions
    CHAT_CONTENT_DESC = "The full chat conversation content"
    COURSE_NAME_DESC = "Name for the Moodle course"
    COURSE_DESC_DESC = "Description for the Moodle course"
    CATEGORY_ID_DESC = "Moodle category ID (optional)"
    COURSE_ID_DESC = "ID of the existing Moodle course"


class ContentTypes:
    """Content type constants"""
    
    CODE = "code"
    TOPIC = "topic"
    MIXED = "mixed"
    
    VALID_TYPES = [CODE, TOPIC, MIXED]


class ActivityTypes:
    """Moodle activity type constants"""
    
    PAGE = "page"
    RESOURCE = "resource"
    LABEL = "label"
    FORUM = "forum"
    ASSIGNMENT = "assign"
    QUIZ = "quiz"
    
    DEFAULT_TYPE = PAGE


class ErrorCodes:
    """Error code constants for better error handling"""
    
    CONFIGURATION_ERROR = "CONFIG_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    AUTHENTICATION_ERROR = "AUTH_ERROR"
    PERMISSION_ERROR = "PERMISSION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    API_ERROR = "API_ERROR"
    PARSING_ERROR = "PARSE_ERROR"
    CONTENT_ERROR = "CONTENT_ERROR"


@dataclass
class HttpStatus:
    """HTTP status codes"""
    
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class Environment:
    """Environment variable names"""
    
    MOODLE_URL = "MOODLE_URL"
    MOODLE_TOKEN = "MOODLE_TOKEN"
    MOODLE_USERNAME = "MOODLE_USERNAME"
    MOODLE_ADMIN_USER = "MOODLE_ADMIN_USER"
    MOODLE_ADMIN_PASSWORD = "MOODLE_ADMIN_PASSWORD"
    
    LOG_LEVEL = "LOG_LEVEL"
    SERVER_NAME = "SERVER_NAME"
    SERVER_VERSION = "SERVER_VERSION"
    
    # Google Cloud specific
    PORT = "PORT"
    PROJECT_ID = "PROJECT_ID"
    GOOGLE_CLOUD_PROJECT = "GOOGLE_CLOUD_PROJECT"


class Patterns:
    """Regex patterns for content parsing"""
    
    CODE_BLOCK = r"```(\w+)?\n(.*?)```"
    CODE_INLINE = r"`([^`]+)`"
    URL_PATTERN = r"https?://[^\s<>\"{}|\\^`\[\]]+"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"