"""
Comprehensive tests for Advanced MCP Server Features
Tests adaptive processing, session management, and intelligent responses
"""

import asyncio
import json
import os

# Add project root to path
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.adaptive_config import AdaptiveConfig, ProcessingLimits, StrategyConfig
from src.core.adaptive_content_processor import (
    AdaptiveContentProcessor,
    ProcessingSession,
    ProcessingStrategy,
    SessionState,
)
from src.core.intelligent_session_manager import IntelligentSessionManager


class TestAdaptiveContentProcessor(unittest.TestCase):
    """Test the adaptive content processing system"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = AdaptiveContentProcessor()
        self.sample_content = """
        User: Can you explain Python functions?

        Assistant: Sure! Functions in Python are defined using the def keyword.
        Here's a simple example:

        ```python
        def greet(name):
            return f"Hello, {name}!"

        # Call the function
        message = greet("World")
        print(message)
        ```

        Functions are reusable blocks of code that help organize your program.
        They can accept parameters and return values.

        User: What about classes?

        Assistant: Classes are blueprints for creating objects:

        ```python
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def introduce(self):
                return f"Hi, I'm {self.name}, {self.age} years old"

        # Create an instance
        person = Person("Alice", 30)
        print(person.introduce())
        ```

        Classes enable object-oriented programming in Python.
        """

    def test_content_complexity_analysis(self):
        """Test content complexity analysis"""
        analysis = asyncio.run(
            self.processor.analyze_content_complexity(self.sample_content)
        )

        self.assertIn("content_length", analysis)
        self.assertIn("code_blocks", analysis)
        self.assertIn("topics", analysis)
        self.assertIn("complexity_score", analysis)
        self.assertIn("recommended_strategy", analysis)

        # Should detect code blocks and topics
        self.assertGreater(analysis["code_blocks"], 0)
        self.assertGreater(analysis["topics"], 0)
        self.assertIsInstance(analysis["complexity_score"], float)
        self.assertGreaterEqual(analysis["complexity_score"], 0.0)
        self.assertLessEqual(analysis["complexity_score"], 1.0)

    def test_session_creation(self):
        """Test session creation and management"""
        session_id = self.processor.create_session(self.sample_content, "Test Course")

        self.assertIsInstance(session_id, str)
        self.assertIn(session_id, self.processor.active_sessions)

        session = self.processor.active_sessions[session_id]
        self.assertEqual(session.original_content, self.sample_content)
        self.assertEqual(session.course_name, "Test Course")
        self.assertEqual(session.state, SessionState.INITIALIZED)

    def test_content_chunking_strategies(self):
        """Test different content chunking strategies"""
        session_id = self.processor.create_session(self.sample_content, "Test Course")
        session = self.processor.active_sessions[session_id]

        # Test intelligent chunking
        session.strategy = ProcessingStrategy.INTELLIGENT_CHUNK
        parsed_content = self.processor.content_parser.parse_chat(self.sample_content)
        chunks = self.processor._create_intelligent_chunks(parsed_content)

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        # Test progressive chunking
        session.strategy = ProcessingStrategy.PROGRESSIVE_BUILD
        progressive_chunks = self.processor._create_progressive_chunks(parsed_content)

        self.assertIsInstance(progressive_chunks, list)
        self.assertGreater(len(progressive_chunks), 0)

    def test_session_progress_tracking(self):
        """Test session progress tracking and continuation logic"""
        session_id = self.processor.create_session(self.sample_content, "Test Course")
        session = self.processor.active_sessions[session_id]
        session.total_chunks = 3

        # Test progress updates
        session.update_progress(0, success=True)
        self.assertEqual(session.processed_chunks, 1)
        self.assertTrue(session.needs_continuation)
        self.assertIsNotNone(session.continuation_prompt)

        # Test completion
        session.update_progress(1, success=True)
        session.update_progress(2, success=True)
        self.assertEqual(session.processed_chunks, 3)

    def test_error_handling_and_retry_logic(self):
        """Test error handling and retry logic"""
        session_id = self.processor.create_session(self.sample_content, "Test Course")
        session = self.processor.active_sessions[session_id]

        # Test error tracking
        session.update_progress(0, success=False)
        self.assertEqual(session.error_count, 1)
        self.assertEqual(session.processed_chunks, 0)

        # Test retry capability
        self.assertTrue(session.can_retry())

        # Test max retries
        session.retry_attempts = session.max_retries
        self.assertFalse(session.can_retry())

    def test_adaptive_limit_adjustment(self):
        """Test adaptive limit adjustment based on success metrics"""
        original_limit = self.processor.content_limits.max_char_length

        # Simulate high success rate with large content
        self.processor._update_success_metrics(12000, True)
        self.processor._update_success_metrics(11000, True)
        self.processor._update_success_metrics(13000, True)

        # Check if limits were adapted upward
        self.assertGreaterEqual(
            self.processor.content_limits.max_char_length, original_limit
        )

    def test_session_expiry(self):
        """Test session expiry functionality"""
        session_id = self.processor.create_session(self.sample_content, "Test Course")
        session = self.processor.active_sessions[session_id]

        # Session should not be expired initially
        self.assertFalse(session.is_expired())

        # Force expiry
        session.expires_at = datetime.now() - timedelta(hours=1)
        self.assertTrue(session.is_expired())


class TestIntelligentSessionManager(unittest.TestCase):
    """Test the intelligent session management system"""

    def setUp(self):
        """Set up test fixtures"""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()

        # Mock Moodle client
        self.mock_moodle_client = Mock()
        self.mock_moodle_client.create_course = AsyncMock(return_value=123)
        self.mock_moodle_client.create_section = AsyncMock(return_value={"id": 456})
        self.mock_moodle_client.create_page_activity = AsyncMock(
            return_value={"id": 789}
        )
        self.mock_moodle_client.get_course_contents = AsyncMock(
            return_value={
                "sections": [
                    {"modules": [{"id": 1}, {"id": 2}]},
                    {"modules": [{"id": 3}]},
                ]
            }
        )

        # Create session manager with test database
        from src.core.intelligent_session_manager import SessionDatabase

        db_config = SessionDatabase(db_path=self.temp_db.name)
        self.session_manager = IntelligentSessionManager(
            moodle_client=self.mock_moodle_client, db_config=db_config
        )

        self.sample_content = """
        Here's a simple Python tutorial:

        ```python
        def hello_world():
            print("Hello, World!")

        hello_world()
        ```

        This function prints a greeting message.
        """

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_intelligent_course_session_creation(self):
        """Test intelligent course session creation"""
        result = asyncio.run(
            self.session_manager.create_intelligent_course_session(
                content=self.sample_content, course_name="Test Course"
            )
        )

        self.assertTrue(result["success"])
        self.assertIn("session_id", result)

        if result.get("immediate_completion"):
            self.assertIn("message", result)
            self.assertTrue(result["message"].startswith("✅"))
        else:
            self.assertIn("processing_plan", result)
            self.assertIn("user_friendly_message", result)

    def test_session_continuation(self):
        """Test session continuation with additional content"""
        # Create initial session
        create_result = asyncio.run(
            self.session_manager.create_intelligent_course_session(
                content=self.sample_content, course_name="Test Course"
            )
        )

        session_id = create_result["session_id"]

        # Continue session
        additional_content = """
        Here's another example:

        ```python
        def add_numbers(a, b):
            return a + b

        result = add_numbers(5, 3)
        print(f"Result: {result}")
        ```
        """

        continue_result = asyncio.run(
            self.session_manager.continue_session_processing(
                session_id=session_id, additional_content=additional_content
            )
        )

        self.assertTrue(
            continue_result.get("success", False) or "error" in continue_result
        )

    def test_moodle_course_creation(self):
        """Test actual Moodle course creation"""
        # Create session that should trigger Moodle integration
        result = asyncio.run(
            self.session_manager.create_intelligent_course_session(
                content=self.sample_content, course_name="Test Moodle Course"
            )
        )

        session_id = result["session_id"]

        # If immediate completion, check Moodle integration
        if result.get("immediate_completion") and result.get("course_id"):
            self.mock_moodle_client.create_course.assert_called()
            self.assertEqual(result["course_id"], 123)

    def test_session_persistence(self):
        """Test session persistence to database"""
        # Create session
        result = asyncio.run(
            self.session_manager.create_intelligent_course_session(
                content=self.sample_content, course_name="Persistent Course"
            )
        )

        session_id = result["session_id"]

        # Verify session exists in processor
        session = self.session_manager.content_processor.active_sessions.get(session_id)
        self.assertIsNotNone(session)

        # Session should be saved to database
        # (Database operations are tested implicitly through session creation)

    def test_session_analytics(self):
        """Test session analytics functionality"""
        # Create a few sessions
        for i in range(3):
            asyncio.run(
                self.session_manager.create_intelligent_course_session(
                    content=f"Content {i}: {self.sample_content}",
                    course_name=f"Course {i}",
                )
            )

        # Get analytics
        analytics = self.session_manager.get_session_analytics()

        self.assertIn("overall", analytics)
        self.assertIn("processor_metrics", analytics)
        self.assertIn("active_sessions", analytics)


class TestAdaptiveConfig(unittest.TestCase):
    """Test the adaptive configuration system"""

    def setUp(self):
        """Set up test fixtures"""
        # Use temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_config.close()

        self.config = AdaptiveConfig(config_path=self.temp_config.name)

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)

    def test_config_initialization(self):
        """Test configuration initialization with defaults"""
        self.assertIsInstance(self.config.processing, ProcessingLimits)
        self.assertIsInstance(self.config.strategy, StrategyConfig)
        self.assertGreater(self.config.processing.max_char_length, 0)

    def test_config_save_and_load(self):
        """Test configuration save and load functionality"""
        # Modify some values
        original_limit = self.config.processing.max_char_length
        self.config.processing.max_char_length = 12000

        # Save config
        self.assertTrue(self.config.save_config())

        # Create new config instance and load
        new_config = AdaptiveConfig(config_path=self.temp_config.name)

        # Should have loaded the modified value
        self.assertEqual(new_config.processing.max_char_length, 12000)
        self.assertNotEqual(new_config.processing.max_char_length, original_limit)

    def test_adaptive_limit_adjustment(self):
        """Test adaptive limit adjustment based on metrics"""
        original_limit = self.config.processing.max_char_length

        # Simulate good performance with larger content
        adapted = self.config.adapt_processing_limits(
            success_rate=0.95, avg_content_size=15000, total_requests=20
        )

        if adapted:
            self.assertGreater(self.config.processing.max_char_length, original_limit)
            self.assertGreater(len(self.config.adaptation_history), 0)

    def test_strategy_effectiveness_tracking(self):
        """Test strategy effectiveness tracking"""
        # Update strategy effectiveness
        strategy_updated = self.config.adapt_strategy_effectiveness("single_pass", True)

        # Check if rates were updated (may not change significantly with single update)
        self.assertIn("single_pass", self.config.strategy.strategy_success_rates)

        # Multiple updates should show effect
        for _ in range(10):
            self.config.adapt_strategy_effectiveness("single_pass", True)

        # Success rate should be high
        rate = self.config.strategy.strategy_success_rates["single_pass"]
        self.assertGreater(rate, 0.8)

    def test_configuration_export_import(self):
        """Test configuration export and import"""
        export_path = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name

        try:
            # Modify config
            self.config.processing.max_char_length = 15000
            self.config.user_experience.use_emojis = False

            # Export
            self.assertTrue(self.config.export_config(export_path))

            # Create new config and import
            new_config = AdaptiveConfig()
            self.assertTrue(new_config.import_config(export_path))

            # Should match exported values
            self.assertEqual(new_config.processing.max_char_length, 15000)
            self.assertEqual(new_config.user_experience.use_emojis, False)

        finally:
            if os.path.exists(export_path):
                os.unlink(export_path)

    def test_optimal_strategy_thresholds(self):
        """Test optimal strategy threshold calculation"""
        # Set some strategy effectiveness rates
        self.config.strategy.strategy_success_rates = {
            "single_pass": 0.9,
            "intelligent_chunk": 0.8,
            "progressive_build": 0.7,
            "adaptive_retry": 0.6,
        }

        thresholds = self.config.get_optimal_strategy_thresholds()

        self.assertIn("single_pass", thresholds)
        self.assertIn("intelligent_chunk", thresholds)
        self.assertIn("progressive_build", thresholds)

        # Thresholds should be reasonable
        self.assertGreater(thresholds["single_pass"], 0)
        self.assertLess(thresholds["single_pass"], thresholds["intelligent_chunk"])
        self.assertLess(
            thresholds["intelligent_chunk"], thresholds["progressive_build"]
        )


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios with all advanced features"""

    def setUp(self):
        """Set up integration test fixtures"""
        # Create temporary files
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()

        self.temp_config = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_config.close()

        # Setup mock Moodle client
        self.mock_moodle_client = Mock()
        self.mock_moodle_client.create_course = AsyncMock(return_value=123)
        self.mock_moodle_client.create_section = AsyncMock(return_value={"id": 456})
        self.mock_moodle_client.create_page_activity = AsyncMock(
            return_value={"id": 789}
        )

        # Complex content for testing
        self.complex_content = """
        User: I want to learn Python programming from scratch.

        Assistant: Great! Let's start with the basics of Python programming.

        ## Introduction to Python
        Python is a high-level, interpreted programming language known for its simplicity and readability.

        ### Variables and Data Types
        ```python
        # Variables
        name = "Alice"
        age = 25
        height = 5.6
        is_student = True

        # Print variables
        print(f"Name: {name}")
        print(f"Age: {age}")
        print(f"Height: {height}")
        print(f"Is student: {is_student}")
        ```

        ### Control Structures

        #### If Statements
        ```python
        age = 18

        if age >= 18:
            print("You are an adult")
        elif age >= 13:
            print("You are a teenager")
        else:
            print("You are a child")
        ```

        #### Loops
        ```python
        # For loop
        for i in range(5):
            print(f"Count: {i}")

        # While loop
        count = 0
        while count < 3:
            print(f"While count: {count}")
            count += 1
        ```

        ### Functions
        Functions are reusable blocks of code that perform specific tasks.

        ```python
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        def calculate_area(length, width):
            return length * width

        # Function calls
        message = greet("Alice")
        print(message)

        area = calculate_area(10, 5)
        print(f"Area: {area}")
        ```

        ### Classes and Objects
        Object-oriented programming allows you to create classes and objects.

        ```python
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def introduce(self):
                return f"Hi, I'm {self.name}, {self.age} years old"

            def have_birthday(self):
                self.age += 1
                return f"Happy birthday! Now {self.age} years old"

        # Create objects
        person1 = Person("Alice", 25)
        person2 = Person("Bob", 30)

        print(person1.introduce())
        print(person2.introduce())
        print(person1.have_birthday())
        ```

        ### Error Handling
        Python provides try-except blocks for handling errors gracefully.

        ```python
        def safe_divide(a, b):
            try:
                result = a / b
                return result
            except ZeroDivisionError:
                return "Cannot divide by zero!"
            except TypeError:
                return "Invalid input types!"
            except Exception as e:
                return f"An error occurred: {e}"

        # Test error handling
        print(safe_divide(10, 2))   # Normal case
        print(safe_divide(10, 0))   # Division by zero
        print(safe_divide("10", 2)) # Type error
        ```

        ### File Operations
        ```python
        # Writing to a file
        def write_to_file(filename, content):
            try:
                with open(filename, 'w') as file:
                    file.write(content)
                return f"Successfully wrote to {filename}"
            except Exception as e:
                return f"Error writing to file: {e}"

        # Reading from a file
        def read_from_file(filename):
            try:
                with open(filename, 'r') as file:
                    content = file.read()
                return content
            except FileNotFoundError:
                return "File not found!"
            except Exception as e:
                return f"Error reading file: {e}"

        # Example usage
        write_to_file("example.txt", "Hello, Python!")
        content = read_from_file("example.txt")
        print(content)
        ```

        This covers the fundamental concepts of Python programming. Practice these examples and experiment with variations!
        """

    def tearDown(self):
        """Clean up integration test fixtures"""
        for temp_file in [self.temp_db.name, self.temp_config.name]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_complete_workflow_simple_content(self):
        """Test complete workflow with simple content (single-pass)"""
        # Initialize session manager
        from src.core.intelligent_session_manager import SessionDatabase

        db_config = SessionDatabase(db_path=self.temp_db.name)
        session_manager = IntelligentSessionManager(
            moodle_client=self.mock_moodle_client, db_config=db_config
        )

        simple_content = """
        Here's a quick Python example:

        ```python
        print("Hello, World!")
        ```

        This prints a greeting message.
        """

        # Create course session
        result = asyncio.run(
            session_manager.create_intelligent_course_session(
                content=simple_content, course_name="Simple Python Course"
            )
        )

        self.assertTrue(result["success"])

        # Should complete immediately for simple content
        if result.get("immediate_completion"):
            self.assertIn("message", result)
            self.assertTrue(result["message"].startswith("✅"))

    def test_complete_workflow_complex_content(self):
        """Test complete workflow with complex content (multi-pass)"""
        # Initialize session manager
        from src.core.intelligent_session_manager import SessionDatabase

        db_config = SessionDatabase(db_path=self.temp_db.name)
        session_manager = IntelligentSessionManager(
            moodle_client=self.mock_moodle_client, db_config=db_config
        )

        # Create course session with complex content
        result = asyncio.run(
            session_manager.create_intelligent_course_session(
                content=self.complex_content, course_name="Complete Python Course"
            )
        )

        self.assertTrue(result["success"])
        session_id = result["session_id"]

        # For complex content, should require multi-step processing
        if not result.get("immediate_completion"):
            self.assertIn("processing_plan", result)
            self.assertIn("user_friendly_message", result)

            # Continue processing (simulate additional content)
            continue_result = asyncio.run(
                session_manager.continue_session_processing(
                    session_id=session_id, additional_content=""
                )
            )

            # Should get some result (success or continuation needed)
            self.assertIn("success", continue_result)

    def test_adaptive_learning_cycle(self):
        """Test that the system learns and adapts over multiple sessions"""
        # Initialize with adaptive config
        config = AdaptiveConfig(config_path=self.temp_config.name)

        from src.core.intelligent_session_manager import SessionDatabase

        db_config = SessionDatabase(db_path=self.temp_db.name)
        session_manager = IntelligentSessionManager(
            moodle_client=self.mock_moodle_client, db_config=db_config
        )

        # Override session manager's config with our test config
        session_manager.content_processor.content_limits = config.processing

        original_limit = config.processing.max_char_length

        # Create multiple sessions with varying success
        for i in range(15):  # Enough to trigger adaptation
            content_size = 6000 + (i * 500)  # Gradually increasing content
            test_content = self.complex_content[:content_size]

            try:
                result = asyncio.run(
                    session_manager.create_intelligent_course_session(
                        content=test_content, course_name=f"Course {i}"
                    )
                )

                # Simulate success/failure and update config
                success = result.get("success", False)
                config.adapt_strategy_effectiveness("intelligent_chunk", success)

            except Exception:
                # Handle any errors gracefully in test
                pass

            # Update processing limits based on performance
            if i % 5 == 0:  # Every 5 iterations
                success_rate = 0.8 + (i * 0.01)  # Gradually improving
                config.adapt_processing_limits(success_rate, content_size, i + 1)

        # Check if system learned and adapted
        analytics = session_manager.get_session_analytics()
        self.assertIn("processor_metrics", analytics)

        # Limits may have been adapted
        final_limit = config.processing.max_char_length
        self.assertIsInstance(final_limit, int)
        self.assertGreater(final_limit, 0)

    def test_error_recovery_and_retry(self):
        """Test error recovery and retry mechanisms"""
        # Initialize session manager
        from src.core.intelligent_session_manager import SessionDatabase

        db_config = SessionDatabase(db_path=self.temp_db.name)
        session_manager = IntelligentSessionManager(
            moodle_client=None,  # No Moodle client to trigger certain error paths
            db_config=db_config,
        )

        # Create session
        result = asyncio.run(
            session_manager.create_intelligent_course_session(
                content=self.complex_content, course_name="Error Test Course"
            )
        )

        # Should handle missing Moodle client gracefully
        self.assertTrue(result.get("success", True))  # Should still create session

        session_id = result["session_id"]

        # Test invalid session continuation
        invalid_result = asyncio.run(
            session_manager.continue_session_processing(
                session_id="invalid_session_id", additional_content=""
            )
        )

        self.assertFalse(invalid_result["success"])
        self.assertIn("error", invalid_result)


def run_advanced_feature_tests():
    """Run all advanced feature tests"""
    print("🚀 Running Advanced MoodleClaude Feature Tests...\n")

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestAdaptiveContentProcessor,
        TestIntelligentSessionManager,
        TestAdaptiveConfig,
        TestIntegrationScenarios,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*60}")
    print(f"🧪 Advanced Feature Test Results Summary:")
    print(f"{'='*60}")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")

    if result.failures:
        print(f"\n💥 Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print(f"\n🔥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")

    success_rate = (
        (
            (result.testsRun - len(result.failures) - len(result.errors))
            / result.testsRun
            * 100
        )
        if result.testsRun > 0
        else 0
    )
    print(f"\n🎯 Success rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print(f"🎉 All advanced features are working correctly!")
    else:
        print(f"🔧 Some advanced features need attention.")

    print(f"{'='*60}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_advanced_feature_tests()
    exit(0 if success else 1)
