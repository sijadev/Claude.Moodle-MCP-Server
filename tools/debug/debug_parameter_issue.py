#!/usr/bin/env python3
"""
Debug the specific parameter issue causing validation failures
"""

import asyncio
import json
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from config.dual_token_config import DualTokenConfig
from src.clients.moodle_client_enhanced import EnhancedMoodleClient
from src.core.content_parser import ChatContentParser
from src.core.content_formatter import ContentFormatter

async def debug_parameter_issue():
    """Debug the exact parameter that's causing validation issues"""
    
    print("🔍 Debugging Parameter Validation Issue")
    print("=" * 60)
    
    config = DualTokenConfig.from_env()
    
    # Test with the simplest possible valid content
    simple_test_content = """
    ## Simple Test
    
    This is a simple test topic for debugging.
    
    ```python
    print("Hello World!")
    ```
    
    This should work without issues.
    """
    
    # Parse the content
    parser = ChatContentParser()
    formatter = ContentFormatter()
    
    parsed_content = parser.parse_chat(simple_test_content)
    print(f"📊 Parsed {len(parsed_content.items)} items")
    
    # Create the sections data structure
    sections_data = []
    
    for item in parsed_content.items:
        if item.topic:
            # Find or create section for this topic
            section = None
            for s in sections_data:
                if s['name'] == item.topic:
                    section = s
                    break
            
            if not section:
                section = {
                    'name': item.topic,
                    'summary': f'Content related to {item.topic}',
                    'activities': []
                }
                sections_data.append(section)
            
            if item.type == "code":
                # Add formatted code content
                formatted_content = formatter.format_code_for_moodle(
                    code=item.content,
                    language=item.language,
                    title=item.title,
                    description=item.description or ""
                )
                
                print(f"\n📝 Code content preview (first 200 chars):")
                print(f"   Title: {item.title}")
                print(f"   Language: {item.language}")
                print(f"   Content: {formatted_content[:200]}...")
                print(f"   Length: {len(formatted_content)} characters")
                
                # Check for problematic characters
                problematic_chars = []
                for char in formatted_content:
                    if ord(char) > 127:  # Non-ASCII characters
                        if char not in [c[0] for c in problematic_chars]:
                            problematic_chars.append((char, ord(char)))
                
                if problematic_chars:
                    print(f"   ⚠️ Non-ASCII characters found: {problematic_chars[:5]}")
                
                section['activities'].extend([
                    {
                        'type': 'file',
                        'name': f"{item.title} - Code File",
                        'content': item.content,  # Raw content for file
                        'filename': f"{item.title.lower().replace(' ', '_')}.{item.language or 'txt'}"
                    },
                    {
                        'type': 'page',
                        'name': item.title,
                        'content': formatted_content,
                        'filename': ''
                    }
                ])
            elif item.type == "topic":
                formatted_content = formatter.format_topic_for_moodle(
                    content=item.content,
                    title=item.title,
                    description=item.description or ""
                )
                
                print(f"\n📝 Topic content preview:")
                print(f"   Title: {item.title}")
                print(f"   Content: {formatted_content[:200]}...")
                print(f"   Length: {len(formatted_content)} characters")
                
                section['activities'].append({
                    'type': 'page',
                    'name': item.title,
                    'content': formatted_content,
                    'filename': ''
                })
    
    print(f"\n🏗️ Final sections data structure:")
    print(f"   Sections: {len(sections_data)}")
    for i, section in enumerate(sections_data):
        print(f"   Section {i+1}: '{section['name']}' with {len(section['activities'])} activities")
        for j, activity in enumerate(section['activities']):
            print(f"      Activity {j+1}: {activity['type']} - '{activity['name']}'")
            print(f"         Content length: {len(activity['content'])}")
            print(f"         Filename: '{activity['filename']}'")
    
    # Test parameter flattening
    plugin_client = EnhancedMoodleClient(
        base_url=config.moodle_url,
        token=config.get_plugin_token()
    )
    
    async with plugin_client as client:
        print(f"\n🔬 Testing parameter flattening...")
        
        test_params = {
            'courseid': 12,  # Use existing course
            'sections': sections_data
        }
        
        flattened = client._flatten_params(test_params)
        print(f"   Flattened parameters ({len(flattened)} keys):")
        
        # Show first few parameters
        for i, (key, value) in enumerate(list(flattened.items())[:10]):
            if isinstance(value, str) and len(value) > 100:
                preview = value[:100] + "..."
            else:
                preview = str(value)
            print(f"      {key}: {preview}")
        
        if len(flattened) > 10:
            print(f"      ... and {len(flattened) - 10} more parameters")
        
        # Check for specific parameter issues
        problematic_params = []
        for key, value in flattened.items():
            if isinstance(value, str):
                # Check for empty values
                if value == "":
                    problematic_params.append((key, "Empty string"))
                # Check for very long values
                elif len(value) > 32000:  # Common API limit
                    problematic_params.append((key, f"Too long ({len(value)} chars)"))
                # Check for null bytes or other problematic characters
                elif '\x00' in value:
                    problematic_params.append((key, "Contains null bytes"))
        
        if problematic_params:
            print(f"\n⚠️ Potentially problematic parameters:")
            for key, issue in problematic_params:
                print(f"      {key}: {issue}")
        else:
            print(f"\n✅ No obvious parameter issues detected")
        
        # Try the API call with detailed error handling
        print(f"\n🧪 Testing API call...")
        try:
            result = await client.create_course_structure(12, sections_data)
            print(f"✅ Success: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")
            
            # Try with even simpler data
            print(f"\n🔧 Trying with minimal data...")
            minimal_data = [{
                'name': 'Test Section',
                'summary': 'Simple test',
                'activities': [{
                    'type': 'page',
                    'name': 'Simple Page',
                    'content': '<p>Simple content</p>',
                    'filename': ''
                }]
            }]
            
            try:
                result = await client.create_course_structure(12, minimal_data)
                print(f"✅ Minimal data worked: {result}")
            except Exception as e2:
                print(f"❌ Even minimal data failed: {e2}")

if __name__ == "__main__":
    asyncio.run(debug_parameter_issue())