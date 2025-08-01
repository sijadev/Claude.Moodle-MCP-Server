# Manual Moodle Web Services Setup

## Environment Status
✅ **Moodle is running**: http://localhost:8080  
✅ **Admin credentials**: simon / Pwd1234!  

## Required Manual Steps

### 1. Enable Web Services
1. Log in to Moodle at http://localhost:8080 with admin credentials (simon / Pwd1234!)
2. Go to **Site administration** → **General** → **Advanced features**
3. Enable **Web services** → Save changes

### 2. Enable REST Protocol  
1. Go to **Site administration** → **Plugins** → **Web services** → **Manage protocols**
2. Enable **REST protocol**

### 3. Create Web Service User
1. Go to **Site administration** → **Users** → **Add a new user**
2. Create user:
   - Username: `wsuser`
   - Password: `MoodleClaudeWS2025!`  
   - Email: `wsuser@moodleclaude.local`
   - First name: `WebService`
   - Last name: `User`

### 4. Create Custom Role
1. Go to **Site administration** → **Users** → **Permissions** → **Define roles**
2. Click **Add a new role**
3. Use archetype: **No archetype**
4. Role details:
   - Short name: `moodleclaude_ws`
   - Full name: `MoodleClaude Web Service`
   - Description: `Role for MoodleClaude web service access`
5. Add capabilities:
   - `webservice/rest:use` → Allow
   - `moodle/course:create` → Allow  
   - `moodle/course:update` → Allow
   - `moodle/course:view` → Allow
   - `moodle/site:config` → Allow

### 5. Assign Role to User
1. Go to **Site administration** → **Users** → **Permissions** → **Assign system roles**
2. Select **MoodleClaude Web Service** role
3. Add **wsuser** to this role

### 6. Create External Service
1. Go to **Site administration** → **Plugins** → **Web services** → **External services**
2. Click **Add** to create new service:
   - Name: `MoodleClaude Service`
   - Short name: `moodleclaude`
   - Enabled: ✅
   - Restricted users: ✅
   - Can download files: ✅
   - Can upload files: ✅

### 7. Add Functions to Service
1. Click **Functions** next to the MoodleClaude Service
2. Add these functions:
   - `core_webservice_get_site_info`
   - `core_course_create_courses`
   - `core_course_get_courses`  
   - `core_course_get_categories`
   - `core_course_update_courses`
   - `core_course_edit_section`
   - `core_files_upload`

### 8. Create Tokens
1. Go to **Site administration** → **Plugins** → **Web services** → **Manage tokens**
2. Create token for **wsuser**:
   - User: `wsuser`
   - Service: `MoodleClaude Service`
   - IP restriction: Leave empty
   - Valid until: Leave empty (no expiration)
3. **Copy the generated token** - you'll need this for MoodleClaude configuration

### 9. Add Authorized Users
1. Go to **Site administration** → **Plugins** → **Web services** → **External services**
2. Click **Authorised users** next to MoodleClaude Service
3. Add **wsuser** to authorized users

## Testing
Once setup is complete, test with:
```bash
curl "http://localhost:8080/webservice/rest/server.php?wstoken=YOUR_TOKEN&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
```

## Next Steps
- Update `config/moodle_tokens_current.env` with the real token
- Test MoodleClaude MCP integration
- Run the v3.0 architecture tests
