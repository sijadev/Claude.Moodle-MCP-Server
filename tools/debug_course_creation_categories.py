#!/usr/bin/env python3
"""
Debug Course Creation - Categories Investigation
==============================================
Untersucht verfügbare Kategorien und Kurserstellungs-Parameter in Moodle.
"""

import asyncio
import json
import os
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
MOODLE_TOKEN = config.get(
    "MOODLE_PLUGIN_TOKEN",
    config.get("MOODLE_BASIC_TOKEN", config.get("MOODLE_ADMIN_TOKEN", "")),
)


class MoodleAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def call_webservice(self, function_name: str, **params):
        """Call Moodle web service function."""
        url = f"{self.base_url}/webservice/rest/server.php"

        data = {
            "wstoken": self.token,
            "wsfunction": function_name,
            "moodlewsrestformat": "json",
            **params,
        }

        async with self.session.post(url, data=data) as response:
            if response.status == 200:
                result = await response.json()
                if isinstance(result, dict) and "exception" in result:
                    raise Exception(
                        f"Moodle error: {result.get('message', 'Unknown error')}"
                    )
                return result
            else:
                raise Exception(f"HTTP {response.status}: {await response.text()}")


async def debug_categories():
    """Debug verfügbare Kategorien."""
    print("🔍 Untersuchung der Moodle-Kategorien...")

    async with MoodleAPIClient(MOODLE_URL, MOODLE_TOKEN) as client:
        try:
            # Kategorie-Informationen abrufen
            categories = await client.call_webservice("core_course_get_categories")

            print(f"📂 Gefundene Kategorien: {len(categories)}")
            for category in categories:
                print(f"  ID: {category.get('id')}")
                print(f"  Name: {category.get('name')}")
                print(f"  Path: {category.get('path', 'N/A')}")
                print(f"  Parent: {category.get('parent', 'N/A')}")
                print(f"  Course Count: {category.get('coursecount', 'N/A')}")
                print("  ---")

        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Kategorien: {e}")


async def test_course_parameters():
    """Teste verschiedene Parameter-Kombinationen für Kurserstellung."""
    print("\n🧪 Teste Kurserstellungs-Parameter...")

    async with MoodleAPIClient(MOODLE_URL, MOODLE_TOKEN) as client:

        # Teste minimale Parameter
        test_cases = [
            {
                "name": "Minimal Required",
                "data": [
                    {
                        "fullname": "Test Course Minimal",
                        "shortname": "testminimal",
                        "categoryid": 1,
                    }
                ],
            },
            {
                "name": "With Summary",
                "data": [
                    {
                        "fullname": "Test Course Summary",
                        "shortname": "testsummary",
                        "categoryid": 1,
                        "summary": "Test course with summary",
                    }
                ],
            },
            {
                "name": "With Format",
                "data": [
                    {
                        "fullname": "Test Course Format",
                        "shortname": "testformat",
                        "categoryid": 1,
                        "summary": "Test course with format",
                        "format": "topics",
                    }
                ],
            },
            {
                "name": "Complete Parameters",
                "data": [
                    {
                        "fullname": "Test Course Complete",
                        "shortname": "testcomplete",
                        "categoryid": 1,
                        "summary": "Complete test course",
                        "format": "topics",
                        "visible": 1,
                        "startdate": 0,
                        "enddate": 0,
                    }
                ],
            },
        ]

        for test_case in test_cases:
            print(f"\n📋 Test: {test_case['name']}")
            print(f"   Parameter: {json.dumps(test_case['data'], indent=2)}")

            try:
                result = await client.call_webservice(
                    "core_course_create_courses", courses=test_case["data"]
                )

                if result and len(result) > 0:
                    course = result[0]
                    print(f"   ✅ Erfolgreich! ID: {course.get('id')}")

                    # Kurs löschen für saubere Tests
                    try:
                        await client.call_webservice(
                            "core_course_delete_courses", courseids=[course.get("id")]
                        )
                        print(f"   🗑️ Test-Kurs gelöscht")
                    except:
                        print(f"   ⚠️ Konnte Test-Kurs nicht löschen")
                else:
                    print(f"   ❌ Fehlgeschlagen: Kein Ergebnis")

            except Exception as e:
                print(f"   ❌ Fehler: {e}")


async def check_webservice_capabilities():
    """Überprüfe verfügbare Web Service Funktionen."""
    print("\n🔧 Überprüfung der Web Service Funktionen...")

    async with MoodleAPIClient(MOODLE_URL, MOODLE_TOKEN) as client:
        try:
            # Site Info abrufen
            site_info = await client.call_webservice("core_webservice_get_site_info")

            print(f"📊 Site Info:")
            print(f"   Sitename: {site_info.get('sitename')}")
            print(f"   Version: {site_info.get('release')}")
            print(f"   User: {site_info.get('fullname')} ({site_info.get('username')})")

            # Verfügbare Funktionen
            functions = site_info.get("functions", [])
            course_functions = [
                f for f in functions if "course" in f.get("name", "").lower()
            ]

            print(f"\n📚 Verfügbare Kurs-Funktionen ({len(course_functions)}):")
            for func in course_functions[:10]:  # Zeige nur erste 10
                print(f"   - {func.get('name')}")

            # Check spezifische Funktionen
            required_functions = [
                "core_course_create_courses",
                "core_course_get_courses",
                "core_course_delete_courses",
                "core_course_get_categories",
            ]

            print(f"\n✅ Erforderliche Funktionen:")
            available_function_names = [f.get("name") for f in functions]
            for func_name in required_functions:
                if func_name in available_function_names:
                    print(f"   ✅ {func_name}")
                else:
                    print(f"   ❌ {func_name} - NICHT VERFÜGBAR")

        except Exception as e:
            print(f"❌ Fehler beim Überprüfen der Funktionen: {e}")


async def main():
    """Haupt-Debug-Funktion."""
    print("🚀 Debug: Moodle Kurserstellung")
    print("=" * 50)

    if not MOODLE_TOKEN:
        print("❌ Kein Moodle Token gefunden!")
        print("   Bitte überprüfen Sie config/moodle_tokens.env")
        return

    print(f"🌐 Moodle URL: {MOODLE_URL}")
    print(f"🔐 Token: {MOODLE_TOKEN[:10]}...")

    await check_webservice_capabilities()
    await debug_categories()
    await test_course_parameters()

    print("\n" + "=" * 50)
    print("🎯 Debug abgeschlossen!")


if __name__ == "__main__":
    asyncio.run(main())
