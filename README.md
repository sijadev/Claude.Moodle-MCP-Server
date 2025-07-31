# MoodleClaude

**Automated Moodle course creation powered by Claude AI and MCP (Model Context Protocol)**

Transform Claude Desktop conversations into complete Moodle courses with activities, resources, and structured content.

## 🚀 Quick Start

```bash
# 1. Start fresh Moodle environment
python tools/setup/setup_fresh_moodle.py

# 2. Configure web services (follow the guide)
# See docs/FRESH_SETUP_GUIDE.md for detailed instructions

# 3. Test the dual-token system
python tools/testing/verify_dual_tokens.py
```

## 📁 Project Structure

```
MoodleClaude/
├── src/                          # Core source code
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration management
│   │   ├── constants.py         # System constants
│   │   ├── content_parser.py    # Chat content parsing
│   │   ├── content_formatter.py # Content formatting
│   │   ├── mcp_server.py        # MCP server implementation
│   │   └── enhanced_mcp_server.py # Enhanced MCP with plugin support
│   ├── clients/                  # Moodle API clients
│   │   ├── moodle_client.py     # Basic Moodle client
│   │   ├── moodle_client_enhanced.py # Enhanced client with plugin support
│   │   └── enhanced_moodle_claude.py # Full MoodleClaude integration
│   └── models/                   # Data models
│       └── models.py            # Pydantic models
├── config/                       # Configuration files
│   └── dual_token_config.py     # Dual-token system configuration
├── tools/                        # Utilities and tools
│   ├── setup/                   # Setup and installation tools
│   │   ├── setup_fresh_moodle.py # Complete fresh setup script
│   │   ├── setup_plugin_service.py # Plugin service setup
│   │   ├── generate_token.py    # Token generation utility
│   │   └── enable_webservices.py # Web services enabler
│   ├── debug/                   # Debug and diagnostic tools
│   │   ├── debug_*.py          # Various debug scripts
│   │   ├── diagnose_service_access.py # Service access diagnostics
│   │   └── explore_*.py        # API exploration tools
│   └── testing/                 # Testing utilities
│       ├── verify_dual_tokens.py # Dual-token system verification
│       ├── test_*.py           # Individual test scripts
│       └── run_all_tests.py    # Test runner
├── moodle_plugin/               # Custom Moodle plugin
│   └── local_moodleclaude/     # Plugin source code
├── tests/                       # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── manual/                 # Manual test scripts
│   └── e2e/                    # End-to-end tests
├── docs/                        # 📚 All Documentation
│   ├── INDEX.md                # Documentation index
│   ├── FRESH_SETUP_GUIDE.md    # Complete setup guide
│   ├── PLUGIN_INSTALLATION.md  # Plugin installation guide
│   ├── TESTING_GUIDE.md        # Testing instructions
│   └── ... (20+ documentation files)
└── docker-compose.yml          # Docker environment
```

## ✨ Features

- **🤖 AI-Powered Content Creation**: Transform Claude conversations into structured courses
- **🔄 Dual-Token System**: Separate tokens for basic and enhanced functionality  
- **📚 Rich Activities**: Create pages, labels, files, and structured sections
- **🔒 Secure Authorization**: "Authorised users only" support
- **🚀 Complete Automation**: From chat to course in seconds
- **🐳 Docker Environment**: Ready-to-use Moodle setup
- **🧪 Comprehensive Testing**: Unit, integration, and E2E tests

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MoodleClaude
   ```

2. **Set up the environment**
   ```bash
   python tools/setup/setup_fresh_moodle.py
   ```

3. **Follow the setup guide**
   See [FRESH_SETUP_GUIDE.md](FRESH_SETUP_GUIDE.md) for detailed instructions.

## 🔧 Configuration

- **Environment**: Copy `.env.example` to `.env` and configure dual tokens
- **Docker**: Use `docker-compose.yml` for Moodle environment  
- **Plugin**: Custom plugin in `moodle_plugin/local_moodleclaude/`
- **Claude Desktop**: Configure MCP server in `claude_desktop_config.json` (see [docs/CLAUDE_DESKTOP_SETUP.md](docs/CLAUDE_DESKTOP_SETUP.md))

## 🧪 Testing

```bash
# Run all tests
python tools/testing/run_all_tests.py

