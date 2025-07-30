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