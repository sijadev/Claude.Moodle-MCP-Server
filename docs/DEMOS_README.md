# Demo Scripts

Dieser Ordner enthält verschiedene Demo- und Test-Scripts für das MoodleClaude-Projekt.

## Demos Overview

### 🎓 **Course Creation with Sections** (NEW!)

#### `course_with_sections_demo.py` ⭐
- **Zweck**: Comprehensive course creation with advanced section management
- **Features**:
  - Structured course creation with multiple sections
  - Section visibility and availability conditions
  - Rich content integration (files, URLs, activities)
  - Section management operations (update, move, bulk operations)
- **Verwendung**: `python course_with_sections_demo.py`
- **Level**: Advanced - demonstrates full MoodleClaude capabilities

#### `advanced_transfer.py` ✨ (Enhanced)
- **Zweck**: Advanced section management with both traditional and enhanced approaches
- **Features**:
  - Traditional section creation methods
  - Enhanced API with SectionConfig
  - Comparison between approaches
  - Interactive demo selection
- **Verwendung**: `python advanced_transfer.py`
- **Level**: Intermediate to Advanced

#### `comprehensive_course_structure.py` 🌟 (NEW!)
- **Zweck**: Complete learning path with multiple interconnected courses
- **Features**:
  - Multi-course learning paths
  - Course dependencies and progression
  - Rich content types (files, code examples, projects)
  - Overview course generation
- **Verwendung**: `python comprehensive_course_structure.py`
- **Level**: Expert - full ecosystem creation

### 📚 **Basic Demos**

#### `demo_content_transfer.py`
- **Zweck**: Grundlegende Demo des Content-Parsers
- **Funktion**: Zeigt wie Chat-Inhalte geparst und strukturiert werden
- **Verwendung**: `python demo_content_transfer.py`

#### `enhanced_demo.py`
- **Zweck**: Erweiterte Demo mit manueller Content-Erstellung
- **Funktion**: Simuliert komplette Moodle-Transfer-Funktionalität
- **Verwendung**: `python enhanced_demo.py`

#### `test_connection.py`
- **Zweck**: Test der Moodle-Verbindung und erweiterte Kurs-Erstellung
- **Funktion**: Testet API-Verbindung und erstellt Kurs mit Sektionen
- **Verwendung**: `python test_connection.py`
- **Hinweis**: Benötigt Moodle-Umgebungsvariablen

#### `simple_transfer.py`
- **Zweck**: Vereinfachter Moodle-Transfer
- **Funktion**: Erstellt Kurs mit eingebettetem Content (funktioniert!)
- **Verwendung**: `python simple_transfer.py`
- **Status**: ✅ Erfolgreich getestet

### 🔧 **Utility Demos**

#### `check_webservices.py`
- **Zweck**: Comprehensive webservice testing and validation
- **Verwendung**: `python check_webservices.py`

#### `verify_setup.py`
- **Zweck**: Complete Moodle setup verification
- **Verwendung**: `python verify_setup.py`

## Umgebungsvariablen

Für die Live-Transfer-Scripts benötigst du:

```bash
export MOODLE_URL=http://localhost:8080
export MOODLE_TOKEN=b2021a7a41309b8c58ad026a751d0cd0
export MOODLE_USERNAME=simon
```

## 🚀 Quick Start Examples

### Einfache Kurserstellung
```bash
# Basic course with sections
python simple_transfer.py
```

### Erweiterte Sektion-Management
```bash
# Enhanced API features  
python advanced_transfer.py
# Choose option 2 for Enhanced API approach
```

### Vollständige Lernpfad-Erstellung
```bash
# Complete learning ecosystem
python course_with_sections_demo.py
```

### Comprehensive Multi-Course Setup
```bash
# Professional course structure
python comprehensive_course_structure.py
```

## 📊 Demo Comparison

| Demo | Complexity | Sections | Content | Best For |
|------|------------|----------|---------|----------|
| `simple_transfer.py` | Basic | ✅ Basic | 📄 Simple | Testing setup |
| `advanced_transfer.py` | Medium | ✅✅ Enhanced | 📄📊 Mixed | Learning API |
| `course_with_sections_demo.py` | Advanced | ✅✅✅ Full | 📄📊🎯 Rich | Production |
| `comprehensive_course_structure.py` | Expert | ✅✅✅✅ Multi | 📄📊🎯🚀 Complete | Enterprise |

## 🎯 Use Cases

### **For Beginners**
1. Start with `simple_transfer.py` to test your setup
2. Try `test_connection.py` to verify connectivity
3. Move to `advanced_transfer.py` for more features

### **For Developers**
1. Study `course_with_sections_demo.py` for best practices
2. Use `enhanced_demo.py` for manual content creation
3. Explore `comprehensive_course_structure.py` for advanced patterns

### **For Production**
1. Use `course_with_sections_demo.py` as template
2. Adapt `comprehensive_course_structure.py` for multi-course setups
3. Leverage section management features for complex curricula

## 📈 Features by Demo

### Section Management
- ✅ Basic: `simple_transfer.py`, `advanced_transfer.py`
- ⭐ Enhanced: `course_with_sections_demo.py`
- 🌟 Advanced: `comprehensive_course_structure.py`

### Content Types
- 📄 Text: All demos
- 🔗 URLs: `course_with_sections_demo.py`, `comprehensive_course_structure.py`
- 📁 Files: `course_with_sections_demo.py`, `comprehensive_course_structure.py`
- 🎯 Activities: `comprehensive_course_structure.py`

### Advanced Features
- 🔒 Availability Conditions: `course_with_sections_demo.py`, `comprehensive_course_structure.py`
- 📊 Bulk Operations: `course_with_sections_demo.py`
- 🏗️ Multi-Course: `comprehensive_course_structure.py`
- 📋 Learning Paths: `comprehensive_course_structure.py`

## Ergebnisse

- `simple_transfer.py` hat erfolgreich einen Kurs erstellt (ID: 9)
- URL: http://localhost/course/view.php?id=9
- ✅ Alle neuen Section-Demos wurden erfolgreich erstellt und getestet!
