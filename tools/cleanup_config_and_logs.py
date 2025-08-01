#!/usr/bin/env python3
"""
Config and Log Cleanup Tool
===========================

Räumt unnötige Config- und Log-Dateien auf und behält nur die essentiellen Dateien.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ConfigLogCleaner:
    """Tool zum Aufräumen von Config- und Log-Dateien."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.removed_files = []
        self.removed_dirs = []
        self.kept_files = []
        self.total_size_removed = 0
    
    def calculate_size(self, path: Path) -> int:
        """Berechnet die Größe einer Datei oder eines Verzeichnisses."""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0
    
    def remove_file_or_dir(self, path: Path, reason: str = ""):
        """Entfernt eine Datei oder Verzeichnis sicher."""
        if not path.exists():
            return
        
        size = self.calculate_size(path)
        
        try:
            if path.is_file():
                path.unlink()
                self.removed_files.append((str(path), reason, size))
                logger.info(f"🗑️  Removed file: {path.name} ({size:,} bytes) - {reason}")
            elif path.is_dir():
                shutil.rmtree(path)
                self.removed_dirs.append((str(path), reason, size))
                logger.info(f"🗑️  Removed directory: {path.name} ({size:,} bytes) - {reason}")
            
            self.total_size_removed += size
            
        except Exception as e:
            logger.error(f"❌ Failed to remove {path}: {e}")
    
    def keep_file(self, path: Path, reason: str = ""):
        """Markiert eine Datei als behalten."""
        if path.exists():
            size = self.calculate_size(path)
            self.kept_files.append((str(path), reason, size))
            logger.info(f"✅ Keeping: {path.name} - {reason}")
    
    def cleanup_duplicate_configs(self):
        """Räumt doppelte und unnötige Config-Dateien auf."""
        logger.info("🧹 Cleaning up duplicate config files...")
        
        config_dir = self.project_root / "config"
        
        # Behalte nur die wichtigen Config-Dateien
        essential_configs = [
            "master_config.py",
            "master_config.json", 
            "claude_desktop_working.json",
            "__init__.py"
        ]
        
        # Prüfe alle Config-Dateien
        if config_dir.exists():
            for config_file in config_dir.iterdir():
                if config_file.is_file():
                    if config_file.name in essential_configs:
                        self.keep_file(config_file, "Essential config")
                    elif config_file.name.startswith("claude_desktop_config"):
                        if "advanced" in config_file.name or "basic" in config_file.name or "simple_test" in config_file.name:
                            self.remove_file_or_dir(config_file, "Duplicate/obsolete config")
                        else:
                            self.keep_file(config_file, "Working config")
                    elif config_file.name.endswith((".env", ".json", ".py")):
                        # Prüfe ob es wichtige Dateien sind
                        if any(keyword in config_file.name.lower() for keyword in ["token", "dual", "adaptive"]):
                            self.keep_file(config_file, "Token/auth config")
                        else:
                            self.remove_file_or_dir(config_file, "Obsolete config")
    
    def cleanup_old_logs(self, keep_days: int = 7):
        """Räumt alte Log-Dateien auf."""
        logger.info(f"🧹 Cleaning up log files older than {keep_days} days...")
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        log_dirs = [
            self.project_root / "logs",
            self.project_root
        ]
        
        for log_dir in log_dirs:
            if not log_dir.exists():
                continue
            
            for log_file in log_dir.glob("*.log"):
                if log_file.is_file():
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_time < cutoff_date:
                        self.remove_file_or_dir(log_file, f"Log older than {keep_days} days")
                    else:
                        self.keep_file(log_file, f"Recent log ({file_time.strftime('%Y-%m-%d')})")
    
    def cleanup_test_artifacts(self):
        """Räumt Test-Artefakte und temporäre Dateien auf."""
        logger.info("🧹 Cleaning up test artifacts...")
        
        # Test result files (behalte nur die neuesten)
        test_files = list(self.project_root.glob("*test*.json")) + list(self.project_root.glob("*test*.log"))
        
        # Sortiere nach Änderungszeit
        test_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Behalte nur die 3 neuesten Test-Dateien
        for i, test_file in enumerate(test_files):
            if i < 3:
                self.keep_file(test_file, f"Recent test result ({i+1}/3)")
            else:
                self.remove_file_or_dir(test_file, "Old test result")
        
        # Temporäre Dateien
        temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store"]
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                if temp_file.is_file():
                    self.remove_file_or_dir(temp_file, "Temporary file")
    
    def cleanup_backup_duplicates(self):
        """Räumt alte Backup-Duplikate auf."""
        logger.info("🧹 Cleaning up backup duplicates...")
        
        backups_dir = self.project_root / "backups"
        if not backups_dir.exists():
            return
        
        # Finde alle Backup-Verzeichnisse
        backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir() and "moodleclaude_" in d.name]
        
        # Sortiere nach Datum (neueste zuerst)
        backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Behalte nur die 3 neuesten Backups
        for i, backup_dir in enumerate(backup_dirs):
            if i < 3:
                self.keep_file(backup_dir, f"Recent backup ({i+1}/3)")
            else:
                self.remove_file_or_dir(backup_dir, "Old backup")
    
    def cleanup_docker_artifacts(self):
        """Räumt Docker-Artefakte auf."""
        logger.info("🧹 Cleaning up Docker artifacts...")
        
        docker_dir = self.project_root / "operations" / "docker"
        if not docker_dir.exists():
            return
        
        # Behalte nur die wichtigen Docker-Compose Dateien
        essential_docker_files = [
            "docker-compose.yml",
            "docker-compose.test.yml", 
            "Dockerfile.test"
        ]
        
        for docker_file in docker_dir.iterdir():
            if docker_file.is_file():
                if docker_file.name in essential_docker_files:
                    self.keep_file(docker_file, "Essential Docker file")
                elif docker_file.name.startswith("docker-compose."):
                    if any(keyword in docker_file.name for keyword in ["fresh", "minimal", "simple", "new", "optimized"]):
                        self.remove_file_or_dir(docker_file, "Duplicate Docker compose")
                    else:
                        self.keep_file(docker_file, "Working Docker file")
    
    def cleanup_obsolete_servers(self):
        """Räumt obsolete MCP Server-Dateien auf."""
        logger.info("🧹 Cleaning up obsolete MCP servers...")
        
        src_core_dir = self.project_root / "src" / "core"
        if not src_core_dir.exists():
            return
        
        # Behalte nur die aktuell verwendeten Server
        essential_servers = [
            "working_mcp_server.py",
            "test_data_storage.py"
        ]
        
        for server_file in src_core_dir.glob("*mcp*.py"):
            if server_file.name in essential_servers:
                self.keep_file(server_file, "Active MCP server")
            else:
                # Prüfe wenn es komplexe/obsolete Server sind
                if any(keyword in server_file.name for keyword in ["optimized", "advanced", "enhanced", "robust", "refactored"]):
                    self.remove_file_or_dir(server_file, "Obsolete MCP server variant")
                else:
                    self.keep_file(server_file, "Base MCP server")
    
    def generate_cleanup_report(self):
        """Generiert einen Bericht über die Aufräumung."""
        report = {
            "cleanup_date": datetime.now().isoformat(),
            "summary": {
                "files_removed": len(self.removed_files),
                "directories_removed": len(self.removed_dirs),
                "files_kept": len(self.kept_files),
                "total_size_removed_bytes": self.total_size_removed,
                "total_size_removed_mb": round(self.total_size_removed / (1024 * 1024), 2)
            },
            "removed_files": self.removed_files,
            "removed_directories": self.removed_dirs,
            "kept_files": self.kept_files[:20]  # Nur erste 20 anzeigen
        }
        
        report_file = self.project_root / "cleanup_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Cleanup report saved to: {report_file}")
        return report
    
    def run_cleanup(self):
        """Führt die komplette Aufräumung durch."""
        logger.info("🚀 Starting comprehensive cleanup...")
        logger.info(f"Project root: {self.project_root}")
        
        # Führe alle Aufräumungsschritte durch
        self.cleanup_duplicate_configs()
        self.cleanup_old_logs(keep_days=7)
        self.cleanup_test_artifacts()
        self.cleanup_backup_duplicates()
        self.cleanup_docker_artifacts()
        self.cleanup_obsolete_servers()
        
        # Generiere Bericht
        report = self.generate_cleanup_report()
        
        # Zusammenfassung
        logger.info("=" * 50)
        logger.info("🎯 CLEANUP SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Files removed: {report['summary']['files_removed']}")
        logger.info(f"Directories removed: {report['summary']['directories_removed']}")
        logger.info(f"Files kept: {report['summary']['files_kept']}")
        logger.info(f"Space freed: {report['summary']['total_size_removed_mb']} MB")
        
        if report['summary']['files_removed'] > 0 or report['summary']['directories_removed'] > 0:
            logger.info("✅ Cleanup completed successfully!")
        else:
            logger.info("ℹ️  No files needed cleanup - project already clean!")
        
        return report

def main():
    """Main cleanup function."""
    project_root = Path(__file__).parent.parent
    
    print("🧹 MoodleClaude Config and Log Cleanup Tool")
    print("=" * 50)
    print("🚀 Starting automatic cleanup...")
    
    cleaner = ConfigLogCleaner(project_root)
    report = cleaner.run_cleanup()
    
    # Zeige wichtige entfernte Dateien
    if report['summary']['files_removed'] > 0:
        print(f"\n📋 Recently removed files:")
        for file_path, reason, size in report['removed_files'][:10]:
            file_name = Path(file_path).name
            print(f"  - {file_name}: {reason} ({size:,} bytes)")
        
        if len(report['removed_files']) > 10:
            print(f"  ... and {len(report['removed_files']) - 10} more files")
    
    print(f"\n💾 Full report saved to: cleanup_report.json")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)