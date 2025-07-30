# 📚 MoodleClaude Documentation

Welcome to the complete documentation for MoodleClaude - an intelligent system that creates structured Moodle courses from chat conversations using Claude Desktop's MCP integration.

## 🚀 Quick Start

### Essential Guides (Start Here!)
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Complete installation and configuration
- **[FEATURES_AND_CAPABILITIES.md](./FEATURES_AND_CAPABILITIES.md)** - What MoodleClaude can do
- **[CONSOLIDATED_TESTING.md](./CONSOLIDATED_TESTING.md)** - Comprehensive testing reference

### Getting Started in 5 Minutes
1. **Setup**: Follow [SETUP_GUIDE.md](./SETUP_GUIDE.md) for Docker environment
2. **Configure**: Set up Moodle web services and MCP integration  
3. **Test**: Run `uv run python test_enhanced_moodle.py` to verify
4. **Use**: Access MCP tools in Claude Desktop for course creation

## 📚 Complete Documentation Index

### 🔧 Setup & Configuration
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - ⭐ **START HERE** - Complete setup guide
- **[MOODLE_SETUP.md](./MOODLE_SETUP.md)** - Detailed web services configuration

### 🚀 Features & Success Stories
- **[FEATURES_AND_CAPABILITIES.md](./FEATURES_AND_CAPABILITIES.md)** - ⭐ Complete feature overview
- **[BREAKTHROUGH_SUCCESS.md](./BREAKTHROUGH_SUCCESS.md)** - WSManageSections breakthrough story

### 🧪 Testing & Validation
- **[CONSOLIDATED_TESTING.md](./CONSOLIDATED_TESTING.md)** - ⭐ Complete testing guide
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Automated test runners
- **[E2E_TESTING.md](./E2E_TESTING.md)** - Browser automation tests
- **[TESTS_README.md](./TESTS_README.md)** - Test structure overview

### 📋 Technical Documentation
- **[DOCUMENTATION.md](./DOCUMENTATION.md)** - Architecture and design
- **[DEMOS_README.md](./DEMOS_README.md)** - Demo scripts and examples
- **[CI_FIX.md](./CI_FIX.md)** - Build and deployment fixes

## 🎯 What MoodleClaude Does

### ✅ Fully Automated Course Creation
```
Chat Content → Intelligent Analysis → Course Structure → Moodle Integration
```

**Key Capabilities:**
- **🎓 Course Creation**: Complete courses with intelligent metadata
- **📖 Section Management**: Dynamic section creation and organization
- **🧠 Content Intelligence**: Smart parsing and categorization
- **🔧 MCP Integration**: Seamless Claude Desktop tools
- **🚀 Professional Results**: Production-ready course structures

### Real-World Example
```python
# From chat conversation to structured Moodle course
chat_content = "Discussion about Python programming..."

# MCP tools automatically:
course_id = create_course_from_chat(
    content=chat_content,
    course_name="Python Programming Fundamentals"
)

# Results in:
# ✅ Course with 5 organized sections
# ✅ Content categorized by topic and complexity  
# ✅ Code examples with syntax highlighting
# ✅ Learning progression structure
```

## 🔗 Related Files

The main project files are located in the parent directory:
- `constants.py` - Centralized configuration and constants
- `config.py` - Configuration management
- `mcp_server.py` - Main MCP server implementation
- `moodle_client.py` - Moodle API client
- `models.py` - Data models and structures
- `content_parser.py` - Chat content parsing logic

---

*Last updated: July 29, 2025*