# Verify dual-token system
python tools/testing/verify_dual_tokens.py

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
```

## 🏗️ Architecture Overview

MoodleClaude uses a layered architecture with intelligent session management and adaptive content processing:

```mermaid
classDiagram
    %% MCP Server Layer
    class AdvancedMoodleMCPServer {
        -server: Server
        -config: DualTokenConfig
        -moodle_client: EnhancedMoodleClient
        -session_manager: IntelligentSessionManager
        +_create_intelligent_course(arguments) List~TextContent~
        +_continue_course_session(arguments) List~TextContent~
        +_validate_course(arguments) List~TextContent~
        +_get_session_status(arguments) List~TextContent~
        +_analyze_content_complexity(arguments) List~TextContent~
    }

    class EnhancedMoodleMCPServer {
        -server: Server
        -config: DualTokenConfig
        -basic_client: MoodleClient
        -enhanced_client: EnhancedMoodleClient
        +_create_course_from_chat(arguments) List~TextContent~
        +_extract_and_preview_content(arguments) List~TextContent~
        +_test_plugin_functionality(arguments) List~TextContent~
        +_organize_content(parsed_content) CourseStructure
    }

    %% Session Management Layer
    class IntelligentSessionManager {
        -content_processor: AdaptiveContentProcessor
        -moodle_client: EnhancedMoodleClient
        -db_config: SessionDatabase
        -active_sessions: Dict~str, ProcessingSession~
        +create_intelligent_course_session(content, course_name, continue_previous) Dict
        +continue_session_processing(session_id, additional_content) Dict
        +_create_moodle_course(session, course_structure) Dict
        +_update_moodle_course(session, course_structure) Dict
        +get_session_analytics() Dict
        +cleanup_and_shutdown()
    }

    %% Content Processing Layer
    class AdaptiveContentProcessor {
        -parser: ChatContentParser
        -sessions: Dict~str, ProcessingSession~
        -current_limits: ContentLimits
        +analyze_content_complexity(content) Dict
        +create_session(content, course_name) str
        +process_content_chunk(session_id, chunk_index, continue_previous) Tuple
        +_create_intelligent_chunks(parsed_content) List~str~
        +_create_progressive_chunks(parsed_content) List~str~
        +get_processing_metrics() Dict
    }

    class ChatContentParser {
        -language_patterns: Dict
        -topic_keywords: List~str~
        +parse_chat(chat_content) ChatContent
        +_split_into_messages(content) List~str~
        +_extract_code_blocks(message, current_topic) List~ContentItem~
        +_detect_language(code) str
        +_extract_topic_descriptions(message) List~ContentItem~
    }

    %% Client Layer
    class EnhancedMoodleClient {
        -base_url: str
        -basic_token: str
        -plugin_token: str
        -session: aiohttp.ClientSession
        +create_course_structure(course_id, sections_data) Dict
        +create_page_activity(course_id, section_id, name, content) Dict
        +create_label_activity(course_id, section_id, content) Dict
        +update_section_content(course_id, section_number, name, summary) bool
        +_check_plugin_availability() bool
    }

    class MoodleClient {
        -base_url: str
        -token: str
        -session: aiohttp.ClientSession
        +create_course(name, description, category_id) int
        +create_section(course_id, name, description, position) int
        +create_page_activity(course_id, section_id, name, content) Dict
        +get_courses() List~Dict~
        +_call_api(function, params) Dict
    }

    %% Configuration Layer
    class DualTokenConfig {
        +moodle_url: str
        +basic_token: str
        +plugin_token: str
        +username: str
        +server_name: str
        +log_level: str
        +from_env() DualTokenConfig
        +get_basic_token() str
        +get_plugin_token() str
        +is_dual_token_mode() bool
    }

    %% Model Layer
    class ContentItem {
        +type: str
        +title: str
        +content: str
        +description: str
        +language: str
        +topic: str
        +metadata: Dict
        +word_count: int
        +to_dict() Dict
    }

    class ChatContent {
        +items: List~ContentItem~
        +metadata: Dict
        +code_items: List~ContentItem~
        +topic_items: List~ContentItem~
        +get_items_by_topic(topic) List~ContentItem~
        +to_dict() Dict
    }

    class CourseSection {
        +name: str
        +description: str
        +items: List~ContentItem~
        +section_id: int
        +add_item(item) void
        +to_dict() Dict
    }

    class CourseStructure {
        +sections: List~CourseSection~
        +course_id: int
        +name: str
        +description: str
        +total_items: int
        +add_section(section) void
        +get_section_by_name(name) CourseSection
        +to_dict() Dict
    }

    %% Processing Session Classes
    class ProcessingSession {
        +session_id: str
        +content: str
        +course_name: str
        +state: SessionState
        +strategy: ProcessingStrategy
        +chunks: List~str~
        +current_chunk_index: int
        +course_structure: CourseStructure
        +created_at: datetime
        +updated_at: datetime
    }

    class ProcessingStrategy {
        <<enumeration>>
        SINGLE_PASS
        INTELLIGENT_CHUNK
        PROGRESSIVE_BUILD
        ADAPTIVE_PROCESS
    }

    class SessionState {
        <<enumeration>>
        CREATED
        PARSING
        CHUNKING
        PROCESSING
        CREATING_COURSE
        COMPLETED
        FAILED
        WAITING_FOR_CONTINUATION
    }

    %% Relationships
    AdvancedMoodleMCPServer --> IntelligentSessionManager
    AdvancedMoodleMCPServer --> DualTokenConfig
    AdvancedMoodleMCPServer --> EnhancedMoodleClient

    EnhancedMoodleMCPServer --> MoodleClient
    EnhancedMoodleMCPServer --> EnhancedMoodleClient
    EnhancedMoodleMCPServer --> DualTokenConfig
    EnhancedMoodleMCPServer --> ChatContentParser

    IntelligentSessionManager --> AdaptiveContentProcessor
    IntelligentSessionManager --> EnhancedMoodleClient
    IntelligentSessionManager --> ProcessingSession

    AdaptiveContentProcessor --> ChatContentParser
    AdaptiveContentProcessor --> ProcessingSession
    AdaptiveContentProcessor --> ProcessingStrategy

    ChatContentParser --> ContentItem
    ChatContentParser --> ChatContent

    EnhancedMoodleClient --|> MoodleClient

    ProcessingSession --> SessionState
    ProcessingSession --> ProcessingStrategy
    ProcessingSession --> CourseStructure

    CourseStructure --> CourseSection
    CourseSection --> ContentItem
    ChatContent --> ContentItem
