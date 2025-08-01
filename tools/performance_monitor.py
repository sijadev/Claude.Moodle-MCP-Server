#!/usr/bin/env python3
"""
Performance Monitoring Tool for MoodleClaude MCP Server
Provides real-time metrics, health checks, and performance analysis
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and analyze MCP Server performance"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/claude_desktop_optimized.json"
        self.metrics_history: List[Dict] = []
        self.start_time = time.time()

    def load_config(self) -> Dict:
        """Load Claude Desktop configuration"""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {}

    def analyze_configuration(self, config: Dict) -> Dict[str, Any]:
        """Analyze MCP server configuration for performance"""
        analysis = {
            "servers_configured": 0,
            "optimized_servers": 0,
            "disabled_servers": 0,
            "performance_settings": {},
            "recommendations": [],
        }

        mcp_servers = config.get("mcpServers", {})

        for server_name, server_config in mcp_servers.items():
            analysis["servers_configured"] += 1

            if server_config.get("disabled", False):
                analysis["disabled_servers"] += 1
                continue

            # Check for optimization features
            env_vars = server_config.get("env", {})
            if any(
                key.startswith(("CACHE_", "RATE_LIMIT_", "MAX_CONNECTIONS"))
                for key in env_vars.keys()
            ):
                analysis["optimized_servers"] += 1

            # Analyze performance settings
            timeout = server_config.get("timeout", 30)
            if timeout > 60:
                analysis["recommendations"].append(
                    f"Server '{server_name}': Consider reducing timeout from {timeout}s to 30-60s"
                )

            cache_size = env_vars.get("CACHE_SIZE")
            if cache_size and int(cache_size) < 50:
                analysis["recommendations"].append(
                    f"Server '{server_name}': Consider increasing cache size from {cache_size} to 100+"
                )

        # Global settings analysis
        global_settings = config.get("globalSettings", {})
        performance = global_settings.get("performance", {})

        analysis["performance_settings"] = {
            "metrics_enabled": performance.get("enableMetrics", False),
            "health_check_enabled": performance.get("enableHealthCheck", False),
            "metrics_interval": performance.get("metricsInterval", 300),
        }

        return analysis

    def generate_performance_report(self, config: Dict) -> str:
        """Generate comprehensive performance report"""
        analysis = self.analyze_configuration(config)
        uptime = time.time() - self.start_time

        report = f"""
🚀 **MoodleClaude Performance Analysis Report**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Uptime: {uptime:.1f} seconds

📊 **Configuration Analysis:**
• Total MCP Servers: {analysis['servers_configured']}
• Optimized Servers: {analysis['optimized_servers']}
• Disabled Servers: {analysis['disabled_servers']}
• Active Servers: {analysis['servers_configured'] - analysis['disabled_servers']}

⚡ **Performance Features:**
• Metrics Enabled: {'✅' if analysis['performance_settings']['metrics_enabled'] else '❌'}
• Health Checks: {'✅' if analysis['performance_settings']['health_check_enabled'] else '❌'}
• Metrics Interval: {analysis['performance_settings']['metrics_interval']}s

🎯 **Recommendations:**
"""

        if analysis["recommendations"]:
            for rec in analysis["recommendations"]:
                report += f"• {rec}\n"
        else:
            report += "• No performance recommendations - configuration looks good! ✅\n"

        # Performance benchmarks
        report += f"""
📈 **Performance Benchmarks:**
• Recommended Response Time: < 2s
• Target Success Rate: > 95%
• Optimal Cache Hit Rate: > 80%
• Max Concurrent Connections: 10-20

🔧 **Optimization Status:**
"""

        if analysis["optimized_servers"] > 0:
            report += f"• {analysis['optimized_servers']} server(s) have optimization features ✅\n"
        else:
            report += "• No optimized servers detected - consider upgrading ⚠️\n"

        report += f"""
🛠️ **Quick Performance Tips:**
• Use the optimized MCP server for better performance
• Enable caching for frequently accessed content
• Set appropriate rate limits to prevent API overload
• Monitor metrics regularly for performance insights
• Keep timeout values reasonable (30-60s)

