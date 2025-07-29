#!/usr/bin/env python3
"""
Test wsmanagesections with correct parameters
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from moodle_client import MoodleClient

async def test_correct_wsmanage():
    load_dotenv()
    
    moodle_url = os.getenv('MOODLE_URL')
    moodle_token = os.getenv('MOODLE_TOKEN')
    
    print(f"🎯 Testing WSManageSections with Correct Parameters")
    print("=" * 60)
    
    async with MoodleClient(moodle_url, moodle_token) as client:
        
        # Create a new test course
        print("🎓 Creating new test course...")
        course_id = await client.create_course(
            name="WSManage Correct Test",
            description="Testing wsmanagesections with correct params",
            numsections=2  # Start with 2 sections
        )
        print(f"✅ Course created with ID: {course_id}")
        
        # Get initial sections
        print(f"\n📖 Initial sections:")
        initial_sections = await client._call_api("local_wsmanagesections_get_sections", {"courseid": course_id})
        print(f"✅ Found {len(initial_sections)} sections:")
        for section in initial_sections:
            print(f"   - Section {section['sectionnum']}: {section['name']}")
        
        # Test 1: Create 1 section at the end (position 0)
        print(f"\n➕ Test 1: Create 1 section at end")
        try:
            result = await client._call_api("local_wsmanagesections_create_sections", {
                "courseid": course_id,
                "position": 0,  # 0 means at the end
                "number": 1     # Create 1 section
            })
            print(f"✅ SUCCESS! Created section: {result}")
            
            # Verify
            updated_sections = await client._call_api("local_wsmanagesections_get_sections", {"courseid": course_id})
            print(f"✅ Now has {len(updated_sections)} sections:")
            for section in updated_sections:
                print(f"   - Section {section['sectionnum']}: {section['name']}")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Test 2: Create 2 sections at position 2
        print(f"\n➕ Test 2: Create 2 sections at position 2")
        try:
            result = await client._call_api("local_wsmanagesections_create_sections", {
                "courseid": course_id,
                "position": 2,  # Insert at position 2
                "number": 2     # Create 2 sections
            })
            print(f"✅ SUCCESS! Created sections: {result}")
            
            # Verify
            final_sections = await client._call_api("local_wsmanagesections_get_sections", {"courseid": course_id})
            print(f"✅ Now has {len(final_sections)} sections:")
            for section in final_sections:
                print(f"   - Section {section['sectionnum']}: {section['name']}")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            
        # Test 3: Update section names
        print(f"\n✏️ Test 3: Update section names with correct function")
        try:
            # Let's try to update section 3 if it exists
            sections_to_check = await client._call_api("local_wsmanagesections_get_sections", {"courseid": course_id})
            
            for section in sections_to_check:
                if section['sectionnum'] >= 2:  # Update section 2 or higher
                    section_id = section['id']
                    section_num = section['sectionnum']
                    
                    # Try using core_course_edit_section with correct parameters
                    update_result = await client._call_api("core_course_edit_section", {
                        "id": section_id,
                        "name": f"Python Topic {section_num}",
                        "summary": f"This is section {section_num} created by WSManageSections",
                        "summaryformat": 1
                    })
                    print(f"✅ Updated section {section_num}: {update_result}")
                    break
                    
        except Exception as e:
            print(f"❌ Update failed: {e}")
            
        # Final verification
        print(f"\n🏁 Final Course Structure:")
        final_structure = await client._call_api("local_wsmanagesections_get_sections", {"courseid": course_id})
        for section in final_structure:
            print(f"   - Section {section['sectionnum']}: {section['name']}")
            if section.get('summary'):
                print(f"     Summary: {section['summary']}")

if __name__ == "__main__":
    asyncio.run(test_correct_wsmanage())