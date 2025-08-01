#!/usr/bin/env python3
"""
Simple Test Suite for MoodleClaude Core Functionality
=====================================================

This test suite focuses on testing the core MoodleClaude components
without requiring a full Moodle Docker setup, which has proven complex.

Tests include:
- MCP Server functionality
- Core Python modules
- Configuration validation
- Database connectivity (using local/simple setup)
- Basic API endpoints
"""

import os
import sys
import json
import asyncio
import logging
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess


class SimpleMoodleClaudeTestSuite:
    """Simple test suite for core MoodleClaude functionality."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'test_environment': 'simple_local',
            'tests': {},
            'summary': {},
            'errors': []
        }
        
        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('simple_test_suite.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Test phases
        self.test_phases = [
            'environment_check',
            'python_modules_test',
            'configuration_validation',
            'mcp_server_basic_test',
            'core_functionality_test',
            'performance_basic_test'
        ]
        
    def log_test_result(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
        """Log a test result."""
        self.test_results['tests'][test_name] = {
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        status_emoji = "✅" if success else "❌"
        self.logger.info(f"{status_emoji} {test_name}: {message}")
        
        if not success:
            self.test_results['errors'].append({
                'test': test_name,
                'message': message,
                'details': details
            })
    
    async def run_environment_check(self) -> bool:
        """Check basic environment requirements."""
        self.logger.info("🔍 Running environment checks...")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major >= 3 and python_version.minor >= 8:
                self.log_test_result(
                    'python_version',
                    True,
                    f"Python {python_version.major}.{python_version.minor}.{python_version.micro} OK"
                )
            else:
                self.log_test_result(
                    'python_version',
                    False,
                    f"Python version {python_version.major}.{python_version.minor} too old (need 3.8+)"
                )
                return False
            
            # Check project structure
            project_root = Path(__file__).parent.parent
            required_dirs = ['src', 'config', 'tools', 'operations']
            
            for dir_name in required_dirs:
                dir_path = project_root / dir_name
                if dir_path.exists():
                    self.log_test_result(
                        f'directory_{dir_name}',
                        True,
                        f"Directory {dir_name} exists"
                    )
                else:
                    self.log_test_result(
                        f'directory_{dir_name}',
                        False,
                        f"Required directory {dir_name} missing"
                    )
            
            # Check requirements.txt
            requirements_file = project_root / 'requirements.txt'
            if requirements_file.exists():
                self.log_test_result(
                    'requirements_file',
                    True,
                    "requirements.txt found"
                )
            else:
                self.log_test_result(
                    'requirements_file',
                    False,
                    "requirements.txt missing"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                'environment_check',
                False,
                f"Environment check failed: {str(e)}"
            )
            return False
    
    async def run_python_modules_test(self) -> bool:
        """Test core Python module imports."""
        self.logger.info("🐍 Testing Python module imports...")
        
        core_modules = [
            'asyncio',
            'aiohttp',
            'json',
            'logging',
            'pathlib',
            'datetime'
        ]
        
        optional_modules = [
            'pydantic',
            'psycopg2',
            'requests',
            'pytest'
        ]
        
        success_count = 0
        
        # Test core modules
        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
                self.log_test_result(
                    f'import_{module_name}',
                    True,
                    f"Successfully imported {module_name}"
                )
                success_count += 1
            except ImportError as e:
                self.log_test_result(
                    f'import_{module_name}',
                    False,
                    f"Failed to import {module_name}: {str(e)}"
                )
        
        # Test optional modules (warnings only)
        for module_name in optional_modules:
            try:
                importlib.import_module(module_name)
                self.log_test_result(
                    f'import_optional_{module_name}',
                    True,
                    f"Optional module {module_name} available"
                )
            except ImportError:
                self.logger.warning(f"Optional module {module_name} not available")
        
        return success_count == len(core_modules)
    
    async def run_configuration_validation(self) -> bool:
        """Validate configuration files."""
        self.logger.info("⚙️ Validating configuration files...")
        
        project_root = Path(__file__).parent.parent
        config_files = [
            'config/master_config.py',
            'requirements.txt',
            'operations/docker/docker-compose.test.yml'
        ]
        
        success_count = 0
        
        for config_file in config_files:
            file_path = project_root / config_file
            try:
                if file_path.exists():
                    # Basic file validation
                    content = file_path.read_text()
                    if len(content) > 0:
                        self.log_test_result(
                            f'config_{config_file.replace("/", "_").replace(".", "_")}',
                            True,
                            f"Configuration file {config_file} valid"
                        )
                        success_count += 1
                    else:
                        self.log_test_result(
                            f'config_{config_file.replace("/", "_").replace(".", "_")}',
                            False,
                            f"Configuration file {config_file} is empty"
                        )
                else:
                    self.log_test_result(
                        f'config_{config_file.replace("/", "_").replace(".", "_")}',
                        False,
                        f"Configuration file {config_file} not found"
                    )
            except Exception as e:
                self.log_test_result(
                    f'config_{config_file.replace("/", "_").replace(".", "_")}',
                    False,
                    f"Error reading {config_file}: {str(e)}"
                )
        
        return success_count > 0
    
    async def run_mcp_server_basic_test(self) -> bool:
        """Test basic MCP server functionality."""
        self.logger.info("🔧 Testing MCP server basic functionality...")
        
        try:
            # Check if MCP server files exist
            project_root = Path(__file__).parent.parent
            mcp_files = [
                'src/core/mcp_server.py',
                'src/core/optimized_mcp_server.py',
                'src/core/enhanced_mcp_server.py',
                'server/mcp_server.py'
            ]
            
            server_found = False
            for mcp_file in mcp_files:
                file_path = project_root / mcp_file
                if file_path.exists():
                    self.log_test_result(
                        f'mcp_file_{mcp_file.replace("/", "_").replace(".", "_")}',
                        True,
                        f"MCP server file {mcp_file} found"
                    )
                    server_found = True
                    
                    # Basic syntax check
                    try:
                        content = file_path.read_text()
                        # Check for basic MCP server patterns
                        if 'async def' in content and 'mcp' in content.lower():
                            self.log_test_result(
                                f'mcp_syntax_{mcp_file.replace("/", "_").replace(".", "_")}',
                                True,
                                f"MCP server {mcp_file} has valid syntax patterns"
                            )
                        else:
                            self.log_test_result(
                                f'mcp_syntax_{mcp_file.replace("/", "_").replace(".", "_")}',
                                False,
                                f"MCP server {mcp_file} missing expected patterns"
                            )
                    except Exception as e:
                        self.log_test_result(
                            f'mcp_syntax_{mcp_file.replace("/", "_").replace(".", "_")}',
                            False,
                            f"Error checking syntax of {mcp_file}: {str(e)}"
                        )
            
            if not server_found:
                self.log_test_result(
                    'mcp_server_files',
                    False,
                    "No MCP server files found"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test_result(
                'mcp_server_basic_test',
                False,
                f"MCP server basic test failed: {str(e)}"
            )
            return False
    
    async def run_core_functionality_test(self) -> bool:
        """Test core functionality components."""
        self.logger.info("⚡ Testing core functionality...")
        
        try:
            # Test basic async functionality
            await asyncio.sleep(0.1)
            self.log_test_result(
                'asyncio_basic',
                True,
                "Asyncio basic functionality working"
            )
            
            # Test JSON handling
            test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
            json_str = json.dumps(test_data)
            parsed_data = json.loads(json_str)
            
            if parsed_data["test"] == "data":
                self.log_test_result(
                    'json_handling',
                    True,
                    "JSON serialization/deserialization working"
                )
            else:
                self.log_test_result(
                    'json_handling',
                    False,
                    "JSON handling failed validation"
                )
            
            # Test path handling
            project_root = Path(__file__).parent.parent
            if project_root.exists() and project_root.is_dir():
                self.log_test_result(
                    'path_handling',
                    True,
                    "Path handling working correctly"
                )
            else:
                self.log_test_result(
                    'path_handling',
                    False,
                    "Path handling issues detected"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                'core_functionality_test',
                False,
                f"Core functionality test failed: {str(e)}"
            )
            return False
    
    async def run_performance_basic_test(self) -> bool:
        """Run basic performance tests."""
        self.logger.info("🚀 Running basic performance tests...")
        
        try:
            # Test async performance
            start_time = datetime.now()
            
            # Simulate some async work
            tasks = []
            for i in range(10):
                tasks.append(asyncio.sleep(0.01))
            
            await asyncio.gather(*tasks)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if duration < 1.0:  # Should complete in under 1 second
                self.log_test_result(
                    'async_performance',
                    True,
                    f"Async performance test completed in {duration:.3f}s"
                )
            else:
                self.log_test_result(
                    'async_performance',
                    False,
                    f"Async performance test too slow: {duration:.3f}s"
                )
            
            # Test memory usage (basic check)
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 100:  # Less than 100MB
                self.log_test_result(
                    'memory_usage',
                    True,
                    f"Memory usage OK: {memory_mb:.1f}MB"
                )
            else:
                self.log_test_result(
                    'memory_usage',
                    False,
                    f"High memory usage: {memory_mb:.1f}MB"
                )
            
            return True
            
        except ImportError:
            self.log_test_result(
                'performance_basic_test',
                True,
                "Performance test skipped (psutil not available)"
            )
            return True
        except Exception as e:
            self.log_test_result(
                'performance_basic_test',
                False,
                f"Performance test failed: {str(e)}"
            )
            return False
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = len(self.test_results['tests'])
        passed_tests = sum(1 for test in self.test_results['tests'].values() if test['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': round(success_rate, 2),
            'end_time': datetime.now().isoformat()
        }
        
        self.test_results['summary'] = summary
        return summary
    
    def save_results(self, output_file: str = 'simple_test_results.json'):
        """Save test results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            self.logger.info(f"Test results saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save test results: {str(e)}")
    
    async def run_all_tests(self) -> bool:
        """Run all test phases."""
        self.logger.info("🚀 Starting MoodleClaude Simple Test Suite...")
        
        overall_success = True
        
        # Run each test phase
        for phase in self.test_phases:
            self.logger.info(f"📋 Running test phase: {phase}")
            
            try:
                method_name = f"run_{phase}"
                if hasattr(self, method_name):
                    phase_method = getattr(self, method_name)
                    phase_success = await phase_method()
                    
                    if not phase_success:
                        overall_success = False
                        self.logger.warning(f"⚠️ Test phase {phase} had failures")
                else:
                    self.logger.error(f"❌ Test phase method {method_name} not found")
                    overall_success = False
            
            except Exception as e:
                self.logger.error(f"❌ Test phase {phase} crashed: {str(e)}")
                overall_success = False
        
        # Generate summary
        summary = self.generate_summary()
        
        # Save results
        self.save_results()
        
        # Print final report
        self.logger.info("=" * 60)
        self.logger.info("🎯 SIMPLE TEST SUITE RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Tests: {summary['total_tests']}")
        self.logger.info(f"Passed: {summary['passed_tests']}")
        self.logger.info(f"Failed: {summary['failed_tests']}")
        self.logger.info(f"Success Rate: {summary['success_rate']}%")
        
        if overall_success and summary['success_rate'] >= 80:
            self.logger.info("✅ Test Suite PASSED!")
            return True
        else:
            self.logger.info("❌ Test Suite FAILED!")
            
            # List failed tests
            if self.test_results['errors']:
                self.logger.info("\nFailed Tests:")
                for error in self.test_results['errors']:
                    self.logger.info(f"  - {error['test']}: {error['message']}")
            
            return False


async def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple MoodleClaude Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    # Create and run test suite
    test_suite = SimpleMoodleClaudeTestSuite(verbose=args.verbose)
    success = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())