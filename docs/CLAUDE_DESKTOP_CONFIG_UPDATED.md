# 🔧 Updated Claude Desktop Configuration

## 📋 Configuration File Location

The Claude Desktop configuration file is located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

## 🚀 Advanced Features Configuration (Recommended)

For the new **MoodleClaude 2.0** with intelligent processing, use this configuration:

```json
{
  "mcpServers": {
    "moodle-advanced": {
      "command": "python",
      "args": ["-m", "src.core.advanced_mcp_server"],
      "cwd": "/path/to/your/MoodleClaude",
      "env": {
        "MOODLE_URL": "http://localhost:8080",
        "MOODLE_BASIC_TOKEN": "your_basic_token_here",
        "MOODLE_PLUGIN_TOKEN": "your_plugin_token_here",
        "MOODLE_USERNAME": "simon",
        "SERVER_NAME": "advanced-moodle-course-creator",
        "LOG_LEVEL": "INFO",
        "MOODLE_CLAUDE_DB_PATH": "data/sessions.db",
        "MOODLE_CLAUDE_BACKUP_INTERVAL": "3600",
        "MOODLE_CLAUDE_MAX_CHARS": "8000",
        "MOODLE_CLAUDE_MAX_SECTIONS": "15",
        "MOODLE_CLAUDE_USE_EMOJIS": "true",
        "MOODLE_CLAUDE_DETAILED_PROGRESS": "true"
      }
    }
  }
}
```

### 🎯 New Advanced Features

With this configuration you get:
- ✅ **6 new intelligent MCP tools**
- ✅ **Adaptive content processing** with automatic chunking
- ✅ **Session management** with persistence
- ✅ **Real-time validation** and error recovery
- ✅ **Progress tracking** and intelligent continuation
- ✅ **Learning system** that adapts to your content

## 🔄 Basic Version Configuration (Legacy)

For the original MoodleClaude version:

```json
{
  "mcpServers": {
    "moodle-course-creator": {
      "command": "python", 
      "args": ["-m", "tools.setup.start_mcp_server"],
      "cwd": "/path/to/your/MoodleClaude",
      "env": {
        "MOODLE_URL": "http://localhost:8080",
        "MOODLE_BASIC_TOKEN": "your_basic_token_here",
        "MOODLE_PLUGIN_TOKEN": "your_plugin_token_here",
        "MOODLE_USERNAME": "simon",
        "SERVER_NAME": "moodle-course-creator",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🔑 Required Tokens (Both Versions)

### 1. MOODLE_BASIC_TOKEN
- **Service**: "Moodle mobile web service"
- **Used for**: Basic course operations, listings
- **Required**: Yes

### 2. MOODLE_PLUGIN_TOKEN  
- **Service**: "MoodleClaude Content Creation Service"
- **Used for**: Enhanced content creation, sections
- **Required**: Yes (for full functionality)

### How to Get Tokens:
1. Go to: **Site Administration → Server → Web services → Manage tokens**
2. Create tokens for both services above
3. Copy tokens to your configuration

## ⚙️ Environment Variables (Advanced)

| Variable | Default | Description |
|----------|---------|-------------|
| `MOODLE_CLAUDE_DB_PATH` | `"data/sessions.db"` | Session database location |
| `MOODLE_CLAUDE_BACKUP_INTERVAL` | `"3600"` | Backup interval in seconds |
| `MOODLE_CLAUDE_MAX_CHARS` | `"8000"` | Initial content limit (auto-adapts) |
| `MOODLE_CLAUDE_MAX_SECTIONS` | `"15"` | Maximum sections per course |
| `MOODLE_CLAUDE_USE_EMOJIS` | `"true"` | Enable emoji responses |
| `MOODLE_CLAUDE_DETAILED_PROGRESS` | `"true"` | Show detailed progress |

## 🎮 Usage Differences

### Advanced Version (Recommended)
```
User: "Create an intelligent course from this chat"
→ System analyzes complexity automatically
→ Chooses optimal processing strategy  
→ Provides progress updates
→ Handles continuation automatically
→ "✅ Course created with 8 sections!"
```

**Available Tools:**
1. `create_intelligent_course` - Smart course creation
2. `continue_course_session` - Session continuation
3. `validate_course` - Real-time validation
4. `get_session_status` - Progress tracking
5. `get_processing_analytics` - System metrics
6. `analyze_content_complexity` - Content analysis

### Basic Version
```
User: "Create course from chat"
→ "Please provide content and course name"
→ Manual parameter input required
→ Single-pass processing only
→ "Course created successfully"
```

**Available Tools:**
1. `create_course_from_chat` - Basic course creation
2. `extract_and_preview_content` - Content preview
3. `test_plugin_functionality` - Plugin testing

## 🚧 Migration Guide

### From Basic to Advanced
1. **Update Configuration**: Replace your Claude Desktop config with the advanced version
2. **Restart Claude Desktop**: Close and reopen the application
3. **Test New Features**: Try `"Create an intelligent course from this conversation"`

### Backward Compatibility
- ✅ All existing tools continue to work
- ✅ No data loss or configuration changes needed
- ✅ Can switch back anytime by changing the config

## 🔧 Troubleshooting

### Issue: "Server not found"
**Solution**: Check that the `cwd` path points to your MoodleClaude directory

### Issue: "Module not found" 
**Solution**: Ensure you're using the correct Python environment with dependencies

### Issue: "Database errors"
**Solution**: Check that the `data/` directory is writable and exists

### Issue: "Token errors"
**Solution**: Verify both tokens are valid and services are enabled in Moodle

## 📊 Configuration Validation

Run this command to validate your setup:
```bash
cd /path/to/MoodleClaude
python tools/debug/validate_claude_config.py
```

## 🎯 Recommended Setup

For the best experience:

1. **Use Advanced Configuration** - Get all new features
2. **Set LOG_LEVEL to "INFO"** - Good balance of logging  
3. **Enable Emojis and Progress** - Better user experience
4. **Use Default Paths** - Let system manage data directories
5. **Keep Both Tokens** - Full functionality requires both

---

**Ready to experience intelligent course creation!** 🚀✨