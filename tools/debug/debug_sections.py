#!/usr/bin/env python3
"""
Debug script to understand section data structure
"""

import asyncio
import logging
from moodle_client import MoodleClient
from config import Config
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_sections():
    """Debug section structure and content update process"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Debugging Section Structure...")
        
        # Use the photography course we just created
        course_id = 13
        
        print(f"📚 Analyzing sections for course {course_id}...")
        
        # Get sections using the API
        sections = await client._call_api("core_course_get_contents", {"courseid": course_id})
        
        print(f"📊 Found {len(sections)} sections")
        
        for i, section in enumerate(sections):
            print(f"\n🔍 Section {i}:")
            print(f"   Keys available: {list(section.keys())}")
            print(f"   Section data:")
            for key, value in section.items():
                if key in ['name', 'summary', 'section', 'id', 'sectionnum']:
                    print(f"      {key}: {repr(value)}")
        
        # Now try to create a new section and see what happens
        print(f"\n🔄 Testing section creation...")
        try:
            new_section_id = await client.create_section(
                course_id=course_id,
                name="Test Section Name",
                description="Test section description content"
            )
            print(f"✅ Created section ID: {new_section_id}")
            
        except Exception as e:
            print(f"❌ Section creation failed: {e}")
        
        # Check sections again after creation attempt
        print(f"\n📊 Sections after creation attempt:")
        sections_after = await client._call_api("core_course_get_contents", {"courseid": course_id})
        for i, section in enumerate(sections_after):
            name = section.get('name', 'NULL')
            summary = section.get('summary', '')
            section_num = section.get('section', 'unknown')
            print(f"   Section {section_num}: name='{name}', summary_length={len(summary)}")

async def main():
    """Main debug function"""
    print("🧪 Section Structure Debug")
    print("=" * 50)
    
    await debug_sections()
    
    print("\n" + "=" * 50)
    print("🎯 Section Debug Complete")

if __name__ == "__main__":
    asyncio.run(main())