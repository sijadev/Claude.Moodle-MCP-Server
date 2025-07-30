# MoodleClaude Directory Structure

## 📁 Organized Project Layout

### Core Application (`src/`)
- **`src/core/`** - Core functionality and business logic
- **`src/clients/`** - Moodle API clients and integrations  
- **`src/models/`** - Data models and schemas

### Configuration (`config/`)
- **`dual_token_config.py`** - Dual-token system configuration
- **`.env`** - Environment variables (not in git)

### Tools & Utilities (`tools/`)
- **`tools/setup/`** - Installation and setup scripts
- **`tools/debug/`** - Debug and diagnostic utilities
- **`tools/testing/`** - Testing tools and verification scripts

### Plugin (`moodle_plugin/`)
- **`local_moodleclaude/`** - Complete Moodle plugin source

### Tests (`tests/`)
- **`unit/`** - Unit tests for individual components
- **`integration/`** - Integration tests for combined functionality
- **`manual/`** - Manual test scripts
- **`e2e/`** - End-to-end tests

### Documentation
- **`readme/`** - Comprehensive documentation
- **`FRESH_SETUP_GUIDE.md`** - Step-by-step setup instructions
- **`README.md`** - Main project overview

### Infrastructure
- **`docker-compose.yml`** - Docker environment configuration
- **`scripts/`** - Shell scripts for automation
- **`logs/`** - Application logs
- **`test_data/`** - Test files and sample data

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `tools/setup/setup_fresh_moodle.py` | Complete fresh installation |
| `tools/testing/verify_dual_tokens.py` | Token system verification |
| `src/core/enhanced_mcp_server.py` | Main MCP server with plugin support |
| `config/dual_token_config.py` | Token configuration management |
| `moodle_plugin/local_moodleclaude/` | Custom Moodle plugin |

## 🚀 Quick Navigation

```bash
# Setup and installation
cd tools/setup/

# Core application code  
cd src/core/

# Test and verify
cd tools/testing/

# Plugin development
cd moodle_plugin/local_moodleclaude/

# Documentation
cd readme/
```

This structure provides clear separation of concerns and makes the project easy to navigate and maintain.