#!/usr/bin/env python3
"""
Comprehensive Test Runner for MoodleClaude

Runs all types of tests: unit, integration, manual, and E2E
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


class ComprehensiveTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}

    def run_command(
        self, command: list, description: str, timeout: int = 300
    ) -> tuple[bool, str]:
        """Run a command and return success status and output"""
        print(f"\n🔧 {description}")
        print("=" * 60)

        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            duration = time.time() - start_time
            success = result.returncode == 0
            output = result.stdout + result.stderr

            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} ({duration:.1f}s)")

            return success, output

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"❌ TIMEOUT ({duration:.1f}s)")
            return False, f"Command timed out after {duration:.1f} seconds"
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ ERROR ({duration:.1f}s): {e}")
            return False, str(e)

    def run_unit_tests(self) -> bool:
        """Run unit tests"""
        success, output = self.run_command(
            ["uv", "run", "pytest", "tests/unit/", "-v"], "Running Unit Tests"
        )
        self.test_results["unit"] = (success, output)
        return success

    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        success, output = self.run_command(
            ["uv", "run", "pytest", "tests/integration/", "-v"],
            "Running Integration Tests",
        )
        self.test_results["integration"] = (success, output)
        return success

    def run_manual_tests(self, category: str = "all") -> bool:
        """Run manual tests"""
        success, output = self.run_command(
            ["python", "tests/manual/run_manual_tests.py", "--category", category],
            f"Running Manual Tests ({category})",
        )
        self.test_results["manual"] = (success, output)
        return success

    def run_e2e_tests(self) -> bool:
        """Run E2E tests"""
        e2e_script = self.project_root / "scripts" / "run_e2e_tests.sh"

        if not e2e_script.exists():
            print("\n⚠️  E2E test script not found, skipping...")
            self.test_results["e2e"] = (True, "E2E tests skipped - script not found")
            return True

        success, output = self.run_command(
            ["bash", str(e2e_script), "--headless"],
            "Running E2E Tests",
            timeout=600,  # 10 minutes for E2E
        )
        self.test_results["e2e"] = (success, output)
        return success

    def check_environment(self) -> bool:
        """Check if the environment is properly set up"""
        print("\n🔍 Checking Environment")
        print("=" * 60)

        checks = []

        # Check Docker containers
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=moodleclaude"],
                capture_output=True,
                text=True,
            )
            if "moodleclaude_app" in result.stdout:
                print("✅ Docker containers running")
                checks.append(True)
            else:
                print("❌ Docker containers not running")
                checks.append(False)
        except:
            print("❌ Docker not available")
            checks.append(False)

        # Check .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            print("✅ .env file exists")
            checks.append(True)
        else:
            print("❌ .env file missing")
            checks.append(False)

        # Check MCP server dependencies
        try:
            result = subprocess.run(
                ["uv", "run", "python", "-c", "import mcp_server"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("✅ MCP server dependencies available")
                checks.append(True)
            else:
                print("❌ MCP server dependencies missing")
                checks.append(False)
        except:
            print("❌ Cannot check MCP server dependencies")
            checks.append(False)

        return all(checks)

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)

        total_suites = len(self.test_results)
        passed_suites = sum(1 for success, _ in self.test_results.values() if success)

        print(f"\n🎯 Test Suite Results:")
        for suite_name, (success, output) in self.test_results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status} {suite_name.upper()} tests")

        print(f"\n📈 Overall Statistics:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed")
        print(f"   Success Rate: {(passed_suites/total_suites*100):.1f}%")

        if passed_suites == total_suites:
            print(f"\n🎉 All test suites passed! MoodleClaude is fully validated.")
        else:
            print(f"\n⚠️  Some test suites failed. Check detailed output for debugging.")

    def print_detailed_output(self):
        """Print detailed output from all test suites"""
        print("\n" + "=" * 60)
        print("📝 DETAILED TEST OUTPUT")
        print("=" * 60)

        for suite_name, (success, output) in self.test_results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"\n📂 {suite_name.upper()} Tests - {status}")
            print("-" * 40)

            if output:
                # Truncate very long output
                if len(output) > 3000:
                    output = output[:3000] + "\n... (output truncated)"
                print(output)
            else:
                print("(No output)")


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive MoodleClaude tests")
    parser.add_argument(
        "--suite",
        choices=["unit", "integration", "manual", "e2e", "all"],
        default="all",
        help="Test suite to run",
    )
    parser.add_argument(
        "--manual-category",
        choices=["core", "advanced", "validation", "all"],
        default="all",
        help="Manual test category",
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Show detailed output from all tests"
    )
    parser.add_argument(
        "--skip-env-check", action="store_true", help="Skip environment validation"
    )

    args = parser.parse_args()

    runner = ComprehensiveTestRunner()

    print("🧪 MoodleClaude Comprehensive Test Runner")
    print("=" * 60)

    # Check environment unless skipped
    if not args.skip_env_check:
        if not runner.check_environment():
            print("\n⚠️  Environment issues detected. Tests may fail.")
            print("   Consider running: docker-compose up -d")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != "y":
                sys.exit(1)

    # Run requested test suites
    success_count = 0
    total_count = 0

    if args.suite in ["unit", "all"]:
        total_count += 1
        if runner.run_unit_tests():
            success_count += 1

    if args.suite in ["integration", "all"]:
        total_count += 1
        if runner.run_integration_tests():
            success_count += 1

    if args.suite in ["manual", "all"]:
        total_count += 1
        if runner.run_manual_tests(args.manual_category):
            success_count += 1

    if args.suite in ["e2e", "all"]:
        total_count += 1
        if runner.run_e2e_tests():
            success_count += 1

    # Print summary
    runner.print_summary()

    # Print detailed output if requested
    if args.detailed:
        runner.print_detailed_output()

    # Exit with appropriate code
    if success_count < total_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
