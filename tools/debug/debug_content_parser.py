#!/usr/bin/env python3
"""
Debug the content parser to see why it's not finding content
"""

from content_parser import ChatContentParser


def test_content_parser():
    parser = ChatContentParser()

    sample_chat = """
    User: Can you explain Python functions and show me some examples?
    
    Assistant: I'd be happy to explain Python functions! Here's what you need to know:
    
    ## What are Python Functions?
    
    Functions are reusable blocks of code that perform specific tasks.
    
    ```python
    def greet(name):
        return f"Hello, {name}!"
    
    message = greet("World")
    print(message)
    ```
    
    Functions help organize your code and make it reusable.
    """

    print("🔍 Testing Content Parser")
    print("=" * 50)

    # Parse the content
    parsed = parser.parse_chat(sample_chat)

    print(f"Total items found: {len(parsed.items)}")
    print(f"Metadata: {parsed.metadata}")

    if parsed.items:
        for i, item in enumerate(parsed.items):
            print(f"\nItem {i+1}:")
            print(f"  Type: {item.type}")
            print(f"  Title: {item.title}")
            print(f"  Language: {getattr(item, 'language', 'N/A')}")
            print(f"  Content preview: {item.content[:100]}...")
    else:
        print("\n⚠️  No items found!")
        print("This might explain why courses appear empty.")

        # Debug the parser
        print(f"\n🔧 Parser configuration:")
        print(f"  Language patterns: {len(parser.language_patterns)} languages")
        print(f"  Topic keywords: {len(parser.topic_keywords)} keywords")
        print(
            f"  Code block pattern: {parser.code_block_pattern.pattern if parser.code_block_pattern else 'None'}"
        )

        # Test pattern matching
        print(f"\n🧪 Testing pattern matching:")
        import re

        if parser.code_block_pattern:
            matches = parser.code_block_pattern.findall(sample_chat)
            print(f"  Code block matches: {len(matches)}")
            for match in matches:
                print(f"    - Language: {match[0] if match else 'None'}")
                print(
                    f"    - Code preview: {match[1][:50]}..."
                    if match and len(match) > 1
                    else "    - No code"
                )


if __name__ == "__main__":
    test_content_parser()
