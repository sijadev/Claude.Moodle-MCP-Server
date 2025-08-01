# MoodleClaude Clean Directory Structure

## 📁 Organized Project Layout

The MoodleClaude project has been reorganized for better maintainability and clarity. Here's the new structure:

```
MoodleClaude/
├── 📂 archive/                      # Historical backups and old versions
│   └── backups/                     # Automatic system backups
├── 📂 config/                       # Configuration files
│   ├── moodle_tokens.env           # Token configuration
│   ├── claude_desktop_working.json # Claude Desktop configuration
│   └── *.json, *.py                # Various config files
├── 📂 deployment/                   # Production deployment files
│   ├── docker/                     # Docker configurations
│   │   ├── docker-compose.yml     # Main Docker setup
│   │   ├── docker-compose.test.yml # Test environment
│   │   ├── Dockerfile.test        # Test container
│   │   └── postgres-init/         # Database initialization
│   └── server/                     # Server deployment scripts
│       ├── enhanced_moodle_claude.py
│       ├── mcp_server.py
│       └── *.py                    # Various server files
├── 📂 development/                  # Development-only files
│   └── bin/                        # Development binaries
├── 📂 docs/                        # All documentation
│   ├── SMOKE_TEST_GUIDE.md        # Testing documentation
│   ├── SETUP_GUIDE.md             # Setup instructions
│   ├── ARCHITECTURE_IMPROVEMENTS.md
│   └── *.md                       # All project documentation
├── 📂 examples/                    # Usage examples and demos
│   ├── advanced_transfer.py       # Advanced usage examples
│   ├── simple_transfer.py         # Basic usage examples
│   └── *.py                       # Demo scripts
├── 📂 logs/                        # System logs
├── 📂 moodle_plugin/               # Moodle plugin code
│   └── local_moodleclaude/         # Plugin implementation
├── 📂 php_scripts/                 # PHP utility scripts
│   ├── create_new_tokens.php      # Token creation
│   ├── fix_capabilities.php       # Permission fixes
│   ├── reassign_tokens.php        # Token management
│   └── setup_webservices.php      # Web service setup
├── 📂 reports/                     # Test and analysis reports
│   └── smoke_test/                 # Smoke test results
├── 📂 scripts/                     # Shell scripts and automation
│   ├── smoke_test.sh              # Main testing script
│   ├── setup_git_hooks.sh         # Git hooks installer
│   └── *.sh                       # Various utility scripts
├── 📂 setup/                       # Setup and installation
│   ├── setup_moodleclaude_v3_fixed.py  # Main setup script
│   ├── backup/                    # Backup utilities
│   │   ├── automated_backup.sh
│   │   └── *.sh                   # Backup scripts
│   ├── *.sh                       # Setup shell scripts
│   └── *.py                       # Setup Python scripts
├── 📂 src/                         # Source code
│   ├── clients/                   # Client implementations
│   ├── core/                      # Core functionality
│   │   ├── working_mcp_server.py  # Main MCP server
│   │   └── *.py                   # Core modules
│   └── models/                    # Data models
├── 📂 storage/                     # Data storage
│   ├── data/                      # Application data
│   ├── test_data/                 # Test data files
│   └── test_storage/              # Test result storage
├── 📂 tests/                       # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── e2e/                       # End-to-end tests
│   ├── manual/                    # Manual test scripts
│   ├── advanced/                  # Advanced test scenarios
│   └── test/                      # Additional test utilities
├── 📂 tools/                       # Development tools
│   ├── debug/                     # Debugging utilities
│   ├── demo/                      # Demo tools
│   ├── setup/                     # Setup tools
│   ├── testing/                   # Testing tools
│   ├── validate_bugfixes.py      # Bug fix validation
│   └── *.py                       # Various development tools
├── 📂 .github/                     # GitHub configuration
│   ├── workflows/                 # CI/CD workflows
│   ├── ISSUE_TEMPLATE/            # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md   # PR template
├── 📂 .githooks/                   # Git hooks
│   └── pre-push                   # Pre-push validation
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # Project license
├── 📄 BUGFIX_DOCUMENTATION.md      # Bug fix documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 pyproject.toml              # Python project config
├── 📄 pytest.ini                  # Test configuration
└── 📄 Makefile                     # Build automation
```

## 🎯 Key Improvements

### ✅ **Logical Organization**
- **`setup/`** - All installation and configuration scripts
- **`deployment/`** - Production and Docker configurations  
- **`php_scripts/`** - PHP utilities separated from Python code
- **`storage/`** - Centralized data storage location
- **`archive/`** - Historical backups moved out of active workspace

### ✅ **Clear Separation of Concerns**
- **Development** vs **Production** files clearly separated
- **Documentation** consolidated in single location
- **Examples** and **Tools** have dedicated directories
- **Tests** organized by type (unit, integration, e2e)

### ✅ **Improved Navigation**
- Main setup script moved to logical location: `setup/setup_moodleclaude_v3_fixed.py`
- Docker files consolidated in `deployment/docker/`
- All documentation accessible in `docs/`
- Clear distinction between source code (`src/`) and utilities (`tools/`)

## 🚀 Usage After Reorganization

### Main Setup
```bash
# Main setup script (moved location)
python setup/setup_moodleclaude_v3_fixed.py
```

### Testing
```bash
# Smoke test (updated paths automatically)
./scripts/smoke_test.sh --quick

# Install Git hooks
./scripts/setup_git_hooks.sh
```

### Development
```bash
# Docker deployment
cd deployment/docker
docker-compose up -d

# PHP utilities
php php_scripts/create_new_tokens.php
```

### Documentation
```bash
# All docs now in one place
open docs/SMOKE_TEST_GUIDE.md
open docs/SETUP_GUIDE.md
```

## 🔧 Updated File References

All internal references have been updated automatically:
- ✅ Smoke test script paths updated
- ✅ Git hooks and pre-commit configs updated
- ✅ GitHub workflows updated
- ✅ Bug fix validation tool updated
- ✅ Documentation links maintained

## 📋 Migration Notes

### What Changed
1. **Root cleanup** - PHP scripts, setup files, and scattered configs moved
2. **Directory consolidation** - `docs/` + `documentation/` merged
3. **Logical grouping** - Related functionality grouped together
4. **Archive separation** - Old backups moved to `archive/`

### No Functional Changes
- All functionality remains identical
- No breaking changes to API or behavior
- All tests pass with updated paths
- CI/CD pipelines work unchanged

This reorganization provides a much cleaner, more maintainable project structure while preserving all existing functionality.