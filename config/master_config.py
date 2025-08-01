#!/usr/bin/env python3
"""
MoodleClaude Master Configuration
=================================
Single Source of Truth for all MoodleClaude configurations
Prevents password chaos and configuration drift

Usage:
    from config.master_config import MoodleConfig
    config = MoodleConfig()
    admin_password = config.admin_password
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class MoodleCredentials:
    """Centralized Moodle credentials"""
    admin_user: str = "admin" 
    admin_password: str = "MoodleClaude2025!"
    admin_email: str = "admin@moodleclaude.local"
    
    # Web Service User
    ws_user: str = "wsuser"
    ws_password: str = "MoodleClaudeWS2025!"
    ws_email: str = "wsuser@moodleclaude.local"
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "bitnami_moodle"
    db_user: str = "bn_moodle"
    db_password: str = ""  # Set by Docker


@dataclass
class MoodleServices:
    """Moodle service configuration"""
    url: str = "http://localhost:8080"
    enable_webservices: bool = True
    webservice_protocols: str = "rest"
    
    # Auto-generated tokens (will be set by setup scripts)
    admin_token: str = ""
    ws_token: str = ""
    plugin_token: str = ""


@dataclass
class ServerConfig:
    """MCP Server configuration"""
    name: str = "robust-moodle-course-creator"
    version: str = "3.0.0"
    log_level: str = "INFO"
    max_chars: int = 8000
    use_emojis: bool = True
    detailed_progress: bool = True


class MoodleConfig:
    """Master Configuration Manager"""
    
    def __init__(self):
        self.credentials = MoodleCredentials()
        self.services = MoodleServices()
        self.server = ServerConfig()
        self.config_version = "3.0.0"
        self.last_updated = datetime.now().isoformat()
        
    def to_env_format(self) -> Dict[str, str]:
        """Export as environment variables format"""
        return {
            # Moodle Credentials
            "MOODLE_URL": self.services.url,
            "MOODLE_ADMIN_USER": self.credentials.admin_user,
            "MOODLE_ADMIN_PASSWORD": self.credentials.admin_password,
            "MOODLE_ADMIN_EMAIL": self.credentials.admin_email,
            
            # Web Service User
            "MOODLE_WS_USER": self.credentials.ws_user,
            "MOODLE_WS_PASSWORD": self.credentials.ws_password,
            "MOODLE_WS_EMAIL": self.credentials.ws_email,
            "MOODLE_USERNAME": self.credentials.ws_user,  # Legacy compatibility
            
            # Tokens (will be populated by setup)
            "MOODLE_BASIC_TOKEN": self.services.admin_token,
            "MOODLE_PLUGIN_TOKEN": self.services.plugin_token,
            "MOODLE_ADMIN_TOKEN": self.services.admin_token,
            "MOODLE_WSUSER_TOKEN": self.services.ws_token,
            
            # Database
            "MOODLE_DB_HOST": self.credentials.db_host,
            "MOODLE_DB_PORT": str(self.credentials.db_port),
            "MOODLE_DB_NAME": self.credentials.db_name,
            "MOODLE_DB_USER": self.credentials.db_user,
            
            # Server Config
            "SERVER_NAME": self.server.name,
            "LOG_LEVEL": self.server.log_level,
            "MOODLE_CLAUDE_MAX_CHARS": str(self.server.max_chars),
            "MOODLE_CLAUDE_USE_EMOJIS": str(self.server.use_emojis).lower(),
            "MOODLE_CLAUDE_DETAILED_PROGRESS": str(self.server.detailed_progress).lower(),
            
            # Meta
            "CONFIG_VERSION": self.config_version,
            "CONFIG_LAST_UPDATED": self.last_updated
        }
    
    def update_tokens(self, admin_token: str = "", ws_token: str = "", plugin_token: str = ""):
        """Update API tokens after generation"""
        if admin_token:
            self.services.admin_token = admin_token
        if ws_token:
            self.services.ws_token = ws_token
        if plugin_token:
            self.services.plugin_token = plugin_token
        self.last_updated = datetime.now().isoformat()
    
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        config_data = {
            "credentials": asdict(self.credentials),
            "services": asdict(self.services), 
            "server": asdict(self.server),
            "meta": {
                "config_version": self.config_version,
                "last_updated": self.last_updated
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str):
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        config = cls()
        config.credentials = MoodleCredentials(**data.get("credentials", {}))
        config.services = MoodleServices(**data.get("services", {}))
        config.server = ServerConfig(**data.get("server", {}))
        
        meta = data.get("meta", {})
        config.config_version = meta.get("config_version", "3.0.0")
        config.last_updated = meta.get("last_updated", datetime.now().isoformat())
        
        return config
    
    def generate_env_file(self, filepath: str):
        """Generate .env file from master config"""
        env_vars = self.to_env_format()
        
        with open(filepath, 'w') as f:
            f.write(f"# MoodleClaude Master Configuration\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Config Version: {self.config_version}\n")
            f.write(f"# DO NOT EDIT - Generated from config/master_config.py\n\n")
            
            # Group related variables
            f.write("# === Moodle Instance ===\n")
            f.write(f"MOODLE_URL={env_vars['MOODLE_URL']}\n\n")
            
            f.write("# === Admin Credentials ===\n")
            f.write(f"MOODLE_ADMIN_USER={env_vars['MOODLE_ADMIN_USER']}\n")
            f.write(f"MOODLE_ADMIN_PASSWORD={env_vars['MOODLE_ADMIN_PASSWORD']}\n")
            f.write(f"MOODLE_ADMIN_EMAIL={env_vars['MOODLE_ADMIN_EMAIL']}\n\n")
            
            f.write("# === Web Service User ===\n")
            f.write(f"MOODLE_WS_USER={env_vars['MOODLE_WS_USER']}\n")
            f.write(f"MOODLE_WS_PASSWORD={env_vars['MOODLE_WS_PASSWORD']}\n")
            f.write(f"MOODLE_USERNAME={env_vars['MOODLE_USERNAME']}\n\n")
            
            f.write("# === API Tokens (Auto-generated) ===\n")
            f.write(f"MOODLE_BASIC_TOKEN={env_vars['MOODLE_BASIC_TOKEN']}\n")
            f.write(f"MOODLE_PLUGIN_TOKEN={env_vars['MOODLE_PLUGIN_TOKEN']}\n")
            f.write(f"MOODLE_ADMIN_TOKEN={env_vars['MOODLE_ADMIN_TOKEN']}\n")
            f.write(f"MOODLE_WSUSER_TOKEN={env_vars['MOODLE_WSUSER_TOKEN']}\n\n")
            
            f.write("# === Server Configuration ===\n")
            f.write(f"SERVER_NAME={env_vars['SERVER_NAME']}\n")
            f.write(f"LOG_LEVEL={env_vars['LOG_LEVEL']}\n")
            f.write(f"MOODLE_CLAUDE_MAX_CHARS={env_vars['MOODLE_CLAUDE_MAX_CHARS']}\n")
            f.write(f"MOODLE_CLAUDE_USE_EMOJIS={env_vars['MOODLE_CLAUDE_USE_EMOJIS']}\n")
            f.write(f"MOODLE_CLAUDE_DETAILED_PROGRESS={env_vars['MOODLE_CLAUDE_DETAILED_PROGRESS']}\n\n")
            
            f.write("# === Meta Information ===\n")
            f.write(f"CONFIG_VERSION={env_vars['CONFIG_VERSION']}\n")
            f.write(f"CONFIG_LAST_UPDATED={env_vars['CONFIG_LAST_UPDATED']}\n")

    def get_claude_desktop_config(self) -> Dict[str, Any]:
        """Generate Claude Desktop MCP server configuration"""
        env_vars = self.to_env_format()
        
        return {
            "command": "/Users/simonjanke/Projects/MoodleClaude/.venv/bin/python",
            "args": ["/Users/simonjanke/Projects/MoodleClaude/server/mcp_server_launcher.py"],
            "cwd": "/Users/simonjanke/Projects/MoodleClaude",
            "env": {
                "PYTHONPATH": "/Users/simonjanke/Projects/MoodleClaude",
                "MOODLE_URL": env_vars["MOODLE_URL"],
                "MOODLE_BASIC_TOKEN": env_vars["MOODLE_BASIC_TOKEN"],
                "MOODLE_PLUGIN_TOKEN": env_vars["MOODLE_PLUGIN_TOKEN"],
                "MOODLE_USERNAME": env_vars["MOODLE_USERNAME"],
                "SERVER_NAME": env_vars["SERVER_NAME"],
                "LOG_LEVEL": env_vars["LOG_LEVEL"],
                "MOODLE_CLAUDE_DB_PATH": "data/sessions.db",
                "MOODLE_CLAUDE_MAX_CHARS": env_vars["MOODLE_CLAUDE_MAX_CHARS"],
                "MOODLE_CLAUDE_USE_EMOJIS": env_vars["MOODLE_CLAUDE_USE_EMOJIS"],
                "MOODLE_CLAUDE_DETAILED_PROGRESS": env_vars["MOODLE_CLAUDE_DETAILED_PROGRESS"]
            }
        }

    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration consistency"""
        issues = []
        warnings = []
        
        # Check password strength
        if len(self.credentials.admin_password) < 8:
            issues.append("Admin password too weak (< 8 characters)")
        
        # Check required tokens
        if not self.services.admin_token and not self.services.ws_token:
            warnings.append("No API tokens configured - run token generation")
        
        # Check URL format
        if not self.services.url.startswith(('http://', 'https://')):
            issues.append("Invalid Moodle URL format")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config_version": self.config_version,
            "last_updated": self.last_updated
        }


# Global instance
_master_config = None

def get_master_config() -> MoodleConfig:
    """Get the global master configuration instance"""
    global _master_config
    if _master_config is None:
        config_file = "/Users/simonjanke/Projects/MoodleClaude/config/master_config.json"
        if os.path.exists(config_file):
            _master_config = MoodleConfig.load_from_file(config_file)
        else:
            _master_config = MoodleConfig()
            # Save default config
            _master_config.save_to_file(config_file)
    return _master_config


if __name__ == "__main__":
    # Demo usage
    config = MoodleConfig()
    print("🎯 Master Configuration Demo")
    print(f"Admin Password: {config.credentials.admin_password}")
    print(f"WS User: {config.credentials.ws_user}")
    print(f"Moodle URL: {config.services.url}")
    
    # Validate
    validation = config.validate_config()
    print(f"Valid: {validation['valid']}")
    if validation['issues']:
        print(f"Issues: {validation['issues']}")