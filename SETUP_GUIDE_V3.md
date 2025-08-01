# MoodleClaude Fresh Installation Guide v3.0

🎯 **Vollautomatischer Setup-Workflow für MoodleClaude mit centralized configuration**

## 🚀 Quick Start

```bash
# Vollautomatische Installation (empfohlen)
python tools/setup/setup_fresh_moodle_v2.py --quick-setup

# Mit manueller Bestätigung
python tools/setup/setup_fresh_moodle_v2.py

# Nur Konfiguration testen
python tools/setup/setup_fresh_moodle_v2.py --config-only --quick-setup
```

## ✨ Was macht der v3.0 Setup automatisch?

### 🔧 **Phase 1: Vorbereitung**
- ✅ Centralized Configuration System aktivieren
- ✅ Alle Config-Dateien (.env, tokens, Claude Desktop) generieren
- ✅ Docker Cleanup (Container, Volumes, persistente Daten)

### 🐳 **Phase 2: Container-Setup**
- ✅ Fresh Docker Container mit unified config starten
- ✅ Moodle Initialisierung warten (health checks)
- ✅ Admin-Passwort automatisch setzen: `admin/MoodleClaude2025!`

### 🌐 **Phase 3: Webservices**
- ✅ Moodle Webservices aktivieren (REST protocol)
- ✅ MoodleClaude Plugin automatisch installieren
- ✅ WebService User automatisch erstellen: `wsuser/MoodleClaudeWS2025!`

### 🔑 **Phase 4: API Integration**
- ✅ Admin Token automatisch generieren
- ✅ WSUser Token automatisch generieren
- ✅ Tokens in master_config.py integrieren
- ✅ Alle Config-Dateien automatisch aktualisieren

### 🖥️ **Phase 5: Claude Desktop**
- ✅ MCP Server Pfad-Probleme automatisch beheben
- ✅ Claude Desktop Konfiguration aktualisieren
- ✅ Server-Funktionalität validieren

### 🧪 **Phase 6: Validierung**
- ✅ 7-stufiger Validierungstest
- ✅ Alle Komponenten durchprüfen
- ✅ End-to-End Funktionalität bestätigen

## 📋 Setup-Verlauf im Detail

```
🚀 MoodleClaude Fresh Installation v2.0
=====================================

🎯 Generating unified configuration...
✅ Generated: .env
✅ Generated: config/moodle_tokens_current.env  
✅ Generated: config/moodle_tokens_fresh.env
✅ Updated Claude Desktop configuration

🧹 Cleaning up existing containers...
✅ Stop and remove containers with volumes
✅ Clean up Docker system
✅ Clean up Docker volumes

🐳 Starting fresh containers...
✅ Start MoodleClaude containers
✅ Containers started

⏳ Waiting for Moodle to be ready...
✅ Moodle is ready!

👤 Setting up Moodle admin...
✅ Admin credentials configured

🌐 Enabling Moodle webservices...
✅ Enable web services
✅ Enable REST protocol

🔌 Installing MoodleClaude plugin...
✅ Copy plugin files to container
✅ Set plugin permissions
✅ Install and upgrade plugin

🔧 Creating webservice user...
✅ WebService user 'wsuser' created successfully

🎫 Generating API tokens...
✅ Admin token generated: bfef4e5ef1f77d5ad173...
✅ WSUser token generated: e14a2f11d2695415dd90...
✅ Tokens updated in master configuration

🔧 Fixing MCP server launcher...
✅ MCP server launcher working correctly

🖥️ Updating Claude Desktop configuration...
✅ Claude Desktop configuration updated
🔄 Please restart Claude Desktop to apply changes

🧪 Running comprehensive validation tests...

1️⃣ Testing basic connectivity...
✅ Test Moodle web interface
✅ Check container status

2️⃣ Testing admin authentication...
✅ Admin login test passed

3️⃣ Testing API tokens...
✅ Admin token validation passed
✅ Plugin token present

4️⃣ Testing MoodleClaude plugin...
✅ Plugin files present

5️⃣ Testing WebService user...
✅ WebService user validation passed

6️⃣ Testing configuration consistency...
✅ Configuration validation passed

7️⃣ Testing MCP Server...
✅ MCP Server test passed

🎯 Validation Summary:
✅ All validation tests passed - System ready!

============================================================
🎉 MoodleClaude Fresh Installation Complete!
============================================================
🌐 Moodle URL: http://localhost:8080
👤 Admin User: admin
🔐 Admin Password: MoodleClaude2025!
🔧 WS User: wsuser  
🔐 WS Password: MoodleClaudeWS2025!

📋 Next Steps:
1. Restart Claude Desktop to apply changes
2. Test MCP server integration
3. Start creating courses with MoodleClaude!
```

