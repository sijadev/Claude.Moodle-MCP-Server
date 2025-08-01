# MoodleClaude v3.0 - Directory Structure

## 📁 Organized Project Structure

### **Root Directory**
```
/MoodleClaude/
├── README.md                    # Main project documentation
├── LICENSE                      # Project license
├── Makefile                     # Build and development commands
├── pyproject.toml              # Python project configuration
├── uv.lock                     # UV dependency lock file
├── requirements-e2e.txt        # E2E testing requirements
├── pytest.ini / pytest_e2e.ini # Test configurations
└── docker-compose.yml          # → Symlink to operations/docker/docker-compose.fresh.yml
```

### **🚀 Quick Start Scripts (Symlinks)**
```
├── setup_fresh.sh              # → operations/setup/setup_fresh_moodleclaude_complete.sh
├── backup.sh                   # → operations/backup/backup_moodleclaude.sh
├── restore_default.sh          # → operations/backup/restore_default_setup.sh
├── list_backups.sh             # → operations/backup/list_backups.sh
└── start_server.py             # → server/mcp_server_launcher.py
```

### **📦 Operations**
```
operations/
├── backup/                     # Backup & Repository Management
│   ├── backup_moodleclaude.sh         # Main backup script
│   ├── backup_strategies.sh           # 6 professional backup strategies
│   ├── restore_moodleclaude.sh        # Restore from any backup
│   ├── restore_default_setup.sh       # Quick restore to fresh state
│   ├── list_backups.sh               # List and manage backups
│   ├── manage_repository.sh           # Git integration
│   ├── automated_backup.sh            # Automated backup script
│   └── backup_cron_examples.txt       # Cron job examples
├── setup/                      # Installation & Configuration
│   ├── setup_fresh_moodleclaude_complete.sh  # Complete fresh setup
│   ├── start_moodleclaude_v3.sh              # Start v3.0 environment
│   ├── setup_webservices_*.sh               # Web service setup variants
│   └── start_moodle_v3.sh                   # Start Moodle containers
└── docker/                     # Docker Configurations
    ├── docker-compose.fresh.yml       # Fresh installation (recommended)
    ├── docker-compose.optimized.yml   # Optimized 2-container setup
    ├── docker-compose.minimal.yml     # Minimal development setup
    └── docker-compose.*.yml           # Other configurations
```

### **🖥️ Server & Core**
```
server/                         # MCP Server Implementations
├── mcp_server_launcher.py             # Main server launcher
├── mcp_server.py                      # Core MCP server
├── enhanced_moodle_claude.py          # Enhanced client
├── refresh_mcp_services.py            # Service refresh utility
└── start_robust_mcp_server.py         # Production server

src/                           # Source Code
├── core/                             # Core architecture
│   ├── enhanced_mcp_server.py               # v3.0 enhanced server
│   ├── robust_mcp_server.py                # Production-ready server
│   ├── dependency_injection.py             # DI container
│   ├── command_system.py                   # Command pattern
│   ├── event_system.py                     # Observer pattern
│   ├── services.py                         # Service layer
│   └── repositories.py                     # Repository pattern
├── clients/                          # Client implementations
│   ├── moodle_client.py                    # Base Moodle client
│   └── enhanced_moodle_claude.py           # Enhanced client
└── models/                           # Data models
    └── models.py                           # Core models
```

### **🔧 Configuration & Data**
```
config/                        # Configuration Files
├── adaptive_config.py                # Adaptive configuration
├── claude_desktop_config_*.json      # Claude Desktop configs
├── moodle_tokens_*.env              # Moodle tokens
└── adaptive_settings.json           # Adaptive settings

data/                          # Application Data
└── sessions.db                      # Session database

backups/                       # Backup Storage
├── default_setup_latest            # → Symlink to latest default backup
└── moodleclaude_YYYYMMDD_HHMMSS/   # Timestamped backups
    ├── backup_manifest.txt         # Backup contents
    ├── database_dump.sql           # PostgreSQL dump
    ├── *.tar.gz                    # Compressed files
    └── default_setup.txt           # Default backup marker (if applicable)
```

