#!/usr/bin/env python3
"""
Test Fixed Course Creation
=========================
Testet die korrigierte Kurserstellungs-Implementierung.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.working_mcp_server import ServerConfig, WorkingMoodleClient


async def test_course_creation():
    """Teste die korrigierte Kurserstellung."""
    print("🚀 Test: Korrigierte Kurserstellung")
    print("=" * 40)

    # Load configuration
    config = ServerConfig()

    if not config.moodle_token_basic:
        print("❌ Kein Moodle Token gefunden!")
        return

    print(f"🌐 Moodle URL: {config.moodle_url}")
    print(f"🔐 Token: {config.moodle_token_basic[:10]}...")

    # Create client with enhanced token (for creation permissions)
    token = config.moodle_token_enhanced or config.moodle_token_basic
    client = WorkingMoodleClient(config.moodle_url, token)

    try:
        print("\n📋 Teste Kurserstellung...")

        courses_data = [
            {
                "fullname": "MCP Test Course Fixed",
                "shortname": "mcpfixed",
                "categoryid": 1,
                "summary": "Test course created with fixed MCP implementation",
            }
        ]

        result = await client.create_courses(courses_data)

        if result and len(result) > 0:
            course = result[0]
            course_id = course.get("id")
            print(f"✅ Kurs erfolgreich erstellt!")
            print(f"   ID: {course_id}")
            print(f"   Short Name: {course.get('shortname')}")
            print(f"   URL: {config.moodle_url}/course/view.php?id={course_id}")

            # Teste auch das Abrufen des erstellten Kurses
            print(f"\n📚 Teste Kursabruf für ID {course_id}...")
            try:
                contents = await client.call_webservice(
                    "core_course_get_contents", courseid=course_id
                )
                print(f"✅ Kurs-Inhalte abgerufen: {len(contents)} Abschnitte")
            except Exception as e:
                print(f"⚠️ Konnte Kurs-Inhalte nicht abrufen: {e}")

        else:
            print("❌ Kurserstellung fehlgeschlagen: Kein Ergebnis")

    except Exception as e:
        print(f"❌ Fehler bei Kurserstellung: {e}")

    finally:
        await client.close()

    print("\n" + "=" * 40)
    print("🎯 Test abgeschlossen!")


if __name__ == "__main__":
    asyncio.run(test_course_creation())
