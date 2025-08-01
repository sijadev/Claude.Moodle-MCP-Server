#!/usr/bin/env python3
"""
Manual Test Runner for MoodleClaude

Executes all manual testing scripts and provides comprehensive reporting.
"""

import argparse
import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


class ManualTestRunner:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent

        # Test categories and their files
        self.test_categories = {
            "core": [
                "test_direct_moodle.py",
                "test_mcp_connection.py",
                "test_realistic_moodle.py",
            ],
            "advanced": [
                "test_enhanced_moodle.py",
                "test_wsmanage_correct.py",
                "test_wsmanagesections.py",
            ],
            "validation": [
                "test_core_functions.py",
                "test_wsmanage_params.py",
                "test_enrollment_config.py",
            ],
        }

        self.results = {}

    def run_test(self, test_file: str) -> Tuple[bool, str, float]:
        """Run a single test file and return success, output, and duration"""
        test_path = self.test_dir / test_file

        if not test_path.exists():
            return False, f"Test file not found: {test_file}", 0.0

        start_time = time.time()

        try:
            # Run the test with uv in the project root directory
            result = subprocess.run(
                ["uv", "run", "python", str(test_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            duration = time.time() - start_time

            # Consider test successful if it exits with code 0 and contains success indicators
            success_indicators = ["✅", "SUCCESS", "PASSED", "ALL TESTS PASSED"]
            has_success = any(
                indicator in result.stdout for indicator in success_indicators
            )

            # Check for error indicators
            error_indicators = ["❌", "FAILED", "ERROR", "Exception:", "Traceback"]
            has_errors = any(
                indicator in result.stderr or indicator in result.stdout
                for indicator in error_indicators
            )

            success = result.returncode == 0 and has_success and not has_errors
            output = result.stdout + result.stderr

            return success, output, duration

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, f"Test timed out after {duration:.1f} seconds", duration
        except Exception as e:
            duration = time.time() - start_time
            return False, f"Failed to run test: {str(e)}", duration

    def run_category(self, category: str) -> Dict[str, Tuple[bool, str, float]]:
        """Run all tests in a category"""
        if category not in self.test_categories:
            print(f"❌ Unknown category: {category}")
            return {}

        print(f"\n🔧 Running {category.upper()} tests...")
        print("=" * 60)

        category_results = {}

        for test_file in self.test_categories[category]:
            print(f"\n▶️  Running {test_file}...")
            success, output, duration = self.run_test(test_file)

            category_results[test_file] = (success, output, duration)

            # Print summary
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} ({duration:.1f}s)")

            # Print key output lines for immediate feedback
            if output:
                lines = output.split("\n")
                key_lines = [
                    line
                    for line in lines
                    if any(
                        indicator in line
                        for indicator in [
                            "✅",
                            "❌",
                            "SUCCESS",
                            "FAILED",
                            "Created",
                            "ERROR",
                        ]
                    )
                ]
                for line in key_lines[:3]:  # Show first 3 key lines
                    if line.strip():
                        print(f"   {line.strip()}")

        return category_results

    def run_all_tests(self) -> Dict[str, Dict[str, Tuple[bool, str, float]]]:
        """Run all manual tests"""
        print("🧪 MoodleClaude Manual Test Runner")
        print("=" * 60)
        print("Running comprehensive manual test suite...")

        all_results = {}

        for category in self.test_categories:
            all_results[category] = self.run_category(category)

        return all_results

    def print_summary(self, results: Dict[str, Dict[str, Tuple[bool, str, float]]]):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 MANUAL TEST SUMMARY")
        print("=" * 60)

        total_tests = 0
        total_passed = 0
        total_duration = 0.0

        for category, category_results in results.items():
            category_tests = len(category_results)
            category_passed = sum(
                1 for success, _, _ in category_results.values() if success
            )
            category_duration = sum(
                duration for _, _, duration in category_results.values()
            )

            total_tests += category_tests
            total_passed += category_passed
            total_duration += category_duration

            print(f"\n📂 {category.upper()} Tests:")
            print(f"   Tests: {category_passed}/{category_tests} passed")
            print(f"   Duration: {category_duration:.1f}s")

            # List individual test results
            for test_file, (success, _, duration) in category_results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {test_file} ({duration:.1f}s)")

        # Overall summary
        print(f"\n🎯 Overall Results:")
        print(f"   Total Tests: {total_passed}/{total_tests} passed")
        print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%")
        print(f"   Total Duration: {total_duration:.1f}s")

        # Recommendations
        if total_passed == total_tests:
            print(f"\n🎉 All tests passed! MoodleClaude is fully functional.")
        else:
            failed_tests = total_tests - total_passed
            print(
                f"\n⚠️  {failed_tests} test(s) failed. Check individual outputs for details."
            )
            print(
                f"   Common issues: Token problems, Docker not running, missing configuration"
            )

    def print_detailed_output(
        self, results: Dict[str, Dict[str, Tuple[bool, str, float]]]
    ):
        """Print detailed output from all tests"""
        print("\n" + "=" * 60)
        print("📝 DETAILED TEST OUTPUT")
        print("=" * 60)

        for category, category_results in results.items():
            print(f"\n📂 {category.upper()} Tests:")
            print("-" * 40)

            for test_file, (success, output, duration) in category_results.items():
                status = "✅ PASSED" if success else "❌ FAILED"
                print(f"\n▶️  {test_file} - {status} ({duration:.1f}s)")
                print("─" * 30)

                if output:
                    # Truncate very long output
                    if len(output) > 2000:
                        output = output[:2000] + "\n... (output truncated)"
                    print(output)
                else:
                    print("(No output)")


def main():
    parser = argparse.ArgumentParser(description="Run MoodleClaude manual tests")
    parser.add_argument(
        "--category",
        choices=["core", "advanced", "validation", "all"],
        default="all",
        help="Test category to run",
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Show detailed output from all tests"
    )
    parser.add_argument(
        "--list", action="store_true", help="List available tests and categories"
    )

    args = parser.parse_args()

    runner = ManualTestRunner()

    if args.list:
        print("📋 Available Test Categories:")
        for category, tests in runner.test_categories.items():
            print(f"\n{category.upper()}:")
            for test in tests:
                print(f"  - {test}")
        return

    # Run tests
    if args.category == "all":
        results = runner.run_all_tests()
    else:
        results = {args.category: runner.run_category(args.category)}

    # Print summary
    runner.print_summary(results)

    # Print detailed output if requested
    if args.detailed:
        runner.print_detailed_output(results)

    # Exit with appropriate code
    total_tests = sum(len(cat_results) for cat_results in results.values())
    total_passed = sum(
        sum(1 for success, _, _ in cat_results.values() if success)
        for cat_results in results.values()
    )

    if total_passed < total_tests:
        sys.exit(1)  # Exit with error if any tests failed


if __name__ == "__main__":
    main()
