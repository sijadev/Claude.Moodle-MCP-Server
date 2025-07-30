#!/usr/bin/env python3
"""
Test content length limits to identify where sections become empty
"""

import asyncio
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from config.dual_token_config import DualTokenConfig
from src.clients.moodle_client_enhanced import EnhancedMoodleClient
from src.clients.moodle_client import MoodleClient

async def test_content_limits():
    """Test different content lengths to find the breaking point"""
    
    print("🔍 Testing Content Length Limits")
    print("=" * 60)
    
    config = DualTokenConfig.from_env()
    
    # Create test course
    basic_client = MoodleClient(
        base_url=config.moodle_url,
        token=config.get_basic_token()
    )
    
    async with basic_client as basic:
        course_id = await basic.create_course(
            name="Content Limit Test Course",
            description="Testing content length limits",
            category_id=1
        )
    
    print(f"✅ Test course created with ID: {course_id}")
    
    # Test different content sizes
    plugin_client = EnhancedMoodleClient(
        base_url=config.moodle_url,
        token=config.get_plugin_token()
    )
    
    async with plugin_client as client:
        # Test sizes: 1KB, 5KB, 10KB, 20KB, 50KB
        test_sizes = [1024, 5*1024, 10*1024, 20*1024, 50*1024]
        
        for i, size in enumerate(test_sizes, 1):
            print(f"\n{i}️⃣ Testing {size//1024}KB content...")
            
            # Generate content of specific size
            base_content = "This is a test content line that will be repeated to reach the target size. "
            repeat_count = size // len(base_content) + 1
            large_content = (base_content * repeat_count)[:size]
            
            print(f"   Content length: {len(large_content)} characters")
            
            try:
                sections_data = [{
                    'name': f'Test Section {size//1024}KB',
                    'summary': f'Section with {size//1024}KB of content',
                    'activities': [{
                        'type': 'page',
                        'name': f'Large Content Page {size//1024}KB',
                        'content': large_content,
                        'filename': ''
                    }]
                }]
                
                result = await client.create_course_structure(course_id, sections_data)
                
                if result.get('success'):
                    activities = result.get('sections', [{}])[0].get('activities', [])
                    if activities and activities[0].get('success'):
                        print(f"   ✅ SUCCESS: {size//1024}KB content stored successfully")
                    else:
                        print(f"   ⚠️ PARTIAL: Section created but activity failed")
                        print(f"      Activity result: {activities}")
                else:
                    print(f"   ❌ FAILED: {result.get('message', 'Unknown error')}")
                    break
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {e}")
                break
        
        # Test the parameter flattening with large content
        print(f"\n🔬 Testing parameter structure with large content...")
        
        large_sections = []
        for i in range(5):  # Multiple sections
            large_sections.append({
                'name': f'Section {i+1}',
                'summary': f'Summary for section {i+1}',
                'activities': [
                    {
                        'type': 'page',
                        'name': f'Page {i+1}',
                        'content': 'A' * 2048,  # 2KB per page
                        'filename': ''
                    },
                    {
                        'type': 'file', 
                        'name': f'File {i+1}',
                        'content': 'print("Hello world")' * 100,  # Code content
                        'filename': f'test_{i+1}.py'
                    }
                ]
            })
        
        # Check total size
        import json
        total_size = len(json.dumps(large_sections))
        print(f"   Total parameter size: {total_size} bytes ({total_size//1024}KB)")
        
        try:
            result = await client.create_course_structure(course_id, large_sections)
            if result.get('success'):
                print(f"   ✅ SUCCESS: Multiple sections with {total_size//1024}KB total data")
            else:
                print(f"   ❌ FAILED: {result.get('message')}")
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(test_content_limits())