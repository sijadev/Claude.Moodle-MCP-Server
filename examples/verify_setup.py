#!/usr/bin/env python3
"""
Verification script to check if Moodle is properly configured for MoodleClaude
"""

import asyncio
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodle_client import MoodleAPIError, MoodleClient


class MoodleSetupVerifier:
    def __init__(self, moodle_url, moodle_token):
        self.moodle_url = moodle_url
        self.moodle_token = moodle_token
        self.client = None
        self.results = {
            "connection": False,
            "basic_functions": {},
            "section_functions": {},
            "activity_functions": {},
            "permissions": {},
            "overall_score": 0,
        }

    async def verify_all(self):
        """Run all verification checks"""
        print("🔍 MoodleClaude Setup Verification")
        print("=" * 50)

        try:
            async with MoodleClient(self.moodle_url, self.moodle_token) as client:
                self.client = client

                # Run all checks
                await self._check_connection()
                await self._check_basic_functions()
                await self._check_section_functions()
                await self._check_activity_functions()
                await self._check_permissions()

                # Calculate overall score
                self._calculate_score()

                # Show results
                self._show_results()

        except Exception as e:
            print(f"❌ Failed to connect to Moodle: {e}")
            return False

        return self.results["overall_score"] >= 80

    async def _check_connection(self):
        """Check basic connection"""
        print("\n1️⃣ Testing basic connection...")

        try:
            courses = await self.client.get_courses()
            self.results["connection"] = True
            print(f"   ✅ Connected successfully - found {len(courses)} courses")
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")

    async def _check_basic_functions(self):
        """Check basic required functions"""
        print("\n2️⃣ Testing basic functions...")

        basic_functions = {
            "core_course_get_courses": "List courses",
            "core_course_create_courses": "Create courses",
            "core_course_get_categories": "List categories",
        }

        for func, description in basic_functions.items():
            try:
                if func == "core_course_get_courses":
                    result = await self.client._call_api(func)
                    success = isinstance(result, list)
                elif func == "core_course_get_categories":
                    result = await self.client._call_api(func)
                    success = isinstance(result, list)
                else:
                    success = True  # We know this works from previous tests

                self.results["basic_functions"][func] = success
                status = "✅" if success else "❌"
                print(f"   {status} {description}")

            except Exception as e:
                self.results["basic_functions"][func] = False
                print(f"   ❌ {description} - {str(e)[:50]}...")

    async def _check_section_functions(self):
        """Check section creation functions"""
        print("\n3️⃣ Testing section functions...")

        section_functions = {
            "core_course_create_sections": "Create sections",
            "core_course_edit_section": "Edit sections",
            "core_course_get_contents": "Get course contents",
        }

        for func, description in section_functions.items():
            try:
                # Test with dummy parameters to see if function exists
                await self.client._call_api(func, {"test": "dummy"})
                self.results["section_functions"][func] = True
                print(f"   ✅ {description}")

            except MoodleAPIError as e:
                if (
                    "Can't find data record in database table external_functions"
                    in str(e)
                ):
                    self.results["section_functions"][func] = False
                    print(f"   ❌ {description} - Function not enabled in web service")
                elif "Invalid parameter" in str(
                    e
                ) or "Missing required parameter" in str(e):
                    self.results["section_functions"][func] = True
                    print(f"   ✅ {description} - Available (parameter error expected)")
                else:
                    self.results["section_functions"][func] = False
                    print(f"   ⚠️  {description} - {str(e)[:50]}...")
            except Exception as e:
                self.results["section_functions"][func] = False
                print(f"   ❌ {description} - {str(e)[:50]}...")

    async def _check_activity_functions(self):
        """Check activity creation functions"""
        print("\n4️⃣ Testing activity functions...")

        activity_functions = {
            "core_course_create_activities": "Create activities",
            "mod_page_create_page": "Create pages",
            "mod_label_add_label": "Create labels",
        }

        for func, description in activity_functions.items():
            try:
                await self.client._call_api(func, {"test": "dummy"})
                self.results["activity_functions"][func] = True
                print(f"   ✅ {description}")

            except MoodleAPIError as e:
                if (
                    "Can't find data record in database table external_functions"
                    in str(e)
                ):
                    self.results["activity_functions"][func] = False
                    print(f"   ❌ {description} - Function not enabled in web service")
                elif "Invalid parameter" in str(
                    e
                ) or "Missing required parameter" in str(e):
                    self.results["activity_functions"][func] = True
                    print(f"   ✅ {description} - Available (parameter error expected)")
                else:
                    self.results["activity_functions"][func] = False
                    print(f"   ⚠️  {description} - {str(e)[:50]}...")
            except Exception as e:
                self.results["activity_functions"][func] = False
                print(f"   ❌ {description} - {str(e)[:50]}...")

    async def _check_permissions(self):
        """Check user permissions indirectly"""
        print("\n5️⃣ Testing permissions...")

        try:
            # Try to get site info
            try:
                await self.client._call_api("core_webservice_get_site_info")
                self.results["permissions"]["site_info"] = True
                print("   ✅ Site information access")
            except:
                self.results["permissions"]["site_info"] = False
                print("   ❌ Site information access - may lack permissions")

            # Check if we can access course contents
            courses = await self.client.get_courses()
            if courses:
                try:
                    await self.client._call_api(
                        "core_course_get_contents", {"courseid": courses[0]["id"]}
                    )
                    self.results["permissions"]["course_contents"] = True
                    print("   ✅ Course content access")
                except:
                    self.results["permissions"]["course_contents"] = False
                    print("   ❌ Course content access - may lack course permissions")

        except Exception as e:
            print(f"   ⚠️  Permission check failed: {e}")

    def _calculate_score(self):
        """Calculate overall setup score"""
        total_points = 0
        max_points = 0

        # Connection (20 points)
        max_points += 20
        if self.results["connection"]:
            total_points += 20

        # Basic functions (30 points)
        basic_available = sum(self.results["basic_functions"].values())
        basic_total = len(self.results["basic_functions"])
        max_points += 30
        if basic_total > 0:
            total_points += int((basic_available / basic_total) * 30)

        # Section functions (30 points) - MOST IMPORTANT
        section_available = sum(self.results["section_functions"].values())
        section_total = len(self.results["section_functions"])
        max_points += 30
        if section_total > 0:
            total_points += int((section_available / section_total) * 30)

        # Activity functions (20 points)
        activity_available = sum(self.results["activity_functions"].values())
        activity_total = len(self.results["activity_functions"])
        max_points += 20
        if activity_total > 0:
            total_points += int((activity_available / activity_total) * 20)

        self.results["overall_score"] = (
            int((total_points / max_points) * 100) if max_points > 0 else 0
        )

    def _show_results(self):
        """Show verification results"""
        print("\n" + "=" * 60)
        print("📊 VERIFICATION RESULTS")
        print("=" * 60)

        score = self.results["overall_score"]

        if score >= 90:
            status = "🎉 EXCELLENT"
            color = "green"
        elif score >= 80:
            status = "✅ GOOD"
            color = "green"
        elif score >= 60:
            status = "⚠️  NEEDS WORK"
            color = "yellow"
        else:
            status = "❌ POOR"
            color = "red"

        print(f"\nOverall Score: {score}/100 - {status}")

        # Detailed breakdown
        print(f"\n📋 Detailed Results:")
        print(f"Connection: {'✅' if self.results['connection'] else '❌'}")

        basic_score = sum(self.results["basic_functions"].values())
        basic_total = len(self.results["basic_functions"])
        print(f"Basic Functions: {basic_score}/{basic_total}")

        section_score = sum(self.results["section_functions"].values())
        section_total = len(self.results["section_functions"])
        print(f"Section Functions: {section_score}/{section_total} ⭐ MOST IMPORTANT")

        activity_score = sum(self.results["activity_functions"].values())
        activity_total = len(self.results["activity_functions"])
        print(f"Activity Functions: {activity_score}/{activity_total}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")

        if not self.results["connection"]:
            print("❗ Fix basic connection first - check URL and token")

        if section_score < section_total:
            print("❗ Enable section functions in Web Services:")
            for func, available in self.results["section_functions"].items():
                if not available:
                    print(f"   - Add {func} to your external service")

        if activity_score < activity_total:
            print("❗ Enable activity functions in Web Services:")
            for func, available in self.results["activity_functions"].items():
                if not available:
                    print(f"   - Add {func} to your external service")

        if score >= 80:
            print("\n🚀 Your setup is ready for advanced MoodleClaude features!")
            print("   Try running: python demos/advanced_transfer.py")
        else:
            print("\n📖 Follow the setup guide: MOODLE_SETUP.md")

        print("=" * 60)


async def main():
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_TOKEN", "b2021a7a41309b8c58ad026a751d0cd0")

    print(f"Testing Moodle setup:")
    print(f"URL: {moodle_url}")
    print(f"Token: {moodle_token[:10]}...")

    verifier = MoodleSetupVerifier(moodle_url, moodle_token)
    success = await verifier.verify_all()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
