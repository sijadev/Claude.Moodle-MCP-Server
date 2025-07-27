# Demo Scripts

Dieser Ordner enthält verschiedene Demo- und Test-Scripts für das MoodleClaude-Projekt.

## Dateien

### `demo_content_transfer.py`
- **Zweck**: Grundlegende Demo des Content-Parsers
- **Funktion**: Zeigt wie Chat-Inhalte geparst und strukturiert werden
- **Verwendung**: `python demo_content_transfer.py`

### `enhanced_demo.py`
- **Zweck**: Erweiterte Demo mit manueller Content-Erstellung
- **Funktion**: Simuliert komplette Moodle-Transfer-Funktionalität
- **Verwendung**: `python enhanced_demo.py`

### `test_connection.py`
- **Zweck**: Test der Moodle-Verbindung und erweiterte Kurs-Erstellung
- **Funktion**: Testet API-Verbindung und erstellt Kurs mit Sektionen
- **Verwendung**: `python test_connection.py`
- **Hinweis**: Benötigt Moodle-Umgebungsvariablen

### `simple_transfer.py`
- **Zweck**: Vereinfachter Moodle-Transfer
- **Funktion**: Erstellt Kurs mit eingebettetem Content (funktioniert!)
- **Verwendung**: `python simple_transfer.py`
- **Status**: ✅ Erfolgreich getestet

## Umgebungsvariablen

Für die Live-Transfer-Scripts benötigst du:

```bash
export MOODLE_URL=http://localhost
export MOODLE_TOKEN=b2021a7a41309b8c58ad026a751d0cd0
export MOODLE_USERNAME=simon
```

## Ergebnisse

- `simple_transfer.py` hat erfolgreich einen Kurs erstellt (ID: 9)
- URL: http://localhost/course/view.php?id=9