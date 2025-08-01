#!/usr/bin/env python3
"""
Direct test of Moodle API with new token
"""

import asyncio
import os

from dotenv import load_dotenv
from moodle_client import MoodleClient


async def test_moodle_api():
    load_dotenv()

    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")

    print(f"🔗 Testing Moodle API")
    print(f"URL: {moodle_url}")
    print(f"Token: {moodle_token[:8]}...")
    print("-" * 50)

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            # Test 1: Site info
            print("📋 Test 1: Site Info")
            site_info = await client._call_api("core_webservice_get_site_info")
            print(f"✅ Site: {site_info.get('sitename', 'Unknown')}")
            print(f"✅ Moodle version: {site_info.get('release', 'Unknown')}")

            # Test 2: Get courses
            print("\n📚 Test 2: Get Courses")
            courses = await client.get_courses()
            print(f"✅ Found {len(courses)} courses")

            # Test 3: Create course
            print("\n🎓 Test 3: Create Course")
            course_id = await client.create_course(
                name="MCP Test Kurs",
                description="Ein Test-Kurs erstellt über MCP",
                category_id=1,
            )
            print(f"✅ Course created with ID: {course_id}")

            # Test 4: Get course sections
            print("\n📖 Test 4: Get Course Sections")
            sections = await client.get_course_sections(course_id)
            print(f"✅ Course has {len(sections)} sections")
            for section in sections:
                print(
                    f"   - Section {section.get('section', '?')}: {section.get('name', 'Unnamed')}"
                )

            print("\n" + "=" * 50)
            print("🎉 ALL TESTS PASSED!")
            print("✅ Moodle API is fully functional")
            print("✅ MCP Server should work perfectly now")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"🔧 Check token and permissions")


if __name__ == "__main__":
    asyncio.run(test_moodle_api())
