# MoodleClaude Plugin Changelog

## Version 1.0.2 (2025-01-30)

### ✅ Added
- **Essential core functions** automatically included in service:
  - `core_webservice_get_site_info` - Required for token validation
  - `core_course_create_courses` - Required for course creation
  - `core_course_get_courses` - Required for course listing  
  - `core_course_get_categories` - Required for category access
- **Complete documentation** for fresh setup process
- **Automated setup script** with full cleanup functionality

### 🔧 Fixed
- **Service configuration** now properly supports "Authorised users only"
- **Token validation** works immediately after installation
- **Course creation** works without manual function addition
- **Plugin detection** works reliably in fresh installations

### 📋 Technical Details
- Service now includes 9 functions total (5 custom + 4 core)
- `restrictedusers => 1` enables proper authorization controls
- All essential web service functions included by default
- No manual function addition required

## Version 1.0.1 (2025-01-30)

### 🔧 Fixed
- Service configuration to support "Authorised users only"
- Changed `restrictedusers` from 0 to 1

## Version 1.0.0 (2025-01-30)

### ✅ Initial Release
- 5 MoodleClaude web service functions
- Page activity creation with real content
- Label activity creation with formatting
- File resource creation with downloads
- Section content updates
- Bulk course structure creation
- Complete external service definition