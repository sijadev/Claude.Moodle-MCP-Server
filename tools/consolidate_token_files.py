#!/usr/bin/env python3
"""
Token Files Consolidation Tool
==============================

Bereinigt doppelte Token-Dateien und behält nur eine aktuelle Version.
"""

import os
import shutil
from pathlib import Path
import logging
import json
from datetime import datetime
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class TokenFileConsolidator:
    """Tool zur Bereinigung von Token-Dateien."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.actions_taken = []
        
    def get_file_hash(self, file_path: Path) -> str:
        """Berechnet den SHA256-Hash einer Datei."""
        if not file_path.exists():
            return ""
        
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    
    def analyze_token_files(self):
        """Analysiert die Token-Dateien."""
        logger.info("🔍 Analyzing token files...")
        
        token_files = [
            "moodle_tokens.env",
            "moodle_tokens.env"
        ]
        
        file_info = {}
        
        for token_file in token_files:
            file_path = self.config_dir / token_file
            if file_path.exists():
                file_info[token_file] = {
                    'path': file_path,
                    'size': file_path.stat().st_size,
                    'mtime': file_path.stat().st_mtime,
                    'hash': self.get_file_hash(file_path)
                }
                logger.info(f"📋 Found: {token_file}")
                logger.info(f"   Size: {file_info[token_file]['size']} bytes")
                logger.info(f"   Modified: {datetime.fromtimestamp(file_info[token_file]['mtime']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        return file_info
    
    def consolidate_identical_files(self, file_info: dict):
        """Konsolidiert identische Dateien."""
        logger.info("🔄 Checking for identical files...")
        
        if len(file_info) < 2:
            logger.info("ℹ️  Less than 2 token files found - no consolidation needed")
            return
        
        # Gruppiere Dateien nach Hash
        hash_groups = {}
        for filename, info in file_info.items():
            file_hash = info['hash']
            if file_hash not in hash_groups:
                hash_groups[file_hash] = []
            hash_groups[file_hash].append((filename, info))
        
        # Finde identische Dateien
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                logger.info(f"🔍 Found {len(files)} identical files (hash: {file_hash[:16]}...)")
                
                # Sortiere nach Änderungszeit (neueste zuerst)
                files.sort(key=lambda x: x[1]['mtime'], reverse=True)
                
                # Behalte die neueste Datei
                keep_file = files[0]
                remove_files = files[1:]
                
                logger.info(f"✅ Keeping: {keep_file[0]} (newest)")
                
                for remove_file, info in remove_files:
                    logger.info(f"🗑️  Removing duplicate: {remove_file}")
                    
                    # Erstelle Backup vor dem Löschen
                    backup_name = f"{remove_file}.backup.{int(info['mtime'])}"
                    backup_path = self.config_dir / backup_name
                    
                    try:
                        shutil.copy2(info['path'], backup_path)
                        logger.info(f"💾 Backup created: {backup_name}")
                        
                        # Lösche das Duplikat
                        info['path'].unlink()
                        
                        self.actions_taken.append({
                            'action': 'removed_duplicate',
                            'file': remove_file,
                            'backup': backup_name,
                            'reason': f'Identical to {keep_file[0]}'
                        })
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to remove {remove_file}: {e}")
    
    def create_canonical_token_file(self):
        """Erstellt eine kanonische Token-Datei."""
        logger.info("📝 Creating canonical token file...")
        
        # Überprüfe welche Dateien noch existieren
        remaining_files = []
        for token_file in ["moodle_tokens.env", "moodle_tokens.env"]:
            file_path = self.config_dir / token_file
            if file_path.exists():
                remaining_files.append((token_file, file_path))
        
        if not remaining_files:
            logger.warning("⚠️  No token files found to create canonical version")
            return
        
        if len(remaining_files) == 1:
            current_file, current_path = remaining_files[0]
            
            # Wenn es nicht schon "moodle_tokens.env" ist, umbenenne es
            if current_file != "moodle_tokens.env":
                canonical_path = self.config_dir / "moodle_tokens.env"
                
                if canonical_path.exists():
                    # Backup der existierenden kanonischen Datei
                    backup_path = canonical_path.with_suffix(f'.env.backup.{int(datetime.now().timestamp())}')
                    shutil.move(canonical_path, backup_path)
                    logger.info(f"💾 Backed up existing canonical file to: {backup_path.name}")
                
                shutil.move(current_path, canonical_path)
                logger.info(f"📝 Renamed {current_file} → moodle_tokens.env")
                
                self.actions_taken.append({
                    'action': 'renamed_to_canonical',
                    'old_name': current_file,
                    'new_name': 'moodle_tokens.env'
                })
            else:
                logger.info("✅ Canonical token file already exists")
    
    def update_references(self):
        """Aktualisiert Referenzen auf die Token-Dateien."""
        logger.info("🔗 Updating references to token files...")
        
        # Finde Dateien die möglicherweise auf die alten Token-Dateien verweisen
        search_patterns = [
            "moodle_tokens.env",
            "moodle_tokens.env"
        ]
        
        # Durchsuche Python-Dateien
        python_files = list(self.project_root.rglob("*.py"))
        
        updated_files = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Ersetze Referenzen
                for old_name in search_patterns:
                    if old_name in content:
                        content = content.replace(old_name, "moodle_tokens.env")
                
                # Schreibe zurück wenn geändert
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    updated_files.append(str(py_file.relative_to(self.project_root)))
                    logger.info(f"🔧 Updated references in: {py_file.relative_to(self.project_root)}")
                    
            except Exception as e:
                logger.warning(f"⚠️  Could not update {py_file}: {e}")
        
        if updated_files:
            self.actions_taken.append({
                'action': 'updated_references',
                'files': updated_files
            })
        else:
            logger.info("ℹ️  No references needed updating")
    
    def generate_consolidation_report(self):
        """Generiert einen Bericht über die Konsolidierung."""
        report = {
            "consolidation_date": datetime.now().isoformat(),
            "actions_taken": self.actions_taken,
            "summary": {
                "total_actions": len(self.actions_taken)
            }
        }
        
        report_file = self.project_root / "reports" / "token_consolidation_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Consolidation report saved to: {report_file}")
        return report
    
    def run_consolidation(self):
        """Führt die komplette Konsolidierung durch."""
        logger.info("🚀 Starting token file consolidation...")
        logger.info(f"Config directory: {self.config_dir}")
        
        # Analysiere Token-Dateien
        file_info = self.analyze_token_files()
        
        if not file_info:
            logger.info("ℹ️  No token files found - nothing to consolidate")
            return
        
        # Konsolidiere identische Dateien
        self.consolidate_identical_files(file_info)
        
        # Erstelle kanonische Datei
        self.create_canonical_token_file()
        
        # Aktualisiere Referenzen
        self.update_references()
        
        # Generiere Bericht
        report = self.generate_consolidation_report()
        
        # Zusammenfassung
        logger.info("=" * 50)
        logger.info("🎯 CONSOLIDATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Actions taken: {report['summary']['total_actions']}")
        
        if report['summary']['total_actions'] > 0:
            logger.info("✅ Token file consolidation completed!")
            
            for action in self.actions_taken:
                if action['action'] == 'removed_duplicate':
                    logger.info(f"  🗑️  Removed duplicate: {action['file']}")
                elif action['action'] == 'renamed_to_canonical':
                    logger.info(f"  📝 Renamed: {action['old_name']} → {action['new_name']}")
                elif action['action'] == 'updated_references':
                    logger.info(f"  🔧 Updated {len(action['files'])} file references")
        else:
            logger.info("ℹ️  Token files were already consolidated!")
        
        return report

def main():
    """Main consolidation function."""
    project_root = Path(__file__).parent.parent
    
    print("🔧 MoodleClaude Token File Consolidation Tool")
    print("=" * 50)
    print("🚀 Starting automatic consolidation...")
    
    consolidator = TokenFileConsolidator(project_root)
    report = consolidator.run_consolidation()
    
    print(f"\n💾 Full report saved to: reports/token_consolidation_report.json")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)