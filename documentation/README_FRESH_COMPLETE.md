# MoodleClaude v3.0 - Fresh Complete Setup

🚀 **Vollautomatisches Fresh Setup mit Plugin und Web Services**

## 🎯 Was macht dieses Setup?

Dieses Setup erstellt eine **komplett frische MoodleClaude Installation** mit:

- ✅ **Fresh PostgreSQL Database** (keine alten Daten)
- ✅ **Fresh Moodle 4.3** (saubere Installation)
- ✅ **MoodleClaude Plugin** automatisch installiert
- ✅ **Web Services** vollständig konfiguriert
- ✅ **Tokens** automatisch generiert
- ✅ **Benutzer & Rollen** vorkonfiguriert
- ✅ **Keine manuellen Schritte** erforderlich

## 🚀 Ein-Klick-Setup

```bash
# Alles in einem Befehl
./setup_fresh_moodleclaude_complete.sh
```

**Das war's!** Nach 3-5 Minuten ist alles bereit für MoodleClaude v3.0.

## 📋 Was passiert automatisch?

### **Phase 1: Docker Environment**
- Entfernt alte Container und Volumes
- Startet PostgreSQL 16 + Moodle 4.3 + pgAdmin
- Wartet bis alle Services bereit sind

### **Phase 2: Plugin Installation**
- Kopiert MoodleClaude Plugin in Container
- Setzt korrekte Berechtigungen
- Führt Moodle Upgrade durch
- Registriert 5 custom Web Service Functions

### **Phase 3: Web Services Konfiguration**
- Aktiviert Web Services & REST Protocol
- Erstellt Web Service User `wsuser`
- Konfiguriert umfassende Rollen & Permissions
- Erstellt "MoodleClaude Content Creation Service"

### **Phase 4: Token Generierung**
- Generiert sichere Admin & WS-User Tokens
- Konfiguriert authorized users für External Service
- Testet Web Service Konnektivität
- Speichert alle Konfigurationen

## 🔑 Automatisch generierte Zugangsdaten

Nach dem Setup findest du alle Credentials in `config/moodle_fresh_complete.env`:

```env
# Moodle Zugang
MOODLE_URL=http://localhost:8080
MOODLE_ADMIN_USER=admin
MOODLE_ADMIN_PASSWORD=Fresh2025Admin!

# Web Service Access  
MOODLE_WS_USER=wsuser
MOODLE_WS_PASSWORD=FreshWS2025!

# Automatisch generierte Tokens
MOODLE_ADMIN_TOKEN=<random-hex>
MOODLE_WS_TOKEN=<random-hex>
```

## 🎯 Verfügbare Services

### **Moodle Web Interface**
- **URL**: http://localhost:8080
- **Admin**: admin / Fresh2025Admin!
- **Features**: Vollständiges Moodle mit installiertem Plugin

### **pgAdmin Database Interface**
- **URL**: http://localhost:8082  
- **Login**: admin@example.com / Fresh2025Admin!
- **Database**: moodle_fresh

### **Web Service Functions**
**Core Functions** (9 verfügbar):
- `core_webservice_get_site_info`
- `core_course_create_courses`
- `core_course_get_courses`
- `core_course_get_categories`
- etc.

**MoodleClaude Plugin Functions** (5 verfügbar):
- `local_moodleclaude_create_course_structure`
- `local_moodleclaude_create_page_activity`
- `local_moodleclaude_create_label_activity`
- `local_moodleclaude_create_file_resource`
- `local_moodleclaude_update_section_content`

## 🧪 Testing

### **Web Service Test**
```bash
# Test mit generiertem Token (aus config file)
curl "http://localhost:8080/webservice/rest/server.php?wstoken=YOUR_TOKEN&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
```

### **Plugin Function Test**
```bash
# Test MoodleClaude Plugin Function
curl "http://localhost:8080/webservice/rest/server.php?wstoken=YOUR_TOKEN&wsfunction=local_moodleclaude_create_course_structure&moodlewsrestformat=json&courseid=1"
```

## 🔧 Management Commands

### **Standard Docker Commands**
```bash
# Status anzeigen
docker-compose ps

# Logs anzeigen  
docker-compose logs -f

# Services neu starten
docker-compose restart

# Komplett neu starten (fresh!)
./setup_fresh_moodleclaude_complete.sh
```

### **Container-spezifische Commands**
```bash
# Moodle CLI Zugriff
docker exec -it moodleclaude_app_fresh bash

# PostgreSQL Zugriff
docker exec -it moodleclaude_postgres_fresh psql -U moodle -d moodle_fresh

# Plugin-Verzeichnis prüfen
docker exec moodleclaude_app_fresh ls -la /opt/bitnami/moodle/local/
```

## 🔄 Integration mit MoodleClaude v3.0

### **MCP Server starten**
```bash
# Mit generierten Tokens
python mcp_server_launcher.py
```

### **Claude Desktop konfigurieren**
Verwende die Tokens aus `config/moodle_fresh_complete.env` in deiner Claude Desktop Konfiguration.

### **Architektur-Komponenten testen**
- ✅ Dependency Injection Container
- ✅ Observer Pattern für Events
- ✅ Command Pattern mit Undo/Redo
- ✅ Repository Pattern für Daten
- ✅ Service Layer für Business Logic

## 🏗️ Architektur-Übersicht

```
🐳 MoodleClaude v3.0 Fresh Complete Setup
├── PostgreSQL 16 (moodleclaude_postgres_fresh)
│   ├── Database: moodle_fresh
│   ├── User: moodle / MoodleFresh2025!
│   └── Fresh data (no volumes)
├── Moodle 4.3 (moodleclaude_app_fresh)
│   ├── Port: 8080, 8443
│   ├── Plugin: local_moodleclaude ✅
│   ├── Web Services: Fully configured ✅
│   └── Fresh installation (no volumes)
└── pgAdmin 4 (moodleclaude_pgadmin_fresh)
    ├── Port: 8082
    └── Database management interface
```

## 🎯 Warum "Fresh Complete"?

### **Immer sauber**
- Keine persistenten Volumes = Immer frische Installation
- Keine alten Kurse, User oder Konfigurationen
- Perfekt für Testing und Development

### **Vollautomatisch**
- Keine manuellen Schritte in Moodle UI
- Alle Konfigurationen via CLI/SQL
- Reproduzierbare Setups

### **Production-Ready**
- Sichere Token-Generierung
- Umfassende Permissions
- Alle Web Service Functions verfügbar

## 🚀 Ready für MoodleClaude v3.0!

Nach dem Setup hast du:
- ✅ **Fresh Moodle** ohne alte Daten
- ✅ **Plugin installiert** mit allen Functions
- ✅ **Web Services konfiguriert** und getestet
- ✅ **Tokens generiert** für MCP Integration
- ✅ **v3.0 Architecture** bereit zum Testen

**Ein Befehl. Alles fertig. Keine manuellen Schritte. 🎉**