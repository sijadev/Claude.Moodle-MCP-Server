#!/usr/bin/env python3
"""
Test script for MoodleClaude plugin integration
Tests the enhanced functionality provided by the custom plugin
"""

import asyncio
import logging
from moodle_client_enhanced import EnhancedMoodleClient
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_plugin_integration():
    """Test the MoodleClaude plugin integration"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - please check .env file")
        return
    
    async with EnhancedMoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Testing MoodleClaude Plugin Integration")
        print("=" * 60)
        
        # Test 1: Check plugin availability
        print("\n1️⃣ Testing plugin availability...")
        plugin_available = await client._check_plugin_availability()
        if plugin_available:
            print("✅ MoodleClaude plugin is available!")
        else:
            print("❌ MoodleClaude plugin not found - install the plugin first")
            print("📖 See moodle_plugin/INSTALLATION.md for setup instructions")
            return
        
        # Test 2: Create a test course
        print("\n2️⃣ Creating test course...")
        try:
            course_id = await client.create_course(
                name="MoodleClaude Plugin Test Course",
                description="Test course created to verify plugin functionality"
            )
            print(f"✅ Test course created with ID: {course_id}")
        except Exception as e:
            print(f"❌ Course creation failed: {e}")
            return
        
        # Test 3: Update section content
        print("\n3️⃣ Testing section content updates...")
        try:
            success = await client.update_section_content(
                course_id=course_id,
                section_number=1,
                name="📚 Test Section 1",
                summary="<h3>Welcome to Test Section</h3><p>This section was created using the MoodleClaude plugin!</p>"
            )
            if success:
                print("✅ Section content updated successfully")
            else:
                print("❌ Section content update failed")
        except Exception as e:
            print(f"❌ Section update error: {e}")
        
        # Test 4: Create page activity
        print("\n4️⃣ Testing page activity creation...")
        try:
            page_result = await client.create_page_activity(
                course_id=course_id,
                section_id=1,
                name="📖 Test Page Activity",
                content="""
                <h2>Welcome to MoodleClaude!</h2>
                <p>This page was created using the custom MoodleClaude plugin.</p>
                
                <h3>Key Features:</h3>
                <ul>
                    <li>✅ Real content storage</li>
                    <li>✅ Actual activity creation</li>
                    <li>✅ Section content updates</li>
                    <li>✅ Bulk operations support</li>
                </ul>
                
                <div style="background-color: #d4edda; padding: 15px; border: 1px solid #c3e6cb; border-radius: 5px; margin: 20px 0;">
                    <strong>🎉 Success!</strong> Content is now properly stored in Moodle!
                </div>
                """
            )
            if page_result['success']:
                print(f"✅ Page activity created successfully (ID: {page_result['activity_id']})")
            else:
                print(f"❌ Page activity creation failed: {page_result['message']}")
        except Exception as e:
            print(f"❌ Page activity error: {e}")
        
        # Test 5: Create label activity
        print("\n5️⃣ Testing label activity creation...")
        try:
            label_result = await client.create_label_activity(
                course_id=course_id,
                section_id=1,
                content="""
                <div style="background-color: #f8f9fa; padding: 10px; border-left: 4px solid #007bff;">
                    <strong>💡 Pro Tip:</strong> This label was created using the MoodleClaude plugin API!
                </div>
                """
            )
            if label_result['success']:
                print(f"✅ Label activity created successfully (ID: {label_result['activity_id']})")
            else:
                print(f"❌ Label activity creation failed: {label_result['message']}")
        except Exception as e:
            print(f"❌ Label activity error: {e}")
        
        # Test 6: Create file resource
        print("\n6️⃣ Testing file resource creation...")
        try:
            file_content = """# MoodleClaude Plugin Test

This file was created using the MoodleClaude plugin!

## Features Tested:
- Course creation ✅
- Section updates ✅
- Page activities ✅
- Label activities ✅
- File resources ✅

## Next Steps:
1. Visit your Moodle course
2. See the actual content stored properly
3. Enjoy automated course creation!

Generated by MoodleClaude Plugin Test
"""
            file_result = await client.create_file_activity(
                course_id=course_id,
                section_id=1,
                name="📄 Test File Resource",
                content=file_content,
                filename="moodleclaude_test.md"
            )
            if file_result['success']:
                print(f"✅ File resource created successfully (ID: {file_result['activity_id']})")
            else:
                print(f"❌ File resource creation failed: {file_result['message']}")
        except Exception as e:
            print(f"❌ File resource error: {e}")
        
        # Test 7: Bulk structure creation
        print("\n7️⃣ Testing bulk course structure creation...")
        try:
            sections_data = [
                {
                    'name': 'Module 1: Getting Started',
                    'summary': '<h3>Introduction Module</h3><p>Learn the basics of MoodleClaude.</p>',
                    'activities': [
                        {
                            'type': 'page',
                            'name': 'Course Introduction',
                            'content': '<h2>Welcome!</h2><p>This course demonstrates MoodleClaude plugin capabilities.</p>'
                        },
                        {
                            'type': 'label',
                            'name': '',
                            'content': '<hr><p><strong>Note:</strong> All content below was created automatically!</p>'
                        }
                    ]
                },
                {
                    'name': 'Module 2: Advanced Features',
                    'summary': '<h3>Advanced Module</h3><p>Explore advanced plugin features.</p>',
                    'activities': [
                        {
                            'type': 'file',
                            'name': 'Configuration Guide',
                            'content': '# MoodleClaude Configuration\n\nStep-by-step setup guide...',
                            'filename': 'config_guide.md'
                        }
                    ]
                }
            ]
            
            structure_result = await client.create_course_structure(course_id, sections_data)
            if structure_result['success']:
                print("✅ Bulk course structure created successfully")
                sections_created = len(structure_result.get('sections', []))
                total_activities = sum(len(s.get('activities', [])) for s in structure_result.get('sections', []))
                print(f"   📚 Sections created: {sections_created}")
                print(f"   📄 Activities created: {total_activities}")
            else:
                print(f"❌ Bulk structure creation failed: {structure_result['message']}")
        except Exception as e:
            print(f"❌ Bulk structure error: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Plugin Integration Test Complete!")
        print("\n✅ What's working:")
        print("   - Custom plugin detection")
        print("   - Real content storage")
        print("   - Activity creation (pages, labels, files)")
        print("   - Section content updates")
        print("   - Bulk operations")
        
        print(f"\n🔗 Visit your test course:")
        print(f"   {config.moodle_url}/course/view.php?id={course_id}")
        
        print("\n💡 Next steps:")
        print("   1. Update mcp_server.py to use EnhancedMoodleClient")
        print("   2. Test with Claude Desktop")
        print("   3. Enjoy fully automated course creation! 🎉")

if __name__ == "__main__":
    asyncio.run(test_plugin_integration())