## 🎛️ Setup-Optionen

### **Vollautomatisch (empfohlen)**
```bash
python tools/setup/setup_fresh_moodle_v2.py --quick-setup
```
- Keine manuellen Eingaben erforderlich
- Komplette Automatisierung aller Schritte
- ~5-10 Minuten Laufzeit

### **Mit Bestätigung**
```bash
python tools/setup/setup_fresh_moodle_v2.py
```
- Bestätigung vor Docker-Cleanup
- Gleicher automatischer Ablauf

### **Nur Konfiguration**
```bash
python tools/setup/setup_fresh_moodle_v2.py --config-only --quick-setup
```
- Testet nur das Configuration System
- Keine Docker-Operationen
- Schnelle Validierung

### **Erweiterte Optionen**
```bash
python tools/setup/setup_fresh_moodle_v2.py --help
```

## 🏗️ Technische Details

### **Centralized Configuration System**
- **Master Config:** `config/master_config.py` - Single Source of Truth
- **Auto-Generated:** `.env`, `config/moodle_tokens_*.env`
- **Synchronized:** Claude Desktop configuration
- **Validated:** Konsistenz-Checks überall

### **Docker-Setup**
- **Container:** PostgreSQL + Moodle 4.3 + PgAdmin
- **Network:** `moodle_fresh_network`
- **Ports:** 8080 (Moodle), 8082 (PgAdmin)
- **Data:** Keine persistenten Volumes = immer fresh

### **Plugin-Integration**
- **Source:** `moodle_plugin/local_moodleclaude/`
- **Target:** `/opt/bitnami/moodle/local/moodleclaude/`
- **Permissions:** `daemon:daemon`
- **Installation:** Automatisch via CLI upgrade

### **Token-Management** 
- **Admin Token:** Via moodle_mobile_app service
- **WSUser Token:** Via external_generate_token()
- **Storage:** Master configuration + sync zu allen files
- **Validation:** API-Calls zur Funktions-Prüfung

## 🔧 Konfiguration verwalten

### **Alles synchronisieren**
```bash
python tools/config_manager.py sync-all
```

### **Status prüfen**
```bash
python tools/config_manager.py validate
python tools/config_manager.py show
```

### **Tokens aktualisieren**  
```bash
python tools/config_manager.py update-tokens \
  --admin-token "new_admin_token" \
  --plugin-token "new_plugin_token"
```

### **Claude Desktop updaten**
```bash
python tools/config_manager.py update-claude-desktop
```

## 🚨 Troubleshooting

### **Installation schlägt fehl**
1. Docker läuft? `docker --version`
2. Ports frei? `lsof -i :8080`
3. Logs prüfen: `docker-compose logs`

### **Token-Probleme**
1. Webservices aktiv? Check Moodle Admin
2. Benutzer existiert? Check User-Management
3. Neu generieren: Setup erneut laufen lassen

### **MCP Server startet nicht**
1. Path-Probleme? Bereits automatisch behoben in v3.0
2. Claude Desktop neustarten
3. Logs prüfen: Claude Desktop → Settings → Logs

### **Config inkonsistent**
```bash
python tools/config_manager.py validate
python tools/config_manager.py sync-all
```

## 🎯 Nach der Installation

### **1. Claude Desktop neustarten**
- Wichtig für MCP Server Updates
- Settings → Restart Application

### **2. Ersten Kurs erstellen**
- Über Claude Desktop interface
- MCP Tools verwenden
- Automatische Content-Generierung testen

### **3. System überwachen**
```bash
# Container Status
docker-compose ps

# Config Validation  
python tools/config_manager.py validate

# MCP Server Test
python server/mcp_server_launcher.py --test
```

## 📈 Neue Features in v3.0

✅ **100% Automatisierung** - Keine manuellen Schritte mehr  
✅ **Robuste Token-Generierung** - API-basiert mit Fallbacks  
✅ **MCP Server Auto-Fix** - Path-Probleme automatisch gelöst  
✅ **7-stufige Validierung** - Umfassende System-Tests  
✅ **Centralized Config** - Single Source of Truth  
✅ **Auto-Sync** - Alle Configs immer konsistent  

---

**🎉 Ready to use! Der v3.0 Setup macht MoodleClaude Installation so einfach wie noch nie.**