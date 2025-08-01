#!/usr/bin/env python3
"""
Test if core_course_create_courses actually works as a web service
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


async def test_core_course_creation():
    load_dotenv()

    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")

    print(f"🔍 Testing Core Course Creation Function")
    print(f"URL: {moodle_url}")
    print("=" * 60)

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            # Test 1: Try to create course directly via API call
            print("📋 Test 1: Direct API Call to core_course_create_courses")

            # Prepare course data as Moodle expects it
            course_data = {
                "courses[0][fullname]": "Direct API Test Course",
                "courses[0][shortname]": f"api_test_{int(asyncio.get_event_loop().time())}",
                "courses[0][categoryid]": 1,
                "courses[0][summary]": "Course created via direct API call",
                "courses[0][summaryformat]": 1,
                "courses[0][format]": "topics",
                "courses[0][visible]": 1,
                "courses[0][numsections]": 3,
            }

            try:
                result = await client._call_api(
                    "core_course_create_courses", course_data
                )
                print(f"✅ Direct API call successful!")
                print(f"   Result: {result}")

                if isinstance(result, list) and len(result) > 0:
                    course_id = result[0].get("id")
                    print(f"   Created course ID: {course_id}")

                    # Test getting the course content
                    print(f"\n📖 Test 2: Get Course Contents")
                    contents = await client._call_api(
                        "core_course_get_contents", {"courseid": course_id}
                    )
                    print(f"✅ Course has {len(contents)} sections")
                    for section in contents:
                        print(
                            f"   - Section {section.get('section', '?')}: {section.get('name', 'Unnamed')}"
                        )

                else:
                    print(f"❌ Unexpected result format: {result}")

            except Exception as e:
                print(f"❌ Direct API call failed: {e}")
                print(
                    f"   This confirms core_course_create_courses might be internal only"
                )

            # Test 2: Try our wrapper method
            print(f"\n🎓 Test 3: Via MoodleClient wrapper")
            try:
                course_id = await client.create_course(
                    name="Wrapper Test Course",
                    description="Course created via wrapper method",
                    numsections=2,
                )
                print(f"✅ Wrapper method successful! Course ID: {course_id}")
            except Exception as e:
                print(f"❌ Wrapper method failed: {e}")

            # Test 3: List existing courses
            print(f"\n📚 Test 4: List All Courses")
            courses = await client.get_courses()
            print(f"✅ Found {len(courses)} total courses:")
            for course in courses[-3:]:  # Show last 3 courses
                print(
                    f"   - ID {course.get('id', '?')}: {course.get('fullname', 'Unnamed')}"
                )

    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_core_course_creation())