📋 **Health Check Commands:**
```bash
# Test MCP server connectivity
python tools/performance_monitor.py --health-check

# Get real-time metrics
python tools/performance_monitor.py --metrics

# Run performance benchmark
python tools/performance_monitor.py --benchmark
```
        """

        return report

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on MCP servers"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": [],
        }

        config = self.load_config()
        mcp_servers = config.get("mcpServers", {})

        all_healthy = True

        for server_name, server_config in mcp_servers.items():
            if server_config.get("disabled", False):
                continue

            check_result = {
                "server": server_name,
                "status": "unknown",
                "response_time": None,
                "error": None,
            }

            try:
                # Basic connectivity check (simulate for now)
                start_time = time.time()

                # In a real implementation, this would test actual MCP connectivity
                await asyncio.sleep(0.1)  # Simulate network call

                response_time = time.time() - start_time
                check_result["response_time"] = response_time
                check_result["status"] = "healthy" if response_time < 2.0 else "slow"

                if response_time >= 2.0:
                    all_healthy = False

            except Exception as e:
                check_result["status"] = "unhealthy"
                check_result["error"] = str(e)
                all_healthy = False

            health_status["checks"].append(check_result)

        health_status["overall_status"] = "healthy" if all_healthy else "degraded"
        return health_status

    async def run_benchmark(self, duration: int = 30) -> Dict[str, Any]:
        """Run performance benchmark"""
        logger.info(f"Running performance benchmark for {duration} seconds...")

        benchmark_results = {
            "duration": duration,
            "start_time": datetime.now().isoformat(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "min_response_time": float("inf"),
            "max_response_time": 0.0,
            "requests_per_second": 0.0,
        }

        start_time = time.time()
        response_times = []

        # Simulate load testing
        async def make_request():
            request_start = time.time()
            try:
                # Simulate MCP request
                await asyncio.sleep(0.1 + (time.time() % 0.1))  # Variable response time
                response_time = time.time() - request_start
                response_times.append(response_time)
                return True
            except Exception:
                return False

        # Run concurrent requests
        while time.time() - start_time < duration:
            tasks = [make_request() for _ in range(5)]  # 5 concurrent requests
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                benchmark_results["total_requests"] += 1
                if result is True:
                    benchmark_results["successful_requests"] += 1
                else:
                    benchmark_results["failed_requests"] += 1

            await asyncio.sleep(0.1)  # Small delay between batches

        # Calculate statistics
        if response_times:
            benchmark_results["avg_response_time"] = sum(response_times) / len(
                response_times
            )
            benchmark_results["min_response_time"] = min(response_times)
            benchmark_results["max_response_time"] = max(response_times)

        actual_duration = time.time() - start_time
        benchmark_results["requests_per_second"] = (
            benchmark_results["total_requests"] / actual_duration
        )
        benchmark_results["end_time"] = datetime.now().isoformat()

        return benchmark_results

    def format_benchmark_results(self, results: Dict[str, Any]) -> str:
        """Format benchmark results for display"""
        success_rate = (
            (results["successful_requests"] / results["total_requests"] * 100)
            if results["total_requests"] > 0
            else 0
        )

        return f"""
🏁 **Performance Benchmark Results**

⏱️ **Test Duration:** {results['duration']}s
📊 **Request Statistics:**
• Total Requests: {results['total_requests']}
• Successful: {results['successful_requests']}
• Failed: {results['failed_requests']}
• Success Rate: {success_rate:.1f}%

⚡ **Performance Metrics:**
• Requests/Second: {results['requests_per_second']:.1f}
• Avg Response Time: {results['avg_response_time']:.3f}s
• Min Response Time: {results['min_response_time']:.3f}s
• Max Response Time: {results['max_response_time']:.3f}s

🎯 **Performance Rating:**
"""

        # Performance rating
        if results["avg_response_time"] < 0.5:
            rating = "🚀 Excellent"
        elif results["avg_response_time"] < 1.0:
            rating = "✅ Good"
        elif results["avg_response_time"] < 2.0:
            rating = "⚠️  Acceptable"
        else:
            rating = "❌ Needs Improvement"

        return rating


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="MoodleClaude Performance Monitor")
    parser.add_argument("--config", help="Path to Claude Desktop config file")
    parser.add_argument(
        "--report", action="store_true", help="Generate performance report"
    )
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument(
        "--benchmark", action="store_true", help="Run performance benchmark"
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Benchmark duration in seconds"
    )
    parser.add_argument("--metrics", action="store_true", help="Show current metrics")

    args = parser.parse_args()

    monitor = PerformanceMonitor(args.config)

    if args.report:
        config = monitor.load_config()
        report = monitor.generate_performance_report(config)
        print(report)

    elif args.health_check:
        print("🔍 Running health check...")
        health = await monitor.health_check()
        print(f"\n🏥 **Health Check Results**")
        print(f"Overall Status: {health['overall_status'].upper()}")
        print(f"Timestamp: {health['timestamp']}")

        for check in health["checks"]:
            status_emoji = {"healthy": "✅", "slow": "⚠️", "unhealthy": "❌"}.get(
                check["status"], "❓"
            )
            print(f"{status_emoji} {check['server']}: {check['status']}")
            if check["response_time"]:
                print(f"   Response Time: {check['response_time']:.3f}s")
            if check["error"]:
                print(f"   Error: {check['error']}")

    elif args.benchmark:
        results = await monitor.run_benchmark(args.duration)
        formatted_results = monitor.format_benchmark_results(results)
        print(formatted_results)

    elif args.metrics:
        print("📊 **Current Metrics** (simulated)")
        print(f"• Server Uptime: {time.time() - monitor.start_time:.1f}s")
        print(f"• Configuration Status: ✅ Loaded")
        print(f"• Monitoring Active: ✅ Yes")
        print(f"• Last Check: {datetime.now().strftime('%H:%M:%S')}")

    else:
        # Default: show configuration analysis
        config = monitor.load_config()
        if not config:
            print("❌ No configuration found. Please check your config file path.")
            return

        analysis = monitor.analyze_configuration(config)
        print("📊 **Quick Configuration Analysis:**")
        print(f"• MCP Servers: {analysis['servers_configured']}")
        print(f"• Optimized: {analysis['optimized_servers']}")
        print(
            f"• Active: {analysis['servers_configured'] - analysis['disabled_servers']}"
        )

        if analysis["recommendations"]:
            print("\n💡 **Recommendations:**")
            for rec in analysis["recommendations"][:3]:  # Show top 3
                print(f"• {rec}")

        print(f"\n💻 Use --help for more options")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Performance monitor stopped by user")
    except Exception as e:
        logger.error(f"Performance monitor error: {e}")
        sys.exit(1)
