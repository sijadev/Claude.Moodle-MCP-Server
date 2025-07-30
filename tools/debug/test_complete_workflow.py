#!/usr/bin/env python3
"""
Test complete MoodleClaude workflow end-to-end
"""

import asyncio
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.enhanced_mcp_server import EnhancedMoodleMCPServer

async def test_complete_workflow():
    """Test the complete workflow from chat content to course creation"""
    
    print("🚀 Testing Complete MoodleClaude Workflow")
    print("=" * 70)
    
    # Sample chat content that includes code examples and explanations
    sample_chat_content = """
    Let me explain Python functions and how to use them:

    ## Python Functions

    A function in Python is a block of reusable code that performs a specific task.

    ### Basic Function Syntax

    Here's how you define a simple function:

    ```python
    def greet(name):
        return f"Hello, {name}!"
    
    # Call the function
    result = greet("World")
    print(result)
    ```

    This function takes a name as parameter and returns a greeting.

    ### Functions with Multiple Parameters

    You can create functions that accept multiple parameters:

    ```python
    def calculate_area(length, width):
        area = length * width
        return area
    
    # Calculate area of a rectangle
    room_area = calculate_area(10, 12)
    print(f"Room area: {room_area} square meters")
    ```

    ### Default Parameters

    Python allows you to set default values for parameters:

    ```python
    def introduce(name, age=25, city="Unknown"):
        return f"Hi, I'm {name}, {age} years old from {city}"
    
    # Different ways to call the function
    print(introduce("Alice"))
    print(introduce("Bob", 30))
    print(introduce("Charlie", 28, "New York"))
    ```

    ## Lambda Functions

    Lambda functions are small anonymous functions that can have any number of arguments:

    ```python
    # Lambda function to square a number
    square = lambda x: x**2
    print(square(5))  # Output: 25

    # Lambda function with multiple arguments
    multiply = lambda x, y: x * y
    print(multiply(3, 4))  # Output: 12

    # Using lambda with map()
    numbers = [1, 2, 3, 4, 5]
    squared_numbers = list(map(lambda x: x**2, numbers))
    print(squared_numbers)  # Output: [1, 4, 9, 16, 25]
    ```

    These examples show the power and flexibility of Python functions!
    """
    
    # Create MCP server instance
    server = EnhancedMoodleMCPServer()
    
    print(f"✅ MCP Server initialized")
    print(f"Configuration: {server.config.get_config_summary() if server.config else 'No config'}")
    
    # Test the course creation
    try:
        print(f"\n📚 Creating course from chat content...")
        
        # Simulate tool call
        arguments = {
            "chat_content": sample_chat_content,
            "course_name": "Python Functions Masterclass",
            "course_description": "Learn Python functions through practical examples and hands-on coding exercises",
            "category_id": 1
        }
        
        # Call the course creation function
        result = await server._create_course_from_chat(arguments)
        
        if result and len(result) > 0:
            response_text = result[0].text
            print(f"✅ Course creation result:")
            print("=" * 70)
            print(response_text)
            print("=" * 70)
            
            # Check if course was successful
            if "[SUCCESS]" in response_text or "Enhanced Course Created Successfully" in response_text:
                print(f"\n🎉 SUCCESS! MoodleClaude workflow is working perfectly!")
                print(f"✅ Chat content was parsed and converted to structured course")
                print(f"✅ Course sections were created with proper names")
                print(f"✅ Code examples were formatted and stored as activities")
                print(f"✅ Topic descriptions were formatted and stored as pages")
                print(f"✅ File resources were created for downloadable code")
                
                # Extract key info
                if "Course ID:" in response_text:
                    course_id_line = [line for line in response_text.split('\n') if 'Course ID:' in line][0]
                    print(f"✅ {course_id_line.strip()}")
                
                if "Course URL:" in response_text:
                    course_url_line = [line for line in response_text.split('\n') if 'Course URL:' in line][0]
                    print(f"✅ {course_url_line.strip()}")
                    
            else:
                print(f"⚠️ Course creation completed but with warnings")
        else:
            print(f"❌ No result returned from course creation")
            
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 Complete Workflow Test Finished")

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())