#!/usr/bin/env python3
"""
Test runner script for MCP Moodle Course Creator
Provides convenient test execution with different configurations
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle output"""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print(f"{'='*60}")

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print(f"❌ {description} failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"✅ {description} completed successfully")

    return result


def main():
    parser = argparse.ArgumentParser(description="Test runner for MCP Moodle Course Creator")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run only end-to-end tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML test report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument(
        "--install-deps", action="store_true", help="Install test dependencies first"
    )
    parser.add_argument("test_files", nargs="*", help="Specific test files to run")

    args = parser.parse_args()

    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Install test dependencies if requested
    if args.install_deps:
        run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"],
            "Installing test dependencies",
        )

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
        if args.html:
            cmd.append("--cov-report=html")

    # Add HTML report
    if args.html:
        cmd.extend(["--html=test-reports/report.html", "--self-contained-html"])

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])

    # Add test type filters
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    elif args.e2e:
        cmd.extend(["-m", "e2e"])

    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])

    # Add specific test files
    if args.test_files:
        cmd.extend(args.test_files)
    else:
        cmd.append("tests/")

    # Create test reports directory
    os.makedirs("test-reports", exist_ok=True)

    # Run tests
    run_command(cmd, "Running tests")

    print(f"\n{'='*60}")
    print("  🎉 All tests completed successfully!")
    print(f"{'='*60}")

    # Show coverage report location if generated
    if args.coverage and args.html:
        coverage_path = project_root / "htmlcov" / "index.html"
        print(f"\n📊 Coverage report: {coverage_path}")

    # Show HTML report location if generated
    if args.html:
        report_path = project_root / "test-reports" / "report.html"
        print(f"📋 Test report: {report_path}")


if __name__ == "__main__":
    main()
