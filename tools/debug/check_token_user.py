#!/usr/bin/env python3
"""
Check which user a Moodle token belongs to
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moodle_client import MoodleClient


async def check_token_user():
    """Check which user the current token belongs to"""
    load_dotenv()

    token = os.getenv("MOODLE_TOKEN")
    if not token:
        print("❌ No MOODLE_TOKEN found")
        return

    print(f"🔍 Checking token user for: {token[:8]}...")

    async with MoodleClient(os.getenv("MOODLE_URL"), token) as client:
        try:
            # Get site info to see current user
            site_info = await client._call_api("core_webservice_get_site_info")

            print(f"📊 Token Info:")
            print(f"   User ID: {site_info.get('userid', 'Unknown')}")
            print(f"   Username: {site_info.get('username', 'Unknown')}")
            print(f"   Full Name: {site_info.get('fullname', 'Unknown')}")
            print(f"   Site Name: {site_info.get('sitename', 'Unknown')}")

            # Also check the current user's courses
            user_courses = await client._call_api(
                "core_enrol_get_users_courses", {"userid": site_info.get("userid")}
            )

            print(f"\n👤 User's enrolled courses: {len(user_courses)}")
            for course in user_courses[:5]:  # Show first 5
                print(
                    f"   - {course.get('fullname', 'Unknown')} (ID: {course.get('id')})"
                )

            return site_info.get("userid")

        except Exception as e:
            print(f"❌ Error: {e}")
            return None


if __name__ == "__main__":
    asyncio.run(check_token_user())