### **🔌 Plugin & Docker**
```
moodle_plugin/                 # MoodleClaude Plugin
└── local_moodleclaude/             # Plugin implementation
    ├── classes/external/           # Web service functions
    ├── db/                        # Database definitions
    ├── lang/en/                   # Language files
    └── version.php                # Plugin version

docker/                        # Docker Support Files
├── moodle-config/                  # Moodle configuration
└── postgres-init/                  # PostgreSQL initialization
    └── 01-init-moodle.sql         # Database setup
```

### **📚 Documentation**
```
docs/                          # Technical Documentation
├── SETUP_GUIDE.md                  # Setup instructions
├── TESTING_GUIDE.md                # Testing documentation
├── PLUGIN_README.md                # Plugin documentation
└── *.md                           # Various technical docs

documentation/                 # User Documentation
├── BACKUP_STRATEGIES_GUIDE.md      # Backup strategies guide
├── COMPLETE_SETUP_GUIDE.md         # Complete setup guide
├── CHANGELOG_v3.0.md               # Version 3.0 changelog
└── README_*.md                     # Feature-specific docs
```

### **🧪 Testing & Development**
```
tests/                         # Test Suite
├── unit/                          # Unit tests
├── integration/                   # Integration tests
├── e2e/                          # End-to-end tests
├── manual/                       # Manual testing scripts
└── advanced/                     # Advanced feature tests

tools/                         # Development Tools
├── debug/                        # Debugging utilities
├── setup/                        # Setup utilities
├── testing/                      # Testing utilities
└── demo/                         # Demo scripts

demos/                         # Usage Examples
├── simple_transfer.py            # Basic usage
├── advanced_transfer.py          # Advanced features
└── *.py                          # Various demos

scripts/                       # Development Scripts
├── run_tests.sh                  # Test runner
├── run_e2e_tests.sh             # E2E test runner
└── *.sh                          # Various utility scripts
```

### **📊 Reports & Logs**
```
logs/                          # Application Logs
├── mcp_server.log                  # MCP server logs
├── advanced_mcp_server.log         # Enhanced server logs
└── cleanup.log                     # Cleanup operation logs

reports/                       # Test & Analysis Reports
├── e2e_report.html                 # E2E test reports
└── test-reports/                   # Generated test reports

bin/                           # Utility Binaries
└── diagnose_moodle_health.py       # Health diagnostic tool
```

## 🎯 Key Improvements

### **✅ Organized Structure**
- **Clear separation** of concerns (operations, server, source, docs)
- **Logical grouping** of related files
- **Consistent naming** conventions

### **✅ Easy Access**
- **Convenience symlinks** for most commonly used scripts
- **Intuitive directory names** (operations, server, documentation)
- **Clear hierarchical organization**

### **✅ Maintainability**
- **Related files grouped together**
- **Reduced root directory clutter**
- **Easy to find and modify** specific components

## 🔧 Usage Examples

### **Quick Operations**
```bash
# Fresh setup
./setup_fresh.sh

# Create backup
./backup.sh

# Restore to default state
./restore_default.sh

# List all backups
./list_backups.sh

# Start MCP server
python start_server.py
```

### **Advanced Operations**
```bash
# Backup strategies
./operations/backup/backup_strategies.sh development
./operations/backup/backup_strategies.sh production

# Specific Docker setup
docker-compose -f operations/docker/docker-compose.optimized.yml up -d

# Manual setup steps
./operations/setup/setup_webservices_v3_optimized.sh
```

### **Development**
```bash
# Run tests
./scripts/run_tests.sh
./scripts/run_e2e_tests.sh

# Debugging
python tools/debug/diagnose_service_access.py
python tools/testing/test_plugin_integration.py

# Demos
python demos/advanced_transfer.py
python tools/demo/advanced_features_demo.py
```

## 📋 Migration Notes

**All frequently used scripts are accessible via symlinks in the root directory.** This maintains backward compatibility while providing better organization.

**File locations have been optimized for:**
- **Development workflow efficiency**
- **Logical grouping of related functionality**
- **Easy maintenance and updates**
- **Clear separation between user scripts and internal tools**

This structure supports both **quick usage** (via root symlinks) and **advanced development** (via organized subdirectories).