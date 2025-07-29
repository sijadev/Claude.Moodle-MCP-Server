#!/usr/bin/env python3
"""
Test script to validate enrollment configuration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from moodle_client import MoodleClient

async def test_enrollment():
    """Test that enrollment configuration is working"""
    load_dotenv()
    
    print("🧪 Testing Enrollment Configuration")
    print("=" * 40)
    
    async with MoodleClient(os.getenv('MOODLE_URL'), os.getenv('MOODLE_TOKEN')) as client:
        try:
            # Get user's enrolled courses
            user_courses = await client._call_api('core_enrol_get_users_courses', {'userid': 2})
            
            print(f"✅ User simon enrolled in {len(user_courses)} courses:")
            for course in user_courses:
                name = course.get('fullname', 'Unknown')
                course_id = course.get('id', '?')
                category = course.get('categoryid', '?')
                print(f"   📚 {name} (ID: {course_id})")
                
            if len(user_courses) > 0:
                print(f"\n🎉 SUCCESS: Courses will appear in 'My Courses' page!")
                print(f"📊 Total visible courses: {len(user_courses)}")
            else:
                print(f"\n⚠️  WARNING: No courses found - enrollment may need configuration")
                
        except Exception as e:
            print(f"❌ Error testing enrollment: {e}")

if __name__ == "__main__":
    asyncio.run(test_enrollment())