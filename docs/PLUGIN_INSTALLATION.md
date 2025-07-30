# MoodleClaude Plugin Installation Guide

This guide will help you install the custom MoodleClaude plugin to enable full content creation functionality.

## Prerequisites

- Moodle 4.3+ running
- Admin access to Moodle
- SSH/file access to Moodle server

## Step 1: Install the Plugin

### Option A: Manual Installation

1. **Copy plugin to Moodle**:
   ```bash
   # From your project directory
   sudo cp -r moodle_plugin/local_moodleclaude /path/to/moodle/local/
   
   # For Docker Moodle setup:
   sudo cp -r moodle_plugin/local_moodleclaude ./moodle_data/local/
   ```

2. **Set proper permissions**:
   ```bash
   sudo chown -R www-data:www-data /path/to/moodle/local/local_moodleclaude
   sudo chmod -R 755 /path/to/moodle/local/local_moodleclaude
   ```

### Option B: Docker Installation

If using the Docker Moodle setup:

1. **Copy to Docker volume**:
   ```bash
   docker cp moodle_plugin/local_moodleclaude moodle_container:/var/www/html/local/
   ```

## Step 2: Run Moodle Installation

1. **Visit Moodle admin**:
   - Go to: `http://your-moodle-site/admin`
   - Login as admin
   - You'll see "New version available" notification

2. **Follow installation prompts**:
   - Click "Upgrade Moodle database now"
   - Confirm plugin installation
   - Complete the upgrade process

## Step 3: Configure Web Services

1. **Enable web services**:
   - Go to: Site Administration → Advanced Features
   - Check "Enable web services"
   - Save changes

2. **Add the service**:
   - Go to: Site Administration → Server → Web services → External services
   - Find "MoodleClaude Content Creation Service"
   - Click "Edit" and enable it
   - Set "Authorised users only" to your preference

3. **Create a token**:
   - Go to: Site Administration → Server → Web services → Manage tokens
   - Click "Create token"
   - Select a user (yourself or service account)
   - Select "MoodleClaude Content Creation Service"
   - Save the token (you'll need this!)

## Step 4: Update MoodleClaude Configuration

1. **Update your `.env` file**:
   ```bash
   # Add or update these lines
   MOODLE_URL=http://localhost:8080
   MOODLE_TOKEN=your_new_token_here
   ```

2. **Test the new functionality**:
   ```bash
   python test_plugin_integration.py
   ```

## Step 5: Verify Installation

The plugin provides these new API functions:

✅ `local_moodleclaude_create_page_activity`  
✅ `local_moodleclaude_create_label_activity`  
✅ `local_moodleclaude_create_file_resource`  
✅ `local_moodleclaude_update_section_content`  
✅ `local_moodleclaude_create_course_structure`  

## Benefits After Installation

- **Real content storage** (no more empty sections!)
- **Actual activity creation** (pages, labels, files)
- **Section content updates** (proper names and summaries)
- **Bulk operations** (create entire course structures at once)

## Troubleshooting

### Plugin not showing up
- Check file permissions
- Ensure files are in correct location: `/moodle/local/local_moodleclaude/`
- Clear Moodle cache: Site Administration → Development → Purge all caches

### Web service not available
- Ensure web services are enabled
- Check user permissions
- Verify token is created for correct service

### Permission errors
- User needs `moodle/course:manageactivities` capability
- User needs `moodle/course:update` capability
- Check role assignments

## Docker-Specific Notes

For Docker setups, you may need to:

1. **Restart containers**:
   ```bash
   docker-compose restart
   ```

2. **Check volume mounts**:
   ```bash
   docker exec -it moodle_container ls -la /var/www/html/local/
   ```

3. **Set permissions inside container**:
   ```bash
   docker exec -it moodle_container chown -R www-data:www-data /var/www/html/local/local_moodleclaude
   ```

## Success Verification

After installation, MoodleClaude will:
- Create actual page activities with content
- Store content properly in Moodle database
- Update section names and summaries
- Provide honest success/failure reporting
- Enable bulk course creation workflows

Your content creation workflow will now be fully automated! 🎉