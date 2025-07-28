# 🔧 Moodle Web Services Konfiguration für MoodleClaude

Diese Anleitung erklärt, wie du dein Moodle so konfigurierst, dass echte Sektionen und Aktivitäten erstellt werden können.

## 📋 Übersicht

Aktuell funktioniert nur:
- ✅ Kurse erstellen (`core_course_create_courses`)
- ✅ Kurse auflisten (`core_course_get_courses`)

Für echte Sektionen brauchen wir:
- ❌ `core_course_create_sections`
- ❌ `core_course_create_activities`
- ❌ `mod_page_create_page`

## 🚀 Schritt-für-Schritt Anleitung

### 1. Web Services aktivieren

1. **Moodle Admin-Panel öffnen**
   - Als Administrator anmelden
   - Gehe zu: **Site Administration**

2. **Web Services einschalten**
   ```
   Site Administration → Advanced features
   → ✅ Enable web services (ankreuzen)
   → Save changes
   ```

### 2. Web Service Protokoll aktivieren

```
Site Administration → Server → Web services → Manage protocols
→ REST protocol: ✅ Enable (ankreuzen)
```

### 3. External Service erstellen/bearbeiten

1. **External Services verwalten**
   ```
   Site Administration → Server → Web services → External services
   ```

2. **Neuen Service erstellen** (falls noch nicht vorhanden)
   - Click **Add**
   - Name: `MoodleClaude API`
   - Short name: `moodleclaude`
   - ✅ Enabled
   - ✅ Authorised users only
   - Click **Add service**

3. **Functions hinzufügen**
   - Bei deinem Service auf **Functions** klicken
   - **Add functions** klicken
   - Folgende Funktionen einzeln hinzufügen:

   **Basis-Funktionen (bereits verfügbar):**
   - `core_course_create_courses`
   - `core_course_get_courses`
   - `core_course_get_categories`
   - `core_webservice_get_site_info`

   **Erweiterte Funktionen (für Sektionen):**
   - `core_course_create_sections` ⭐
   - `core_course_edit_section`
   - `core_course_get_contents`
   - `core_course_create_activities` ⭐
   - `mod_page_create_page` ⭐
   - `mod_label_add_label`
   - `core_files_upload`

### 4. Token erstellen/prüfen

1. **Tokens verwalten**
   ```
   Site Administration → Server → Web services → Manage tokens
   ```

2. **Neuen Token erstellen** (falls nötig)
   - User: `simon` (dein Admin-User)
   - Service: `MoodleClaude API`
   - Click **Create token**
   
3. **Token kopieren**
   - Der Token sollte so aussehen: `b2021a7a41309b8c58ad026a751d0cd0`

### 5. User-Berechtigungen setzen

1. **User-Rolle überprüfen**
   ```
   Site Administration → Users → Permissions → Define roles
   ```

2. **Manager/Admin Rolle bearbeiten**
   - Suche nach deiner Rolle (meist `Manager` oder `Administrator`)
   - **Edit** klicken
   - Folgende Capabilities auf **Allow** setzen:

   **Kurs-Management:**
   - `moodle/course:create`
   - `moodle/course:manageactivities` ⭐
   - `moodle/course:activityvisibility` ⭐
   - `moodle/course:sectionvisibility` ⭐
   - `moodle/course:changefullname`
   - `moodle/course:changeshortname`

   **Web Services:**
   - `webservice/rest:use`
   - `moodle/webservice:createtoken`

   **Content-Erstellung:**
   - `mod/page:addinstance` ⭐
   - `mod/label:addinstance`
   - `moodle/site:uploadusers`

### 6. Authorised Users hinzufügen

1. **Service Authorisation**
   ```
   Site Administration → Server → Web services → External services
   → Bei deinem Service: "Authorised users"
   ```

2. **User hinzufügen**
   - **Add users** klicken  
   - `simon` auswählen
   - **Add** klicken

## 🧪 Konfiguration testen

Nach der Konfiguration teste mit unserem Script:

```bash
cd /Users/simonjanke/Projects/MoodleClaude
MOODLE_URL=http://localhost MOODLE_TOKEN=dein_token python demos/check_webservices.py
```

**Erwartetes Ergebnis nach Konfiguration:**
```
core_course_create_sections         ✅ Available
core_course_create_activities       ✅ Available  
mod_page_create_page                ✅ Available
```

## 🎯 Finale Demo

Wenn alles konfiguriert ist, führe die erweiterte Demo aus:

```bash
MOODLE_URL=http://localhost MOODLE_TOKEN=dein_token python demos/advanced_transfer.py
```

**Dann solltest du sehen:**
- ✅ Echte Sektionen (nicht nur ID: 0)
- ✅ Separate Aktivitäten pro Sektion
- ✅ Strukturierten Kursaufbau

## ⚠️ Troubleshooting

### Problem: "Can't find data record in database table external_functions"
**Lösung:** Function nicht zum Web Service hinzugefügt
- Gehe zu External services → Functions → Add functions

### Problem: "Access control exception"  
**Lösung:** User hat nicht die nötigen Berechtigungen
- Capabilities in der User-Rolle setzen
- User zu "Authorised users" hinzufügen

### Problem: Token funktioniert nicht
**Lösung:** Token neu generieren
- Manage tokens → Delete old token → Create new token

## 📚 Zusätzliche Ressourcen

- [Moodle Web Services Dokumentation](https://docs.moodle.org/dev/Web_services)
- [External Functions API](https://docs.moodle.org/dev/External_functions_API)
- [REST Protocol](https://docs.moodle.org/dev/Creating_a_web_service_client#REST)

## 🎉 Nach erfolgreicher Konfiguration

Deine MoodleClaude-Demos werden dann:
- ✅ Echte Sektionen erstellen
- ✅ Individuelle Page-Aktivitäten hinzufügen
- ✅ Strukturierte Kurse mit Navigation aufbauen
- ✅ Downloads und interaktive Inhalte ermöglichen

Viel Erfolg! 🚀