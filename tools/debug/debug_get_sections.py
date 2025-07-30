#!/usr/bin/env python3
"""
Debug GET_SECTIONS API call
"""

import asyncio
import logging
from moodle_client import MoodleClient
from config import Config
from constants import MoodleWebServices

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_get_sections():
    """Debug the GET_SECTIONS API call"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Debugging GET_SECTIONS API...")
        
        course_id = 13
        
        print(f"📚 Getting sections for course {course_id}...")
        
        # Test both API calls that might be used
        print("\n1️⃣ Testing core_course_get_contents:")
        try:
            contents_result = await client._call_api("core_course_get_contents", {"courseid": course_id})
            print(f"   Returned {len(contents_result)} items")
            for item in contents_result:
                section_num = item.get('section', 'unknown')
                name = item.get('name', 'NULL')
                print(f"   Section {section_num}: '{name}'")
        except Exception as e:
            print(f"   Error: {e}")
        
        print(f"\n2️⃣ Testing {MoodleWebServices.GET_SECTIONS}:")
        try:
            sections_result = await client._call_api(MoodleWebServices.GET_SECTIONS, {"courseid": course_id})
            print(f"   Returned {len(sections_result)} items")
            for item in sections_result:
                print(f"   Keys: {list(item.keys())}")
                section_num = item.get('section', item.get('sectionnum', 'unknown'))
                name = item.get('name', 'NULL')
                print(f"   Section {section_num}: '{name}'")
                break  # Just show first one
        except Exception as e:
            print(f"   Error: {e}")
        
        print(f"\n3️⃣ Testing core_course_get_course_sections:")
        try:
            course_sections_result = await client._call_api("core_course_get_course_sections", {"courseid": course_id})
            print(f"   Returned {len(course_sections_result)} items")
            for item in course_sections_result:
                print(f"   Keys: {list(item.keys())}")
                section_num = item.get('section', item.get('sectionnumber', 'unknown'))
                name = item.get('name', 'NULL')
                print(f"   Section {section_num}: '{name}'")
                break  # Just show first one
        except Exception as e:
            print(f"   Error: {e}")

async def main():
    """Main debug function"""
    print("🧪 GET_SECTIONS API Debug")
    print("=" * 50)
    
    await debug_get_sections()
    
    print("\n" + "=" * 50)
    print("🎯 GET_SECTIONS Debug Complete")

if __name__ == "__main__":
    asyncio.run(main())