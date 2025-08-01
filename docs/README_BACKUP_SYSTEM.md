# MoodleClaude v3.0 - Backup & Repository System

🔄 **Komplettes Backup-System für Docker Container und lokales Repository**

## 🎯 Überblick

Das Backup-System ermöglicht:
- **Vollständige Container-Backups** (Database, Files, Configuration)
- **Lokale Repository-Verwaltung** mit Git Integration
- **Automatische Wiederherstellung** kompletter Umgebungen
- **Smart Storage Management** (Große Dateien extern, Metadata in Git)

## 📦 Backup-System

### **Backup erstellen**
```bash
# Vollständiges Backup der aktuellen Umgebung
./backup_moodleclaude.sh
```

**Was wird gesichert:**
- ✅ **PostgreSQL Database** (vollständiger Dump)
- ✅ **Moodle Application Files** (alle PHP-Dateien)  
- ✅ **Moodle Data Directory** (User-Uploads, Cache)
- ✅ **MoodleClaude Plugin** (Custom Code)
- ✅ **Configuration Files** (Tokens, Settings)
- ✅ **Docker Images** (für Offline-Wiederherstellung)
- ✅ **Environment Snapshot** (System-Info)

### **Backups auflisten**
```bash
# Alle verfügbaren Backups anzeigen
./list_backups.sh
```

**Ausgabe-Beispiel:**
```
📦 MoodleClaude Backup Management
=================================

[1] moodleclaude_20250131_201530
    📅 Created: 2025-01-31
    ⏰ Timestamp: 2025-01-31 20:15:30  
    📊 Size: 2.1GB
    🎯 Type: fresh
    🗄️  Database: moodle_fresh
    🔄 Restore: ./restore_moodleclaude.sh moodleclaude_20250131_201530

Total Backups: 5, Total Size: 8.3GB
```

### **Backup wiederherstellen**
```bash
# Spezifisches Backup wiederherstellen
./restore_moodleclaude.sh moodleclaude_20250131_201530
```

**Was passiert beim Restore:**
1. **Container stoppen** und Volumes löschen
2. **Docker Images** wiederherstellen  
3. **Infrastructure starten** (PostgreSQL, Moodle, pgAdmin)
4. **Database importieren** aus SQL-Dump
5. **Dateien wiederherstellen** (Application, Data, Plugin)
6. **Permissions setzen** und Services starten
7. **Verification** - Web Interface testen

## 🗃️ Repository-Management

### **Repository initialisieren**
```bash
# Git Repository für Backup-Management vorbereiten
./manage_repository.sh init
```

**Was wird erstellt:**
- `.gitignore` für große Backup-Dateien
- `.backup_tracking` für Backup-Metadaten
- Repository-Struktur für Code + Backups

### **Development Snapshot**
```bash
# Schneller Snapshot der aktuellen Entwicklung
./manage_repository.sh save-snapshot
```

### **Backup + Git Commit**
```bash
# Vollständiges Backup erstellen UND in Git committen
./manage_repository.sh backup-commit
```

**Smart Storage Strategie:**
- **In Git**: Metadata, Konfiguration, Code-Änderungen
- **Extern**: Große Dateien (Database Dumps, Container Images)
- **Tracking**: `.backup_tracking` verfolgt externe Dateien

### **Repository Status**
```bash
# Überblick über Repository und Backups
./manage_repository.sh status
```

**Beispiel-Output:**
```
🗃️ Repository Status
===================

Git Status:
M  src/core/enhanced_mcp_server.py
A  new_feature.py

Recent Commits:
a1b2c3d 🔄 Backup: moodleclaude_20250131_201530
e4f5g6h 💾 Development Snapshot - 2025-01-31 19:45
h7i8j9k ✨ Add new architecture features

Backups: 5 total, 8.3GB
Latest: moodleclaude_20250131_201530 (2.1GB)

Repository Size: 1.2GB
Remote: git@github.com:user/moodleclaude.git
```

## 📋 Workflow-Beispiele

### **Tägliche Entwicklung**
```bash
# Regelmäßige Snapshots während Entwicklung
./manage_repository.sh save-snapshot

# Nach wichtigen Features
git add .
git commit -m "✨ New feature implemented"
```

