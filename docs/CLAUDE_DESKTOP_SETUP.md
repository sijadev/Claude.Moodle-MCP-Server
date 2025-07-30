# Claude Desktop Configuration for MoodleClaude

## 📋 Configuration File Location

The Claude Desktop configuration file is located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

## 🔧 MoodleClaude Server Configuration

Add this configuration to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "moodle-course-creator": {
      "command": "/path/to/your/MoodleClaude/.venv/bin/python",
      "args": ["/path/to/your/MoodleClaude/tools/setup/start_mcp_server.py"],
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

## 🔑 Token Configuration

### Required Environment Variables:

1. **MOODLE_BASIC_TOKEN**: Token for "Moodle mobile web service"
   - Used for basic operations (course listing, creation)
   - Service: `Moodle mobile web service`

2. **MOODLE_PLUGIN_TOKEN**: Token for "MoodleClaude Content Creation Service"
   - Used for enhanced plugin features (page activities, file resources)
   - Service: `MoodleClaude Content Creation Service`

### How to Get Tokens:

1. **Go to**: Site Administration → Server → Web services → Manage tokens
2. **Create Basic Token**:
   - User: simon
   - Service: Moodle mobile web service
3. **Create Plugin Token**:
   - User: simon  
   - Service: MoodleClaude Content Creation Service
4. **Update the configuration** with your actual token values

## 📁 Updated File Structure

The MCP server now uses:
- **Startup script**: `tools/setup/start_mcp_server.py`
- **Main server**: `src/core/enhanced_mcp_server.py`
- **Configuration**: `config/dual_token_config.py`

## ✅ Verification

After updating the configuration:

1. **Restart Claude Desktop** application
2. **Check connection** in a new conversation
3. **Test functionality** with: "Create a test Moodle course about Python basics"

## 🎯 Features Available

With the updated configuration, you can:

- **Create courses** from chat conversations
- **Generate activities** with real content (pages, labels, files)
- **Update sections** with formatted content
- **Use dual-token system** for optimal functionality
- **Automatic token switching** based on operation type

## 🔧 Troubleshooting

### Common Issues:

1. **Server not starting**: Check that all file paths are correct
2. **Token errors**: Verify tokens are valid and services are enabled
3. **Import errors**: Ensure all dependencies are installed in the virtual environment

### Debug Steps:

1. **Check server logs**: `tail -f /path/to/MoodleClaude/logs/mcp_server.log`
2. **Test manually**: `python tools/setup/start_mcp_server.py`
3. **Verify tokens**: `python tools/testing/verify_dual_tokens.py`

## 📝 Example Working Configuration

```json
{
  "mcpServers": {
    "moodle-course-creator": {
      "command": "/Users/simonjanke/Projects/MoodleClaude/.venv/bin/python",
      "args": ["/Users/simonjanke/Projects/MoodleClaude/tools/setup/start_mcp_server.py"],
      "cwd": "/Users/simonjanke/Projects/MoodleClaude",
      "env": {
        "MOODLE_URL": "http://localhost:8080",
        "MOODLE_BASIC_TOKEN": "8545ed4837f1faf6cd246e470815f67b",
        "MOODLE_PLUGIN_TOKEN": "a72c43335a0974fc34c53a55c7231681",
        "MOODLE_USERNAME": "simon",
        "SERVER_NAME": "moodle-course-creator",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

This configuration enables the full dual-token functionality with enhanced MoodleClaude features!