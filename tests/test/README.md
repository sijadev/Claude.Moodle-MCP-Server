# MoodleClaude Docker Test Suite

Umfassende Test-Suite, die eine isolierte Docker-Umgebung erstellt, alle System-Tests ausführt und anschließend wieder sauber aufräumt.

## 🎯 Übersicht

Das Docker Test Suite System bietet:

- 🐳 **Isolierte Test-Umgebung** - Keine Konflikte mit lokalen Installationen
- 🧪 **Comprehensive Tests** - Vollständige Validierung aller Systemkomponenten  
- 📊 **Detailliertes Reporting** - HTML/JSON Reports mit allen Testergebnissen
- 🧹 **Automatisches Cleanup** - Saubere Aufräumung nach den Tests
- ⚡ **CI/CD Ready** - Bereit für Automatisierung in Build-Pipelines

## 🚀 Quick Start

### Einfacher Test-Lauf
```bash
# Vollständige Test-Suite ausführen
python tools/run_docker_test_suite.py

# Mit verbose Output
python tools/run_docker_test_suite.py --verbose

# Test-Umgebung für Debugging beibehalten
python tools/run_docker_test_suite.py --keep-environment
```

### Nur Cleanup
```bash
# Bestehende Test-Umgebung aufräumen
python tools/run_docker_test_suite.py --cleanup-only
```

## 🏗️ Test-Architektur

### Docker Services

1. **postgres_test** - PostgreSQL Datenbank (Port 5433)
2. **moodle_test** - Moodle Application (Port 8081)  
3. **pgadmin_test** - PgAdmin Interface (Port 8083, nur mit --profile debug)
4. **test_runner** - Test Execution Container

### Test-Phasen

1. **Environment Validation** - Python, Module, File-Struktur
2. **Moodle Connectivity** - Basis-Konnektivität und Admin-Login
3. **Plugin Installation** - MoodleClaude Plugin Validation
4. **Webservice Setup** - API-Endpoints und Konfiguration
5. **Token Generation** - API Token Erstellung und Validierung
6. **MCP Server Tests** - Performance-optimierte Server Tests
7. **Performance Tests** - Benchmarks und Leistungsmessungen
8. **Integration Tests** - End-to-End Szenarien
9. **Cleanup Validation** - Aufräumung und Ressourcen-Management

## 📊 Test Reports

### Generierte Reports

- **`test-results/test_report.json`** - Maschinell lesbare Testergebnisse
- **`test-results/test_report.html`** - Benutzerfreundlicher HTML-Report
- **`test-results/docker_test_runner_report.json`** - Docker Runner Metriken
- **`logs/test_suite.log`** - Detaillierte Logs

### Report-Struktur

```json
{
  "start_time": "2025-08-01T12:00:00",
  "end_time": "2025-08-01T12:15:00", 
  "tests": {
    "test_name": {
      "success": true,
      "message": "Test passed",
      "timestamp": "2025-08-01T12:05:00",
      "details": {}
    }
  },
  "summary": {
    "total_tests": 25,
    "passed_tests": 23,
    "failed_tests": 2,
    "success_rate": 92.0
  }
}
```

## 🔧 Konfiguration

### Environment Variables

Test-Container verwenden diese Umgebungsvariablen:

```bash
# Moodle Configuration
MOODLE_URL=http://moodle_test:8080
MOODLE_ADMIN_USER=admin
MOODLE_ADMIN_PASSWORD=MoodleClaude2025!
MOODLE_WS_USER=wsuser  
MOODLE_WS_PASSWORD=MoodleClaudeWS2025!

# Database Configuration
DATABASE_URL=postgresql://moodleuser:MoodleTestPass2025!@postgres_test:5432/moodletest

# Test Configuration
TEST_ENV=docker
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

### Docker Ports

- **8081** - Moodle Test Instance
- **5433** - PostgreSQL Test Database
- **8083** - PgAdmin (nur mit debug profile)

## 🧪 Test-Kategorien

### 1. Unit Tests
- Python Module Imports
- Konfigurationsdateien
- Basis-Funktionalität

### 2. Integration Tests  
- Moodle API Connectivity
- Plugin Installation
- Token Generation
- MCP Server Communication

### 3. Performance Tests
- Response Time Benchmarks
- Memory Usage Validation
- Throughput Measurements
- Cache Efficiency

### 4. End-to-End Tests
- Complete Course Creation Workflow
- Error Handling Scenarios
- Context-Aware Processing
- Multi-User Scenarios

## 🐳 Docker Compose Konfiguration

### Test Services

```yaml
# Aus docker-compose.test.yml
services:
  postgres_test:
    image: postgres:13
    environment:
      POSTGRES_DB: moodletest
      POSTGRES_USER: moodleuser
      POSTGRES_PASSWORD: MoodleTestPass2025!
    ports:
      - "5433:5432"

  moodle_test:
    image: bitnami/moodle:4.1
    environment:
      MOODLE_USERNAME: admin
      MOODLE_PASSWORD: MoodleClaude2025!
      MOODLE_DATABASE_TYPE: pgsql
      MOODLE_DATABASE_HOST: postgres_test
    ports:
      - "8081:8080"

  test_runner:
    build:
      context: ../../
      dockerfile: operations/docker/Dockerfile.test
    volumes:
      - test_results:/app/test-results
      - test_logs:/app/logs
