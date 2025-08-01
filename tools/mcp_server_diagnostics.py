#!/usr/bin/env python3
"""
MCP Server Diagnostics Tool
===========================

Testet die MCP Server Verbindung und analysiert warum Claude Desktop "Server disconnected" anzeigt.
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class MCPServerDiagnostics:
    """Diagnostics für MCP Server Verbindungsprobleme."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.claude_config_path = (
            Path.home()
            / "Library/Application Support/Claude/claude_desktop_config.json"
        )
        self.mcp_server_path = self.project_root / "src/core/working_mcp_server.py"

    def check_claude_desktop_config(self):
        """Überprüft die Claude Desktop Konfiguration."""
        logger.info("🔍 Checking Claude Desktop configuration...")

        if not self.claude_config_path.exists():
            logger.error(
                f"❌ Claude Desktop config not found: {self.claude_config_path}"
            )
            return False

        try:
            with open(self.claude_config_path, "r") as f:
                config = json.load(f)

            logger.info("✅ Claude Desktop config loaded successfully")

            if "mcpServers" not in config:
                logger.error("❌ No mcpServers section in config")
                return False

            if "moodleclaude-stable" not in config["mcpServers"]:
                logger.error("❌ moodleclaude-stable not found in mcpServers")
                return False

            server_config = config["mcpServers"]["moodleclaude-stable"]
            logger.info("📋 MCP Server Config:")
            logger.info(f"   Command: {server_config.get('command', 'N/A')}")
            logger.info(f"   Args: {server_config.get('args', 'N/A')}")
            logger.info(f"   Disabled: {server_config.get('disabled', False)}")

            # Check environment variables
            env_vars = server_config.get("env", {})
            logger.info("🔧 Environment Variables:")
            for key, value in env_vars.items():
                if "TOKEN" in key:
                    logger.info(f"   {key}: {'✅ Set' if value else '❌ Empty'}")
                else:
                    logger.info(f"   {key}: {value}")

            return True

        except Exception as e:
            logger.error(f"❌ Error reading Claude Desktop config: {e}")
            return False

    def check_mcp_server_file(self):
        """Überprüft die MCP Server Datei."""
        logger.info("🔍 Checking MCP Server file...")

        if not self.mcp_server_path.exists():
            logger.error(f"❌ MCP Server file not found: {self.mcp_server_path}")
            return False

        logger.info(f"✅ MCP Server file exists: {self.mcp_server_path}")

        # Check if file is executable
        if not os.access(self.mcp_server_path, os.R_OK):
            logger.error("❌ MCP Server file is not readable")
            return False

        logger.info("✅ MCP Server file is readable")
        return True

    def test_python_import(self):
        """Testet ob Python das MCP Server Modul importieren kann."""
        logger.info("🔍 Testing Python import of MCP Server...")

        try:
            # Test basic Python syntax
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f'import sys; sys.path.insert(0, "{self.mcp_server_path.parent}"); exec(open("{self.mcp_server_path}").read())',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info("✅ Python can import MCP Server successfully")
                return True
            else:
                logger.error(f"❌ Python import failed:")
                logger.error(f"   Return code: {result.returncode}")
                logger.error(f"   Stderr: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Python import test timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error testing Python import: {e}")
            return False

    def test_mcp_server_startup(self):
        """Testet den MCP Server Start mit korrekten Umgebungsvariablen."""
        logger.info("🔍 Testing MCP Server startup...")

        # Load tokens from config file
        token_file = self.project_root / "config/moodle_tokens.env"
        env_vars = os.environ.copy()

        if token_file.exists():
            logger.info(f"📋 Loading tokens from: {token_file}")
            try:
                with open(token_file, "r") as f:
                    for line in f:
                        if "=" in line and not line.strip().startswith("#"):
                            key, value = line.strip().split("=", 1)
                            env_vars[key] = value.strip("\"'")
                            if "TOKEN" in key:
                                logger.info(
                                    f"   {key}: {'✅ Loaded' if value.strip() else '❌ Empty'}"
                                )
            except Exception as e:
                logger.error(f"❌ Error loading token file: {e}")
        else:
            logger.warning(f"⚠️  Token file not found: {token_file}")

        # Set specific environment variables for the test
        env_vars.update(
            {
                "MOODLE_URL": "http://localhost:8080",
                "SERVER_NAME": "diagnostic-test",
                "LOG_LEVEL": "INFO",
            }
        )

        try:
            logger.info("🚀 Starting MCP Server test...")
            process = subprocess.Popen(
                ["python", str(self.mcp_server_path)],
                env=env_vars,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for a short time to see if server starts
            time.sleep(2)

            # Check if process is still running
            if process.poll() is None:
                logger.info("✅ MCP Server is running")
                process.terminate()
                process.wait(timeout=5)
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error("❌ MCP Server exited immediately")
                logger.error(f"   Return code: {process.returncode}")
                if stdout:
                    logger.error(f"   Stdout: {stdout}")
                if stderr:
                    logger.error(f"   Stderr: {stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error testing MCP Server startup: {e}")
            return False

    def check_claude_desktop_logs(self):
        """Sucht nach Claude Desktop Log-Dateien."""
        logger.info("🔍 Searching for Claude Desktop logs...")

        possible_log_locations = [
            Path.home() / "Library/Logs/Claude",
            Path.home() / "Library/Application Support/Claude/logs",
            "/Users/simonjanke/Library/Logs/Claude",
            self.project_root / "logs",
        ]

        found_logs = []

        for log_dir in possible_log_locations:
            if log_dir.exists():
                logger.info(f"📁 Found log directory: {log_dir}")

                # Look for log files
                for log_file in log_dir.glob("*.log"):
                    found_logs.append(log_file)
                    logger.info(f"   📄 {log_file.name}")

                for log_file in log_dir.glob("**/*.log"):
                    if log_file not in found_logs:
                        found_logs.append(log_file)
                        logger.info(f"   📄 {log_file.relative_to(log_dir)}")

        if not found_logs:
            logger.warning("⚠️  No Claude Desktop log files found")

        return found_logs

    def analyze_recent_logs(self, log_files):
        """Analysiert die neuesten Log-Einträge."""
        logger.info("🔍 Analyzing recent log entries...")

        recent_entries = []

        for log_file in log_files:
            try:
                with open(log_file, "r") as f:
                    lines = f.readlines()

                # Get last 20 lines
                recent_lines = lines[-20:] if len(lines) > 20 else lines

                for line in recent_lines:
                    if any(
                        keyword in line.lower()
                        for keyword in ["mcp", "server", "disconnect", "error", "fail"]
                    ):
                        recent_entries.append(
                            {"file": log_file.name, "line": line.strip()}
                        )

            except Exception as e:
                logger.warning(f"⚠️  Could not read {log_file}: {e}")

        if recent_entries:
            logger.info("📋 Recent relevant log entries:")
            for entry in recent_entries[-10:]:  # Show last 10 relevant entries
                logger.info(f"   [{entry['file']}] {entry['line']}")
        else:
            logger.info("ℹ️  No recent relevant log entries found")

        return recent_entries

    def create_diagnostic_report(self):
        """Erstellt einen vollständigen Diagnosebericht."""
        logger.info("📊 Creating diagnostic report...")

        report = {
            "diagnostic_date": datetime.now().isoformat(),
            "claude_desktop_config": False,
            "mcp_server_file": False,
            "python_import": False,
            "server_startup": False,
            "log_files_found": [],
            "recent_log_entries": [],
            "recommendations": [],
        }

        # Run all diagnostics
        report["claude_desktop_config"] = self.check_claude_desktop_config()
        report["mcp_server_file"] = self.check_mcp_server_file()
        report["python_import"] = self.test_python_import()
        report["server_startup"] = self.test_mcp_server_startup()

        log_files = self.check_claude_desktop_logs()
        report["log_files_found"] = [str(f) for f in log_files]
        report["recent_log_entries"] = self.analyze_recent_logs(log_files)

        # Generate recommendations
        if not report["claude_desktop_config"]:
            report["recommendations"].append("Fix Claude Desktop configuration file")

        if not report["mcp_server_file"]:
            report["recommendations"].append(
                "Check MCP Server file permissions and location"
            )

        if not report["python_import"]:
            report["recommendations"].append("Fix Python import issues in MCP Server")

        if not report["server_startup"]:
            report["recommendations"].append("Fix MCP Server startup configuration")

        if not report["log_files_found"]:
            report["recommendations"].append(
                "Enable Claude Desktop logging to diagnose connection issues"
            )

        # Save report
        report_file = self.project_root / "reports" / "mcp_server_diagnostics.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Diagnostic report saved to: {report_file}")

        # Summary
        logger.info("=" * 60)
        logger.info("🎯 DIAGNOSTIC SUMMARY")
        logger.info("=" * 60)

        total_checks = 4
        passed_checks = sum(
            [
                report["claude_desktop_config"],
                report["mcp_server_file"],
                report["python_import"],
                report["server_startup"],
            ]
        )

        logger.info(f"Checks passed: {passed_checks}/{total_checks}")

        if passed_checks == total_checks:
            logger.info("✅ All diagnostics passed - MCP Server should work correctly")
        else:
            logger.info(
                "❌ Some diagnostics failed - this explains the 'Server disconnected' error"
            )
            logger.info("🔧 Recommendations:")
            for rec in report["recommendations"]:
                logger.info(f"   • {rec}")

        return report

    def run_full_diagnostics(self):
        """Führt die vollständige Diagnose durch."""
        logger.info("🚀 Starting MCP Server diagnostics...")
        logger.info("=" * 60)

        return self.create_diagnostic_report()


def main():
    """Main diagnostic function."""
    print("🔧 MoodleClaude MCP Server Diagnostics")
    print("=" * 60)
    print("🚀 Analyzing 'Server disconnected' error...")

    diagnostics = MCPServerDiagnostics()
    report = diagnostics.run_full_diagnostics()

    print(f"\n💾 Full diagnostic report saved to: reports/mcp_server_diagnostics.json")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
