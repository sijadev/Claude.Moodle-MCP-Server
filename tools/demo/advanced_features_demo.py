#!/usr/bin/env python3
"""
Advanced Features Demo for MoodleClaude
Demonstrates the new intelligent course creation capabilities
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.adaptive_config import AdaptiveConfig, get_adaptive_config
from src.core.adaptive_content_processor import AdaptiveContentProcessor
from src.core.intelligent_session_manager import IntelligentSessionManager


class AdvancedFeaturesDemo:
    """
    Interactive demonstration of advanced MoodleClaude features
    """

    def __init__(self):
        """Initialize the demo"""
        print("🚀 MoodleClaude Advanced Features Demo")
        print("=" * 50)

        # Initialize adaptive configuration
        self.config = get_adaptive_config()
        print(f"✅ Adaptive configuration loaded")

        # Initialize session manager (without Moodle client for demo)
        self.session_manager = IntelligentSessionManager(moodle_client=None)
        print(f"✅ Intelligent session manager initialized")

        # Sample content for demonstrations
        self.sample_contents = {
            "simple": """
            User: How do I print in Python?

            Assistant: You can use the print() function:

            ```python
            print("Hello, World!")
            ```

            This will output: Hello, World!
            """,
            "moderate": """
            User: Can you explain Python functions?

            Assistant: Sure! Functions are reusable blocks of code.

            ## Basic Function Syntax
            ```python
            def greet(name):
                return f"Hello, {name}!"

            # Call the function
            message = greet("Alice")
            print(message)
            ```

            ## Functions with Multiple Parameters
            ```python
            def calculate_area(length, width):
                area = length * width
                return area

            result = calculate_area(10, 5)
            print(f"Area: {result}")
            ```

            Functions help organize your code and make it reusable!
            """,
            "complex": """
            User: I want to learn Python programming comprehensively.

            Assistant: Great! Let's cover Python from basics to advanced concepts.

            ## 1. Variables and Data Types
            ```python
            # Basic data types
            name = "Alice"          # String
            age = 25               # Integer
            height = 5.6           # Float
            is_student = True      # Boolean
            grades = [85, 92, 78]  # List

            print(f"Name: {name}, Age: {age}")
            ```

            ## 2. Control Structures

            ### If Statements
            ```python
            score = 85

            if score >= 90:
                grade = "A"
            elif score >= 80:
                grade = "B"
            elif score >= 70:
                grade = "C"
            else:
                grade = "F"

            print(f"Grade: {grade}")
            ```

            ### Loops
            ```python
            # For loop
            for i in range(5):
                print(f"Iteration {i}")

            # While loop
            count = 0
            while count < 3:
                print(f"Count: {count}")
                count += 1

            # List comprehension
            squares = [x**2 for x in range(10)]
            print(squares)
            ```

            ## 3. Functions and Modules
            ```python
            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)

            def factorial(n):
                if n <= 1:
                    return 1
                return n * factorial(n-1)

            # Using functions
            print(f"Fibonacci(10): {fibonacci(10)}")
            print(f"Factorial(5): {factorial(5)}")
            ```

            ## 4. Object-Oriented Programming
            ```python
            class Animal:
                def __init__(self, name, species):
                    self.name = name
                    self.species = species

                def make_sound(self):
                    pass

                def info(self):
                    return f"{self.name} is a {self.species}"

            class Dog(Animal):
                def __init__(self, name, breed):
                    super().__init__(name, "Dog")
                    self.breed = breed

                def make_sound(self):
                    return "Woof!"

                def fetch(self):
                    return f"{self.name} is fetching the ball!"

            # Using classes
            my_dog = Dog("Buddy", "Golden Retriever")
            print(my_dog.info())
            print(my_dog.make_sound())
            print(my_dog.fetch())
            ```

            ## 5. Error Handling
            ```python
            def safe_divide(a, b):
                try:
                    result = a / b
                    return result
                except ZeroDivisionError:
                    print("Error: Cannot divide by zero!")
                    return None
                except TypeError:
                    print("Error: Invalid input types!")
                    return None
                finally:
                    print("Division operation completed.")

            # Test error handling
            print(safe_divide(10, 2))   # Normal case
            print(safe_divide(10, 0))   # Division by zero
            ```

            ## 6. File Operations and Data Processing
            ```python
            import json
            import csv

            def process_student_data(filename):
                students = []

                try:
                    with open(filename, 'r') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            student = {
                                'name': row['name'],
                                'grade': float(row['grade']),
                                'subject': row['subject']
                            }
                            students.append(student)

                    # Calculate statistics
                    total_grade = sum(s['grade'] for s in students)
                    average_grade = total_grade / len(students)

                    return {
                        'students': students,
                        'count': len(students),
                        'average_grade': average_grade
                    }

                except FileNotFoundError:
                    print(f"File {filename} not found!")
                    return None
                except Exception as e:
                    print(f"Error processing file: {e}")
                    return None

            # Save results to JSON
            def save_results(data, output_file):
                try:
                    with open(output_file, 'w') as file:
                        json.dump(data, file, indent=2)
                    print(f"Results saved to {output_file}")
                except Exception as e:
                    print(f"Error saving results: {e}")
            ```

            This comprehensive overview covers the essential Python concepts you need to know!
            """,
        }

    async def demo_content_analysis(self):
        """Demonstrate content complexity analysis"""
        print(f"\n📊 Content Complexity Analysis Demo")
        print("-" * 40)

        for content_type, content in self.sample_contents.items():
            print(f"\n🔍 Analyzing {content_type.title()} Content:")

            analysis = (
                await self.session_manager.content_processor.analyze_content_complexity(
                    content
                )
            )

            print(f"  📏 Length: {analysis['content_length']:,} characters")
            print(f"  💻 Code blocks: {analysis['code_blocks']}")
            print(f"  📚 Topics: {analysis['topics']}")
            print(f"  🧠 Complexity: {analysis['complexity_score']:.2f}/1.0")
            print(
                f"  ⚡ Strategy: {analysis['recommended_strategy'].value.replace('_', ' ').title()}"
            )
            print(f"  🔧 Est. chunks: {analysis['estimated_chunks']}")
            print(f"  ⏱️  Est. time: {analysis['processing_time_estimate']}s")

    async def demo_intelligent_session_creation(self):
        """Demonstrate intelligent session creation"""
        print(f"\n🎯 Intelligent Session Creation Demo")
        print("-" * 40)

        for content_type, content in self.sample_contents.items():
            print(f"\n🚀 Creating session for {content_type.title()} content:")

            result = await self.session_manager.create_intelligent_course_session(
                content=content, course_name=f"Demo {content_type.title()} Course"
            )

            if result["success"]:
                print(f"  ✅ Session created: {result['session_id']}")

                if result.get("immediate_completion"):
                    print(f"  🎉 Completed immediately!")
                    if result.get("final_summary"):
                        summary = result["final_summary"]
                        print(f"     - Sections: {summary.get('total_sections', 0)}")
                        print(f"     - Items: {summary.get('total_items', 0)}")
                        print(f"     - Time: {summary.get('processing_time', 0):.1f}s")
                else:
                    print(f"  🔄 Multi-step processing initiated")
                    if result.get("processing_plan"):
                        plan = result["processing_plan"]
                        print(
                            f"     - Strategy: {plan['strategy'].replace('_', ' ').title()}"
                        )
                        print(f"     - Parts: {plan['estimated_chunks']}")
                        print(f"     - Complexity: {plan['complexity_score']:.2f}")
            else:
                print(
                    f"  ❌ Session creation failed: {result.get('error', 'Unknown error')}"
                )

    async def demo_session_continuation(self):
        """Demonstrate session continuation"""
        print(f"\n🔄 Session Continuation Demo")
        print("-" * 40)

        # Create a session with complex content
        result = await self.session_manager.create_intelligent_course_session(
            content=self.sample_contents["complex"],
            course_name="Continuation Demo Course",
        )

        if result["success"]:
            session_id = result["session_id"]
            print(f"✅ Created session: {session_id}")

            # Try to continue the session
            additional_content = """

            ## 7. Advanced Python Features
            ```python
            # Decorators
            def timer(func):
                import time
                def wrapper(*args, **kwargs):
                    start = time.time()
                    result = func(*args, **kwargs)
                    end = time.time()
                    print(f"{func.__name__} took {end-start:.2f} seconds")
                    return result
                return wrapper

            @timer
            def slow_function():
                import time
                time.sleep(1)
                return "Done!"

            # Context managers
            class FileManager:
                def __init__(self, filename, mode):
                    self.filename = filename
                    self.mode = mode

                def __enter__(self):
                    self.file = open(self.filename, self.mode)
                    return self.file

                def __exit__(self, exc_type, exc_val, exc_tb):
                    self.file.close()

            # Using context manager
            with FileManager('example.txt', 'w') as f:
                f.write("Hello, Context Manager!")
            ```
            """

            continue_result = await self.session_manager.continue_session_processing(
                session_id=session_id, additional_content=additional_content
            )

            if continue_result["success"]:
                print(f"✅ Session continued successfully")
                if continue_result.get("progress"):
                    progress = continue_result["progress"]
                    print(f"   📊 Progress: {progress['percentage']:.1f}%")
                    print(
                        f"   🔢 Parts: {progress['completed_chunks']}/{progress['total_chunks']}"
                    )
            else:
                print(
                    f"❌ Continuation failed: {continue_result.get('error', 'Unknown error')}"
                )

    def demo_adaptive_configuration(self):
        """Demonstrate adaptive configuration features"""
        print(f"\n⚙️  Adaptive Configuration Demo")
        print("-" * 40)

        # Show current configuration
        summary = self.config.get_configuration_summary()

        print(f"📋 Current Configuration:")
        print(
            f"  💾 Character limit: {summary['processing_limits']['max_char_length']:,}"
        )
        print(f"  📚 Max sections: {summary['processing_limits']['max_sections']}")
        print(
            f"  🎯 Adaptation sensitivity: {summary['processing_limits']['adaptation_sensitivity']}"
        )

        print(f"\n🧠 Strategy Effectiveness:")
        for strategy, rate in summary["strategy_effectiveness"].items():
            print(f"  - {strategy.replace('_', ' ').title()}: {rate:.1%}")

        print(f"\n📊 Adaptation Stats:")
        print(
            f"  🔄 Total adaptations: {summary['adaptation_stats']['total_adaptations']}"
        )
        print(f"  💾 Config path: {summary['adaptation_stats']['config_path']}")

        # Demonstrate adaptation
        print(f"\n🔧 Simulating Adaptation:")
        original_limit = self.config.processing.max_char_length

        # Simulate good performance with larger content
        adapted = self.config.adapt_processing_limits(
            success_rate=0.95, avg_content_size=12000, total_requests=15
        )

        if adapted:
            new_limit = self.config.processing.max_char_length
            print(f"  ✅ Limits adapted: {original_limit:,} → {new_limit:,} characters")
        else:
            print(f"  ℹ️  No adaptation needed (insufficient data or optimal limits)")

        # Show optimal strategy thresholds
        thresholds = self.config.get_optimal_strategy_thresholds()
        print(f"\n🎯 Optimal Strategy Thresholds:")
        for strategy, threshold in thresholds.items():
            print(f"  - {strategy.replace('_', ' ').title()}: {threshold:.2f}")

    def demo_session_analytics(self):
        """Demonstrate session analytics"""
        print(f"\n📈 Session Analytics Demo")
        print("-" * 40)

        analytics = self.session_manager.get_session_analytics()

        if analytics.get("error"):
            print(f"❌ Analytics error: {analytics['error']}")
            return

        print(f"📊 Overall Metrics:")
        if analytics.get("overall"):
            overall = analytics["overall"]
            print(f"  📝 Total sessions: {overall.get('total_sessions', 0)}")
            print(f"  ✅ Completed: {overall.get('completed_sessions', 0)}")
            print(f"  ❌ Failed: {overall.get('failed_sessions', 0)}")
            print(
                f"  📊 Avg completion rate: {overall.get('avg_completion_rate', 0):.1%}"
            )
            print(
                f"  📏 Avg content size: {overall.get('avg_content_size', 0):.0f} chars"
            )

        print(f"\n🎯 Current Status:")
        print(f"  🔄 Active sessions: {analytics.get('active_sessions', 0)}")

        if analytics.get("processor_metrics"):
            metrics = analytics["processor_metrics"]
            if metrics.get("success_metrics"):
                success = metrics["success_metrics"]
                success_rate = success.get("successful_requests", 0) / max(
                    success.get("total_requests", 1), 1
                )
                print(f"  ✅ Success rate: {success_rate:.1%}")
                print(f"  📊 Total requests: {success.get('total_requests', 0)}")

            print(
                f"  🧠 Learning status: {metrics.get('learning_status', 'Unknown').title()}"
            )

    async def run_complete_demo(self):
        """Run the complete demonstration"""
        print(
            f"\nStarting comprehensive demo at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 60)

        try:
            # 1. Content Analysis Demo
            await self.demo_content_analysis()

            # 2. Session Creation Demo
            await self.demo_intelligent_session_creation()

            # 3. Session Continuation Demo
            await self.demo_session_continuation()

            # 4. Configuration Demo
            self.demo_adaptive_configuration()

            # 5. Analytics Demo
            self.demo_session_analytics()

            print(f"\n🎉 Demo completed successfully!")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            import traceback

            traceback.print_exc()

        finally:
            # Cleanup
            await self.session_manager.cleanup_and_shutdown()

    def run_interactive_mode(self):
        """Run interactive mode for manual testing"""
        print(f"\n🎮 Interactive Mode")
        print("=" * 30)
        print("Commands:")
        print("  1 - Analyze content complexity")
        print("  2 - Create intelligent session")
        print("  3 - Show session analytics")
        print("  4 - Show configuration")
        print("  q - Quit")

        while True:
            try:
                choice = input(f"\n> Enter command: ").strip().lower()

                if choice == "q" or choice == "quit":
                    break
                elif choice == "1":
                    content = input("Enter content to analyze: ")
                    if content:
                        analysis = asyncio.run(
                            self.session_manager.content_processor.analyze_content_complexity(
                                content
                            )
                        )
                        print(
                            f"Analysis: {json.dumps(analysis, indent=2, default=str)}"
                        )
                elif choice == "2":
                    content = input("Enter content for course creation: ")
                    name = input("Enter course name (optional): ")
                    if content:
                        result = asyncio.run(
                            self.session_manager.create_intelligent_course_session(
                                content, name
                            )
                        )
                        print(f"Result: {json.dumps(result, indent=2, default=str)}")
                elif choice == "3":
                    analytics = self.session_manager.get_session_analytics()
                    print(f"Analytics: {json.dumps(analytics, indent=2, default=str)}")
                elif choice == "4":
                    summary = self.config.get_configuration_summary()
                    print(
                        f"Configuration: {json.dumps(summary, indent=2, default=str)}"
                    )
                else:
                    print("Invalid command. Try again.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print(f"\n👋 Goodbye!")


def main():
    """Main demo function"""
    import argparse

    parser = argparse.ArgumentParser(description="MoodleClaude Advanced Features Demo")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Run quick demo (skip complex scenarios)",
    )

    args = parser.parse_args()

    demo = AdvancedFeaturesDemo()

    if args.interactive:
        demo.run_interactive_mode()
    else:
        asyncio.run(demo.run_complete_demo())


if __name__ == "__main__":
    main()