```

## 📋 Erweiterte Verwendung

### Debugging Tests

```bash
# Umgebung nach Tests beibehalten
python tools/run_docker_test_suite.py --keep-environment

# In die Test-Umgebung einloggen
docker exec -it moodle_app_test bash

# Logs anzeigen
docker-compose -f operations/docker/docker-compose.test.yml logs moodle_test
```

### Debug mit PgAdmin

```bash
# Mit PgAdmin für Datenbank-Debugging
docker-compose -f operations/docker/docker-compose.test.yml --profile debug up -d

# PgAdmin: http://localhost:8083
# Login: admin@moodleclaude.test / MoodleClaude2025!
```

### Einzelne Test-Phasen

```bash
# Nur bestimmte Tests ausführen (durch Modifikation des Test-Scripts)
# Im test_runner Container:
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v  
python -m pytest tests/performance/ -v
```

## 🔍 Troubleshooting

### Häufige Probleme

1. **Docker nicht verfügbar**
   ```bash
   # Docker Status prüfen
   docker info
   
   # Docker Daemon starten
   sudo systemctl start docker  # Linux
   # oder Docker Desktop starten (Mac/Windows)
   ```

2. **Port-Konflikte**
   ```bash
   # Verwendete Ports prüfen
   netstat -tulpn | grep -E ':(5433|8081|8083)'
   
   # Ports in docker-compose.test.yml anpassen
   ```

3. **Speicher-Probleme**
   ```bash
   # Docker System bereinigen
   docker system prune -a
   
   # Nicht verwendete Volumes entfernen
   docker volume prune
   ```

4. **Tests schlagen fehl**
   ```bash
   # Detaillierte Logs anzeigen
   python tools/run_docker_test_suite.py --verbose
   
   # Test-Umgebung für Debugging beibehalten
   python tools/run_docker_test_suite.py --keep-environment
   
   # Manuell in Container einloggen
   docker exec -it moodleclaude_test_runner bash
   ```

### Log-Analyse

```bash
# Test Suite Logs
tail -f logs/test_suite.log

# Docker Compose Logs
docker-compose -f operations/docker/docker-compose.test.yml logs -f

# Spezifische Service Logs
docker logs moodle_app_test
docker logs moodle_postgres_test
```

## 🚦 CI/CD Integration

### GitHub Actions Beispiel

```yaml
name: MoodleClaude Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker
      uses: docker/setup-buildx-action@v2
      
    - name: Run Test Suite
      run: |
        python tools/run_docker_test_suite.py
        
    - name: Upload Test Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: test-results/
```

### Jenkins Pipeline Beispiel

```groovy
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'python tools/run_docker_test_suite.py'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'test-results/*', fingerprint: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'test-results',
                reportFiles: 'test_report.html',
                reportName: 'MoodleClaude Test Report'
            ])
        }
    }
}
```

## 📈 Performance Metriken

### Typische Test-Laufzeiten

- **Environment Setup**: 2-3 Minuten
- **Moodle Startup**: 1-2 Minuten  
- **Test Execution**: 3-5 Minuten
- **Cleanup**: 30 Sekunden
- **Total**: 7-11 Minuten

### Erfolgs-Kriterien

- **Gesamt-Erfolgsrate**: ≥ 80%
- **Kritische Tests**: 100% (Connectivity, MCP Server, Plugin)
- **Performance Tests**: Response Time < 2s
- **Memory Usage**: < 512MB für Test Runner

## 🤝 Beitragen

### Neue Tests hinzufügen

1. Test-Methode in `run_comprehensive_tests.py` erstellen
2. Test zur entsprechenden Phase hinzufügen
3. Documentation in diesem README aktualisieren

### Test-Umgebung erweitern

1. Services in `docker-compose.test.yml` hinzufügen
2. Dependencies in `requirements.txt` aktualisieren
3. Dockerfile.test entsprechend anpassen

---

**🎯 Ziel**: Vollständige Qualitätssicherung für MoodleClaude durch isolierte, reproduzierbare Tests in Docker-Umgebung.