#!/usr/bin/env python3
"""
Enhanced Course Creation Demo with Sections and Content
Demonstrates the full capabilities of the MoodleClaude integration including:
- Creating courses with structured sections
- Adding content to sections
- Managing section visibility and restrictions
- Bulk operations on sections
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_moodle_claude import (
    EnhancedMoodleAPI,
    FileUploadConfig,
    MoodleClaudeIntegration,
    SectionConfig,
)


class CourseStructureDemo:
    """Demo class for creating structured courses with sections"""

    def __init__(self, moodle_url: str, token: str):
        self.integration = MoodleClaudeIntegration(moodle_url, token)
        self.api = self.integration.api

    async def create_python_course_with_sections(self) -> dict:
        """Create a comprehensive Python course with structured sections"""

        print("🚀 Creating comprehensive Python course with sections...")

        # Course details
        course_data = {
            "fullname": "Python Programming - Complete Course",
            "shortname": f"python_complete_{self._get_timestamp()}",
            "category": 1,
            "summary": """
            <h3>Willkommen zum Python Komplettkurs!</h3>
            <p>Dieser Kurs führt Sie systematisch durch alle wichtigen Aspekte der Python-Programmierung.</p>
            <ul>
                <li>📚 Strukturierte Lernmodule</li>
                <li>💻 Praktische Übungen</li>
                <li>🔧 Realistische Projekte</li>
                <li>📈 Aufbauende Schwierigkeitsgrade</li>
            </ul>
            <p><strong>Zielgruppe:</strong> Programmier-Anfänger bis Fortgeschrittene</p>
            """,
            "format": "topics",
        }

        # Create course
        course_response = await self.api._make_request(
            "core_course_create_courses", {"courses": [course_data]}
        )

        course_id = course_response[0]["id"]
        print(f"✅ Course created with ID: {course_id}")

        # Define section structure
        sections = [
            {
                "config": SectionConfig(
                    name="🎯 Kursübersicht und Ziele",
                    summary="""
                    <h4>Willkommen!</h4>
                    <p>In diesem Abschnitt erhalten Sie:</p>
                    <ul>
                        <li>Einen Überblick über den Kursaufbau</li>
                        <li>Lernziele und Erwartungen</li>
                        <li>Einrichtung der Entwicklungsumgebung</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content_type": "intro",
            },
            {
                "config": SectionConfig(
                    name="📝 Python Grundlagen",
                    summary="""
                    <p>Erlernen Sie die Basis der Python-Programmierung:</p>
                    <ul>
                        <li>Syntax und Datentypen</li>
                        <li>Variablen und Operatoren</li>
                        <li>Ein- und Ausgabe</li>
                        <li>Erste Programme schreiben</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content_type": "fundamentals",
            },
            {
                "config": SectionConfig(
                    name="🔧 Kontrollstrukturen",
                    summary="""
                    <p>Programmlogik und Entscheidungen:</p>
                    <ul>
                        <li>If-Else Anweisungen</li>
                        <li>For- und While-Schleifen</li>
                        <li>Break und Continue</li>
                        <li>Verschachtelte Strukturen</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content_type": "control",
            },
            {
                "config": SectionConfig(
                    name="📊 Datenstrukturen",
                    summary="""
                    <p>Arbeiten mit komplexen Datentypen:</p>
                    <ul>
                        <li>Listen und Tupel</li>
                        <li>Dictionaries und Sets</li>
                        <li>List Comprehensions</li>
                        <li>Datenmanipulation</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content_type": "data_structures",
            },
            {
                "config": SectionConfig(
                    name="⚙️ Funktionen und Module",
                    summary="""
                    <p>Code-Organisation und Wiederverwendung:</p>
                    <ul>
                        <li>Funktionen definieren und aufrufen</li>
                        <li>Parameter und Rückgabewerte</li>
                        <li>Module und Packages</li>
                        <li>Bibliotheken verwenden</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content_type": "functions",
            },
            {
                "config": SectionConfig(
                    name="🎯 Praktische Projekte",
                    summary="""
                    <p>Anwendung des Gelernten in realen Projekten:</p>
                    <ul>
                        <li>Mini-Spiele entwickeln</li>
                        <li>Datenanalyse-Tools</li>
                        <li>Web-Scraping</li>
                        <li>Automatisierungsscripts</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content_type": "projects",
            },
            {
                "config": SectionConfig(
                    name="🔬 Erweiterte Themen",
                    summary="""
                    <p>Für Fortgeschrittene (optional):</p>
                    <ul>
                        <li>Objektorientierte Programmierung</li>
                        <li>Exception Handling</li>
                        <li>File I/O und Datenbanken</li>
                        <li>APIs und Webservices</li>
                    </ul>
                    """,
                    visible=False,  # Initially hidden
                    availability_conditions={
                        "op": "&",
                        "c": [{"type": "completion", "cm": "previous_activities"}],
                        "showc": [True],
                    },
                ),
                "content_type": "advanced",
            },
            {
                "config": SectionConfig(
                    name="🏆 Abschlussprojekt und Zertifikat",
                    summary="""
                    <p>Zeigen Sie Ihr erworbenes Wissen:</p>
                    <ul>
                        <li>Individuelles Abschlussprojekt</li>
                        <li>Code Review und Feedback</li>
                        <li>Präsentation der Ergebnisse</li>
                        <li>Kurszertifikat</li>
                    </ul>
                    """,
                    visible=False,  # Hidden until prerequisites met
                    availability_conditions={
                        "op": "&",
                        "c": [{"type": "completion", "cm": "all_previous_sections"}],
                        "showc": [True],
                    },
                ),
                "content_type": "final",
            },
        ]

        # Create all sections
        created_sections = []
        for i, section_data in enumerate(sections, 1):
            print(f"📝 Creating section {i}: {section_data['config'].name}")

            try:
                section_result = await self.api.create_course_section(
                    course_id, section_data["config"]
                )
                created_sections.append(
                    {
                        "section_id": section_result.get("id"),
                        "name": section_data["config"].name,
                        "content_type": section_data["content_type"],
                    }
                )
                print(f"   ✅ Section created with ID: {section_result.get('id')}")

            except Exception as e:
                print(f"   ❌ Failed to create section: {e}")
                # Continue with other sections
                continue

        return {
            "course_id": course_id,
            "course_url": f"{self.api.base_url}/course/view.php?id={course_id}",
            "sections": created_sections,
            "summary": {
                "total_sections": len(created_sections),
                "visible_sections": len([s for s in sections if s["config"].visible]),
                "restricted_sections": len(
                    [s for s in sections if s["config"].availability_conditions]
                ),
            },
        }

    async def add_sample_content_to_sections(self, course_id: int, sections: list):
        """Add sample content to the created sections"""

        print("\n📚 Adding sample content to sections...")

        # Sample content for different section types
        content_templates = {
            "intro": [
                {
                    "type": "text",
                    "title": "Kursübersicht",
                    "content": """
                    <h3>🎓 Herzlich willkommen zum Python Komplettkurs!</h3>
                    <p>Sie sind dabei, eine der wertvollsten Fähigkeiten des 21. Jahrhunderts zu erlernen.</p>
                    <h4>Was Sie in diesem Kurs lernen werden:</h4>
                    <ol>
                        <li><strong>Python Grundlagen</strong> - Syntax, Variablen, Datentypen</li>
                        <li><strong>Programmlogik</strong> - Entscheidungen und Wiederholungen</li>
                        <li><strong>Datenverarbeitung</strong> - Listen, Dictionaries, etc.</li>
                        <li><strong>Code-Organisation</strong> - Funktionen und Module</li>
                        <li><strong>Praktische Anwendung</strong> - Echte Projekte entwickeln</li>
                    </ol>
                    """,
                }
            ],
            "fundamentals": [
                {
                    "type": "text",
                    "title": "Python Grundlagen - Einführung",
                    "content": """
                    <h3>🐍 Willkommen in der Welt von Python!</h3>
                    <p><strong>Python</strong> ist eine der beliebtesten Programmiersprachen weltweit.</p>
                    
                    <h4>Warum Python?</h4>
                    <ul>
                        <li>✅ <strong>Einfach zu lernen</strong> - Klare, lesbare Syntax</li>
                        <li>🔧 <strong>Vielseitig</strong> - Web, Data Science, AI, Automation</li>
                        <li>🌍 <strong>Große Community</strong> - Millionen von Entwicklern</li>
                        <li>📚 <strong>Viele Bibliotheken</strong> - Für fast jeden Anwendungsfall</li>
                    </ul>
                    
                    <h4>Ihr erstes Python-Programm:</h4>
                    <pre><code>print("Hallo Welt!")
print("Ich lerne Python!")

# Das war's - Sie haben gerade programmiert! 🎉</code></pre>
                    """,
                }
            ],
            "projects": [
                {
                    "type": "text",
                    "title": "Projektübersicht",
                    "content": """
                    <h3>🎯 Praktische Projekte</h3>
                    <p>Theorie ist wichtig, aber Programmieren lernt man durch Programmieren!</p>
                    
                    <h4>Unsere Projekt-Roadmap:</h4>
                    <div style="background: #f0f8ff; padding: 15px; border-radius: 5px;">
                        <h5>🎮 Projekt 1: Zahlenraten-Spiel</h5>
                        <p>Entwickeln Sie ein interaktives Spiel mit Zufallszahlen und Benutzereingaben.</p>
                        <p><strong>Skills:</strong> Variablen, Schleifen, If-Statements, Input/Output</p>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 10px;">
                        <h5>📊 Projekt 2: Datenanalyse-Tool</h5>
                        <p>Analysieren Sie CSV-Dateien und erstellen Sie automatische Reports.</p>
                        <p><strong>Skills:</strong> File I/O, Listen, Dictionaries, String-Manipulation</p>
                    </div>
                    """,
                }
            ],
        }

        added_content = []

        for section in sections:
            content_type = section.get("content_type", "intro")
            section_id = section.get("section_id")

            if not section_id or content_type not in content_templates:
                continue

            print(f"   📝 Adding content to: {section['name']}")

            # Add text content
            for content_item in content_templates[content_type]:
                try:
                    # Create a text and media area (page resource)
                    result = await self._create_page_resource(
                        course_id,
                        section_id,
                        content_item["title"],
                        content_item["content"],
                    )

                    added_content.append(
                        {
                            "section": section["name"],
                            "content": content_item["title"],
                            "result": result,
                        }
                    )

                    print(f"      ✅ Added: {content_item['title']}")

                except Exception as e:
                    print(f"      ❌ Failed to add content: {e}")

        return added_content

    async def _create_page_resource(
        self, course_id: int, section_num: int, name: str, content: str
    ):
        """Create a page resource with content"""

        try:
            # Get site info for context
            site_info = await self.api._make_request(
                "core_webservice_get_site_info", {}
            )

            # Create page module
            module_data = {
                "courseid": course_id,
                "name": name,
                "modname": "page",
                "section": section_num,
                "instance": 0,
                "visible": 1,
                "page": {
                    "name": name,
                    "intro": f"<p>{name}</p>",
                    "content": content,
                    "contentformat": 1,
                    "printheading": 1,
                    "printintro": 0,
                },
            }

            result = await self.api._make_request(
                "core_course_create_modules", {"modules": [module_data]}
            )

            return result[0] if result else None

        except Exception as e:
            # Fallback: Try to create as label (text block)
            return await self._create_label_resource(
                course_id, section_num, name, content
            )

    async def _create_label_resource(
        self, course_id: int, section_num: int, name: str, content: str
    ):
        """Fallback: Create a label (text block) resource"""

        module_data = {
            "courseid": course_id,
            "name": name,
            "modname": "label",
            "section": section_num,
            "instance": 0,
            "visible": 1,
            "label": {"name": name, "intro": content, "introformat": 1},
        }

        result = await self.api._make_request(
            "core_course_create_modules", {"modules": [module_data]}
        )

        return result[0] if result else None

    async def demonstrate_section_management(self, course_id: int, sections: list):
        """Demonstrate advanced section management features"""

        print("\n🔧 Demonstrating section management features...")

        if len(sections) < 3:
            print("❌ Not enough sections for management demo")
            return

        try:
            # 1. Update a section
            section_to_update = sections[1]  # Second section
            print(f"📝 Updating section: {section_to_update['name']}")

            await self.api.update_section(
                section_to_update["section_id"],
                {
                    "name": f"✨ {section_to_update['name']} (Updated!)",
                    "summary": "<p><strong>This section has been updated!</strong></p>",
                },
            )
            print("   ✅ Section updated successfully")

            # 2. Demonstrate bulk operations
            print(f"🔄 Performing bulk operations on sections...")

            bulk_operations = [
                {
                    "operation": "update",
                    "sectionid": sections[0]["section_id"],
                    "data": {
                        "summary": "<p>🆕 <strong>Updated via bulk operation!</strong></p>"
                    },
                }
            ]

            # Note: This might not work with all Moodle versions
            try:
                result = await self.api.bulk_section_operations(bulk_operations)
                print("   ✅ Bulk operations completed")
            except Exception as e:
                print(f"   ⚠️ Bulk operations not supported: {e}")

            # 3. Move sections (if supported)
            print(f"🔀 Testing section movement...")
            try:
                move_operations = [
                    {"sectionid": sections[-1]["section_id"], "position": 2}
                ]
                result = await self.api.move_sections(move_operations)
                print("   ✅ Section moved successfully")
            except Exception as e:
                print(f"   ⚠️ Section movement not supported: {e}")

        except Exception as e:
            print(f"❌ Section management demo failed: {e}")

    def _get_timestamp(self) -> str:
        """Get current timestamp for unique naming"""
        import time

        return str(int(time.time()))

    async def run_complete_demo(self):
        """Run the complete course creation demo"""

        print("=" * 60)
        print("🎓 MOODLE COURSE CREATION DEMO WITH SECTIONS")
        print("=" * 60)

        try:
            # 1. Create course with sections
            result = await self.create_python_course_with_sections()

            print(f"\n✅ Course creation completed!")
            print(f"   📋 Course ID: {result['course_id']}")
            print(f"   🌐 Course URL: {result['course_url']}")
            print(f"   📊 Sections created: {result['summary']['total_sections']}")
            print(f"   👁️ Visible sections: {result['summary']['visible_sections']}")
            print(
                f"   🔒 Restricted sections: {result['summary']['restricted_sections']}"
            )

            # 2. Add sample content
            if result["sections"]:
                content_result = await self.add_sample_content_to_sections(
                    result["course_id"], result["sections"]
                )
                print(f"\n📚 Content added to {len(content_result)} activities")

            # 3. Demonstrate section management
            if result["sections"]:
                await self.demonstrate_section_management(
                    result["course_id"], result["sections"]
                )

            # 4. Final summary
            print("\n" + "=" * 60)
            print("🎉 DEMO COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"🌐 Visit your course: {result['course_url']}")
            print("👩‍🏫 Login as admin to see all features")
            print("🔧 Check the course structure and content")
            print("📱 Test section visibility and restrictions")

            return result

        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            import traceback

            traceback.print_exc()
            return None


async def main():
    """Main function to run the demo"""

    # Get environment variables
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_TOKEN", "your-moodle-token-here")

    print(f"🔗 Connecting to: {moodle_url}")
    print(f"🔑 Using token: {moodle_token[:10]}...")

    # Create demo instance
    demo = CourseStructureDemo(moodle_url, moodle_token)

    # Run complete demo
    result = await demo.run_complete_demo()

    if result:
        print(f"\n🎯 Quick access link:")
        print(f"   {result['course_url']}")


if __name__ == "__main__":
    # Set default environment variables if not provided
    if not os.getenv("MOODLE_TOKEN"):
        os.environ["MOODLE_TOKEN"] = "your-moodle-token-here"

    if not os.getenv("MOODLE_URL"):
        os.environ["MOODLE_URL"] = "http://localhost:8080"

    print("🐍 MoodleClaude Course Creation Demo")
    print("📋 This demo will create a complete course with sections and content")
    print("⚡ Starting in 3 seconds...\n")

    import time

    time.sleep(1)

    # Run the demo
    asyncio.run(main())
