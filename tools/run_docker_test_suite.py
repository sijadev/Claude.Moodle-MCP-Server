#!/usr/bin/env python3
"""
MoodleClaude Docker Test Suite Runner
====================================
Creates isolated Docker test environment, runs comprehensive tests, and cleans up
"""

import os
import sys
import subprocess
import time
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class DockerTestSuiteRunner:
    """Orchestrates Docker-based test environment and test execution"""
    
    def __init__(self, keep_environment: bool = False, verbose: bool = False):
        self.project_root = PROJECT_ROOT
        self.keep_environment = keep_environment
        self.verbose = verbose
        
        # Docker configuration
        self.compose_file = self.project_root / "operations" / "docker" / "docker-compose.test.yml"
        self.test_network = "moodle_test_network"
        self.test_containers = [
            "moodle_postgres_test",
            "moodle_app_test", 
            "pgladmin_test",
            "moodleclaude_test_runner"
        ]
        
        # Test results
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'phases': {},
            'summary': {},
            'environment_info': {}
        }
        
        # Ensure required directories exist
        self._setup_directories()
    
    def _setup_directories(self):
        """Setup required directories"""
        directories = [
            self.project_root / "test-results",
            self.project_root / "logs",
            self.project_root / "operations" / "test"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def log_phase(self, phase: str, success: bool, message: str, details: Dict = None):
        """Log test phase results"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'message': message,
            'details': details or {}
        }
        
        self.test_results['phases'][phase] = result
        
        status = "✅" if success else "❌"
        logger.info(f"{status} {phase}: {message}")
    
    def run_command(self, cmd: str, description: str = "", capture_output: bool = True, 
                   timeout: int = 300) -> subprocess.CompletedProcess:
        """Run shell command with proper error handling"""
        logger.info(f"🔧 {description}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root,
                timeout=timeout
            )
            
            if self.verbose and result.stdout:
                logger.info(f"Output: {result.stdout[:500]}")
            
            if result.returncode != 0 and result.stderr:
                logger.error(f"Error: {result.stderr[:500]}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {cmd}")
            raise
        except Exception as e:
            logger.error(f"Command failed: {cmd} - {str(e)}")
            raise
    
    def check_docker_availability(self) -> bool:
        """Check if Docker and Docker Compose are available"""
        logger.info("🐳 Checking Docker availability...")
        
        try:
            # Check Docker
            result = self.run_command("docker --version", "Checking Docker")
            if result.returncode != 0:
                self.log_phase("docker_check", False, "Docker not available")
                return False
            
            # Check Docker Compose
            result = self.run_command("docker-compose --version", "Checking Docker Compose")
            if result.returncode != 0:
                self.log_phase("docker_compose_check", False, "Docker Compose not available")
                return False
            
            # Check Docker daemon
            result = self.run_command("docker info", "Checking Docker daemon")
            if result.returncode != 0:
                self.log_phase("docker_daemon_check", False, "Docker daemon not running")
                return False
            
            self.log_phase("docker_availability", True, "Docker environment ready")
            return True
            
        except Exception as e:
            self.log_phase("docker_availability", False, f"Docker check failed: {str(e)}")
            return False
    
    def cleanup_existing_environment(self) -> bool:
        """Cleanup any existing test environment"""
        logger.info("🧹 Cleaning up existing test environment...")
        
        try:
            # Stop and remove containers
            cleanup_cmd = f"docker-compose -f {self.compose_file} down -v --remove-orphans"
            result = self.run_command(cleanup_cmd, "Stopping existing containers", timeout=120)
            
            # Force remove containers if they exist
            for container in self.test_containers:
                self.run_command(f"docker rm -f {container}", f"Force removing {container}", 
                               capture_output=True)
            
            # Remove test network if it exists
            self.run_command(f"docker network rm {self.test_network}", 
                           "Removing test network", capture_output=True)
            
            # Remove test volumes
            volume_patterns = [
                "moodle_postgres_test_data",
                "moodle_test_data", 
                "moodle_test_files",
                "pgladmin_test_data",
                "moodleclaude_test_results",
                "moodleclaude_test_logs"
            ]
            
            for volume in volume_patterns:
                self.run_command(f"docker volume rm {volume}", 
                               f"Removing volume {volume}", capture_output=True)
            
            self.log_phase("cleanup_existing", True, "Existing environment cleaned up")
            return True
            
        except Exception as e:
            self.log_phase("cleanup_existing", False, f"Cleanup failed: {str(e)}")
            return False
    
    def create_test_environment(self) -> bool:
        """Create fresh test environment"""
        logger.info("🏗️  Creating test environment...")
        
        try:
            # Build test runner image if needed
            build_cmd = f"docker-compose -f {self.compose_file} build test_runner"
            result = self.run_command(build_cmd, "Building test runner image", timeout=600)
            
            if result.returncode != 0:
                self.log_phase("build_test_image", False, "Failed to build test runner image")
                return False
            
            # Start database and Moodle services
            services_cmd = f"docker-compose -f {self.compose_file} up -d postgres_test moodle_test"
            result = self.run_command(services_cmd, "Starting database and Moodle services", timeout=300)
            
            if result.returncode != 0:
                self.log_phase("start_services", False, "Failed to start services")
                return False
            
            # Wait for services to be healthy
            if not self._wait_for_services():
                return False
            
            self.log_phase("create_environment", True, "Test environment created successfully")
            return True
            
        except Exception as e:
            self.log_phase("create_environment", False, f"Environment creation failed: {str(e)}")
            return False
    
    def _wait_for_services(self, timeout: int = 300) -> bool:
        """Wait for services to be healthy"""
        logger.info("⏳ Waiting for services to be ready...")
        
        services = ["postgres_test", "moodle_test"]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service in services:
                health_cmd = f"docker-compose -f {self.compose_file} ps {service}"
                result = self.run_command(health_cmd, f"Checking {service} health", 
                                        capture_output=True)
                
                if result.returncode != 0 or "healthy" not in result.stdout.lower():
                    all_healthy = False
                    break
            
            if all_healthy:
                self.log_phase("services_ready", True, "All services are healthy")
                return True
            
            time.sleep(10)
        
        self.log_phase("services_ready", False, f"Services not ready after {timeout}s")
        return False
    
    def run_test_suite(self) -> bool:
        """Run the comprehensive test suite"""
        logger.info("🧪 Running comprehensive test suite...")
        
        try:
            # Run test container
            test_cmd = f"docker-compose -f {self.compose_file} run --rm test_runner"
            result = self.run_command(test_cmd, "Running test suite", 
                                    capture_output=False, timeout=1800)  # 30 minutes
            
            success = result.returncode == 0
            
            if success:
                self.log_phase("test_execution", True, "Test suite completed successfully")
            else:
                self.log_phase("test_execution", False, "Test suite failed")
            
            # Copy test results from volume
            self._copy_test_results()
            
            return success
            
        except subprocess.TimeoutExpired:
            self.log_phase("test_execution", False, "Test suite timed out")
            return False
        except Exception as e:
            self.log_phase("test_execution", False, f"Test execution failed: {str(e)}")
            return False
    
    def _copy_test_results(self):
        """Copy test results from Docker volume to host"""
        logger.info("📋 Copying test results...")
        
        try:
            # Create temporary container to access volume
            temp_container = "moodleclaude_results_copy"
            
            # Create container with volume mounted
            create_cmd = f"docker create --name {temp_container} -v moodleclaude_test_results:/data alpine"
            self.run_command(create_cmd, "Creating temporary container for results copy")
            
            # Copy results
            results_dir = self.project_root / "test-results"
            copy_cmd = f"docker cp {temp_container}:/data/. {results_dir}/"
            self.run_command(copy_cmd, "Copying test results")
            
            # Copy logs
            logs_dir = self.project_root / "logs"
            logs_copy_cmd = f"docker cp {temp_container}:/app/logs/. {logs_dir}/"
            self.run_command(logs_copy_cmd, "Copying test logs", capture_output=True)
            
            # Cleanup temporary container
            self.run_command(f"docker rm {temp_container}", "Removing temporary container")
            
            self.log_phase("copy_results", True, "Test results copied successfully")
            
        except Exception as e:
            self.log_phase("copy_results", False, f"Failed to copy results: {str(e)}")
    
    def analyze_test_results(self) -> Dict[str, Any]:
        """Analyze test results and generate summary"""
        logger.info("📊 Analyzing test results...")
        
        try:
            results_file = self.project_root / "test-results" / "test_report.json"
            
            if results_file.exists():
                with open(results_file, 'r') as f:
                    test_data = json.load(f)
                
                summary = test_data.get('summary', {})
                
                analysis = {
                    'total_tests': summary.get('total_tests', 0),
                    'passed_tests': summary.get('passed_tests', 0),
                    'failed_tests': summary.get('failed_tests', 0),
                    'success_rate': summary.get('success_rate', 0),
                    'test_results_available': True,
                    'critical_failures': self._identify_critical_failures(test_data)
                }
                
                self.log_phase("analyze_results", True, 
                             f"Analysis complete: {analysis['success_rate']:.1f}% success rate",
                             analysis)
                
                return analysis
            else:
                self.log_phase("analyze_results", False, "No test results file found")
                return {'test_results_available': False}
                
        except Exception as e:
            self.log_phase("analyze_results", False, f"Analysis failed: {str(e)}")
            return {'analysis_error': str(e)}
    
    def _identify_critical_failures(self, test_data: Dict) -> List[str]:
        """Identify critical test failures"""
        critical_failures = []
        
        critical_tests = [
            'env_python_version',
            'moodle_connectivity', 
            'mcp_server_functionality',
            'plugin_installation'
        ]
        
        tests = test_data.get('tests', {})
        for test_name in critical_tests:
            if test_name in tests and not tests[test_name].get('success', False):
                critical_failures.append(test_name)
        
        return critical_failures
    
    def cleanup_test_environment(self) -> bool:
        """Cleanup test environment"""
        if self.keep_environment:
            logger.info("🔧 Keeping test environment as requested")
            self.log_phase("cleanup", True, "Environment kept for debugging")
            return True
        
        logger.info("🧹 Cleaning up test environment...")
        
        try:
            # Stop and remove all test containers and volumes
            cleanup_cmd = f"docker-compose -f {self.compose_file} down -v --remove-orphans"
            result = self.run_command(cleanup_cmd, "Cleaning up test environment", timeout=120)
            
            if result.returncode == 0:
                self.log_phase("cleanup", True, "Test environment cleaned up successfully")
                return True
            else:
                self.log_phase("cleanup", False, "Cleanup completed with warnings")
                return False
                
        except Exception as e:
            self.log_phase("cleanup", False, f"Cleanup failed: {str(e)}")
            return False
    
    def generate_final_report(self, analysis: Dict[str, Any]):
        """Generate final comprehensive report"""
        logger.info("📄 Generating final report...")
        
        self.test_results['summary'] = analysis
        self.test_results['end_time'] = datetime.now().isoformat()
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.test_results['start_time'])
        end_time = datetime.fromisoformat(self.test_results['end_time'])
        duration = end_time - start_time
        
        self.test_results['duration_seconds'] = duration.total_seconds()
        
        # Save Docker test runner report
        runner_report_path = self.project_root / "test-results" / "docker_test_runner_report.json"
        with open(runner_report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Generate console summary
        self._print_final_summary(analysis, duration)
    
    def _print_final_summary(self, analysis: Dict[str, Any], duration):
        """Print final summary to console"""
        print("\n" + "="*70)
        print("🚀 MOODLECLAUDE DOCKER TEST SUITE FINAL REPORT")
        print("="*70)
        
        # Overall status
        if analysis.get('test_results_available'):
            success_rate = analysis.get('success_rate', 0)
            print(f"📊 Overall Success Rate: {success_rate:.1f}%")
            print(f"✅ Tests Passed: {analysis.get('passed_tests', 0)}")
            print(f"❌ Tests Failed: {analysis.get('failed_tests', 0)}")
            print(f"📋 Total Tests: {analysis.get('total_tests', 0)}")
        else:
            print("⚠️  Test results not available")
        
        # Duration
        print(f"⏱️  Total Duration: {duration.total_seconds():.1f} seconds")
        
        # Phase results
        print(f"\n🔄 Phase Results:")
        for phase, result in self.test_results['phases'].items():
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {phase}: {result['message']}")
        
        # Critical failures
        critical_failures = analysis.get('critical_failures', [])
        if critical_failures:
            print(f"\n🚨 Critical Failures ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"  • {failure}")
        
        # File locations
        print(f"\n📁 Report Files:")
        print(f"  • JSON Report: test-results/test_report.json")
        print(f"  • HTML Report: test-results/test_report.html")
        print(f"  • Docker Runner Report: test-results/docker_test_runner_report.json")
        print(f"  • Logs: logs/")
        
        # Next steps
        overall_success = analysis.get('success_rate', 0) >= 80
        if overall_success:
            print(f"\n🎉 Test Suite PASSED! System is ready for production.")
        else:
            print(f"\n⚠️  Test Suite FAILED. Please review failures and fix issues.")
            print(f"     Re-run with --keep-environment to debug issues.")
        
        print("="*70)
    
    def run_complete_test_cycle(self) -> bool:
        """Run the complete Docker test cycle"""
        logger.info("🚀 Starting MoodleClaude Docker Test Suite...")
        
        try:
            # Phase 1: Environment setup
            if not self.check_docker_availability():
                return False
            
            if not self.cleanup_existing_environment():
                return False
            
            if not self.create_test_environment():
                return False
            
            # Phase 2: Test execution
            test_success = self.run_test_suite()
            
            # Phase 3: Analysis and cleanup
            analysis = self.analyze_test_results()
            
            if not self.keep_environment:
                self.cleanup_test_environment()
            
            # Phase 4: Final reporting
            self.generate_final_report(analysis)
            
            # Determine overall success
            overall_success = (
                test_success and 
                analysis.get('success_rate', 0) >= 80 and
                len(analysis.get('critical_failures', [])) == 0
            )
            
            return overall_success
            
        except Exception as e:
            logger.error(f"💥 Test cycle failed: {str(e)}")
            self.log_phase("test_cycle", False, f"Test cycle crashed: {str(e)}")
            
            # Emergency cleanup
            if not self.keep_environment:
                try:
                    self.cleanup_test_environment()
                except:
                    pass
            
            return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="MoodleClaude Docker Test Suite Runner")
    parser.add_argument("--keep-environment", action="store_true",
                       help="Keep test environment running after tests (for debugging)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--cleanup-only", action="store_true",
                       help="Only cleanup existing test environment")
    
    args = parser.parse_args()
    
    if args.cleanup_only:
        # Only cleanup existing environment
        runner = DockerTestSuiteRunner()
        success = runner.cleanup_existing_environment()
        print("✅ Cleanup completed" if success else "❌ Cleanup failed")
        return
    
    # Run complete test cycle
    runner = DockerTestSuiteRunner(
        keep_environment=args.keep_environment,
        verbose=args.verbose
    )
    
    try:
        success = runner.run_complete_test_cycle()
        
        if success:
            print("\n🎉 Docker Test Suite COMPLETED SUCCESSFULLY!")
            print("The MoodleClaude system is ready for production use.")
        else:
            print("\n⚠️  Docker Test Suite FAILED!")
            print("Please review the test results and fix any issues.")
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        if not args.keep_environment:
            print("Cleaning up...")
            runner.cleanup_test_environment()
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Test suite failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()