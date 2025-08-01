# Debug Tools and Scripts

This folder contains debugging tools and validation scripts for the MoodleClaude project.

## Files Overview

### Core Debug Scripts

- **`debug_content_parser.py`** - Test and debug the content parser functionality
  - Tests regex patterns for code block detection
  - Validates content parsing with sample chat data
  - Useful for troubleshooting content extraction issues

- **`mcp_server_debug.py`** - Enhanced MCP server with detailed logging
  - Debug version of the main MCP server with comprehensive logging
  - Logs all Claude Desktop interactions and tool calls
  - Helps troubleshoot MCP integration issues

- **`validate_mcp_integration.py`** - Comprehensive integration validation
  - Checks Claude Desktop configuration
  - Validates MCP server logs and functionality
  - Verifies Moodle database consistency
  - Cross-references all data sources

## Usage

### Debug Content Parser
```bash
python debug/debug_content_parser.py
```
Use this when courses appear empty or content isn't being detected properly.

### Run Debug MCP Server
```bash
python debug/mcp_server_debug.py
```
Use this instead of the regular MCP server when troubleshooting Claude Desktop integration.

### Validate Complete Integration
```bash
python debug/validate_mcp_integration.py
```
Run this for a comprehensive health check of the entire system.

## When to Use These Tools

1. **Content Parser Issues**: Use `debug_content_parser.py` if:
   - Courses are created but appear empty
   - Code blocks aren't being detected
   - Content parsing returns 0 items

2. **MCP Integration Issues**: Use `mcp_server_debug.py` if:
   - Claude Desktop can't connect to MCP server
   - Tool calls aren't working
   - Need detailed logging of MCP interactions

3. **System Health Check**: Use `validate_mcp_integration.py` if:
   - Need to verify entire system status
   - Troubleshooting course visibility issues
   - Want to cross-reference logs with database

## Output Locations

- Debug logs are written to `mcp_server_debug.log`
- Validation results are displayed in console
- All scripts provide detailed status information

## Integration with Main Project

These debug tools complement the main project files and can be used alongside the regular MCP server and testing framework. They're designed to help identify and resolve issues quickly during development and troubleshooting.