### **Vor größeren Änderungen**  
```bash
# Vollständiges Backup als Sicherheitspunkt
./manage_repository.sh backup-commit

# Danach experimentieren
./setup_fresh_moodleclaude_complete.sh  # Fresh start
# ... development work ...

# Falls etwas schief geht
./restore_moodleclaude.sh moodleclaude_20250131_201530
```

### **Release-Management**
```bash
# Production-ready Backup erstellen
./backup_moodleclaude.sh

# Tag für Release
git tag -a v3.0.1 -m "MoodleClaude v3.0.1 Release"

# Push mit Tags
git push origin main --tags
```

### **Wartung**
```bash
# Alte Backups aufräumen (behält die letzten 5)
./manage_repository.sh clean-old-backups

# Remote synchronisieren
./manage_repository.sh sync-remote
```

## 🏗️ Backup-Struktur

```
backups/
├── moodleclaude_20250131_201530/
│   ├── container_info.json          # Container-Metadata
│   ├── backup_manifest.txt          # Backup-Übersicht
│   ├── environment_snapshot.txt     # System-Snapshot
│   ├── docker-compose.yml           # Docker-Konfiguration
│   ├── database_dump.sql            # PostgreSQL-Dump
│   ├── moodle_files.tar.gz          # Moodle-Application
│   ├── moodle_data.tar.gz           # Moodle-Daten
│   ├── plugin_files.tar.gz          # MoodleClaude-Plugin
│   ├── postgres_image.tar.gz        # Docker-Image
│   ├── moodle_image.tar.gz          # Docker-Image
│   ├── pgadmin_image.tar.gz          # Docker-Image
│   └── config/                      # Konfigurationsdateien
│       ├── moodle_fresh_complete.env
│       └── tokens.env
```

## 🔧 Erweiterte Features

### **Backup-Automatisierung**
```bash
# Cron-Job für tägliche Backups
echo "0 2 * * * cd /path/to/moodleclaude && ./backup_moodleclaude.sh" | crontab -
```

### **Remote-Backup-Sync**
```bash
# Backups zu Remote-Storage synchronisieren
rsync -av backups/ user@backup-server:/backups/moodleclaude/
```

### **Backup-Validierung**
```bash
# Backup-Integrität prüfen
cd backups/moodleclaude_20250131_201530/
sha256sum -c backup_manifest.txt
```

## ⚠️ Wichtige Hinweise

### **Disk Space Management**
- **Backups sind groß** (1-3GB pro Backup)
- **Regelmäßig aufräumen** mit `clean-old-backups`
- **Monitoring** des verfügbaren Speicherplatzes

### **Security**
- **Tokens in Backups** sind im Klartext gespeichert
- **Backup-Verzeichnis** sollte sicher sein (Permissions)
- **Remote-Backups** verschlüsselt übertragen

### **Performance**
- **Backup dauert** 2-5 Minuten je nach Datenmenge
- **Restore dauert** 5-10 Minuten für komplette Wiederherstellung
- **Fresh Setup** ist schneller als Restore für Development

## 🎯 Use Cases

### **Development Team**
```bash
# Team-Mitglied A erstellt Feature-Backup
./manage_repository.sh backup-commit

# Team-Mitglied B kann exakte Umgebung wiederherstellen
git pull
./restore_moodleclaude.sh moodleclaude_20250131_201530
```

### **Testing & QA**
```bash
# Definierte Test-Umgebung wiederherstellen
./restore_moodleclaude.sh test_baseline_backup

# Nach Tests: Fresh start für nächsten Test
./setup_fresh_moodleclaude_complete.sh
```

### **Production Deployment**
```bash
# Backup vor Deployment
./backup_moodleclaude.sh

# Bei Problemen: Rollback
./restore_moodleclaude.sh production_backup_pre_deployment
```

## 🚀 Integration mit MoodleClaude v3.0

Das Backup-System ist perfekt integriert mit:
- ✅ **Fresh Setup System** - Saubere Basis für Backups
- ✅ **Plugin Architecture** - Plugin-Code wird mit gesichert
- ✅ **v3.0 Architecture** - Alle neuen Features enthalten
- ✅ **Container Management** - Docker-optimiert
- ✅ **Development Workflow** - Git-Integration

**Perfekte Kombination für professionelle MoodleClaude-Entwicklung!** 🎉