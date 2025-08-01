#!/usr/bin/env python3
"""
Test the improved enrollment logic
"""

import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moodle_client import MoodleClient


async def test_enrollment_fix():
    """Test the improved enrollment logic"""
    print("🔧 Testing Improved Enrollment Logic")
    print("=" * 50)

    load_dotenv()

    if not os.getenv("MOODLE_URL") or not os.getenv("MOODLE_TOKEN"):
        print("❌ MOODLE_URL or MOODLE_TOKEN not configured")
        return

    async with MoodleClient(
        os.getenv("MOODLE_URL"), os.getenv("MOODLE_TOKEN")
    ) as client:
        try:
            # Test 1: Get current user
            print("👤 Testing current user detection...")
            current_user = await client._get_current_user()
            print(
                f"   Current user: {current_user.get('username')} (ID: {current_user.get('userid')})"
            )

            # Test 2: Create a new course to test enrollment
            print("\n🎓 Creating test course...")
            test_course_name = (
                f"Enrollment Test Course - {datetime.now().strftime('%H%M%S')}"
            )
            course_id = await client.create_course(
                name=test_course_name,
                description="Testing improved enrollment logic",
                category_id=1,
            )
            print(f"   Course created: ID {course_id}")

            # Test 3: Check if user got enrolled
            print(f"\n📋 Checking enrollment status...")
            user_courses = await client._call_api(
                "core_enrol_get_users_courses", {"userid": current_user.get("userid")}
            )

            enrolled_course_ids = [c.get("id") for c in user_courses]
            is_enrolled = course_id in enrolled_course_ids

            print(f"   User enrolled in course: {'✅ YES' if is_enrolled else '❌ NO'}")
            print(f"   Total enrolled courses: {len(user_courses)}")

            if is_enrolled:
                # Find the course details
                enrolled_course = next(
                    (c for c in user_courses if c.get("id") == course_id), None
                )
                if enrolled_course:
                    print(f"   Course name: {enrolled_course.get('fullname')}")
                    print(
                        f"   Course URL: {os.getenv('MOODLE_URL')}/course/view.php?id={course_id}"
                    )

            # Test 4: Check enrollment methods for this course
            print(f"\n🔍 Checking enrollment methods for course {course_id}...")
            try:
                enrol_methods = await client._call_api(
                    "core_enrol_get_course_enrolment_methods", {"courseid": course_id}
                )

                print(f"   Available enrollment methods: {len(enrol_methods)}")
                for method in enrol_methods:
                    status = "Enabled" if method.get("status") == 0 else "Disabled"
                    print(f"   - {method.get('type')}: {status}")

            except Exception as e:
                print(f"   ⚠️  Could not get enrollment methods: {e}")

            print(f"\n🎯 Test Summary:")
            print(f"   ✅ User detection: Working")
            print(f"   ✅ Course creation: Working")
            print(
                f"   {'✅' if is_enrolled else '❌'} User enrollment: {'Working' if is_enrolled else 'Failed'}"
            )
            print(
                f"   🔗 Direct access: {os.getenv('MOODLE_URL')}/course/view.php?id={course_id}"
            )

            if is_enrolled:
                print(f"\n🎉 SUCCESS: The enrollment fix is working!")
                print(
                    f"   Courses created via Claude Desktop should now appear in 'My Courses'"
                )
            else:
                print(f"\n⚠️  ISSUE: User enrollment still not working automatically")
                print(f"   Manual enrollment may be required")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_enrollment_fix())
