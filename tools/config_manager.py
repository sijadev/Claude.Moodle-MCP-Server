#!/usr/bin/env python3
"""
MoodleClaude Configuration Manager
=================================
Central tool to manage all MoodleClaude configurations
Prevents password chaos and ensures consistency

Usage:
    python tools/config_manager.py generate-env
    python tools/config_manager.py update-claude-desktop
    python tools/config_manager.py validate
    python tools/config_manager.py sync-all
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.master_config import get_master_config


def generate_env_files():
    """Generate all .env files from master config"""
    config = get_master_config()
    
    files_to_generate = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "config" / "moodle_tokens_current.env",
        PROJECT_ROOT / "config" / "moodle_tokens_fresh.env"
    ]
    
    print("🔧 Generating .env files from master configuration...")
    
    for filepath in files_to_generate:
        config.generate_env_file(str(filepath))
        print(f"✅ Generated: {filepath.relative_to(PROJECT_ROOT)}")
    
    print(f"🎯 Using unified admin password: {config.credentials.admin_password}")
    print(f"🎯 Using unified WS user: {config.credentials.ws_user}")


def update_claude_desktop_config():
    """Update Claude Desktop configuration"""
    config = get_master_config()
    claude_config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    
    if not claude_config_path.exists():
        print(f"❌ Claude Desktop config not found: {claude_config_path}")
        return
    
    # Read existing config
    with open(claude_config_path, 'r') as f:
        claude_config = json.load(f)
    
    # Update moodle-robust server config
    mcp_servers = claude_config.get("mcpServers", {})
    moodle_server_config = config.get_claude_desktop_config()
    
    mcp_servers["moodle-robust"] = moodle_server_config
    claude_config["mcpServers"] = mcp_servers
    
    # Backup original
    backup_path = claude_config_path.with_suffix('.json.backup')
    if claude_config_path.exists():
        import shutil
        shutil.copy2(claude_config_path, backup_path)
        print(f"📦 Backup created: {backup_path}")
    
    # Write updated config
    with open(claude_config_path, 'w') as f:
        json.dump(claude_config, f, indent=2)
    
    print("✅ Updated Claude Desktop configuration")
    print(f"🎯 Admin Token: {config.services.admin_token}")
    print(f"🎯 Plugin Token: {config.services.plugin_token}")


def validate_configuration():
    """Validate configuration consistency"""
    config = get_master_config()
    validation = config.validate_config()
    
    print("🔍 Configuration Validation Report")
    print("=" * 40)
    print(f"Status: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
    print(f"Version: {validation['config_version']}")
    print(f"Last Updated: {validation['last_updated']}")
    
    if validation['issues']:
        print("\n🚨 Issues Found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    if validation['warnings']:
        print("\n⚠️ Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if not validation['issues'] and not validation['warnings']:
        print("\n🎉 Configuration is clean!")
    
    return validation['valid']


def sync_all_configurations():
    """Synchronize all configuration files"""
    print("🔄 Synchronizing all MoodleClaude configurations...")
    
    # 1. Generate env files
    generate_env_files()
    
    # 2. Update Claude Desktop
    update_claude_desktop_config()
    
    # 3. Validate everything
    is_valid = validate_configuration()
    
    if is_valid:
        print("\n🎉 All configurations synchronized successfully!")
    else:
        print("\n⚠️ Synchronization completed with warnings/issues")
    
    return is_valid


def update_tokens(admin_token: str = "", ws_token: str = "", plugin_token: str = ""):
    """Update API tokens in master config"""
    config = get_master_config()
    config.update_tokens(admin_token, ws_token, plugin_token)
    
    # Save updated config
    config_file = PROJECT_ROOT / "config" / "master_config.json"
    config.save_to_file(str(config_file))
    
    print("✅ Tokens updated in master configuration")
    
    # Re-sync everything
    sync_all_configurations()


def cleanup_legacy_configs():
    """Clean up old/duplicate configuration files"""
    legacy_files = [
        ".env.bak",
        "config/moodle_tokens_old.env",
        "config/moodle_tokens_backup.env"
    ]
    
    print("🧹 Cleaning up legacy configuration files...")
    
    for file_path in legacy_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            full_path.unlink()
            print(f"🗑️ Removed: {file_path}")
    
    print("✅ Legacy cleanup completed")


def show_current_config():
    """Display current configuration summary"""
    config = get_master_config()
    
    print("📋 Current MoodleClaude Configuration")
    print("=" * 40)
    print(f"🌐 Moodle URL: {config.services.url}")
    print(f"👤 Admin User: {config.credentials.admin_user}")
    print(f"🔐 Admin Password: {config.credentials.admin_password}")
    print(f"🔧 WS User: {config.credentials.ws_user}")
    print(f"🚀 Server Name: {config.server.name}")
    print(f"📊 Version: {config.config_version}")
    print(f"🕒 Last Updated: {config.last_updated}")
    
    if config.services.admin_token:
        print(f"🎫 Admin Token: {config.services.admin_token[:20]}...")
    if config.services.plugin_token:
        print(f"🎫 Plugin Token: {config.services.plugin_token[:20]}...")


def main():
    parser = argparse.ArgumentParser(description="MoodleClaude Configuration Manager")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate env files
    subparsers.add_parser('generate-env', help='Generate .env files from master config')
    
    # Update Claude Desktop
    subparsers.add_parser('update-claude-desktop', help='Update Claude Desktop configuration')
    
    # Validate
    subparsers.add_parser('validate', help='Validate configuration consistency')
    
    # Sync all
    subparsers.add_parser('sync-all', help='Synchronize all configurations')
    
    # Update tokens
    token_parser = subparsers.add_parser('update-tokens', help='Update API tokens')
    token_parser.add_argument('--admin-token', help='Admin API token')
    token_parser.add_argument('--ws-token', help='Web service user token')
    token_parser.add_argument('--plugin-token', help='Plugin token')
    
    # Cleanup
    subparsers.add_parser('cleanup', help='Clean up legacy configuration files')
    
    # Show config
    subparsers.add_parser('show', help='Show current configuration')
    
    args = parser.parse_args()
    
    if args.command == 'generate-env':
        generate_env_files()
    elif args.command == 'update-claude-desktop':
        update_claude_desktop_config()
    elif args.command == 'validate':
        validate_configuration()
    elif args.command == 'sync-all':
        sync_all_configurations()
    elif args.command == 'update-tokens':
        update_tokens(
            admin_token=args.admin_token or "",
            ws_token=args.ws_token or "",
            plugin_token=args.plugin_token or ""
        )
    elif args.command == 'cleanup':
        cleanup_legacy_configs()
    elif args.command == 'show':
        show_current_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()