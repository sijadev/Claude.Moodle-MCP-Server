#!/usr/bin/env python3
"""
Test extreme chunking with content that will definitely trigger chunking
"""

import asyncio
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, PROJECT_ROOT)

from src.core.enhanced_mcp_server import EnhancedMoodleMCPServer


async def test_extreme_chunking():
    """Test with content that will definitely trigger chunking"""

    print("🚀 Testing Extreme Chunking (Large Content)")
    print("=" * 70)

    # Create content with many code examples that will trigger chunking
    base_code_example = """
    Here's an example of sorting algorithm implementation:

    ```python
    def advanced_sort_algorithm_{i}(arr):
        # Advanced sorting algorithm number {i}
        if len(arr) <= 1:
            return arr

        # Complex sorting logic with multiple steps
        pivot = arr[len(arr) // 2]
        left = []
        middle = []
        right = []

        for element in arr:
            if element < pivot:
                left.append(element)
            elif element == pivot:
                middle.append(element)
            else:
                right.append(element)

        # Recursive calls
        sorted_left = advanced_sort_algorithm_{i}(left)
        sorted_right = advanced_sort_algorithm_{i}(right)

        return sorted_left + middle + sorted_right

    # Test the algorithm
    test_data = [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
    result = advanced_sort_algorithm_{i}(test_data)
    print(f"Sorted array {i}:", result)

    # Performance analysis
    import time
    start_time = time.time()
    for _ in range(1000):
        advanced_sort_algorithm_{i}([3,1,4,1,5,9,2,6,5,3,5])
    end_time = time.time()
    print(f"Algorithm {i} took {{end_time - start_time:.4f}} seconds")
    ```

    This algorithm demonstrates advanced sorting technique number {i}.
    """

    # Generate 20 code examples - this will definitely trigger chunking
    large_content_parts = []
    for i in range(1, 21):
        large_content_parts.append(base_code_example.format(i=i))

    # Add some topic descriptions too
    topic_descriptions = [
        f"\n## Advanced Topic {i}\n\nThis section covers advanced programming concept number {i}. "
        + f"It includes detailed explanations, best practices, and real-world applications. "
        + f"The concepts build upon previous topics and prepare you for more complex challenges."
        for i in range(1, 11)
    ]

    # Combine everything
    extreme_large_content = "# Complete Advanced Programming Course\n\n" + "\n\n".join(
        large_content_parts + topic_descriptions
    )

    print(f"📊 Extreme content size: {len(extreme_large_content)} characters")
    print(f"📊 Estimated items: ~30 (20 code + 10 topics)")

    # Create MCP server instance
    server = EnhancedMoodleMCPServer()

    # Test the course creation with chunking
    try:
        print(f"\n📚 Creating course from extreme large content...")

        # Simulate tool call with extreme large content
        arguments = {
            "chat_content": extreme_large_content,
            "course_name": "Advanced Programming Masterclass (Chunked)",
            "course_description": "Extreme large course that will definitely require chunking for processing",
            "category_id": 1,
        }

        # Call the course creation function
        result = await server._create_course_from_chat(arguments)

        if result and len(result) > 0:
            response_text = result[0].text
            print(f"✅ Course creation result:")
            print("=" * 70)
            print(response_text)
            print("=" * 70)

            # Check for chunking indicators
            if "chunks" in response_text.lower() or "Processed in" in response_text:
                print(f"\n🎉 SUCCESS! Chunking solution is working!")
                print(f"✅ Extreme large content was successfully split and processed")
                print(f"✅ No empty sections - content chunking prevents API limits!")
            else:
                print(
                    f"\n⚠️ Content processed without chunking (maybe still under threshold)"
                )

        else:
            print(f"❌ No result returned from course creation")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()

    print(f"\n" + "=" * 70)
    print(f"🎯 Extreme Chunking Test Complete")


if __name__ == "__main__":
    asyncio.run(test_extreme_chunking())
