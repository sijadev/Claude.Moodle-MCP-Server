"""
Dual-token configuration system for MoodleClaude
Handles both basic Moodle operations and enhanced plugin functionality
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DualTokenConfig:
    """Configuration class supporting dual tokens for basic and enhanced functionality"""

    # Basic configuration
    moodle_url: str

    # Dual token support
    basic_token: str  # For standard Moodle operations
    plugin_token: Optional[str] = None  # For MoodleClaude plugin operations

    # Fallback to single token if only one provided
    single_token: Optional[str] = None

    # Other config
    username: str = ""
    server_name: str = "moodle-course-creator"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "DualTokenConfig":
        """Load configuration from environment variables"""

        # Load from .env file if it exists
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

        moodle_url = os.getenv("MOODLE_URL", "")
        if not moodle_url:
            raise ValueError("MOODLE_URL environment variable is required")

        # Check for dual token configuration
        basic_token = os.getenv("MOODLE_BASIC_TOKEN", "")
        plugin_token = os.getenv("MOODLE_PLUGIN_TOKEN", "")

        # Fallback to single token if dual tokens not provided
        single_token = os.getenv("MOODLE_TOKEN", "")

        # Determine token configuration
        if basic_token and plugin_token:
            # Dual token mode
            return cls(
                moodle_url=moodle_url,
                basic_token=basic_token,
                plugin_token=plugin_token,
                username=os.getenv("MOODLE_USERNAME", ""),
                server_name=os.getenv("SERVER_NAME", "moodle-course-creator"),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
            )
        elif single_token:
            # Single token mode (try to use for both basic and plugin operations)
            return cls(
                moodle_url=moodle_url,
                basic_token=single_token,
                plugin_token=None,  # Will attempt to use basic_token for plugin ops
                single_token=single_token,
                username=os.getenv("MOODLE_USERNAME", ""),
                server_name=os.getenv("SERVER_NAME", "moodle-course-creator"),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
            )
        else:
            raise ValueError(
                "No valid token configuration found. Please set either:\n"
                "1. MOODLE_BASIC_TOKEN and MOODLE_PLUGIN_TOKEN (dual mode), or\n"
                "2. MOODLE_TOKEN (single mode)"
            )

    def get_basic_token(self) -> str:
        """Get token for basic Moodle operations"""
        return self.basic_token

    def get_plugin_token(self) -> str:
        """Get token for plugin operations (falls back to basic token if not set)"""
        return self.plugin_token or self.basic_token

    def is_dual_token_mode(self) -> bool:
        """Check if we're in dual token mode"""
        return bool(self.plugin_token)

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging"""
        return {
            "moodle_url": self.moodle_url,
            "username": self.username,
            "token_mode": "dual" if self.is_dual_token_mode() else "single",
            "basic_token_set": bool(self.basic_token),
            "plugin_token_set": bool(self.plugin_token),
            "server_name": self.server_name,
            "log_level": self.log_level,
        }
