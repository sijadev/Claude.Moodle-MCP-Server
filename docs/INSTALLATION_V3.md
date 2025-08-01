# 🚀 MoodleClaude v3.0 - One-Command Installation

**Vollautomatischer Setup für MoodleClaude mit centralized configuration**

## ⚡ Quick Install

```bash
python tools/setup/setup_fresh_moodle_v2.py --quick-setup
```

**Das war's! 🎉** 

- ⏱️ **~5-10 Minuten** Laufzeit
- 🔧 **100% automatisch** - keine manuellen Schritte
- ✅ **Vollständige Validierung** - 7-stufiger Test
- 🎯 **Ready-to-use** - direkt einsatzbereit

## 📋 Was passiert automatisch?

✅ **Docker Cleanup** - Alte Container & Daten entfernen  
✅ **Fresh Installation** - Neue Container mit PostgreSQL  
✅ **Admin Setup** - `admin/MoodleClaude2025!`  
✅ **Plugin Installation** - MoodleClaude automatisch installiert  
✅ **WebService User** - `wsuser/MoodleClaudeWS2025!` erstellt  
✅ **API Tokens** - Automatisch generiert und konfiguriert  
✅ **MCP Server** - Path-Fixes und Validation  
✅ **Claude Desktop** - Konfiguration aktualisiert  
✅ **System Tests** - End-to-End Validierung  

## 🎛️ Nach der Installation

1. **Claude Desktop neustarten** (wichtig!)
2. **Erste Kurse erstellen** über MCP interface
3. **System nutzen** - vollständig einsatzbereit!

## 📖 Ausführliche Dokumentation

→ [**SETUP_GUIDE_V3.md**](SETUP_GUIDE_V3.md) - Komplette Anleitung  
→ [**README_CONFIG_MANAGEMENT.md**](README_CONFIG_MANAGEMENT.md) - Config-System

## 🔧 Konfiguration verwalten

```bash
# Status prüfen
python tools/config_manager.py validate

# Alles synchronisieren  
python tools/config_manager.py sync-all

# Aktuelle Config anzeigen
python tools/config_manager.py show
```

## 🎯 Features v3.0

- **🔥 Zero-Touch Installation** - Ein Befehl, fertig!
- **🏗️ Centralized Config** - Single Source of Truth
- **🔄 Auto-Sync** - Alle Configs immer konsistent
- **🧪 Comprehensive Testing** - 7-stufige Validierung
- **🛡️ Error Recovery** - Robuste Fehlerbehandlung
- **📊 Live Progress** - Detaillierte Status-Updates

---

**Ready? Let's go! 🚀**

```bash
python tools/setup/setup_fresh_moodle_v2.py --quick-setup
```