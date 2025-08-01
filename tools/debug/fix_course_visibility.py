#!/usr/bin/env python3
"""
Fix course visibility by enabling enrollment and enrolling user
"""

import asyncio
import os

from dotenv import load_dotenv


async def fix_course_visibility():
    print("🔧 Fixing Course Visibility Issues")
    print("=" * 50)

    # Use Docker to directly fix enrollment in database
    import subprocess

    # SQL to enable self-enrollment for all courses and enroll user simon
    sql_commands = """
-- Enable self-enrollment for all courses (except site course)
INSERT IGNORE INTO mdl_enrol (enrol, status, courseid, sortorder, name, enrolperiod, enrolstartdate, enrolenddate, expirynotify, expirythreshold, notifyall, password, cost, currency, roleid, customint1, customint2, customint3, customint4, customint5, customint6, customdec1, customdec2, customchar1, customchar2, customchar3, customtext1, customtext2, customtext3, customtext4, timecreated, timemodified)
SELECT 'self', 0, c.id, 0, NULL, 0, 0, 0, 0, 86400, 0, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL, NULL, NULL, 0.000000, 0.000000, NULL, NULL, NULL, NULL, NULL, NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()
FROM mdl_course c
WHERE c.id > 1
AND NOT EXISTS (SELECT 1 FROM mdl_enrol e WHERE e.courseid = c.id AND e.enrol = 'self');

-- Enroll user simon (ID 2) in all courses
INSERT IGNORE INTO mdl_user_enrolments (status, enrolid, userid, timestart, timeend, modifierid, timecreated, timemodified)
SELECT 0, e.id, 2, 0, 0, 2, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()
FROM mdl_enrol e
JOIN mdl_course c ON e.courseid = c.id
WHERE c.id > 1
AND e.enrol = 'self'
AND e.status = 0
AND NOT EXISTS (SELECT 1 FROM mdl_user_enrolments ue WHERE ue.enrolid = e.id AND ue.userid = 2);

-- Count results
SELECT
    (SELECT COUNT(*) FROM mdl_course WHERE id > 1) as total_courses,
    (SELECT COUNT(*) FROM mdl_enrol WHERE enrol = 'self' AND status = 0) as self_enrol_enabled,
    (SELECT COUNT(DISTINCT e.courseid) FROM mdl_user_enrolments ue JOIN mdl_enrol e ON ue.enrolid = e.id WHERE ue.userid = 2) as user_enrolled_courses;
"""

    try:
        print("🔧 Enabling self-enrollment for all courses...")
        result = subprocess.run(
            [
                "docker",
                "exec",
                "moodleclaude_db",
                "mysql",
                "-u",
                "bn_moodle",
                "-D",
                "bitnami_moodle",
                "-e",
                sql_commands,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Database updates completed")
            print("📊 Results:")
            lines = result.stdout.strip().split("\n")
            for line in lines[-3:]:  # Last 3 lines should be the results
                if "total_courses" in line or any(char.isdigit() for char in line):
                    print(f"   {line}")
        else:
            print(f"❌ Database update failed: {result.stderr}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Now test with API
    print(f"\n🧪 Testing with Moodle API...")

    load_dotenv()
    from moodle_client import MoodleClient

    async with MoodleClient(
        os.getenv("MOODLE_URL"), os.getenv("MOODLE_TOKEN")
    ) as client:
        try:
            # Check user enrollments
            user_courses = await client._call_api(
                "core_enrol_get_users_courses", {"userid": 2}
            )
            print(f"👤 User simon is now enrolled in {len(user_courses)} courses:")

            for course in user_courses:
                print(
                    f"   ✅ {course.get('fullname', 'Unnamed')} (ID: {course.get('id', '?')})"
                )

            if len(user_courses) > 0:
                print(f"\n🎉 Success! Courses should now appear in 'My Courses' page")
            else:
                print(f"\n⚠️  No courses found - may need manual enrollment")

        except Exception as e:
            print(f"❌ API test failed: {e}")


if __name__ == "__main__":
    asyncio.run(fix_course_visibility())
