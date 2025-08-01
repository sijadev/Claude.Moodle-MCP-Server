#!/usr/bin/env python3
"""
Persistent Test Suite für MoodleClaude
=====================================

Erweiterte Test-Suite mit lokaler Datenspeicherung für:
- Test-Ergebnisse und Verlauf
- Performance-Benchmarks
- Konfigurationscaching
- Trend-Analyse
"""

import asyncio
import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.test_data_storage import (
    BenchmarkData,
    TestDataStorage,
    TestResult,
    create_test_data_storage,
)


class PersistentMoodleClaudeTestSuite:
    """Test suite with persistent local data storage."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.storage = create_test_data_storage()

        # Test session ID
        self.session_id = hashlib.md5(
            f"{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]

        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("persistent_test_suite.log"),
            ],
        )
        self.logger = logging.getLogger(__name__)

        # Current test run data
        self.current_run = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "environment": "persistent_local",
            "version": "3.0.0",
            "tests": {},
            "benchmarks": [],
        }

    def log_and_store_test_result(
        self,
        test_name: str,
        success: bool,
        message: str,
        duration: float = 0.0,
        details: Optional[Dict] = None,
    ):
        """Log and store test result with persistence."""
        # Create test result
        test_id = f"{self.session_id}_{test_name}"
        result = TestResult(
            test_id=test_id,
            test_name=test_name,
            success=success,
            duration=duration,
            timestamp=datetime.now().isoformat(),
            details=details or {},
            environment=self.current_run["environment"],
            version=self.current_run["version"],
        )

        # Store in database
        self.storage.store_test_result(result)

        # Store in current run
        self.current_run["tests"][test_name] = {
            "success": success,
            "message": message,
            "duration": duration,
            "details": details or {},
        }

        # Log to console
        status_emoji = "✅" if success else "❌"
        duration_str = f" ({duration:.3f}s)" if duration > 0 else ""
        self.logger.info(f"{status_emoji} {test_name}: {message}{duration_str}")

    def store_benchmark(
        self,
        test_name: str,
        metric_name: str,
        value: float,
        unit: str = "seconds",
        metadata: Optional[Dict] = None,
    ):
        """Store performance benchmark data."""
        benchmark_id = f"{self.session_id}_{test_name}_{metric_name}"
        benchmark = BenchmarkData(
            benchmark_id=benchmark_id,
            test_name=test_name,
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            environment=self.current_run["environment"],
            metadata=metadata or {},
        )

        self.storage.store_benchmark(benchmark)
        self.current_run["benchmarks"].append(
            {
                "test_name": test_name,
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
            }
        )

    async def run_environment_check_with_persistence(self) -> bool:
        """Environment check with historical comparison."""
        self.logger.info("🔍 Running persistent environment checks...")

        start_time = time.time()

        try:
            # Check previous results for comparison
            previous_results = self.storage.get_test_results(
                test_name="environment_check", since=datetime.now() - timedelta(days=7)
            )

            # Basic environment checks
            success_count = 0
            total_checks = 0

            # Python version check
            total_checks += 1
            python_version = sys.version_info
            if python_version.major >= 3 and python_version.minor >= 8:
                success_count += 1
                self.log_and_store_test_result(
                    "python_version_check",
                    True,
                    f"Python {python_version.major}.{python_version.minor}.{python_version.micro}",
                    details={
                        "version": f"{python_version.major}.{python_version.minor}.{python_version.micro}"
                    },
                )
            else:
                self.log_and_store_test_result(
                    "python_version_check",
                    False,
                    f"Python version too old: {python_version.major}.{python_version.minor}",
                )

            # Directory structure check
            project_root = Path(__file__).parent.parent
            required_dirs = ["src", "config", "tools", "operations"]

            for dir_name in required_dirs:
                total_checks += 1
                dir_path = project_root / dir_name
                if dir_path.exists():
                    success_count += 1
                    self.log_and_store_test_result(
                        f"directory_{dir_name}",
                        True,
                        f"Directory {dir_name} exists",
                        details={"path": str(dir_path)},
                    )
                else:
                    self.log_and_store_test_result(
                        f"directory_{dir_name}",
                        False,
                        f"Required directory {dir_name} missing",
                    )

            # Storage system check
            total_checks += 1
            try:
                # Test storage functionality
                test_data = {
                    "test": "storage_check",
                    "timestamp": datetime.now().isoformat(),
                }
                if self.storage.store_json_data("storage_test", test_data):
                    loaded_data = self.storage.load_json_data("storage_test")
                    if loaded_data and loaded_data.get("test") == "storage_check":
                        success_count += 1
                        self.log_and_store_test_result(
                            "storage_system_check",
                            True,
                            "Storage system working",
                            details={"storage_dir": str(self.storage.storage_dir)},
                        )
                    else:
                        self.log_and_store_test_result(
                            "storage_system_check",
                            False,
                            "Storage system data integrity issue",
                        )
                else:
                    self.log_and_store_test_result(
                        "storage_system_check", False, "Storage system write failed"
                    )
            except Exception as e:
                self.log_and_store_test_result(
                    "storage_system_check", False, f"Storage system error: {str(e)}"
                )

            duration = time.time() - start_time

            # Store overall environment check result
            overall_success = success_count == total_checks
            self.log_and_store_test_result(
                "environment_check",
                overall_success,
                f"Environment check: {success_count}/{total_checks} passed",
                duration=duration,
                details={
                    "total_checks": total_checks,
                    "passed_checks": success_count,
                    "previous_runs": len(previous_results),
                },
            )

            # Store benchmark
            self.store_benchmark(
                "environment_check", "check_duration", duration, "seconds"
            )

            return overall_success

        except Exception as e:
            duration = time.time() - start_time
            self.log_and_store_test_result(
                "environment_check",
                False,
                f"Environment check failed: {str(e)}",
                duration=duration,
            )
            return False

    async def run_module_import_tests_with_benchmarks(self) -> bool:
        """Module import tests with performance benchmarking."""
        self.logger.info("🐍 Running module import tests with benchmarks...")

        import importlib

        core_modules = ["asyncio", "aiohttp", "json", "logging", "pathlib", "datetime"]

        optional_modules = ["pydantic", "requests", "pytest", "sqlite3"]

        success_count = 0
        total_imports = 0

        for module_name in core_modules:
            total_imports += 1
            start_time = time.time()

            try:
                importlib.import_module(module_name)
                duration = time.time() - start_time
                success_count += 1

                self.log_and_store_test_result(
                    f"import_{module_name}",
                    True,
                    f"Successfully imported {module_name}",
                    duration=duration,
                )

                # Store import time benchmark
                self.store_benchmark(
                    f"import_{module_name}",
                    "import_time",
                    duration,
                    "seconds",
                    {"module_type": "core"},
                )

            except ImportError as e:
                duration = time.time() - start_time
                self.log_and_store_test_result(
                    f"import_{module_name}",
                    False,
                    f"Failed to import {module_name}: {str(e)}",
                    duration=duration,
                )

        # Test optional modules (non-critical)
        for module_name in optional_modules:
            start_time = time.time()
            try:
                importlib.import_module(module_name)
                duration = time.time() - start_time
                self.log_and_store_test_result(
                    f"import_optional_{module_name}",
                    True,
                    f"Optional module {module_name} available",
                    duration=duration,
                )
                self.store_benchmark(
                    f"import_{module_name}",
                    "import_time",
                    duration,
                    "seconds",
                    {"module_type": "optional"},
                )
            except ImportError:
                duration = time.time() - start_time
                self.logger.warning(f"Optional module {module_name} not available")

        return success_count == len(core_modules)

    async def run_performance_benchmarks(self) -> bool:
        """Run comprehensive performance benchmarks."""
        self.logger.info("🚀 Running performance benchmarks...")

        try:
            # Async performance test
            start_time = time.time()
            tasks = [asyncio.sleep(0.01) for _ in range(20)]
            await asyncio.gather(*tasks)
            async_duration = time.time() - start_time

            self.log_and_store_test_result(
                "async_performance_test",
                async_duration < 1.0,
                f"Async performance: {async_duration:.3f}s",
                duration=async_duration,
            )

            self.store_benchmark(
                "async_performance_test",
                "execution_time",
                async_duration,
                "seconds",
                {"concurrent_tasks": 20},
            )

            # JSON processing benchmark
            test_data = {"data": list(range(1000)), "metadata": {"test": True}}

            start_time = time.time()
            json_str = json.dumps(test_data)
            serialize_duration = time.time() - start_time

            start_time = time.time()
            parsed_data = json.loads(json_str)
            deserialize_duration = time.time() - start_time

            json_success = parsed_data.get("metadata", {}).get("test") is True
            total_json_time = serialize_duration + deserialize_duration

            self.log_and_store_test_result(
                "json_processing_benchmark",
                json_success,
                f"JSON processing: {total_json_time:.4f}s",
                duration=total_json_time,
            )

            self.store_benchmark(
                "json_processing", "serialize_time", serialize_duration, "seconds"
            )
            self.store_benchmark(
                "json_processing", "deserialize_time", deserialize_duration, "seconds"
            )

            # File I/O benchmark
            test_file = Path("benchmark_test.tmp")
            test_content = "Benchmark test content\n" * 100

            start_time = time.time()
            test_file.write_text(test_content)
            write_duration = time.time() - start_time

            start_time = time.time()
            read_content = test_file.read_text()
            read_duration = time.time() - start_time

            # Cleanup
            test_file.unlink(missing_ok=True)

            io_success = read_content == test_content
            self.log_and_store_test_result(
                "file_io_benchmark",
                io_success,
                f"File I/O: write {write_duration:.4f}s, read {read_duration:.4f}s",
                duration=write_duration + read_duration,
            )

            self.store_benchmark("file_io", "write_time", write_duration, "seconds")
            self.store_benchmark("file_io", "read_time", read_duration, "seconds")

            return True

        except Exception as e:
            self.log_and_store_test_result(
                "performance_benchmarks",
                False,
                f"Performance benchmark failed: {str(e)}",
            )
            return False

    def analyze_test_trends(self) -> Dict[str, Any]:
        """Analyze test trends from historical data."""
        self.logger.info("📊 Analyzing test trends...")

        try:
            # Get recent test results
            recent_results = self.storage.get_test_results(
                since=datetime.now() - timedelta(days=30)
            )

            # Get benchmark data
            recent_benchmarks = self.storage.get_benchmarks()

            # Analyze trends
            trend_analysis = {
                "total_test_runs": len(recent_results),
                "success_rate_trend": [],
                "performance_trends": {},
                "most_failing_tests": {},
                "performance_regression": [],
            }

            # Group by day for trend analysis
            daily_results = {}
            for result in recent_results:
                date = result.timestamp[:10]  # YYYY-MM-DD
                if date not in daily_results:
                    daily_results[date] = {"total": 0, "passed": 0}
                daily_results[date]["total"] += 1
                if result.success:
                    daily_results[date]["passed"] += 1

            # Calculate daily success rates
            for date, stats in daily_results.items():
                success_rate = (
                    (stats["passed"] / stats["total"] * 100)
                    if stats["total"] > 0
                    else 0
                )
                trend_analysis["success_rate_trend"].append(
                    {
                        "date": date,
                        "success_rate": success_rate,
                        "total_tests": stats["total"],
                    }
                )

            # Analyze performance trends
            benchmark_groups = {}
            for benchmark in recent_benchmarks:
                key = f"{benchmark.test_name}_{benchmark.metric_name}"
                if key not in benchmark_groups:
                    benchmark_groups[key] = []
                benchmark_groups[key].append(benchmark)

            for key, benchmarks in benchmark_groups.items():
                if len(benchmarks) >= 2:
                    # Sort by timestamp
                    benchmarks.sort(key=lambda x: x.timestamp)
                    latest = benchmarks[-1]
                    previous = benchmarks[-2]

                    change_percent = (
                        ((latest.value - previous.value) / previous.value * 100)
                        if previous.value > 0
                        else 0
                    )

                    trend_analysis["performance_trends"][key] = {
                        "latest_value": latest.value,
                        "previous_value": previous.value,
                        "change_percent": change_percent,
                        "unit": latest.unit,
                    }

                    # Flag regressions (performance getting worse)
                    if abs(change_percent) > 20:  # More than 20% change
                        trend_analysis["performance_regression"].append(
                            {
                                "test": key,
                                "change_percent": change_percent,
                                "latest_value": latest.value,
                                "unit": latest.unit,
                            }
                        )

            # Store trend analysis
            self.storage.store_json_data(
                f"trend_analysis_{self.session_id}", trend_analysis
            )

            return trend_analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze trends: {e}")
            return {}

    async def run_all_tests(self) -> bool:
        """Run all test phases with persistence."""
        self.logger.info("🚀 Starting Persistent MoodleClaude Test Suite...")

        overall_success = True

        # Run test phases
        test_phases = [
            ("Environment Check", self.run_environment_check_with_persistence),
            ("Module Import Tests", self.run_module_import_tests_with_benchmarks),
            ("Performance Benchmarks", self.run_performance_benchmarks),
        ]

        for phase_name, phase_method in test_phases:
            self.logger.info(f"📋 Running: {phase_name}")

            try:
                phase_success = await phase_method()
                if not phase_success:
                    overall_success = False
                    self.logger.warning(f"⚠️ {phase_name} had failures")
            except Exception as e:
                self.logger.error(f"❌ {phase_name} crashed: {str(e)}")
                overall_success = False

        # Analyze trends
        trend_analysis = self.analyze_test_trends()

        # Store current run data
        self.current_run["end_time"] = datetime.now().isoformat()
        self.current_run["overall_success"] = overall_success
        self.current_run["trend_analysis"] = trend_analysis

        # Save to storage
        self.storage.store_json_data(f"test_run_{self.session_id}", self.current_run)

        # Get and display statistics
        stats = self.storage.get_test_statistics()

        self.logger.info("=" * 60)
        self.logger.info("🎯 PERSISTENT TEST SUITE RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Current Run Success: {'✅' if overall_success else '❌'}")
        self.logger.info(f"Total Historical Tests: {stats.get('total_tests', 0)}")
        self.logger.info(f"Overall Success Rate: {stats.get('success_rate', 0):.1f}%")

        if trend_analysis.get("performance_regression"):
            self.logger.warning("⚠️ Performance Regressions Detected:")
            for regression in trend_analysis["performance_regression"]:
                self.logger.warning(
                    f"  - {regression['test']}: {regression['change_percent']:+.1f}%"
                )

        return overall_success


async def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Persistent MoodleClaude Test Suite")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Cleanup old test data (30+ days)"
    )
    parser.add_argument("--snapshot", type=str, help="Create snapshot of test data")
    parser.add_argument(
        "--stats", action="store_true", help="Show test statistics only"
    )
    args = parser.parse_args()

    # Create test suite
    test_suite = PersistentMoodleClaudeTestSuite(verbose=args.verbose)

    # Handle special operations
    if args.cleanup:
        print("🧹 Cleaning up old test data...")
        test_suite.storage.cleanup_old_data(days=30)
        return

    if args.snapshot:
        print(f"📸 Creating snapshot: {args.snapshot}")
        test_suite.storage.create_snapshot(args.snapshot)
        return

    if args.stats:
        stats = test_suite.storage.get_test_statistics()
        print("📊 Test Statistics:")
        print(json.dumps(stats, indent=2))
        return

    # Run tests
    success = await test_suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
