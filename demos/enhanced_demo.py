#!/usr/bin/env python3
"""
Enhanced demo with manual content creation to show Moodle transfer capabilities
"""

import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content_formatter import ContentFormatter
from models import ContentItem, CourseStructure


def create_demo_course_structure() -> CourseStructure:
    """Create a demo course structure manually"""

    # Create content items
    intro_item = ContentItem(
        type="topic",
        title="Python Einführung",
        content="""Python ist eine der beliebtesten Programmiersprachen der Welt und eignet sich hervorragend für Einsteiger. Mit ihrer klaren Syntax und vielseitigen Anwendungsmöglichkeiten ist Python ideal für Webentwicklung, Datenanalyse, Künstliche Intelligenz und vieles mehr.

Warum Python lernen?
- Einfache Syntax: Python Code ist leicht zu lesen und zu verstehen
- Vielseitigkeit: Von Webapps bis zu Machine Learning
- Große Community: Unzählige Bibliotheken und hilfreiche Ressourcen
- Karrieremöglichkeiten: Hohe Nachfrage in der Tech-Branche""",
        description="Grundlegende Einführung in Python",
        topic="Python Grundlagen",
    )

    code_item = ContentItem(
        type="code",
        title="Erstes Python Beispiel",
        content="""# Einfaches "Hallo Welt" Programm
def begruessung(name):
    return f"Hallo {name}! Willkommen bei Python!"

# Programm ausführen
benutzername = "Max"
nachricht = begruessung(benutzername)
print(nachricht)""",
        language="python",
        description="Erstes einfaches Python-Programm mit Funktionen",
        topic="Python Grundlagen",
    )

    variables_item = ContentItem(
        type="code",
        title="Variablen und Datentypen",
        content="""# Verschiedene Datentypen in Python
name = "Alice"           # String
alter = 25              # Integer
groesse = 1.75          # Float
ist_student = True      # Boolean

# Listen und Dictionaries
hobbies = ["Lesen", "Programmieren", "Sport"]
person = {
    "name": name,
    "alter": alter,
    "hobbies": hobbies
}

print(f"{name} ist {alter} Jahre alt")
print(f"Hobbies: {', '.join(hobbies)}")""",
        language="python",
        description="Grundlegende Datentypen und Strukturen in Python",
        topic="Python Grundlagen",
    )

    # Create section
    section = CourseStructure.Section(
        name="Python Grundlagen",
        description="Einführung in die Python-Programmierung mit praktischen Beispielen",
        items=[intro_item, code_item, variables_item],
    )

    return CourseStructure(sections=[section])


async def simulate_moodle_transfer(course_structure: CourseStructure, course_name: str):
    """Simulate what would happen when transferring to Moodle"""
    formatter = ContentFormatter()

    print("=" * 70)
    print("MOODLE TRANSFER SIMULATION")
    print("=" * 70)

    print(f"🎓 Creating Course: '{course_name}'")
    print(f"📚 Course will have {len(course_structure.sections)} section(s)")

    total_activities = 0

    for section_num, section in enumerate(course_structure.sections, 1):
        print(f"\n📖 Section {section_num}: '{section.name}'")
        print(f"   Description: {section.description}")
        print(f"   Items to create: {len(section.items)}")

        for item_num, item in enumerate(section.items, 1):
            if item.type == "code":
                print(f"\n   💻 Code Activity {section_num}.{item_num}: '{item.title}'")
                print(f"      Language: {item.language}")
                print(f"      Lines of code: {len(item.content.splitlines())}")
                print(f"      Will create:")
                print(f"        - 📄 Page with syntax-highlighted code")
                print(f"        - 📁 Downloadable {item.language} file")

                # Show formatted preview
                formatted_code = formatter.format_code_for_moodle(
                    code=item.content,
                    language=item.language,
                    title=item.title,
                    description=item.description or "",
                )
                print(f"      Content preview: {len(formatted_code)} characters of HTML")

                total_activities += 2  # Page + File

            elif item.type == "topic":
                print(f"\n   📝 Topic Activity {section_num}.{item_num}: '{item.title}'")
                print(f"      Content length: {len(item.content)} characters")
                print(f"      Will create:")
                print(f"        - 📄 Formatted page with rich content")

                # Show formatted preview
                formatted_topic = formatter.format_topic_for_moodle(
                    content=item.content, title=item.title, description=item.description or ""
                )
                print(f"      Content preview: {len(formatted_topic)} characters of HTML")

                total_activities += 1  # Page only

    print("\n" + "=" * 70)
    print("TRANSFER SUMMARY")
    print("=" * 70)
    print(f"✅ Course created: '{course_name}'")
    print(f"✅ {len(course_structure.sections)} section(s) created")
    print(f"✅ {total_activities} total activities created")

    code_count = sum(
        1 for section in course_structure.sections for item in section.items if item.type == "code"
    )
    topic_count = sum(
        1 for section in course_structure.sections for item in section.items if item.type == "topic"
    )

    print(f"   - {code_count} code examples (with downloadable files)")
    print(f"   - {topic_count} topic descriptions")
    print(f"   - All content formatted with HTML and syntax highlighting")
    print(f"   - Mobile-friendly responsive design")

    print(f"\n📍 Course URL would be: https://your-moodle-site.com/course/view.php?id=<course_id>")


async def main():
    print("🚀 MoodleClaude - Content Transfer Demo")
    print("Generierter Text wird für Moodle-Transfer vorbereitet...\n")

    # Create demo course structure
    course_structure = create_demo_course_structure()
    course_name = "Python Programmierung - Einführungskurs"

    # Simulate transfer
    await simulate_moodle_transfer(course_structure, course_name)

    print("\n" + "=" * 70)
    print("NÄCHSTE SCHRITTE")
    print("=" * 70)
    print("Um den Transfer tatsächlich durchzuführen:")
    print("1. Moodle-Credentials konfigurieren:")
    print("   export MOODLE_URL='https://your-moodle-site.com'")
    print("   export MOODLE_TOKEN='your-web-service-token'")
    print("2. MCP Server starten:")
    print("   python mcp_server.py")
    print("3. Mit Claude Code verbinden und Tool verwenden:")
    print("   create_course_from_chat(...)")


if __name__ == "__main__":
    asyncio.run(main())
