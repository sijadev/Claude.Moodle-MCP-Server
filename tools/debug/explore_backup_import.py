#!/usr/bin/env python3
"""
Explore Moodle backup/import functionality for automatic content population
"""

import asyncio
import logging
from moodle_client import MoodleClient
from config import Config
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def explore_backup_apis():
    """Explore available backup/import/restore APIs"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Exploring Backup/Import APIs...")
        
        # Get site info to see available functions
        try:
            site_info = await client._call_api("core_webservice_get_site_info", {})
            if 'functions' in site_info:
                functions = site_info['functions']
                print(f"📊 Total available functions: {len(functions)}")
                
                # Look for backup/restore/import related functions
                backup_functions = []
                for func in functions:
                    func_name = func.get('name', '').lower()
                    if any(keyword in func_name for keyword in ['backup', 'restore', 'import', 'export', 'course_backup', 'course_restore']):
                        backup_functions.append(func)
                
                print(f"\n🎯 Backup/Import related functions ({len(backup_functions)}):")
                for func in backup_functions:
                    print(f"   - {func.get('name')}")
                
                # Look for file upload functions (needed for backup files)
                file_functions = []
                for func in functions:
                    func_name = func.get('name', '').lower()
                    if any(keyword in func_name for keyword in ['file', 'upload', 'repository']):
                        file_functions.append(func)
                
                print(f"\n📁 File/Upload related functions ({len(file_functions)}):")
                for func in file_functions:
                    print(f"   - {func.get('name')}")
                
                # Look for course duplication functions
                duplicate_functions = []
                for func in functions:
                    func_name = func.get('name', '').lower()
                    if any(keyword in func_name for keyword in ['duplicate', 'copy', 'clone']):
                        duplicate_functions.append(func)
                
                print(f"\n🔄 Course duplication functions ({len(duplicate_functions)}):")
                for func in duplicate_functions:
                    print(f"   - {func.get('name')}")
                        
        except Exception as e:
            print(f"❌ Could not get site info: {e}")

async def test_file_upload():
    """Test file upload functionality for backup files"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print(f"\n🔬 Testing File Upload Capabilities...")
        
        # Test core_files_upload function
        print("1️⃣ Testing core_files_upload:")
        try:
            # Create a simple test file to upload
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test backup file content\nThis is a test file for upload testing.")
                test_file_path = f.name
            
            print(f"   Created test file: {test_file_path}")
            
            # Try to upload the file
            upload_result = await client._upload_file(test_file_path, "test_backup.txt")
            print(f"   ✅ File upload successful: {upload_result}")
            
            # Clean up
            os.unlink(test_file_path)
            
        except Exception as e:
            print(f"   ❌ File upload failed: {e}")

async def explore_course_templates():
    """Explore if we can create course templates or use existing courses as templates"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print(f"\n🎨 Exploring Course Template Approaches...")
        
        # Check if we can get course content/structure from existing courses
        print("1️⃣ Testing course content retrieval:")
        try:
            # Get courses to find a template candidate
            courses = await client.get_courses()
            if courses:
                template_course = courses[0]  # Use first course as test
                course_id = template_course.get('id')
                course_name = template_course.get('fullname', 'Unknown')
                
                print(f"   Using course '{course_name}' (ID: {course_id}) as template test")
                
                # Get course contents
                contents = await client._call_api("core_course_get_contents", {"courseid": course_id})
                print(f"   Course has {len(contents)} sections")
                
                # Get course modules/activities
                for section in contents[:1]:  # Just first section
                    modules = section.get('modules', [])
                    print(f"   Section {section.get('section', 0)} has {len(modules)} modules")
                    for module in modules[:2]:  # First 2 modules
                        print(f"      - {module.get('modname', 'unknown')}: {module.get('name', 'unnamed')}")
                
        except Exception as e:
            print(f"   ❌ Course content retrieval failed: {e}")

async def test_course_duplication():
    """Test if we can duplicate/copy courses"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print(f"\n🔄 Testing Course Duplication...")
        
        # Test course duplication function if available
        print("1️⃣ Testing core_course_duplicate_course:")
        try:
            courses = await client.get_courses()
            if courses and len(courses) > 1:
                source_course = courses[0]
                source_id = source_course.get('id')
                
                result = await client._call_api("core_course_duplicate_course", {
                    "courseid": source_id,
                    "fullname": "Duplicated Test Course",
                    "shortname": f"dup_test_{source_id}",
                    "categoryid": 1,
                    "visible": 1
                })
                print(f"   ✅ Course duplication successful: {result}")
                
        except Exception as e:
            print(f"   ❌ Course duplication failed: {e}")

async def main():
    """Main exploration function"""
    print("🧪 Backup/Import Functionality Exploration")
    print("=" * 60)
    
    await explore_backup_apis()
    await test_file_upload()
    await explore_course_templates()
    await test_course_duplication()
    
    print("\n" + "=" * 60)
    print("🎯 Backup/Import Exploration Complete")
    
    print("\n💡 Alternative Approaches to Consider:")
    print("1. Course duplication: Copy a template course with pre-made structure")
    print("2. Backup/restore: Create backup files programmatically and restore them")
    print("3. Template-based: Use existing course as template and modify content")
    print("4. File upload + import: Upload course backup files and import them")

if __name__ == "__main__":
    asyncio.run(main())