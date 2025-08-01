# MoodleClaude Content Creator Plugin

A custom Moodle plugin that provides advanced web service functions for creating course content from Claude chat conversations.

## Features

- **Create Page Activities**: Create full page activities with rich HTML content
- **Create Label Activities**: Create label activities for quick content display
- **Create File Resources**: Create downloadable file resources with custom content
- **Update Section Content**: Update section names and summaries programmatically
- **Bulk Course Structure Creation**: Create entire course structures with multiple sections and activities

## Installation

1. **Copy plugin files**:
   ```bash
   cp -r local_moodleclaude /path/to/moodle/local/
   ```

2. **Visit admin page**:
   - Go to Site Administration → Notifications
   - Follow the installation prompts

3. **Enable web services**:
   - Go to Site Administration → Advanced Features
   - Enable "Web services"

4. **Configure the service**:
   - Go to Site Administration → Server → Web services → External services
   - Enable "MoodleClaude Content Creation Service"
   - Add authorized users

5. **Create tokens**:
   - Go to Site Administration → Server → Web services → Manage tokens
   - Create tokens for users who will use MoodleClaude

## API Functions

### local_moodleclaude_create_page_activity
Creates a page activity with content.

**Parameters:**
- `courseid` (int): Course ID
- `section` (int): Section number
- `name` (string): Activity name
- `content` (string): HTML content
- `intro` (string, optional): Activity introduction

### local_moodleclaude_create_label_activity
Creates a label activity.

**Parameters:**
- `courseid` (int): Course ID
- `section` (int): Section number
- `content` (string): HTML content

### local_moodleclaude_create_file_resource
Creates a file resource with downloadable content.

**Parameters:**
- `courseid` (int): Course ID
- `section` (int): Section number
- `name` (string): Resource name
- `filename` (string): File name
- `content` (string): File content
- `intro` (string, optional): Resource introduction

### local_moodleclaude_update_section_content
Updates section name and summary.

**Parameters:**
- `courseid` (int): Course ID
- `section` (int): Section number
- `name` (string, optional): Section name
- `summary` (string, optional): Section summary

### local_moodleclaude_create_course_structure
Creates complete course structure from structured data.

**Parameters:**
- `courseid` (int): Course ID
- `sections` (array): Array of section objects with activities

## Permissions

The plugin requires the following capabilities:
- `moodle/course:manageactivities` - For creating activities
- `moodle/course:update` - For updating sections
- `local/moodleclaude:createcontent` - Plugin-specific capability
- `local/moodleclaude:managecourses` - Plugin-specific capability

## Integration with MoodleClaude

This plugin is designed to work with the MoodleClaude system, providing the missing functionality for:
- ✅ Actual content storage (no more empty sections!)
- ✅ Real activity creation (pages, labels, files)
- ✅ Section content updates
- ✅ Bulk course structure creation

## Requirements

- Moodle 4.3+
- Web services enabled
- Appropriate user permissions

## Support

For issues and questions, please refer to the MoodleClaude project documentation.

## License

GPL v3 or later
