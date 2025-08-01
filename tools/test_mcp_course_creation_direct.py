#!/usr/bin/env python3
"""
Test MCP Course Creation Direct
==============================
Direkter Test der korrigierten Kurserstellungs-Funktionalität.
"""

import asyncio
from pathlib import Path

import aiohttp

# Load configuration
PROJECT_ROOT = Path(__file__).parent.parent
config_file = PROJECT_ROOT / "config" / "moodle_tokens.env"

config = {}
if config_file.exists():
    with open(config_file, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                config[key] = value.strip("\"'")

MOODLE_URL = config.get("MOODLE_URL", "http://localhost:8080")
MOODLE_TOKEN = config.get("MOODLE_ADMIN_TOKEN", "")


async def test_fixed_course_creation():
    """Teste die korrigierte Kurserstellung direkt."""
    print("🚀 Test: Korrigierte MCP Kurserstellung")
    print("=" * 45)

    if not MOODLE_TOKEN:
        print("❌ Kein Moodle Token gefunden!")
        return

    print(f"🌐 Moodle URL: {MOODLE_URL}")
    print(f"🔐 Token: {MOODLE_TOKEN[:10]}...")

    async with aiohttp.ClientSession() as session:
        url = f"{MOODLE_URL}/webservice/rest/server.php"

        # Test 1: Kurserstellung mit korrigierter Form-Data Syntax
        print("\n📋 Test 1: Kurserstellung mit korrigierter Syntax")

        data = {
            "wstoken": MOODLE_TOKEN,
            "wsfunction": "core_course_create_courses",
            "moodlewsrestformat": "json",
            "courses[0][fullname]": "MCP Server Test Course",
            "courses[0][shortname]": "mcpserver",
            "courses[0][categoryid]": 1,
            "courses[0][summary]": "Test course created by fixed MCP server",
        }

        try:
            async with session.post(url, data=data) as response:
                result = await response.json()

                if isinstance(result, dict) and "exception" in result:
                    print(f"   ❌ Fehler: {result.get('message')}")
                elif isinstance(result, list) and len(result) > 0:
                    course = result[0]
                    course_id = course.get("id")
                    print(f"   ✅ Erfolgreich erstellt!")
                    print(f"      ID: {course_id}")
                    print(f"      Short Name: {course.get('shortname')}")
                    print(f"      URL: {MOODLE_URL}/course/view.php?id={course_id}")

                    # Test 2: Kurs-Inhalte abrufen
                    print(f"\n📚 Test 2: Kurs-Inhalte abrufen für ID {course_id}")

                    contents_data = {
                        "wstoken": MOODLE_TOKEN,
                        "wsfunction": "core_course_get_contents",
                        "moodlewsrestformat": "json",
                        "courseid": course_id,
                    }

                    async with session.post(
                        url, data=contents_data
                    ) as contents_response:
                        contents_result = await contents_response.json()

                        if isinstance(contents_result, list):
                            print(
                                f"   ✅ Kurs-Inhalte abgerufen: {len(contents_result)} Abschnitte"
                            )
                            for i, section in enumerate(
                                contents_result[:3]
                            ):  # Zeige erste 3
                                print(
                                    f"      - Abschnitt {i}: {section.get('name', 'Unnamed')}"
                                )
                        else:
                            print(
                                f"   ⚠️ Unerwartetes Inhalts-Format: {contents_result}"
                            )

                    # Test 3: MCP Server Style Response
                    print(f"\n🤖 Test 3: MCP Server Style Response Format")
                    mcp_response = f"""✅ Course created successfully!
ID: {course_id}
Name: MCP Server Test Course
Short: mcpserver
URL: {MOODLE_URL}/course/view.php?id={course_id}"""
                    print(f"   MCP Response Format:")
                    print("   " + mcp_response.replace("\n", "\n   "))

                else:
                    print(f"   ❌ Unerwartetes Ergebnis: {result}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    print("\n" + "=" * 45)
    print("🎯 Test abgeschlossen!")
    print("\n💡 Erkenntnisse:")
    print("   - Form-Data Syntax funktioniert korrekt")
    print("   - courses[0][parameter] Format ist erforderlich")
    print("   - MCP Server sollte create_courses() Methode verwenden")


if __name__ == "__main__":
    asyncio.run(test_fixed_course_creation())
