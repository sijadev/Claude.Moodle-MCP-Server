# MoodleClaude v3.0 - Optimized Setup

🚀 **Streamlined 2-Container Architecture für beste Performance**

## 🎯 Optimierte Architektur

```
┌─────────────────────┐    ┌──────────────────────┐
│   PostgreSQL 16     │◄───┤    Moodle 4.3        │
│   (Internal DB)     │    │  (Web Interface)     │
│   Port: 5432        │    │  Port: 8080/8443     │
└─────────────────────┘    └──────────────────────┘
         db                        moodle
```

### ✅ **Vorteile dieser Lösung:**
- **🚀 Schnell**: ~90 Sekunden Startzeit
- **💾 Effizient**: Nur 2 Container statt 6
- **🔧 Einfach**: Weniger Komplexität
- **💪 Robust**: PostgreSQL für Production
- **📏 Skalierbar**: Services getrennt

## 🚀 Quick Start

### 1. **Environment starten**
```bash
./start_moodleclaude_v3.sh
```

### 2. **Web Services konfigurieren**
```bash
./setup_webservices_v3_optimized.sh
```

### 3. **Zugriff**
- **Moodle**: http://localhost:8080
- **Admin**: admin / MoodleClaude2025Admin!

## 📋 Systemanforderungen

- **Docker** & **Docker Compose**
- **4GB RAM** (minimum)
- **10GB Speicher** für Volumes

## 🔧 Container Details

### **PostgreSQL Container** (`moodleclaude_db_opt`)
- **Image**: postgres:16-alpine
- **Database**: moodle
- **User**: moodle / moodle123
- **Internal Port**: 5432 (nicht extern erreichbar)
- **Volume**: `moodleclaude_db_opt`

### **Moodle Container** (`moodleclaude_app_opt`)
- **Image**: bitnami/moodle:4.3
- **PHP Memory**: 384M
- **Upload Limit**: 64M
- **Execution Time**: 240s
- **Ports**: 8080 (HTTP), 8443 (HTTPS)
- **Volumes**: `moodleclaude_app_opt`, `moodleclaude_config_opt`

## 🔌 MCP Integration

### **Generated Tokens**
Tokens werden automatisch generiert und in `config/moodle_tokens_v3_optimized.env` gespeichert:

```env
MOODLE_URL=http://localhost:8080
MOODLE_BASIC_TOKEN=<generated>
MOODLE_PLUGIN_TOKEN=<generated>
MOODLE_ADMIN_USER=admin
MOODLE_ADMIN_PASSWORD=MoodleClaude2025Admin!
```

### **Web Service Functions**
- `core_webservice_get_site_info`
- `core_course_create_courses`
- `core_course_get_courses`
- `core_course_get_categories`
- `core_course_update_courses`
- `core_course_edit_section`
- `core_files_upload`

## 🛠️ Management Commands

### **Standard Docker Compose**
```bash
# Starten
docker-compose up -d

# Stoppen  
docker-compose down

# Logs anzeigen
docker-compose logs -f

# Services neu starten
docker-compose restart

# Volumes löschen (ACHTUNG: Alle Daten verloren!)
docker-compose down --volumes
```

### **Container-spezifische Commands**
```bash
# Moodle CLI Zugriff
docker exec -it moodleclaude_app_opt bash

# PostgreSQL Zugriff
docker exec -it moodleclaude_db_opt psql -U moodle -d moodle

# Container Stats
docker stats moodleclaude_app_opt moodleclaude_db_opt
```

## 🔍 Troubleshooting

### **Service Health Checks**
```bash
# Container Status
docker-compose ps

# Service Logs  
docker-compose logs moodle
docker-compose logs db

# Health Status
docker inspect moodleclaude_app_opt | grep -A 5 Health
docker inspect moodleclaude_db_opt | grep -A 5 Health
```

### **Common Issues**

#### **Moodle startet nicht**
```bash
# Logs prüfen
docker-compose logs moodle

# Neustart
docker-compose restart moodle
```

#### **Database Connection Error**
```bash
# PostgreSQL Status prüfen
docker exec moodleclaude_db_opt pg_isready -U moodle -d moodle

# Database Logs
docker-compose logs db
```

#### **Port bereits belegt (8080)**
```bash
# Port-Nutzung prüfen
lsof -i :8080

# Anderen Port verwenden (in docker-compose.yml)
ports:
  - "8081:8080"  # Ändere 8080 zu 8081
```

## 🔐 Security Notes

### **Production Deployment**
Für Production folgende Änderungen vornehmen:

1. **Starke Passwörter**:
   ```yaml
   POSTGRES_PASSWORD: <secure-password>
   MOODLE_PASSWORD: <secure-admin-password>
   ```

2. **Network Isolation**:
   ```yaml
   # PostgreSQL nicht extern erreichbar
   ports: []  # Keine externen Ports für DB
   ```

3. **SSL/HTTPS**:
   - Reverse Proxy (nginx)
   - SSL Certificates
   - HTTPS-only Zugriff

## 📊 Performance Tuning

### **PHP Settings** (bereits optimiert)
```yaml
PHP_MEMORY_LIMIT: 384M
PHP_POST_MAX_SIZE: 64M
PHP_UPLOAD_MAX_FILESIZE: 64M
PHP_MAX_EXECUTION_TIME: 240
PHP_MAX_INPUT_VARS: 3000
```

### **PostgreSQL Tuning**
```yaml
# Für größere Installationen
environment:
  POSTGRES_INITDB_ARGS: "--encoding=UTF8 --wal-buffers=16MB --shared-buffers=256MB"
```

## 🎯 Integration mit MoodleClaude v3.0

### **Architektur-Komponenten**
- ✅ **Dependency Injection Container**
- ✅ **Observer Pattern**  
- ✅ **Command Pattern**
- ✅ **Repository Pattern**
- ✅ **Service Layer**

### **MCP Server Integration**
```bash
# MCP Server starten (nach Web Services Setup)
python mcp_server_launcher.py
```

### **Claude Desktop Konfiguration**
Die generierten Tokens aus `config/moodle_tokens_v3_optimized.env` in Claude Desktop konfigurieren.

---

## 🎉 **Ready for MoodleClaude v3.0!**

Das optimierte Setup ist jetzt bereit für die Integration mit der refactored MoodleClaude v3.0 Architektur!

**Nächste Schritte:**
1. ✅ Environment läuft
2. ✅ Web Services konfiguriert  
3. 🔄 MCP Server testen
4. 🚀 Claude Desktop integrieren