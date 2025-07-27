# Replit MCP Moodle Course Creator

## Overview

This is a Model Context Protocol (MCP) server application that creates Moodle courses from Claude chat conversations. The system extracts code examples and educational topics from chat content, formats them appropriately, and creates structured Moodle courses with activities and resources.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **MCP Server Layer**: Handles MCP protocol communication and tool registration
- **Content Processing Layer**: Parses chat content and extracts meaningful educational materials
- **Moodle Integration Layer**: Manages API interactions with Moodle instances
- **Configuration Layer**: Manages environment-based settings and defaults

The system is designed as an asynchronous Python application using the MCP (Model Context Protocol) framework for AI agent integration.

## Key Components

### Core Modules

1. **mcp_server.py** - Main MCP server implementation that handles tool registration and orchestrates the course creation workflow
2. **content_parser.py** - Intelligent parser that extracts code blocks and educational topics from chat conversations using pattern matching and language detection
3. **moodle_client.py** - Async HTTP client for Moodle Web Services API integration with proper error handling and session management
4. **content_formatter.py** - Formats extracted content into Moodle-compatible HTML with syntax highlighting and proper styling
5. **models.py** - Data models defining the structure for content items, chat content, and course organization
6. **config.py** - Configuration management using environment variables with sensible defaults

### Content Processing Pipeline

The system processes content through these stages:
1. **Parsing**: Identifies code blocks and topics using regex patterns and language detection
2. **Classification**: Categorizes content by programming language and subject matter
3. **Formatting**: Converts content to Moodle-compatible HTML with syntax highlighting
4. **Organization**: Structures content into logical course sections and activities

### Language Detection

Supports automatic detection of 20+ programming languages using pattern matching:
- Python, JavaScript, TypeScript, Java, C++, C
- HTML, CSS, SQL, Bash, JSON, YAML, XML
- Go, Rust, PHP, Ruby, Swift, Kotlin, R, MATLAB, Scala

## Data Flow

1. **Input**: Chat conversation content received via MCP tools
2. **Parsing**: Content parser extracts code examples and educational topics
3. **Processing**: Content formatter applies syntax highlighting and Moodle styling
4. **API Integration**: Moodle client creates courses, sections, and activities
5. **Output**: Structured Moodle course with organized learning materials

## External Dependencies

### Required Services
- **Moodle Instance**: Target Moodle site with Web Services API enabled
- **Moodle Web Service Token**: Authentication token with course creation permissions

### Python Libraries
- **mcp**: Model Context Protocol framework for AI agent integration
- **aiohttp**: Async HTTP client for Moodle API communication
- **pygments**: Syntax highlighting for code examples
- **markdown**: Markdown to HTML conversion for topic content

### Environment Variables
- `MOODLE_URL`: Base URL of the target Moodle instance (required)
- `MOODLE_TOKEN`: Web service authentication token (required)
- `MOODLE_USERNAME`: Optional username for API calls
- `LOG_LEVEL`: Logging level (default: INFO)
- `SERVER_NAME`: MCP server name (default: moodle-course-creator)

## Deployment Strategy

### Configuration Requirements
- Moodle instance with Web Services enabled
- Web service token with appropriate permissions (course creation, activity management)
- Python 3.8+ environment with required dependencies

### Integration Options
- **MCP Agent Integration**: Primary deployment as an MCP server for AI agents
- **Standalone Usage**: Can be extended for direct API usage
- **Development Mode**: Local development with environment variable configuration

### Error Handling
- Graceful degradation when Moodle credentials are unavailable
- Comprehensive logging for debugging and monitoring
- Validation of content length and quality before processing

The architecture prioritizes modularity, allowing easy extension for additional content types, Moodle activity formats, or integration with other learning management systems.