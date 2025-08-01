#!/usr/bin/env python3
"""
Enhanced Error Handling for MoodleClaude MCP Server
Provides structured error responses, context-aware suggestions, and better Claude Desktop UX
"""

import json
import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""

    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    VALIDATION = "validation"
    MOODLE_API = "moodle_api"
    PLUGIN = "plugin"
    PERFORMANCE = "performance"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for errors"""

    timestamp: datetime = field(default_factory=datetime.now)
    operation: Optional[str] = None
    user_action: Optional[str] = None
    system_state: Dict[str, Any] = field(default_factory=dict)
    request_data: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)


class EnhancedError(BaseModel):
    """Enhanced error model with rich context and suggestions"""

    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    message: str
    technical_details: Optional[str] = None
    context: ErrorContext
    suggestions: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    documentation_links: List[str] = field(default_factory=list)
    user_friendly_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def to_claude_response(self) -> str:
        """Format error for Claude Desktop display"""
        emoji_map = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "❌",
            ErrorSeverity.CRITICAL: "🚨",
        }

        emoji = emoji_map.get(self.severity, "❓")

        response = f"{emoji} **{self.title}**\n\n"

        # User-friendly message or technical message
        if self.user_friendly_message:
            response += f"{self.user_friendly_message}\n\n"
        else:
            response += f"{self.message}\n\n"

        # Add suggestions if available
        if self.suggestions:
            response += "💡 **Suggestions:**\n"
            for suggestion in self.suggestions:
                response += f"• {suggestion}\n"
            response += "\n"

        # Add recovery actions
        if self.recovery_actions:
            response += "🔧 **Try these steps:**\n"
            for i, action in enumerate(self.recovery_actions, 1):
                response += f"{i}. {action}\n"
            response += "\n"

        # Add documentation links
        if self.documentation_links:
            response += "📚 **Learn more:**\n"
            for link in self.documentation_links:
                response += f"• {link}\n"
            response += "\n"

        # Add technical details for debugging
        if self.technical_details and self.severity in [
            ErrorSeverity.HIGH,
            ErrorSeverity.CRITICAL,
        ]:
            response += (
                f"🔍 **Technical Details:**\n```\n{self.technical_details}\n```\n"
            )

        response += f"⏰ **Time:** {self.context.timestamp.strftime('%H:%M:%S')}\n"
        response += f"🏷️ **Error ID:** {self.error_id}"

        return response

    def to_json(self) -> str:
        """Convert to JSON for logging or storage"""
        return self.model_dump_json(indent=2)


class ErrorHandlerMixin:
    """Mixin class for enhanced error handling capabilities"""

    def __init__(self):
        self.error_count = 0
        self.error_history: List[EnhancedError] = []
        self.max_error_history = 50

    def create_error(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        title: str,
        message: str,
        operation: Optional[str] = None,
        user_action: Optional[str] = None,
        exception: Optional[Exception] = None,
        context_data: Optional[Dict] = None,
    ) -> EnhancedError:
        """Create an enhanced error with context and suggestions"""

        self.error_count += 1
        error_id = f"MCP-{category.value.upper()}-{self.error_count:04d}"

        # Build context
        context = ErrorContext(
            operation=operation,
            user_action=user_action,
            system_state=context_data or {},
            request_data=getattr(self, "_current_request_data", {}),
            environment={
                "server_type": "mcp",
                "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
            },
        )

        # Extract technical details from exception
        technical_details = None
        if exception:
            technical_details = f"{type(exception).__name__}: {str(exception)}"
            if hasattr(exception, "__traceback__") and exception.__traceback__:
                technical_details += f"\n\nTraceback:\n{''.join(traceback.format_tb(exception.__traceback__))}"

        # Create error
        error = EnhancedError(
            error_id=error_id,
            category=category,
            severity=severity,
            title=title,
            message=message,
            technical_details=technical_details,
            context=context,
        )

        # Add category-specific suggestions and recovery actions
        self._add_contextual_suggestions(error, exception)

        # Store in history
        self.error_history.append(error)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)

        # Log the error
        logger.error(f"Enhanced Error [{error_id}]: {title} - {message}")
        if technical_details:
            logger.debug(f"Technical details for {error_id}: {technical_details}")

        return error

    def _add_contextual_suggestions(
        self, error: EnhancedError, exception: Optional[Exception] = None
    ):
        """Add context-aware suggestions based on error category"""

        base_docs = [
            "https://github.com/sijadev/MoodleClaude/blob/main/README.md",
            "https://github.com/sijadev/MoodleClaude/blob/main/docs/troubleshooting.md",
        ]

        if error.category == ErrorCategory.CONFIGURATION:
            error.suggestions.extend(
                [
                    "Check your environment variables (.env file)",
                    "Verify Claude Desktop configuration",
                    "Ensure all required tokens are set",
                    "Run configuration validation tool",
                ]
            )
            error.recovery_actions.extend(
                [
                    "Run: python tools/config_manager.py validate",
                    "Check .env file exists and has correct values",
                    "Restart Claude Desktop after config changes",
                    "Use the fresh setup script if needed",
                ]
            )
            error.user_friendly_message = (
                "It looks like there's an issue with your configuration. "
                "This usually means environment variables or tokens need to be set up correctly."
            )

        elif error.category == ErrorCategory.AUTHENTICATION:
            error.suggestions.extend(
                [
                    "Check if your Moodle tokens are valid",
                    "Verify token permissions in Moodle",
                    "Ensure webservices are enabled",
                    "Check token expiration",
                ]
            )
            error.recovery_actions.extend(
                [
                    "Generate new tokens in Moodle",
                    "Run: python tools/config_manager.py update-tokens",
                    "Check Moodle webservice settings",
                    "Verify user permissions in Moodle",
                ]
            )
            error.user_friendly_message = (
                "Authentication failed. Your Moodle tokens might be expired or invalid. "
                "Try generating new tokens in your Moodle admin panel."
            )

        elif error.category == ErrorCategory.NETWORK:
            error.suggestions.extend(
                [
                    "Check if Moodle server is running",
                    "Verify network connectivity",
                    "Check firewall settings",
                    "Try accessing Moodle in browser",
                ]
            )
            error.recovery_actions.extend(
                [
                    "Test: curl http://localhost:8080",
                    "Check Docker containers: docker ps",
                    "Restart Moodle: docker-compose restart",
                    "Check network configuration",
                ]
            )
            error.user_friendly_message = "Can't connect to your Moodle server. Make sure it's running and accessible."

        elif error.category == ErrorCategory.MOODLE_API:
            error.suggestions.extend(
                [
                    "Check Moodle API documentation",
                    "Verify API endpoint exists",
                    "Check required parameters",
                    "Ensure plugin is installed",
                ]
            )
            error.recovery_actions.extend(
                [
                    "Check Moodle error logs",
                    "Verify plugin installation",
                    "Test API endpoint manually",
                    "Check Moodle webservice functions",
                ]
            )
            error.user_friendly_message = (
                "There was an issue with the Moodle API. This might be due to missing plugins "
                "or incorrect API configuration."
            )

        elif error.category == ErrorCategory.VALIDATION:
            error.suggestions.extend(
                [
                    "Check input format and requirements",
                    "Verify all required fields are provided",
                    "Check data types and constraints",
                    "Review API documentation",
                ]
            )
            error.recovery_actions.extend(
                [
                    "Review your input data",
                    "Check required vs optional parameters",
                    "Validate data format",
                    "Try with minimal test data",
                ]
            )
            error.user_friendly_message = "The input data doesn't meet the requirements. Please check the format and try again."

        elif error.category == ErrorCategory.PERFORMANCE:
            error.suggestions.extend(
                [
                    "Try with smaller content chunks",
                    "Check server resources",
                    "Enable caching if available",
                    "Reduce concurrent requests",
                ]
            )
            error.recovery_actions.extend(
                [
                    "Monitor system resources",
                    "Clear cache if needed",
                    "Reduce request size",
                    "Check server performance metrics",
                ]
            )
            error.user_friendly_message = "The operation is taking longer than expected. Try with smaller content or check server performance."

        elif error.category == ErrorCategory.PLUGIN:
            error.suggestions.extend(
                [
                    "Check if MoodleClaude plugin is installed",
                    "Verify plugin version compatibility",
                    "Check plugin configuration",
                    "Review plugin permissions",
                ]
            )
            error.recovery_actions.extend(
                [
                    "Install/update MoodleClaude plugin",
                    "Check plugin status in Moodle admin",
                    "Verify plugin configuration",
                    "Check plugin logs",
                ]
            )
            error.user_friendly_message = "There's an issue with the MoodleClaude plugin. Make sure it's properly installed and configured."

        # Add exception-specific suggestions
        if exception:
            exception_name = type(exception).__name__

            if "Connection" in exception_name or "Timeout" in exception_name:
                error.suggestions.insert(
                    0, "Check network connectivity and server status"
                )
                error.recovery_actions.insert(
                    0, "Verify Moodle server is running and accessible"
                )

            elif "Permission" in exception_name or "Forbidden" in exception_name:
                error.suggestions.insert(0, "Check user permissions and token validity")
                error.recovery_actions.insert(
                    0, "Verify user has required permissions in Moodle"
                )

            elif "NotFound" in exception_name:
                error.suggestions.insert(0, "Check if the requested resource exists")
                error.recovery_actions.insert(
                    0, "Verify the resource ID or path is correct"
                )

        # Add documentation links
        error.documentation_links.extend(base_docs)

        if error.category == ErrorCategory.CONFIGURATION:
            error.documentation_links.append(
                "https://github.com/sijadev/MoodleClaude/blob/main/README_CONFIG_MANAGEMENT.md"
            )

        if error.category in [ErrorCategory.MOODLE_API, ErrorCategory.PLUGIN]:
            error.documentation_links.append("https://docs.moodle.org/dev/Web_services")

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        if not self.error_history:
            return {"total_errors": 0, "recent_errors": []}

        # Group by category
        by_category = {}
        for error in self.error_history[-10:]:  # Last 10 errors
            category = error.category.value
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1

        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(
                [
                    e
                    for e in self.error_history
                    if (datetime.now() - e.context.timestamp).seconds < 3600
                ]
            ),
            "by_category": by_category,
            "last_error": self.error_history[-1].error_id
            if self.error_history
            else None,
        }

    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_count = 0
        logger.info("Error history cleared")


# Helper functions for common error scenarios
def create_configuration_error(
    handler: ErrorHandlerMixin, message: str, missing_config: str = None
) -> EnhancedError:
    """Create a configuration error"""
    context_data = {"missing_config": missing_config} if missing_config else {}
    return handler.create_error(
        category=ErrorCategory.CONFIGURATION,
        severity=ErrorSeverity.HIGH,
        title="Configuration Error",
        message=message,
        operation="configuration_check",
        context_data=context_data,
    )


def create_moodle_api_error(
    handler: ErrorHandlerMixin,
    message: str,
    api_function: str = None,
    exception: Exception = None,
) -> EnhancedError:
    """Create a Moodle API error"""
    context_data = {"api_function": api_function} if api_function else {}
    return handler.create_error(
        category=ErrorCategory.MOODLE_API,
        severity=ErrorSeverity.MEDIUM,
        title="Moodle API Error",
        message=message,
        operation="moodle_api_call",
        exception=exception,
        context_data=context_data,
    )


def create_validation_error(
    handler: ErrorHandlerMixin, message: str, invalid_field: str = None
) -> EnhancedError:
    """Create a validation error"""
    context_data = {"invalid_field": invalid_field} if invalid_field else {}
    return handler.create_error(
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.LOW,
        title="Validation Error",
        message=message,
        operation="input_validation",
        context_data=context_data,
    )


# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced error handling
    class TestHandler(ErrorHandlerMixin):
        def __init__(self):
            super().__init__()

    handler = TestHandler()

    # Test different error types
    config_error = create_configuration_error(
        handler, "Missing MOODLE_TOKEN environment variable", "MOODLE_TOKEN"
    )
    print("Configuration Error:")
    print(config_error.to_claude_response())
    print("\n" + "=" * 50 + "\n")

    api_error = create_moodle_api_error(
        handler,
        "Failed to create course",
        "core_course_create_courses",
        Exception("Invalid course category"),
    )
    print("API Error:")
    print(api_error.to_claude_response())
    print("\n" + "=" * 50 + "\n")

    # Show error summary
    summary = handler.get_error_summary()
    print("Error Summary:")
    print(json.dumps(summary, indent=2))
