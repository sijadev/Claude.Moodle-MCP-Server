#!/usr/bin/env python3
"""
Demo script to show how content would be transferred to Moodle
"""

import asyncio
from content_parser import ChatContentParser
from content_formatter import ContentFormatter
from models import CourseStructure


def organize_content(parsed_content) -> CourseStructure:
    """Organize parsed content into course structure"""
    sections = []
    
    # Group content by topics
    topic_groups = {}
    
    for item in parsed_content.items:
        if item.topic:
            if item.topic not in topic_groups:
                topic_groups[item.topic] = []
            topic_groups[item.topic].append(item)
        else:
            # Create a general section for items without specific topics
            if "Python Einführung" not in topic_groups:
                topic_groups["Python Einführung"] = []
            topic_groups["Python Einführung"].append(item)
    
    # Create sections from topic groups
    for topic_name, items in topic_groups.items():
        section = CourseStructure.Section(
            name=topic_name,
            description=f"Content related to {topic_name}",
            items=items,
        )
        sections.append(section)
    
    return CourseStructure(sections=sections)


async def main():
    # Beispieltext für Moodle
    chat_content = """
    ## Einführung in die Programmierung mit Python

    Python ist eine der beliebtesten Programmiersprachen der Welt und eignet sich hervorragend für Einsteiger. Mit ihrer klaren Syntax und vielseitigen Anwendungsmöglichkeiten ist Python ideal für Webentwicklung, Datenanalyse, Künstliche Intelligenz und vieles mehr.

    ### Warum Python lernen?
    - **Einfache Syntax**: Python Code ist leicht zu lesen und zu verstehen
    - **Vielseitigkeit**: Von Webapps bis zu Machine Learning
    - **Große Community**: Unzählige Bibliotheken und hilfreiche Ressourcen
    - **Karrieremöglichkeiten**: Hohe Nachfrage in der Tech-Branche

    ### Erstes Beispiel
    ```python
    # Einfaches "Hallo Welt" Programm
    def begruessung(name):
        return f"Hallo {name}! Willkommen bei Python!"

    # Programm ausführen
    benutzername = "Max"
    nachricht = begruessung(benutzername)
    print(nachricht)
    ```

    Dieses Beispiel zeigt die Grundlagen von Python-Funktionen und String-Formatting.
    """
    
    # Parse content
    parser = ChatContentParser()
    parsed_content = parser.parse_chat(chat_content)
    
    # Organize into course structure
    course_structure = organize_content(parsed_content)
    
    # Format content for display
    formatter = ContentFormatter()
    
    print("=" * 60)
    print("MOODLE CONTENT TRANSFER DEMO")
    print("=" * 60)
    print(f"\nParsed Content Summary:")
    print(f"- Total items found: {len(parsed_content.items)}")
    print(f"- Code examples: {len([item for item in parsed_content.items if item.type == 'code'])}")
    print(f"- Topic descriptions: {len([item for item in parsed_content.items if item.type == 'topic'])}")
    
    print(f"\nCourse Structure:")
    print(f"- Sections to create: {len(course_structure.sections)}")
    
    for i, section in enumerate(course_structure.sections, 1):
        print(f"\n{i}. Section: '{section.name}'")
        print(f"   Description: {section.description}")
        print(f"   Items: {len(section.items)}")
        
        for j, item in enumerate(section.items, 1):
            if item.type == "code":
                print(f"   {i}.{j} 💻 Code: '{item.title}'")
                print(f"        Language: {item.language or 'Unknown'}")
                print(f"        Lines: {len(item.content.splitlines())}")
                
                # Show formatted content preview
                formatted = formatter.format_code_for_moodle(
                    code=item.content,
                    language=item.language,
                    title=item.title,
                    description=item.description or ""
                )
                print(f"        Preview (first 100 chars): {formatted[:100]}...")
                
            elif item.type == "topic":
                print(f"   {i}.{j} 📝 Topic: '{item.title}'")
                print(f"        Content length: {len(item.content)} characters")
                
                # Show formatted content preview
                formatted = formatter.format_topic_for_moodle(
                    content=item.content,
                    title=item.title,
                    description=item.description or ""
                )
                print(f"        Preview (first 100 chars): {formatted[:100]}...")
    
    print("\n" + "=" * 60)
    print("MOODLE TRANSFER WOULD CREATE:")
    print("=" * 60)
    print(f"✅ 1 New Course: 'Python Einführung'")
    print(f"✅ {len(course_structure.sections)} Section(s)")
    
    total_activities = 0
    for section in course_structure.sections:
        for item in section.items:
            if item.type == "code":
                total_activities += 2  # File + Page activity
            else:
                total_activities += 1  # Page activity
    
    print(f"✅ {total_activities} Activity/Activities")
    print(f"   - Pages with formatted content")
    print(f"   - Downloadable code files")
    print(f"   - Syntax highlighted code displays")
    
    print("\nHinweis: Um tatsächlich nach Moodle zu übertragen, setze diese Umgebungsvariablen:")
    print("export MOODLE_URL='https://your-moodle-site.com'")
    print("export MOODLE_TOKEN='your-web-service-token'")


if __name__ == "__main__":
    asyncio.run(main())