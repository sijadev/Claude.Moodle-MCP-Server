# 🚀 MoodleClaude Fresh Setup Guide

**Complete installation from scratch - Follow these steps in order**

## ✅ **Status: Ready for Configuration**

- ✅ Fresh Docker containers running
- ✅ MoodleClaude plugin installed
- ⚠️ Manual configuration required

## 📋 **Step-by-Step Setup Process**

### **1️⃣ Initial Moodle Setup**
1. **Visit:** http://localhost:8080/admin/
2. **Login:**
   - Username: `simon`
   - Password: `Pwd1234!`
3. **Look for notifications** about new plugins
4. **If MoodleClaude plugin appears:** Click "Install" or "Upgrade"

### **2️⃣ Enable Web Services**
1. **Go to:** Site Administration → Advanced Features
2. **Find:** "Enable web services"
3. **Check the box** and **Save changes**

### **3️⃣ Verify MoodleClaude Service**
1. **Go to:** Site Administration → Server → Web services → External services
2. **Find:** "MoodleClaude Content Creation Service"
3. **Verify settings:**
   - ✅ **Enabled:** Yes (should be enabled by default)
   - ✅ **Authorised users only:** Yes (automatically configured)
   - ✅ **Functions:** 9 total (5 MoodleClaude + 4 essential core functions)
4. **No changes needed** - the service is pre-configured with all required functions

### **4️⃣ Enable REST Protocol**
1. **Go to:** Site Administration → Server → Web services → Manage protocols
2. **Find:** "REST protocol"
3. **Enable it** if not already enabled
4. **Save changes**

### **5️⃣ Create Tokens**

#### **Basic Token:**
1. **Go to:** Site Administration → Server → Web services → Manage tokens
2. **Click:** "Create token"
3. **Select:**
   - **User:** simon
   - **Service:** Moodle mobile web service
4. **Save** and **copy the token**

#### **Plugin Token:**
1. **Click:** "Create token" again
2. **Select:**
   - **User:** simon
   - **Service:** MoodleClaude Content Creation Service
3. **Save** and **copy the token**

### **6️⃣ Authorize User**
1. **Go back to:** Site Administration → Server → Web services → External services
2. **Find:** "MoodleClaude Content Creation Service"
3. **Click:** "Authorised users"
4. **Add:** simon to the authorized users list
5. **Save**

### **7️⃣ Update Configuration**
Update your `.env` file:
```bash
# Moodle Configuration
MOODLE_URL=http://localhost:8080
MOODLE_BASIC_TOKEN=your_basic_token_here
MOODLE_PLUGIN_TOKEN=your_moodleclaude_token_here
MOODLE_USERNAME=simon

# Server Configuration
SERVER_NAME=moodle-course-creator
LOG_LEVEL=INFO

# Admin Credentials
MOODLE_ADMIN_USER=simon
MOODLE_ADMIN_PASSWORD=Pwd1234!
MOODLE_ADMIN_EMAIL=simon@example.com
```

### **8️⃣ Test the Setup**
Run these tests to verify everything works:

```bash
# Test basic connectivity
python test_simple_plugin_access.py

# Test dual-token system
python test_dual_token_system.py

# Comprehensive verification
python verify_dual_tokens.py
```

## 🎯 **Expected Results After Setup**

✅ **Basic Token Test:**
```
✅ Basic operations work - found X courses
✅ Course creation works - ID: X
```

✅ **Plugin Token Test:**
```
✅ Plugin functions detected!
✅ MoodleClaude functions: 5
   - local_moodleclaude_create_page_activity
   - local_moodleclaude_create_label_activity
   - local_moodleclaude_create_file_resource
   - local_moodleclaude_update_section_content
   - local_moodleclaude_create_course_structure
```

✅ **Full Functionality:**
- Real page activities with content
- File resources with downloads
- Label activities with formatting
- Section name and summary updates
- Bulk course structure creation

## 🔧 **Troubleshooting**

### **Plugin Not Detected**
```bash
# Force plugin detection
docker exec moodleclaude_app php /bitnami/moodle/admin/cli/upgrade.php --non-interactive
```

### **Service Not Appearing**
- Check plugin is properly installed
- Purge caches: Site Administration → Development → Purge all caches
- Restart containers: `docker-compose restart`

### **Token Access Issues**
- Verify token is for correct service
- Check user is authorized for MoodleClaude service
- Ensure service is enabled

## 🎉 **Success Confirmation**

When everything is working, you'll be able to:
1. **Create courses** with full content automatically
2. **Store real content** in Moodle (no more empty sections!)
3. **Use Claude Desktop** with complete automation
4. **Generate actual activities** with formatting and files

The fresh setup ensures no configuration conflicts and optimal performance! 🚀
