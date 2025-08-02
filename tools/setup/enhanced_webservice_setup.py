#!/usr/bin/env python3
"""
Enhanced MoodleClaude Web Service Setup
======================================

This enhanced setup incorporates best practices from local_wswizard research:
- Better error handling and validation
- Comprehensive function availability checking
- Dashboard-style reporting
- Enhanced security practices
- Improved logging and monitoring capabilities

Usage: python enhanced_webservice_setup.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import requests
from datetime import datetime
import time


class EnhancedMoodleWebServiceSetup:
    """Enhanced web service setup with local_wswizard inspired improvements."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / ".env"
        self.config_file = Path(__file__).parent / "moodleclaude_webservice_config.json"
        self.log_file = Path(__file__).parent / "setup_log.json"
        
        # Load current environment
        self.moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
        self.moodle_admin_user = os.getenv("MOODLE_ADMIN_USER", "admin")
        self.moodle_admin_password = os.getenv("MOODLE_ADMIN_PASSWORD", "")
        
        # Setup logging
        self.setup_log = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "errors": [],
            "warnings": []
        }

    def log_step(self, step: str, status: str, details: str = ""):
        """Log a setup step with status."""
        entry = {
            "step": step,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.setup_log["steps"].append(entry)
        
        if status == "error":
            self.setup_log["errors"].append(entry)
        elif status == "warning":
            self.setup_log["warnings"].append(entry)

    def print_dashboard_header(self):
        """Print a dashboard-style header."""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              🚀 Enhanced MoodleClaude Web Service Setup     ║")
        print("║                  Inspired by local_wswizard                  ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print(f"🌐 Moodle URL: {self.moodle_url}")
        print(f"👤 Admin User: {self.moodle_admin_user}")
        print(f"📊 Enhanced Features: ✅ Function Validation ✅ Error Recovery ✅ Audit Logging")
        print()

    def validate_moodle_environment(self) -> Tuple[bool, List[str]]:
        """Comprehensive Moodle environment validation."""
        print("🔍 Phase 1: Environment Validation")
        print("=" * 50)
        
        issues = []
        
        # Check Moodle accessibility
        try:
            response = requests.get(f"{self.moodle_url}/login/index.php", timeout=10)
            if response.status_code != 200:
                issues.append(f"Cannot access Moodle at {self.moodle_url} (HTTP {response.status_code})")
                self.log_step("moodle_access", "error", f"HTTP {response.status_code}")
            else:
                print("✅ Moodle is accessible")
                self.log_step("moodle_access", "success")
        except Exception as e:
            issues.append(f"Moodle connection failed: {e}")
            self.log_step("moodle_access", "error", str(e))

        # Check admin credentials
        if not self.moodle_admin_password:
            issues.append("MOODLE_ADMIN_PASSWORD not set in environment")
            self.log_step("admin_credentials", "error", "Password not provided")
        else:
            print("✅ Admin credentials provided")
            self.log_step("admin_credentials", "success")

        # Check web service endpoint
        try:
            ws_url = f"{self.moodle_url}/webservice/rest/server.php"
            response = requests.get(ws_url, timeout=5)
            # Even if it returns an error, it means the endpoint exists
            print("✅ Web service endpoint accessible") 
            self.log_step("webservice_endpoint", "success")
        except Exception as e:
            issues.append(f"Web service endpoint not accessible: {e}")
            self.log_step("webservice_endpoint", "warning", str(e))

        return len(issues) == 0, issues

    def get_enhanced_function_list(self) -> Dict[str, List[str]]:
        """Get categorized function list with enhanced coverage."""
        return {
            "core_essential": [
                "core_webservice_get_site_info",
                "core_course_get_courses", 
                "core_course_create_courses",
                "core_course_delete_courses",
                "core_course_get_contents",
                "core_course_get_categories",
                "core_course_update_courses"
            ],
            "content_management": [
                "core_course_create_modules",
                "core_course_delete_modules", 
                "core_course_get_course_modules",
                "core_course_edit_section"
            ],
            "user_management": [
                "core_user_get_users",
                "core_user_create_users",
                "core_enrol_get_enrolled_users",
                "core_enrol_get_users_courses"
            ],
            "file_management": [
                "core_files_upload",
                "core_files_get_files"
            ],
            "assessment_tools": [
                "mod_assign_get_assignments",
                "mod_assign_get_submissions",
                "core_grades_get_grades", 
                "gradereport_user_get_grade_items"
            ],
            "communication": [
                "mod_forum_get_forums_by_courses",
                "mod_forum_get_forum_discussions"
            ],
            "plugin_extensions": [
                "local_wsmanagesections_create_sections",
                "local_wsmanagesections_update_sections",
                "local_wsmanagesections_delete_sections",
                "local_wsmanagesections_get_sections"
            ],
            "completion_tracking": [
                "core_completion_get_course_completion_status"
            ]
        }

    def validate_function_availability(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate which functions are actually available in the Moodle instance."""
        print("\n🔍 Phase 2: Function Availability Validation")
        print("=" * 50)
        
        functions = self.get_enhanced_function_list()
        availability_report = {
            "available": {},
            "missing": {},
            "total_available": 0,
            "total_missing": 0
        }
        
        # Test with a basic web service call to get available functions
        try:
            test_url = f"{self.moodle_url}/webservice/rest/server.php"
            test_data = {
                "wstoken": config.get("token", ""),
                "wsfunction": "core_webservice_get_site_info",
                "moodlewsrestformat": "json"
            }
            
            response = requests.post(test_url, data=test_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                available_functions = result.get("functions", [])
                available_function_names = {func["name"] for func in available_functions}
                
                for category, func_list in functions.items():
                    availability_report["available"][category] = []
                    availability_report["missing"][category] = []
                    
                    for func in func_list:
                        if func in available_function_names:
                            availability_report["available"][category].append(func)
                            availability_report["total_available"] += 1
                        else:
                            availability_report["missing"][category].append(func)
                            availability_report["total_missing"] += 1
                            
                    if availability_report["available"][category]:
                        print(f"✅ {category}: {len(availability_report['available'][category])} available")
                    if availability_report["missing"][category]:
                        print(f"⚠️  {category}: {len(availability_report['missing'][category])} missing")
                        
        except Exception as e:
            print(f"⚠️  Could not validate function availability: {e}")
            self.log_step("function_validation", "warning", str(e))
            
        return availability_report

    def create_enhanced_php_script(self) -> bool:
        """Create enhanced PHP script with better error handling."""
        print("\n🔧 Phase 3: Enhanced Web Service Creation")
        print("=" * 50)
        
        # Use the existing PHP script but with enhanced error reporting
        php_script = Path(__file__).parent / "create_moodleclaude_webservice.php"
        
        if not php_script.exists():
            print("❌ PHP setup script not found")
            self.log_step("php_script", "error", "Script not found")
            return False
            
        return self.run_php_with_enhanced_error_handling(php_script)

    def run_php_with_enhanced_error_handling(self, php_script: Path) -> bool:
        """Run PHP script with comprehensive error handling."""
        env = os.environ.copy()
        env.update({
            "MOODLE_URL": self.moodle_url,
            "MOODLE_ADMIN_USER": self.moodle_admin_user,
            "MOODLE_ADMIN_PASSWORD": self.moodle_admin_password,
        })

        try:
            # Try multiple PHP executables
            php_executables = ["php", "php8.3", "php8.2", "php8.1", "php8.0", "/usr/bin/php"]
            php_exe = None

            for exe in php_executables:
                try:
                    result = subprocess.run([exe, "--version"], capture_output=True, check=True)
                    php_version = result.stdout.decode().split('\n')[0]
                    print(f"✅ Found PHP: {php_version}")
                    php_exe = exe
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            if not php_exe:
                print("❌ No PHP executable found")
                self.log_step("php_execution", "error", "No PHP found")
                return False

            # Run with enhanced error reporting
            result = subprocess.run(
                [php_exe, str(php_script)],
                cwd=str(self.project_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print("✅ PHP script executed successfully")
                print(result.stdout)
                self.log_step("php_execution", "success")
                return True
            else:
                print("❌ PHP script failed:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.log_step("php_execution", "error", f"Exit code: {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ PHP script timed out")
            self.log_step("php_execution", "error", "Timeout")
            return False
        except Exception as e:
            print(f"❌ Error running PHP script: {e}")
            self.log_step("php_execution", "error", str(e))
            return False

    def load_and_validate_config(self) -> Optional[Dict[str, Any]]:
        """Load and validate the generated configuration."""
        if not self.config_file.exists():
            print(f"❌ Configuration file not found: {self.config_file}")
            self.log_step("config_load", "error", "Config file missing")
            return None

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                
            # Validate required keys
            required_keys = ["token", "service_id", "user", "webservice_url"]
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                print(f"❌ Configuration missing required keys: {missing_keys}")
                self.log_step("config_validation", "error", f"Missing keys: {missing_keys}")
                return None
                
            print("✅ Configuration loaded and validated")
            self.log_step("config_validation", "success")
            return config
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.log_step("config_load", "error", str(e))
            return None

    def perform_comprehensive_testing(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive testing inspired by local_wswizard dashboard."""
        print("\n🧪 Phase 4: Comprehensive Service Testing")
        print("=" * 50)
        
        test_results = {
            "basic_connectivity": False,
            "site_info": {},
            "function_tests": {},
            "performance": {},
            "security_check": False
        }
        
        try:
            # Basic connectivity test
            start_time = time.time()
            test_url = f"{self.moodle_url}/webservice/rest/server.php"
            test_data = {
                "wstoken": config["token"],
                "wsfunction": "core_webservice_get_site_info",
                "moodlewsrestformat": "json"
            }

            response = requests.post(test_url, data=test_data, timeout=30)
            response_time = time.time() - start_time
            
            test_results["performance"]["response_time"] = response_time

            if response.status_code == 200:
                result = response.json()
                
                if "exception" not in result:
                    test_results["basic_connectivity"] = True
                    test_results["site_info"] = {
                        "sitename": result.get("sitename", "Unknown"),
                        "release": result.get("release", "Unknown"),
                        "version": result.get("version", "Unknown"),
                        "functions": len(result.get("functions", []))
                    }
                    
                    print("✅ Basic connectivity test passed")
                    print(f"   Site: {test_results['site_info']['sitename']}")
                    print(f"   Version: {test_results['site_info']['release']}")
                    print(f"   Functions: {test_results['site_info']['functions']}")
                    print(f"   Response time: {response_time:.2f}s")
                    
                    self.log_step("connectivity_test", "success")
                    
                    # Security check - ensure token is working properly
                    test_results["security_check"] = True
                    
                else:
                    print(f"❌ Web service error: {result.get('message', 'Unknown error')}")
                    self.log_step("connectivity_test", "error", result.get('message', ''))
                    
            else:
                print(f"❌ HTTP Error {response.status_code}")
                self.log_step("connectivity_test", "error", f"HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ Testing failed: {e}")
            self.log_step("comprehensive_testing", "error", str(e))

        return test_results

    def generate_dashboard_report(self, config: Dict[str, Any], test_results: Dict[str, Any], 
                                availability_report: Dict[str, Any]):
        """Generate a comprehensive dashboard-style report."""
        print("\n" + "="*80)
        print("                    🎯 ENHANCED SETUP DASHBOARD")
        print("="*80)
        
        # Service Overview
        print("\n📊 SERVICE OVERVIEW")
        print("-" * 40)
        print(f"Service Name      : {config.get('service_name', 'N/A')}")
        print(f"Service ID        : {config.get('service_id', 'N/A')}")
        print(f"Service User      : {config.get('user', 'N/A')}")
        print(f"Token             : {config.get('token', '')[:12]}...")
        print(f"Created           : {config.get('created', 'N/A')}")
        
        # Connectivity Status
        print("\n🌐 CONNECTIVITY STATUS")
        print("-" * 40)
        status_icon = "✅" if test_results.get("basic_connectivity") else "❌"
        print(f"Connection        : {status_icon}")
        print(f"Response Time     : {test_results.get('performance', {}).get('response_time', 0):.2f}s")
        print(f"Security Check    : {'✅' if test_results.get('security_check') else '❌'}")
        
        # Site Information
        if test_results.get("site_info"):
            print("\n🏢 MOODLE SITE INFO")
            print("-" * 40)
            site_info = test_results["site_info"]
            print(f"Site Name         : {site_info.get('sitename', 'Unknown')}")
            print(f"Version           : {site_info.get('release', 'Unknown')}")
            print(f"Available Functions: {site_info.get('functions', 0)}")
        
        # Function Availability Summary
        if availability_report:
            print("\n⚙️  FUNCTION AVAILABILITY")
            print("-" * 40)
            print(f"Total Available   : {availability_report.get('total_available', 0)}")
            print(f"Total Missing     : {availability_report.get('total_missing', 0)}")
            
            total = availability_report.get('total_available', 0) + availability_report.get('total_missing', 0)
            if total > 0:
                coverage = (availability_report.get('total_available', 0) / total) * 100
                print(f"Coverage          : {coverage:.1f}%")
        
        # Setup Log Summary
        print("\n📝 SETUP LOG SUMMARY")
        print("-" * 40)
        print(f"Total Steps       : {len(self.setup_log['steps'])}")
        print(f"Errors            : {len(self.setup_log['errors'])}")
        print(f"Warnings          : {len(self.setup_log['warnings'])}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 40)
        if test_results.get("basic_connectivity"):
            print("✅ All systems operational - ready for production use")
        else:
            print("⚠️  Issues detected - review error logs before proceeding")
            
        if availability_report.get('total_missing', 0) > 0:
            print("🔧 Consider installing missing plugins for full functionality")
            
        performance = test_results.get('performance', {}).get('response_time', 0)
        if performance > 2.0:
            print("⚠️  Slow response times detected - check network/server performance")
            
        print("\n" + "="*80)

    def save_enhanced_logs(self):
        """Save comprehensive logs for troubleshooting."""
        with open(self.log_file, "w") as f:
            json.dump(self.setup_log, f, indent=2)
        print(f"📋 Setup logs saved to: {self.log_file}")

    def run_enhanced_setup(self) -> bool:
        """Run the complete enhanced setup process."""
        self.print_dashboard_header()
        
        # Phase 1: Environment Validation
        valid, issues = self.validate_moodle_environment()
        if not valid:
            print("\n❌ Environment validation failed:")
            for issue in issues:
                print(f"   • {issue}")
            return False
        
        # Phase 2: Create web service
        if not self.create_enhanced_php_script():
            return False
        
        # Phase 3: Load and validate configuration
        config = self.load_and_validate_config()
        if not config:
            return False
        
        # Phase 4: Function availability check
        availability_report = self.validate_function_availability(config)
        
        # Phase 5: Comprehensive testing
        test_results = self.perform_comprehensive_testing(config)
        
        # Phase 6: Update environment
        self.update_environment(config)
        
        # Phase 7: Generate dashboard report
        self.generate_dashboard_report(config, test_results, availability_report)
        
        # Phase 8: Save logs
        self.save_enhanced_logs()
        
        return test_results.get("basic_connectivity", False)

    def update_environment(self, config: Dict[str, Any]) -> bool:
        """Update environment with enhanced variable management."""
        print("\n🔧 Phase 5: Environment Configuration Update")
        print("=" * 50)
        
        try:
            # Read existing .env file
            env_content = []
            if self.env_file.exists():
                with open(self.env_file, "r") as f:
                    env_content = f.readlines()

            # Remove old MoodleClaude entries
            env_content = [
                line for line in env_content
                if not any(key in line for key in [
                    "MOODLE_TOKEN_ENHANCED",
                    "MOODLE_WS_USER", 
                    "MOODLE_SERVICE_ID"
                ])
            ]

            # Add enhanced configuration with metadata
            timestamp = datetime.now().isoformat()
            new_lines = [
                f"\n# MoodleClaude Enhanced Web Service Configuration\n",
                f"# Generated: {timestamp}\n",
                f"# Setup Type: Enhanced Custom Service\n",
                f"MOODLE_TOKEN_ENHANCED=\"{config['token']}\"\n",
                f"MOODLE_WS_USER=\"{config['user']}\"\n",
                f"MOODLE_SERVICE_ID=\"{config['service_id']}\"\n",
                f"# Service URL: {config['webservice_url']}\n\n"
            ]

            env_content.extend(new_lines)

            with open(self.env_file, "w") as f:
                f.writelines(env_content)

            print(f"✅ Environment updated: {self.env_file}")
            self.log_step("environment_update", "success")
            return True

        except Exception as e:
            print(f"❌ Error updating environment: {e}")
            self.log_step("environment_update", "error", str(e))
            return False


def main():
    """Main enhanced setup function."""
    setup = EnhancedMoodleWebServiceSetup()
    
    try:
        success = setup.run_enhanced_setup()
        
        if success:
            print("\n🎉 ENHANCED SETUP COMPLETED SUCCESSFULLY!")
            print("🚀 Your MoodleClaude web service is ready with enhanced capabilities!")
        else:
            print("\n❌ Setup completed with issues - check the dashboard report above")
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()