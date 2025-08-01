#!/usr/bin/env python3
"""
Root Directory Organization Tool
===============================

Organisiert alle Dateien im Root-Verzeichnis und verschiebt sie in passende Ordner
oder löscht unnötige Dateien.
"""

import os
import shutil
from pathlib import Path
import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class RootDirectoryOrganizer:
    """Tool zum Organisieren des Root-Verzeichnisses."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.moved_files = []
        self.deleted_files = []
        self.kept_files = []
        
    def move_file(self, source: Path, destination: Path, reason: str = ""):
        """Verschiebt eine Datei sicher."""
        try:
            # Erstelle Zielverzeichnis falls nötig
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Vermeide Überschreibung
            if destination.exists():
                counter = 1
                stem = destination.stem
                suffix = destination.suffix
                while destination.exists():
                    destination = destination.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            shutil.move(str(source), str(destination))
            self.moved_files.append((str(source), str(destination), reason))
            logger.info(f"📦 Moved: {source.name} → {destination.parent.name}/{destination.name} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to move {source}: {e}")
            return False
    
    def delete_file(self, file_path: Path, reason: str = ""):
        """Löscht eine Datei sicher."""
        try:
            size = file_path.stat().st_size if file_path.exists() else 0
            file_path.unlink()
            self.deleted_files.append((str(file_path), reason, size))
            logger.info(f"🗑️  Deleted: {file_path.name} ({size:,} bytes) - {reason}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete {file_path}: {e}")
            return False
    
    def keep_file(self, file_path: Path, reason: str = ""):
        """Markiert eine Datei als im Root behalten."""
        self.kept_files.append((str(file_path), reason))
        logger.info(f"✅ Keeping in root: {file_path.name} - {reason}")
    
    def organize_documentation_files(self):
        """Organisiert Dokumentationsdateien."""
        logger.info("📚 Organizing documentation files...")
        
        # Markdown-Dateien die ins docs/ Verzeichnis gehören
        doc_files = [
            "BACKUP_SYSTEM_UPDATE.md",
            "CLAUDE_DESKTOP_STATUS.md", 
            "DIRECTORY_STRUCTURE.md",
            "INSTALLATION_V3.md",
            "MERGE_SUMMARY_V3.md",
            "PERFORMANCE_OPTIMIZATION_IMPLEMENTATION.md",
            "README_CONFIG_MANAGEMENT.md",
            "SETUP_GUIDE_V3.md"
        ]
        
        docs_dir = self.project_root / "docs"
        
        for doc_file in doc_files:
            source = self.project_root / doc_file
            if source.exists():
                destination = docs_dir / doc_file
                self.move_file(source, destination, "Documentation file")
        
        # README.md und LICENSE im Root behalten
        for essential_file in ["README.md", "LICENSE"]:
            file_path = self.project_root / essential_file
            if file_path.exists():
                self.keep_file(file_path, "Essential project file")
    
    def organize_script_files(self):
        """Organisiert Script-Dateien."""
        logger.info("📜 Organizing script files...")
        
        # Shell scripts nach scripts/ oder operations/
        shell_scripts = [
            "backup.sh",
            "list_backups.sh", 
            "restore_default.sh",
            "setup_fresh.sh"
        ]
        
        for script_name in shell_scripts:
            source = self.project_root / script_name
            if source.exists():
                if "backup" in script_name.lower() or "restore" in script_name.lower():
                    destination = self.project_root / "operations" / "backup" / script_name
                else:
                    destination = self.project_root / "scripts" / script_name
                self.move_file(source, destination, "Shell script")
    
    def organize_config_files(self):
        """Organisiert Konfigurationsdateien."""
        logger.info("⚙️ Organizing configuration files...")
        
        # Python config files
        config_files = ["pyproject.toml", "pytest.ini", "pytest_e2e.ini", "requirements.txt", "requirements-e2e.txt"]
        
        for config_file in config_files:
            source = self.project_root / config_file
            if source.exists():
                self.keep_file(source, "Essential Python config")
        
        # Docker compose im Root behalten (häufig verwendet)
        docker_compose = self.project_root / "docker-compose.yml"
        if docker_compose.exists():
            self.keep_file(docker_compose, "Main Docker compose file")
    
    def organize_log_and_result_files(self):
        """Organisiert Log- und Ergebnisdateien."""
        logger.info("📋 Organizing log and result files...")
        
        # Log-Dateien nach logs/
        log_files = [
            "persistent_test_suite.log",
            "simple_test_suite.log"
        ]
        
        logs_dir = self.project_root / "logs"
        
        for log_file in log_files:
            source = self.project_root / log_file
            if source.exists():
                destination = logs_dir / log_file
                self.move_file(source, destination, "Log file")
        
        # Test result files nach test-results/ oder reports/
        result_files = [
            "simple_test_results.json",
            "cleanup_report.json"
        ]
        
        reports_dir = self.project_root / "reports"
        
        for result_file in result_files:
            source = self.project_root / result_file
            if source.exists():
                destination = reports_dir / result_file
                self.move_file(source, destination, "Report/result file")
    
    def organize_executable_files(self):
        """Organisiert ausführbare Dateien."""
        logger.info("🚀 Organizing executable files...")
        
        # Python executable files
        executable_files = [
            "start_server.py"
        ]
        
        for exec_file in executable_files:
            source = self.project_root / exec_file
            if source.exists():
                if exec_file == "start_server.py":
                    # Nach tools/ verschieben da es ein utility ist
                    destination = self.project_root / "tools" / exec_file
                    self.move_file(source, destination, "Utility script")
    
    def clean_empty_directories(self):
        """Entfernt leere Verzeichnisse."""
        logger.info("🧹 Cleaning empty directories...")
        
        # Finde alle Verzeichnisse
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    # Prüfe ob Verzeichnis leer ist (ignoriere versteckte Dateien)
                    contents = [f for f in dir_path.iterdir() if not f.name.startswith('.')]
                    if not contents:
                        dir_path.rmdir()
                        logger.info(f"🗑️  Removed empty directory: {dir_path.relative_to(self.project_root)}")
                except OSError:
                    # Verzeichnis nicht leer oder andere Probleme
                    pass
    
    def handle_special_files(self):
        """Behandelt spezielle Dateien."""
        logger.info("🔧 Handling special files...")
        
        # Makefile im Root behalten
        makefile = self.project_root / "Makefile"
        if makefile.exists():
            self.keep_file(makefile, "Build system file")
        
        # uv.lock (dependency lock file) im Root behalten  
        uv_lock = self.project_root / "uv.lock"
        if uv_lock.exists():
            self.keep_file(uv_lock, "Dependency lock file")
    
    def generate_organization_report(self):
        """Generiert einen Bericht über die Organisation."""
        report = {
            "organization_date": datetime.now().isoformat(),
            "summary": {
                "files_moved": len(self.moved_files),
                "files_deleted": len(self.deleted_files),
                "files_kept_in_root": len(self.kept_files)
            },
            "moved_files": self.moved_files,
            "deleted_files": self.deleted_files,
            "kept_files": self.kept_files
        }
        
        report_file = self.project_root / "reports" / "root_organization_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Organization report saved to: {report_file}")
        return report
    
    def run_organization(self):
        """Führt die komplette Organisation durch."""
        logger.info("🚀 Starting root directory organization...")
        logger.info(f"Project root: {self.project_root}")
        
        # Führe alle Organisationsschritte durch
        self.organize_documentation_files()
        self.organize_script_files()
        self.organize_config_files()
        self.organize_log_and_result_files()
        self.organize_executable_files()
        self.handle_special_files()
        
        # Aufräumen
        self.clean_empty_directories()
        
        # Generiere Bericht
        report = self.generate_organization_report()
        
        # Zusammenfassung
        logger.info("=" * 50)
        logger.info("🎯 ORGANIZATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Files moved: {report['summary']['files_moved']}")
        logger.info(f"Files deleted: {report['summary']['files_deleted']}")
        logger.info(f"Files kept in root: {report['summary']['files_kept_in_root']}")
        
        if report['summary']['files_moved'] > 0:
            logger.info("✅ Root directory organization completed!")
        else:
            logger.info("ℹ️  Root directory was already well organized!")
        
        # Zeige was im Root geblieben ist
        if self.kept_files:
            logger.info("\n📁 Files remaining in root:")
            for file_path, reason in self.kept_files:
                file_name = Path(file_path).name
                logger.info(f"  ✅ {file_name} - {reason}")
        
        return report

def main():
    """Main organization function."""
    project_root = Path(__file__).parent.parent
    
    print("🗂️  MoodleClaude Root Directory Organization Tool")
    print("=" * 55)
    print("🚀 Starting automatic organization...")
    
    organizer = RootDirectoryOrganizer(project_root)
    report = organizer.run_organization()
    
    # Zeige moved files
    if report['summary']['files_moved'] > 0:
        print(f"\n📦 Recently moved files:")
        for source, dest, reason in report['moved_files'][:10]:
            source_name = Path(source).name
            dest_name = Path(dest).parent.name + "/" + Path(dest).name
            print(f"  📦 {source_name} → {dest_name}")
        
        if len(report['moved_files']) > 10:
            print(f"  ... and {len(report['moved_files']) - 10} more files")
    
    print(f"\n💾 Full report saved to: reports/root_organization_report.json")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)