# MoodleClaude Configuration Management

## 🎯 Problem gelöst: Ende des Passwort-Chaos

**Vorher:** 4+ verschiedene Admin-Passwörter in verschiedenen Dateien  
**Nachher:** 1 zentrales Konfigurationssystem für alles

## 🏗️ Neue Architektur

### **Single Source of Truth**

```
config/master_config.py  ← EINZIGE Wahrheitsquelle
├── Generiert: .env
├── Generiert: config/moodle_tokens_*.env  
├── Generiert: Claude Desktop Config
└── Validiert: Konsistenz überall
```

### **Einheitliche Credentials**

- **Admin:** `admin` / `MoodleClaude2025!`
- **WS User:** `wsuser` / `MoodleClaudeWS2025!`
- **Tokens:** Auto-generiert und synchronisiert

## 🚀 Verwendung

### **Alles synchronisieren**

```bash
python tools/config_manager.py sync-all
```

### **Nur .env Dateien neu generieren**  

```bash
python tools/config_manager.py generate-env
```

### **Claude Desktop aktualisieren**

```bash
python tools/config_manager.py update-claude-desktop
```

### **Konfiguration validieren**

```bash
python tools/config_manager.py validate
```

### **Aktuelle Config anzeigen**

```bash
python tools/config_manager.py show
```

### **API Tokens aktualisieren**

```bash
python tools/config_manager.py update-tokens \
  --admin-token "abc123..." \
  --plugin-token "def456..."
```

## 🔧 Wie es funktioniert

### **1. Master Config (config/master_config.py)**

- Zentrale Python-Klasse mit allen Einstellungen
- Typsicher, dokumentiert, erweiterbar
- Validation und Konsistenz-Checks

### **2. Config Manager (tools/config_manager.py)**

- CLI-Tool für alle Config-Operationen
- Automatische Synchronisation
- Backup und Rollback

### **3. Generated Files**

Alle diese Dateien werden **automatisch generiert**:

- `.env` - Hauptkonfiguration
- `config/moodle_tokens_current.env` - Legacy Support
- `config/moodle_tokens_fresh.env` - Legacy Support  
- Claude Desktop Config - MCP Server Settings

## ⚠️ Wichtige Regeln

### **❌ NIEMALS editieren:**

- `.env` (auto-generated)
- `config/moodle_tokens_*.env` (auto-generated)

### **✅ NUR editieren:**

- `config/master_config.py` - Dann `sync-all` ausführen

### **🔄 Nach Änderungen immer:**

```bash
python tools/config_manager.py sync-all
```

## 🛡️ Sicherheitsfeatures

- **Automatische Backups** vor Config-Updates
- **Validation** aller Einstellungen
- **Konsistenz-Checks** zwischen Dateien  
- **Typsichere** Konfiguration
- **Versionierung** und Timestamps

## 🎉 Vorteile

✅ **Ein Passwort für alles**  
✅ **Automatische Synchronisation**  
✅ **Keine Config-Drift mehr**  
✅ **Typsichere Einstellungen**  
✅ **Einfache Updates**  
✅ **Automatische Validation**  

## 🔧 Migration bestehender Setups

1. **Backup erstellen:**

   ```bash
   cp .env .env.backup
   ```

2. **Auf neues System migrieren:**

   ```bash
   python tools/config_manager.py sync-all
   ```

3. **Tokens neu generieren:**

   ```bash
   # Nach Moodle-Setup:
   python tools/config_manager.py update-tokens \
     --admin-token "new_token_here"
   ```

4. **Claude Desktop neustarten**

## 📋 Troubleshooting

### **Config inkonsistent?**

```bash
python tools/config_manager.py validate
python tools/config_manager.py sync-all
```

### **Tokens funktionieren nicht?**

```bash
# Neue Tokens generieren, dann:
python tools/config_manager.py update-tokens --admin-token "new_token"
```

### **Claude Desktop startet nicht?**

```bash
python tools/config_manager.py update-claude-desktop
# Dann Claude Desktop neustarten
```

---

**🎯 Ziel erreicht: Nie wieder Passwort-Chaos!**