```

### Key Architecture Components

#### 🎯 **MCP Server Layer**
- **AdvancedMoodleMCPServer**: Advanced server with intelligent session management and adaptive processing
- **EnhancedMoodleMCPServer**: Enhanced server with dual-token support and plugin functionality

#### 🧠 **Session Management Layer**
- **IntelligentSessionManager**: Orchestrates course creation with database persistence and analytics
- **AdaptiveContentProcessor**: Analyzes content complexity and selects optimal processing strategies

#### 📝 **Content Processing Layer**
- **ChatContentParser**: Extracts structured content from Claude conversations
- **ProcessingStrategy**: Defines content processing approaches (single-pass, chunked, progressive, adaptive)

#### 🌐 **Client Layer**
- **EnhancedMoodleClient**: Full-featured client using custom MoodleClaude plugin
- **MoodleClient**: Basic client for standard Moodle Web Services API

#### 📊 **Data Layer**
- **ContentItem**: Individual pieces of content (code blocks, topics, descriptions)
- **ChatContent**: Parsed conversation with metadata and organization
- **CourseStructure**: Complete Moodle course representation with sections and activities

### Data Flow

1. **Input** → Chat content enters through MCP server
2. **Parsing** → ChatContentParser extracts ContentItems into ChatContent
3. **Analysis** → AdaptiveContentProcessor analyzes complexity and selects strategy
4. **Session** → IntelligentSessionManager creates ProcessingSession with database persistence
5. **Processing** → Content is chunked and processed according to selected strategy
6. **Creation** → EnhancedMoodleClient creates CourseStructure in Moodle
7. **Validation** → System validates creation and provides analytics

## 📖 Documentation

**📚 [Complete Documentation Index](docs/INDEX.md)** - All documentation organized by topic

**Quick Links:**
- [Fresh Setup Guide](docs/FRESH_SETUP_GUIDE.md) - Complete installation instructions  
- [Plugin Installation](docs/PLUGIN_INSTALLATION.md) - Moodle plugin setup
- [Testing Guide](docs/TESTING_GUIDE.md) - Testing procedures
- [Features Overview](docs/FEATURES_AND_CAPABILITIES.md) - Detailed feature list
- [Claude Desktop Setup](docs/CLAUDE_DESKTOP_SETUP.md) - MCP integration guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🎯 Quick Links

- **Setup**: [FRESH_SETUP_GUIDE.md](FRESH_SETUP_GUIDE.md)
- **Claude Desktop**: [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md)
- **Testing**: `python tools/testing/verify_dual_tokens.py`
- **Plugin**: [moodle_plugin/local_moodleclaude/](moodle_plugin/local_moodleclaude/)
- **Docker**: `docker-compose up -d`