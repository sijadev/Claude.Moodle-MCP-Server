# 🚀 MoodleClaude Setup Guide

Complete guide for setting up MoodleClaude with Docker and configuring all components.

## 📋 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ with uv
- Claude Desktop

### 1. Start Docker Environment

```bash
# Clone and navigate to project
cd /path/to/MoodleClaude

# Start fresh containers
docker-compose down
docker volume rm $(docker volume ls | grep moodle | awk '{print $2}') 2>/dev/null || true
docker-compose up -d

# Wait for Moodle to start (2-3 minutes)
```

### 2. Configure Web Services

**Option A: Automatic (Recommended)**
```bash
# Run the automated setup
./scripts/setup_webservice_functions_docker.sh
```

✅ **The automated setup now includes:**
- Web services and REST protocol enablement
- External service creation with WSManageSections functions
- Course enrollment configuration for visibility
- Auto-enrollment of admin user in all courses

**Option B: Manual Configuration**
1. Go to http://localhost:8080/login (admin: `simon` / `Pwd1234!`)
2. **Site Administration → Advanced features** → ✅ Enable web services
3. **Site Administration → Server → Web services → Manage protocols** → ✅ REST protocol
4. **Site Administration → Server → Web services → External services** → Add service:
   - Name: `MoodleClaude API`
   - Short name: `moodleclaude_api`
   - ✅ Enabled, ✅ Authorised users only
5. **Add Functions** to the service:
   ```
   core_course_create_courses
   core_course_get_courses
   core_course_get_categories
   core_course_get_contents
   core_course_edit_section
   core_files_upload
   core_webservice_get_site_info
   local_wsmanagesections_create_sections
   local_wsmanagesections_get_sections
   local_wsmanagesections_update_sections
   ```
6. **Create Token**: Site Administration → Server → Web services → Manage tokens
   - User: simon, Service: MoodleClaude API
7. **Authorize User**: Add simon to service authorized users

### 3. Configure Environment

```bash
# Update .env with your token
MOODLE_URL=http://localhost:8080
MOODLE_TOKEN=your_32_character_token_here
MOODLE_USERNAME=simon
```

### 4. Start MCP Server

```bash
# Install dependencies and start server
uv sync
uv run python mcp_server.py &
```

### 5. Test Setup

```bash
# Test Moodle connection
uv run python test_realistic_moodle.py

# Test enhanced features
uv run python test_enhanced_moodle.py
```

## 🔧 Troubleshooting

### Web Services Issues
- **403 Forbidden**: Check token is correct and user is authorized
- **Function not found**: Ensure all functions are added to the service
- **Invalid parameter**: Verify function parameters match Moodle expectations

### Docker Issues
- **Container won't start**: Check ports 8080, 8443, 8081 aren't in use
- **Database errors**: Remove volumes and restart fresh
- **Slow startup**: Moodle takes 2-3 minutes to fully initialize

### MCP Issues
- **Tools not available**: Restart Claude Desktop after server changes
- **Empty logs**: Check MCP server is running and configured correctly
- **Connection errors**: Verify .env token matches Moodle token

## 🎯 Features Available

### ✅ Working Features
- **Course Creation**: Full courses with auto-sections
- **Section Management**: Create, update, position sections dynamically
- **Content Organization**: Smart content placement by section
- **File Upload**: Upload files to Moodle
- **Course Structure**: Get detailed course/section information

### ❌ Requires Manual Setup
- **Activity Creation**: Pages, labels, assignments need manual creation
- **Advanced Permissions**: Complex role/capability management
- **Custom Plugins**: Additional functionality beyond standard Moodle

## 🚀 Usage

Once setup is complete, you can use these MCP tools in Claude Desktop:

1. **`extract_and_preview_content`** - Parse chat content for course creation
2. **`create_course_from_chat`** - Create complete structured courses  
3. **`add_content_to_course`** - Add content to existing courses

The system will automatically:
- Create courses with intelligent section organization
- Place content in appropriate sections
- Format content for Moodle display
- Log planned activities for manual creation

## 📊 Access Points

- **Moodle**: http://localhost:8080 (simon / Pwd1234!)
- **phpMyAdmin**: http://localhost:8081
- **Docker Status**: `docker ps`
- **Logs**: `docker logs moodleclaude_app`

## 🎉 Success Indicators

When everything is working:
- ✅ Moodle responds at http://localhost:8080
- ✅ Token test returns site information
- ✅ MCP server starts without errors
- ✅ Test scripts create courses successfully
- ✅ Claude Desktop shows MoodleClaude tools
