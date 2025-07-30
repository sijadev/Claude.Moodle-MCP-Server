#!/usr/bin/env python3
"""
Debug WSManageSections edit capabilities
"""

import asyncio
import logging
from moodle_client import MoodleClient
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_wsmanage_edit():
    """Debug WSManageSections editing capabilities"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Debugging WSManageSections edit capabilities...")
        
        course_id = 13
        
        # Try different WSManageSections edit functions
        test_name = "Test Section Name Update"
        test_summary = "<p>Test section summary content via WSManage</p>"
        
        print(f"🔄 Testing different WSManageSections edit methods...")
        
        # Method 1: local_wsmanagesections_edit_section
        print("1️⃣ Testing local_wsmanagesections_edit_section")
        try:
            result = await client._call_api("local_wsmanagesections_edit_section", {
                "courseid": course_id,
                "sectionnumber": 1,
                "name": test_name,
                "summary": test_summary,
                "summaryformat": 1
            })
            print(f"   Success: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: local_wsmanagesections_update_section
        print("2️⃣ Testing local_wsmanagesections_update_section")
        try:
            result = await client._call_api("local_wsmanagesections_update_section", {
                "courseid": course_id,
                "sectionnumber": 1,
                "name": test_name,
                "summary": test_summary
            })
            print(f"   Success: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 3: Try using section ID instead
        print("3️⃣ Testing with section database ID")
        
        # Get the section database ID
        sections = await client._call_api("local_wsmanagesections_get_sections", {"courseid": course_id})
        target_section = None
        for section in sections:
            if section.get('sectionnum') == 1:
                target_section = section
                break
        
        if target_section:
            section_db_id = target_section['id']
            try:
                result = await client._call_api("local_wsmanagesections_edit_section", {
                    "id": section_db_id,
                    "name": test_name,
                    "summary": test_summary,
                    "summaryformat": 1
                })
                print(f"   Success: {result}")
            except Exception as e:
                print(f"   Error: {e}")
        
        # Method 4: Check available functions
        print("4️⃣ Let's see what functions are actually available")
        try:
            # This might not work, but worth trying
            functions = await client._call_api("core_webservice_get_site_info", {})
            if 'functions' in functions:
                wsmanage_functions = [f for f in functions['functions'] if 'wsmanage' in f.get('name', '').lower()]
                print(f"   Available WSManage functions: {wsmanage_functions}")
        except Exception as e:
            print(f"   Could not get function list: {e}")

async def main():
    """Main debug function"""
    print("🧪 WSManageSections Edit Debug")
    print("=" * 50)
    
    await debug_wsmanage_edit()
    
    print("\n" + "=" * 50)
    print("🎯 WSManageSections Edit Debug Complete")

if __name__ == "__main__":
    asyncio.run(main())