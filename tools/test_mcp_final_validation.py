#!/usr/bin/env python3
"""
Final MCP Validation Test
========================
Umfassende Validierung aller MCP Server Funktionen.
"""

import asyncio
import json
import os
import random
import string
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set environment variables from config
PROJECT_ROOT = Path(__file__).parent.parent
config_file = PROJECT_ROOT / "config" / "moodle_tokens.env"

if config_file.exists():
    with open(config_file, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value.strip("\"'")

from core.working_mcp_server import (
    handle_create_course,
    handle_get_course_contents,
    handle_get_courses,
    handle_test_connection,
)


def generate_unique_name():
    """Generate unique course name."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test{suffix}"


async def comprehensive_mcp_test():
    """Umfassender MCP Server Test."""
    print("🚀 Comprehensive MCP Server Validation")
    print("=" * 50)

    test_results = []

    # Test 1: Connection Test
    print("\n📡 Test 1: Connection Test")
    try:
        result = await handle_test_connection({})
        if result and len(result) > 0:
            response = result[0].text
            if "Connected to Moodle successfully" in response:
                print("✅ Connection test passed")
                test_results.append(("Connection Test", "PASS"))
            else:
                print(f"❌ Unexpected response: {response}")
                test_results.append(("Connection Test", "FAIL"))
        else:
            print("❌ No result from connection test")
            test_results.append(("Connection Test", "FAIL"))
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        test_results.append(("Connection Test", "FAIL"))

    # Test 2: Get Courses
    print("\n📚 Test 2: Get Courses")
    try:
        result = await handle_get_courses({})
        if result and len(result) > 0:
            response = result[0].text
            if "Found" in response and "courses" in response:
                print("✅ Get courses test passed")
                test_results.append(("Get Courses", "PASS"))
            else:
                print(f"❌ Unexpected response: {response}")
                test_results.append(("Get Courses", "FAIL"))
        else:
            print("❌ No result from get courses")
            test_results.append(("Get Courses", "FAIL"))
    except Exception as e:
        print(f"❌ Get courses failed: {e}")
        test_results.append(("Get Courses", "FAIL"))

    # Test 3: Create Course (with unique name)
    print("\n🏗️ Test 3: Create Course")
    unique_short = generate_unique_name()
    try:
        arguments = {
            "fullname": f"Final Validation Test Course {unique_short.upper()}",
            "shortname": unique_short,
            "category_id": 1,
        }

        result = await handle_create_course(arguments)
        if result and len(result) > 0:
            response = result[0].text
            if "Course created successfully" in response:
                print("✅ Course creation test passed")
                test_results.append(("Create Course", "PASS"))

                # Extract course ID for next test
                import re

                id_match = re.search(r"ID: (\d+)", response)
                if id_match:
                    course_id = int(id_match.group(1))
                    print(f"   📋 Created course ID: {course_id}")

                    # Test 4: Get Course Contents
                    print("\n📖 Test 4: Get Course Contents")
                    try:
                        contents_result = await handle_get_course_contents(
                            {"course_id": course_id}
                        )
                        if contents_result and len(contents_result) > 0:
                            contents_response = contents_result[0].text
                            if (
                                "Course contents" in contents_response
                                or "sections" in contents_response
                            ):
                                print("✅ Get course contents test passed")
                                test_results.append(("Get Course Contents", "PASS"))
                            else:
                                print(
                                    f"❌ Unexpected contents response: {contents_response}"
                                )
                                test_results.append(("Get Course Contents", "FAIL"))
                        else:
                            print("❌ No result from get course contents")
                            test_results.append(("Get Course Contents", "FAIL"))
                    except Exception as e:
                        print(f"❌ Get course contents failed: {e}")
                        test_results.append(("Get Course Contents", "FAIL"))

            else:
                print(f"❌ Unexpected create response: {response}")
                test_results.append(("Create Course", "FAIL"))
        else:
            print("❌ No result from course creation")
            test_results.append(("Create Course", "FAIL"))
    except Exception as e:
        print(f"❌ Course creation failed: {e}")
        test_results.append(("Create Course", "FAIL"))

    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary")
    print("=" * 50)

    passed = sum(1 for _, result in test_results if result == "PASS")
    total = len(test_results)

    for test_name, result in test_results:
        emoji = "✅" if result == "PASS" else "❌"
        print(f"{emoji} {test_name}: {result}")

    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("🎉 ALL MCP SERVER TESTS PASSED!")
        return True
    else:
        print(f"💥 {total-passed} tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(comprehensive_mcp_test())
    sys.exit(0 if success else 1)
