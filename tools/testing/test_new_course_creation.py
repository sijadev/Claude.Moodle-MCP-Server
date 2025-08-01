#!/usr/bin/env python3
"""
Test script to verify new course creation functionality
"""

import asyncio
import logging

from moodle_client import MoodleClient

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_new_course_creation():
    """Test that we can create brand new courses with proper IDs"""
    config = Config()

    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return

    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Testing New Course Creation...")

        # Get current course count before creation
        courses_before = await client.get_courses()
        print(f"📚 Courses before creation: {len(courses_before)}")
        if courses_before:
            highest_id_before = max(c.get("id", 0) for c in courses_before)
            print(f"📊 Highest course ID before: {highest_id_before}")

        # Test creating a new course
        test_course_name = "Test New Course Creation - Photography Basics"
        test_description = (
            "This is a test course to verify new course creation works properly."
        )

        print(f"🔄 Creating new course: '{test_course_name}'...")
        try:
            new_course_id = await client.create_course(
                name=test_course_name,
                description=test_description,
                category_id=1,
                numsections=3,
            )

            print(f"✅ New course created with ID: {new_course_id}")

            # Verify the course was actually created
            courses_after = await client.get_courses()
            print(f"📚 Courses after creation: {len(courses_after)}")

            # Find the new course
            new_course = next(
                (c for c in courses_after if c.get("id") == new_course_id), None
            )

            if new_course:
                actual_name = new_course.get("fullname", "Unknown")
                actual_shortname = new_course.get("shortname", "Unknown")
                actual_summary = new_course.get("summary", "")

                print(f"✅ Course verification:")
                print(f"   ID: {new_course_id}")
                print(f"   Name: '{actual_name}'")
                print(f"   Shortname: '{actual_shortname}'")
                print(f"   Summary: '{actual_summary[:100]}...'")

                # Check if name matches
                if actual_name == test_course_name:
                    print("✅ Course name matches perfectly!")
                else:
                    print(f"⚠️ Course name mismatch:")
                    print(f"   Expected: '{test_course_name}'")
                    print(f"   Actual: '{actual_name}'")

                # Check if it's a truly new course (higher ID than before)
                if courses_before and new_course_id > highest_id_before:
                    print(
                        f"✅ New course has proper sequential ID ({new_course_id} > {highest_id_before})"
                    )
                else:
                    print(f"⚠️ Course ID may not be properly sequential")

                return new_course_id
            else:
                print("❌ Could not find the newly created course in the course list")
                return None

        except Exception as e:
            print(f"❌ Course creation failed: {e}")
            return None


async def main():
    """Main test function"""
    print("🧪 New Course Creation Test")
    print("=" * 50)

    new_course_id = await test_new_course_creation()

    if new_course_id:
        print(f"\n🔍 Database verification command:")
        print(
            f'docker exec moodleclaude_db mariadb -u root bitnami_moodle -e "SELECT id, fullname, shortname, summary FROM mdl_course WHERE id = {new_course_id};"'
        )

    print("\n" + "=" * 50)
    print("🎯 New Course Creation Test Complete")


if __name__ == "__main__":
    asyncio.run(main())
