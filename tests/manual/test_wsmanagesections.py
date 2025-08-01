#!/usr/bin/env python3
"""
Test the local_wsmanagesections plugin functionality
"""

import asyncio
import os

from dotenv import load_dotenv
from moodle_client import MoodleClient


async def test_wsmanagesections_plugin():
    load_dotenv()

    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")

    print(f"🔧 Testing WSManageSections Plugin")
    print(f"URL: {moodle_url}")
    print("=" * 60)

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            # First create a test course
            print("🎓 Step 1: Create Test Course")
            course_id = await client.create_course(
                name="WSManageSections Test Course",
                description="Testing the wsmanagesections plugin",
                numsections=1,  # Start with minimal sections
            )
            print(f"✅ Course created with ID: {course_id}")

            # Get initial sections
            print(f"\n📖 Step 2: Get Initial Sections")
            initial_sections = await client.get_course_sections(course_id)
            print(f"✅ Initial sections: {len(initial_sections)}")
            for section in initial_sections:
                print(
                    f"   - Section {section.get('section', '?')}: {section.get('name', 'Unnamed')}"
                )

            # Test 1: Try to get sections via wsmanagesections
            print(f"\n🔍 Test 1: Get Sections via WSManageSections")
            try:
                wms_sections = await client._call_api(
                    "local_wsmanagesections_get_sections", {"courseid": course_id}
                )
                print(f"✅ WSManageSections get_sections successful!")
                print(f"   Result: {wms_sections}")
            except Exception as e:
                print(f"❌ WSManageSections get_sections failed: {e}")

            # Test 2: Try to create a new section
            print(f"\n➕ Test 2: Create New Section via WSManageSections")
            try:
                new_section_data = {
                    "courseid": course_id,
                    "name": "Python Advanced Topics",
                    "summary": "Advanced Python programming concepts",
                    "summaryformat": 1,
                    "section": 2,  # Try to create section 2
                }

                create_result = await client._call_api(
                    "local_wsmanagesections_create_sections", new_section_data
                )
                print(f"✅ Section creation successful!")
                print(f"   Result: {create_result}")

                # Verify the new section was created
                print(f"\n🔍 Verification: Get Updated Sections")
                updated_sections = await client.get_course_sections(course_id)
                print(f"✅ Updated sections: {len(updated_sections)}")
                for section in updated_sections:
                    section_num = section.get("section", "?")
                    section_name = section.get("name", "Unnamed")
                    print(f"   - Section {section_num}: {section_name}")

            except Exception as e:
                print(f"❌ Section creation failed: {e}")
                print(f"   This might need different parameters")

            # Test 3: Try alternative parameter format
            print(f"\n🔄 Test 3: Alternative Parameter Format")
            try:
                alt_params = {
                    "courseid": course_id,
                    "sections": [
                        {
                            "name": "JavaScript Fundamentals",
                            "summary": "Introduction to JavaScript",
                            "summaryformat": 1,
                        }
                    ],
                }

                alt_result = await client._call_api(
                    "local_wsmanagesections_create_sections", alt_params
                )
                print(f"✅ Alternative format successful!")
                print(f"   Result: {alt_result}")

            except Exception as e:
                print(f"❌ Alternative format failed: {e}")

            # Test 4: Try update sections
            print(f"\n✏️ Test 4: Update Existing Section")
            try:
                update_params = {
                    "courseid": course_id,
                    "section": 1,
                    "name": "Updated Section Name",
                    "summary": "This section has been updated via WSManageSections",
                }

                update_result = await client._call_api(
                    "local_wsmanagesections_update_sections", update_params
                )
                print(f"✅ Section update successful!")
                print(f"   Result: {update_result}")

            except Exception as e:
                print(f"❌ Section update failed: {e}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_wsmanagesections_plugin())
