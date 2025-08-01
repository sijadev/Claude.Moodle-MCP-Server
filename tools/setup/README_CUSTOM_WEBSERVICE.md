# MoodleClaude Custom Web Service Setup

🚀 **Lösung für alle "external_functions" Datenbankfehler!**

## Problem

Die Standard-Moodle Mobile App Web-Services enthalten nicht alle Funktionen, die MoodleClaude benötigt. Dies führt zu Fehlern wie:

```
❌ Can't find data record in database table external_functions
```

## Lösung: Eigener MoodleClaude Web-Service

Anstatt den unvollständigen Mobile-Service zu verwenden, erstellen wir einen **dedizierten MoodleClaude Web-Service** mit allen benötigten Funktionen.

## 🎯 Vorteile

✅ **Alle Funktionen verfügbar** - Keine external_functions Fehler mehr  
✅ **Einfache Konfiguration** - Automatische Setup-Skripte  
✅ **Bessere Sicherheit** - Dedizierter Service-User mit minimalen Rechten  
✅ **Einfache Wartung** - Nur benötigte Funktionen, keine unnötigen Mobile-Features  
✅ **Vollständige Kompatibilität** - Funktioniert mit allen Moodle 4.x Versionen  

## 🚀 Automatische Installation

### Methode 1: Ein-Klick-Setup (Empfohlen)

```bash
./tools/setup/create_custom_webservice.sh
```

Dieses Skript:
- Prüft Voraussetzungen
- Erstellt den MoodleClaude Web-Service
- Fügt alle benötigten Funktionen hinzu
- Erstellt Service-User mit korrekten Berechtigungen
- Generiert sicheres Token
- Aktualisiert .env Datei
- Testet die Konfiguration

### Methode 2: Python-Setup

```bash
python3 tools/setup/setup_custom_webservice.py
```

### Methode 3: Direkte PHP-Ausführung

```bash
php tools/setup/create_moodleclaude_webservice.php
```

## 📋 Manuelle Installation

Falls die automatischen Skripte nicht funktionieren:

1. **Kopiere PHP-Skript** auf deinen Moodle-Server:
   ```bash
   scp tools/setup/create_moodleclaude_webservice.php user@moodle-server:/tmp/
   ```

2. **Führe auf dem Moodle-Server aus**:
   ```bash
   cd /path/to/moodle
   php /tmp/create_moodleclaude_webservice.php
   ```

3. **Kopiere das Token** aus der Ausgabe in deine `.env` Datei:
   ```env
   MOODLE_TOKEN_ENHANCED="dein_neues_token_hier"
   ```

## 🔧 Enthaltene Funktionen

Der Custom Web-Service enthält alle für MoodleClaude benötigten Funktionen:

### Core-Funktionen
- `core_webservice_get_site_info` - Site-Informationen
- `core_course_get_courses` - Kurse abrufen  
- `core_course_create_courses` - Kurse erstellen
- `core_course_get_contents` - Kursinhalte
- `core_course_update_courses` - Kurse aktualisieren

### Modul-Management
- `core_course_create_modules` - **Aktivitäten/Module erstellen** ⭐
- `core_course_delete_modules` - Module löschen
- `core_course_get_course_modules` - Module abrufen

### Sektion-Management
- `core_course_edit_section` - Sektionen bearbeiten
- `local_wsmanagesections_create_sections` - Sektionen erstellen (Plugin)
- `local_wsmanagesections_update_sections` - Sektionen aktualisieren (Plugin)

### Benutzer-Management
- `core_user_get_users` - Benutzer abrufen
- `core_user_create_users` - Benutzer erstellen
- `core_enrol_get_enrolled_users` - Eingeschriebene Benutzer

### Datei-Management
- `core_files_upload` - Dateien hochladen
- `core_files_get_files` - Dateien abrufen

### Spezielle Module (falls verfügbar)
- `mod_assign_get_assignments` - Assignments
- `mod_forum_get_forums_by_courses` - Foren
- `core_grades_get_grades` - Bewertungen

## 🔐 Sicherheit

Der Custom Web-Service verwendet:

✅ **Dedicated Service User**: `moodleclaude_service`  
✅ **Minimale Berechtigungen**: Nur erforderliche Capabilities  
✅ **Manager-Rolle**: Auf System-Ebene für erforderliche Funktionen  
✅ **Sicheres Token**: Automatisch generiert mit externem Token-System  
✅ **Audit-Log**: Alle Aktionen werden in Moodle geloggt  

## 🧪 Testing

Nach der Installation kannst du testen:

### 1. Diagnose-Tool im MCP Server
```
diagnose_webservices
```

### 2. Direkte API-Tests
```bash
curl -X POST "http://your-moodle/webservice/rest/server.php" \
  -d "wstoken=YOUR_TOKEN" \
  -d "wsfunction=core_webservice_get_site_info" \
  -d "moodlewsrestformat=json"
```

### 3. MoodleClaude Funktionen
Teste alle Funktionen in Claude Desktop:
- ✅ `create_course` - Kurs erstellen
- ✅ `create_course_section` - Sektion erstellen  
- ✅ `add_course_module` - Modul hinzufügen
- ✅ `create_assignment` - Assignment erstellen
- ✅ `create_forum` - Forum erstellen

## 📁 Generierte Dateien

Nach erfolgreicher Installation:

- `tools/setup/moodleclaude_webservice_config.json` - Konfiguration
- `.env` - Aktualisiert mit neuem Token
- Moodle-Datenbank - Neuer Service und Benutzer

## 🔄 Migration vom Mobile Service

Falls du bereits den Mobile Service verwendest:

1. **Backup** deiner aktuellen Konfiguration
2. **Führe Setup aus**: `./tools/setup/create_custom_webservice.sh`  
3. **Teste alle Funktionen** mit `diagnose_webservices`
4. **Entferne alte Token** aus der Umgebung (optional)

## 🆘 Troubleshooting

### "Permission denied" Fehler
```bash
chmod +x tools/setup/create_custom_webservice.sh
```

### "PHP not found" 
Installiere PHP oder verwende Docker:
```bash
docker exec your-moodle-container php /tmp/create_moodleclaude_webservice.php
```

### "Database connection failed"
Stelle sicher, dass du Admin-Rechte hast und die Moodle-Datenbank erreichbar ist.

### Token funktioniert nicht
1. Prüfe `MOODLE_URL` in der .env Datei
2. Teste mit `curl` (siehe oben)
3. Überprüfe Moodle-Logs: `Site Administration → Reports → Logs`

## 🎉 Erfolg!

Nach erfolgreicher Installation:

✅ **Alle MoodleClaude-Funktionen arbeiten ohne Fallbacks**  
✅ **Keine "external_functions" Fehler mehr**  
✅ **Vollständige API-Funktionalität verfügbar**  
✅ **Bessere Performance und Zuverlässigkeit**  

**Teste jetzt alle Funktionen in Claude Desktop - sie sollten alle einwandfrei funktionieren!** 🚀