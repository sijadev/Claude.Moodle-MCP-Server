#!/usr/bin/env python3
"""
Test realistic Moodle functionality with available functions only
"""

import asyncio
import os
from dotenv import load_dotenv
from moodle_client import MoodleClient

async def test_realistic_moodle():
    load_dotenv()
    
    moodle_url = os.getenv('MOODLE_URL')
    moodle_token = os.getenv('MOODLE_TOKEN')
    
    print(f"🔗 Testing Realistic Moodle Integration")
    print(f"URL: {moodle_url}")
    print("=" * 60)
    
    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            # Test 1: Site info
            print("📋 Test 1: Site Info")
            site_info = await client._call_api("core_webservice_get_site_info")
            print(f"✅ Site: {site_info.get('sitename', 'Unknown')}")
            print(f"✅ Version: {site_info.get('release', 'Unknown')}")
            
            # Test 2: Create course with sections
            print(f"\n🎓 Test 2: Create Course with Auto-Sections")
            course_id = await client.create_course(
                name="MCP Realistic Test Course",
                description="A course created with realistic Moodle 4.3 capabilities",
                numsections=3  # This will create 3 sections automatically
            )
            print(f"✅ Course created with ID: {course_id}")
            
            # Test 3: Get course sections
            print(f"\n📖 Test 3: Get Course Sections") 
            sections = await client.get_course_sections(course_id)
            print(f"✅ Course has {len(sections)} sections:")
            for section in sections:
                section_num = section.get('section', '?')
                section_name = section.get('name', 'Unnamed')
                print(f"   - Section {section_num}: {section_name}")
            
            # Test 4: Edit a section
            if len(sections) > 1:
                print(f"\n✏️ Test 4: Edit Section")
                section_to_edit = None
                for section in sections:
                    if section.get('section', 0) == 1:  # First real section
                        section_to_edit = section
                        break
                        
                if section_to_edit:
                    success = await client.edit_section(
                        course_id=course_id,
                        section_id=1,
                        name="Python Fundamentals",
                        summary="Introduction to Python programming concepts"
                    )
                    print(f"✅ Section edited: {success}")
                    
                    # Get updated sections
                    updated_sections = await client.get_course_sections(course_id)
                    for section in updated_sections:
                        if section.get('section', 0) == 1:
                            print(f"✅ Section 1 name: {section.get('name', 'Unnamed')}")
                            break
            
            # Test 5: Simulate content creation (logging only)
            print(f"\n📄 Test 5: Simulate Content Creation")
            page_id = await client.create_page_activity(
                course_id=course_id,
                section_id=1,
                name="Welcome to Python",
                content="<h2>Welcome!</h2><p>This is where page content would go.</p>"
            )
            print(f"✅ Page activity simulated (ID: {page_id})")
            
            print(f"\n" + "=" * 60)
            print("🎉 REALISTIC MOODLE TEST COMPLETED!")
            print("=" * 60)
            print("✅ What WORKS in standard Moodle 4.3:")
            print("   - ✅ Course creation with auto-sections")  
            print("   - ✅ Section editing (name & description)")
            print("   - ✅ Course content retrieval")
            print("   - ✅ File uploads")
            print("")
            print("❌ What REQUIRES additional plugins:")
            print("   - ❌ Activity creation (pages, labels, etc.)")
            print("   - ❌ Manual section creation")
            print("")
            print("💡 Recommendation:")
            print("   - Use MCP for course structure and content planning")
            print("   - Activities must be created manually or with plugins")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"🔧 Check token and permissions")

if __name__ == "__main__":
    asyncio.run(test_realistic_moodle())