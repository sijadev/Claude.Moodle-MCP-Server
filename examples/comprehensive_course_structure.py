#!/usr/bin/env python3
"""
Comprehensive Course Structure Demo
Demonstrates advanced course creation with:
- Multi-level section hierarchies
- Rich content types (files, URLs, activities)
- Section dependencies and prerequisites
- Progress tracking and completion
- Bulk content management
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_moodle_claude import (
    EnhancedMoodleAPI,
    FileUploadConfig,
    MoodleClaudeIntegration,
    SectionConfig,
)


class ComprehensiveCourseBuilder:
    """Advanced course builder with complex structures and dependencies"""

    def __init__(self, moodle_url: str, token: str):
        self.integration = MoodleClaudeIntegration(moodle_url, token)
        self.api = self.integration.api
        self.created_courses = []
        self.created_sections = []

    async def create_complete_learning_path(self) -> Dict[str, Any]:
        """Create a complete learning path with multiple interconnected courses"""

        print("🎓 Creating Complete Python Learning Path")
        print("=" * 60)

        # Define the learning path structure
        learning_path = {
            "title": "Complete Python Developer Learning Path",
            "description": "From beginner to professional Python developer",
            "courses": [
                {
                    "name": "Python Fundamentals",
                    "level": "Beginner",
                    "duration": "4 weeks",
                    "sections": self._get_fundamentals_sections(),
                },
                {
                    "name": "Intermediate Python",
                    "level": "Intermediate",
                    "duration": "6 weeks",
                    "sections": self._get_intermediate_sections(),
                },
                {
                    "name": "Advanced Python & Projects",
                    "level": "Advanced",
                    "duration": "8 weeks",
                    "sections": self._get_advanced_sections(),
                },
            ],
        }

        created_courses = []

        # Create each course in the learning path
        for course_info in learning_path["courses"]:
            print(f"\n🚀 Creating: {course_info['name']} ({course_info['level']})")

            course_result = await self._create_structured_course(
                course_info["name"],
                course_info["level"],
                course_info["duration"],
                course_info["sections"],
            )

            if course_result:
                created_courses.append(course_result)
                print(f"✅ Course created: {course_result['course_id']}")
            else:
                print(f"❌ Failed to create course: {course_info['name']}")

        # Create overview/navigation course
        if created_courses:
            overview_course = await self._create_learning_path_overview(
                learning_path, created_courses
            )
            if overview_course:
                created_courses.insert(0, overview_course)

        return {
            "learning_path": learning_path,
            "created_courses": created_courses,
            "total_courses": len(created_courses),
            "total_sections": sum(
                len(course.get("sections", [])) for course in created_courses
            ),
        }

    def _get_fundamentals_sections(self) -> List[Dict[str, Any]]:
        """Define sections for Python Fundamentals course"""
        return [
            {
                "config": SectionConfig(
                    name="🎯 Course Overview & Setup",
                    summary="""
                    <h4>Welcome to Python Fundamentals!</h4>
                    <p>In this section you'll learn:</p>
                    <ul>
                        <li>Course structure and objectives</li>
                        <li>Python installation and setup</li>
                        <li>Development environment configuration</li>
                        <li>Your first Python program</li>
                    </ul>
                    <p><strong>Estimated time:</strong> 2-3 hours</p>
                    """,
                    visible=True,
                ),
                "content": [
                    {
                        "type": "file",
                        "name": "Python Installation Guide",
                        "filename": "python_setup_guide.md",
                        "content": self._get_setup_guide_content(),
                    },
                    {
                        "type": "url",
                        "name": "Official Python Documentation",
                        "url": "https://docs.python.org/3/",
                        "description": "Official Python 3 documentation and tutorials",
                    },
                ],
            },
            {
                "config": SectionConfig(
                    name="🐍 Python Basics",
                    summary="""
                    <h4>Master the Building Blocks</h4>
                    <p>Core Python concepts:</p>
                    <ul>
                        <li>Variables and data types</li>
                        <li>Operators and expressions</li>
                        <li>Input and output</li>
                        <li>Comments and documentation</li>
                    </ul>
                    <p><span style="color: #28a745;"><strong>Hands-on:</strong> 5 practical exercises</span></p>
                    """,
                    visible=True,
                ),
                "content": [
                    {
                        "type": "file",
                        "name": "Python Basics Cheat Sheet",
                        "filename": "python_basics.py",
                        "content": self._get_basics_code_content(),
                    }
                ],
            },
            {
                "config": SectionConfig(
                    name="🔧 Control Flow",
                    summary="""
                    <h4>Program Logic and Decision Making</h4>
                    <ul>
                        <li>If, elif, else statements</li>
                        <li>For and while loops</li>
                        <li>Break and continue</li>
                        <li>Nested structures</li>
                    </ul>
                    <p><strong>Project:</strong> Build a simple guessing game</p>
                    """,
                    visible=True,
                ),
                "content": [
                    {
                        "type": "file",
                        "name": "Control Flow Examples",
                        "filename": "control_flow_examples.py",
                        "content": self._get_control_flow_content(),
                    }
                ],
            },
            {
                "config": SectionConfig(
                    name="📊 Data Structures",
                    summary="""
                    <h4>Organizing and Managing Data</h4>
                    <ul>
                        <li>Lists and list methods</li>
                        <li>Tuples and when to use them</li>
                        <li>Dictionaries and key-value pairs</li>
                        <li>Sets and set operations</li>
                    </ul>
                    <p><strong>Mini-project:</strong> Student grade calculator</p>
                    """,
                    visible=True,
                ),
                "content": [
                    {
                        "type": "file",
                        "name": "Data Structures Guide",
                        "filename": "data_structures.py",
                        "content": self._get_data_structures_content(),
                    }
                ],
            },
            {
                "config": SectionConfig(
                    name="🎯 Final Project",
                    summary="""
                    <h4>Apply Everything You've Learned</h4>
                    <p>Create a complete Python application that demonstrates:</p>
                    <ul>
                        <li>All basic Python concepts</li>
                        <li>User interaction</li>
                        <li>Data processing</li>
                        <li>Error handling basics</li>
                    </ul>
                    <p><strong>Project:</strong> Personal expense tracker</p>
                    """,
                    visible=False,
                    availability_conditions={
                        "op": "&",
                        "c": [{"type": "completion", "cm": "previous_sections"}],
                        "showc": [True],
                    },
                ),
                "content": [
                    {
                        "type": "file",
                        "name": "Project Requirements",
                        "filename": "final_project_requirements.md",
                        "content": self._get_project_requirements(),
                    }
                ],
            },
        ]

    def _get_intermediate_sections(self) -> List[Dict[str, Any]]:
        """Define sections for Intermediate Python course"""
        return [
            {
                "config": SectionConfig(
                    name="⚙️ Functions & Modules",
                    summary="""
                    <h4>Code Organization and Reusability</h4>
                    <ul>
                        <li>Defining and calling functions</li>
                        <li>Parameters, arguments, and return values</li>
                        <li>Scope and namespaces</li>
                        <li>Creating and importing modules</li>
                        <li>Package management with pip</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content": [],
            },
            {
                "config": SectionConfig(
                    name="🔍 Error Handling & Debugging",
                    summary="""
                    <h4>Robust Code Development</h4>
                    <ul>                                                                                                                                                           
                        <li>Understanding exceptions</li>
                        <li>Try, except, finally blocks</li>
                        <li>Custom exceptions</li>
                        <li>Debugging techniques</li>
                        <li>Testing basics</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content": [],
            },
            {
                "config": SectionConfig(
                    name="📁 File Operations & Data Processing",
                    summary="""
                    <h4>Working with External Data</h4>
                    <ul>
                        <li>Reading and writing files</li>
                        <li>CSV and JSON processing</li>
                        <li>File system operations</li>
                        <li>Data validation and cleaning</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content": [],
            },
            {
                "config": SectionConfig(
                    name="🌐 APIs & Web Scraping",
                    summary="""
                    <h4>Connecting to the Internet</h4>
                    <ul>
                        <li>HTTP requests with requests library</li>
                        <li>API consumption and JSON handling</li>
                        <li>Web scraping with BeautifulSoup</li>
                        <li>Rate limiting and ethical scraping</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content": [],
            },
        ]

    def _get_advanced_sections(self) -> List[Dict[str, Any]]:
        """Define sections for Advanced Python course"""
        return [
            {
                "config": SectionConfig(
                    name="🏗️ Object-Oriented Programming",
                    summary="""
                    <h4>Professional Code Architecture</h4>
                    <ul>
                        <li>Classes and objects</li>
                        <li>Inheritance and polymorphism</li>
                        <li>Encapsulation and abstraction</li>
                        <li>Magic methods and properties</li>
                        <li>Design patterns</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content": [],
            },
            {
                "config": SectionConfig(
                    name="🚀 Advanced Topics",
                    summary="""
                    <h4>Professional Python Development</h4>
                    <ul>
                        <li>Decorators and context managers</li>
                        <li>Generators and iterators</li>
                        <li>Multithreading and multiprocessing</li>
                        <li>Regular expressions</li>
                        <li>Database connectivity</li>
                    </ul>
                    """,
                    visible=True,
                ),
                "content": [],
            },
            {
                "config": SectionConfig(
                    name="🛠️ Real-World Projects",
                    summary="""
                    <h4>Portfolio-Ready Applications</h4>
                    <p>Choose from:</p>
                    <ul>
                        <li>Web application with Flask/Django</li>
                        <li>Data analysis project with Pandas</li>
                        <li>Automation tool for daily tasks</li>
                        <li>API service with documentation</li>
                    </ul>
                    """,
                    visible=False,
                    availability_conditions={
                        "op": "&",
                        "c": [{"type": "completion", "cm": "previous_sections"}],
                        "showc": [True],
                    },
                ),
                "content": [],
            },
        ]

    async def _create_structured_course(
        self, name: str, level: str, duration: str, sections: List[Dict]
    ) -> Dict[str, Any]:
        """Create a single structured course with sections and content"""

        try:
            # Create course
            course_data = {
                "fullname": f"{name} - {level} Level",
                "shortname": f"python_{level.lower()}_{self._get_timestamp()}",
                "category": 1,
                "summary": f"""
                <h3>🎓 {name}</h3>
                <p><strong>Level:</strong> {level}</p>
                <p><strong>Duration:</strong> {duration}</p>
                <p><strong>Sections:</strong> {len(sections)}</p>
                <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h4>What you'll learn:</h4>
                    <p>This course is part of the Complete Python Developer Learning Path.</p>
                </div>
                """,
                "format": "topics",
            }

            course_response = await self.api._make_request(
                "core_course_create_courses", {"courses": [course_data]}
            )
            course_id = course_response[0]["id"]

            # Create sections
            created_sections = []
            for section_data in sections:
                try:
                    section_result = await self.api.create_course_section(
                        course_id, section_data["config"]
                    )
                    section_info = {
                        "id": section_result.get("id"),
                        "name": section_data["config"].name,
                        "content_added": 0,
                    }

                    # Add content to section if defined
                    if "content" in section_data and section_data["content"]:
                        content_count = await self._add_content_to_section(
                            course_id, section_result.get("id"), section_data["content"]
                        )
                        section_info["content_added"] = content_count

                    created_sections.append(section_info)

                except Exception as e:
                    print(f"   ❌ Failed to create section: {e}")

            return {
                "course_id": course_id,
                "course_name": name,
                "level": level,
                "sections": created_sections,
                "course_url": f"{self.api.base_url}/course/view.php?id={course_id}",
            }

        except Exception as e:
            print(f"❌ Failed to create course {name}: {e}")
            return None

    async def _add_content_to_section(
        self, course_id: int, section_id: int, content_list: List[Dict]
    ) -> int:
        """Add various types of content to a section"""

        added_count = 0

        for content_item in content_list:
            try:
                if content_item["type"] == "file":
                    # Create file resource
                    await self.api.create_file_resource(
                        courseid=course_id,
                        sectionnum=section_id,
                        name=content_item["name"],
                        file_content=content_item["content"].encode("utf-8"),
                        filename=content_item["filename"],
                    )
                    added_count += 1

                elif content_item["type"] == "url":
                    # Create URL resource
                    await self._create_url_resource(
                        course_id,
                        section_id,
                        content_item["name"],
                        content_item["url"],
                        content_item.get("description", ""),
                    )
                    added_count += 1

            except Exception as e:
                print(f"      ⚠️ Failed to add content '{content_item['name']}': {e}")

        return added_count

    async def _create_url_resource(
        self, course_id: int, section_num: int, name: str, url: str, description: str
    ):
        """Create a URL resource"""

        module_data = {
            "courseid": course_id,
            "name": name,
            "modname": "url",
            "section": section_num,
            "instance": 0,
            "visible": 1,
            "url": {
                "name": name,
                "intro": description,
                "externalurl": url,
                "display": 0,
            },
        }

        result = await self.api._make_request(
            "core_course_create_modules", {"modules": [module_data]}
        )

        return result[0] if result else None

    async def _create_learning_path_overview(
        self, learning_path: Dict, created_courses: List[Dict]
    ) -> Dict:
        """Create an overview course that links all courses in the learning path"""

        print(f"\n📋 Creating Learning Path Overview Course...")

        try:
            overview_content = f"""
            <h2>🎓 {learning_path['title']}</h2>
            <p>{learning_path['description']}</p>
            
            <h3>📚 Course Progression:</h3>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
            """

            for i, course in enumerate(created_courses, 1):
                overview_content += f"""
                <div style="margin: 15px 0; padding: 15px; background: white; border-left: 4px solid #007bff; border-radius: 4px;">
                    <h4>{i}. {course['course_name']} ({course['level']})</h4>
                    <p><strong>Sections:</strong> {len(course['sections'])}</p>
                    <p><a href="{course['course_url']}" target="_blank">🔗 Go to Course</a></p>
                </div>
                """

            overview_content += "</div>"

            # Create overview course
            course_data = {
                "fullname": f"📋 {learning_path['title']} - Overview",
                "shortname": f"python_overview_{self._get_timestamp()}",
                "category": 1,
                "summary": overview_content,
                "format": "singleactivity",
            }

            course_response = await self.api._make_request(
                "core_course_create_courses", {"courses": [course_data]}
            )
            course_id = course_response[0]["id"]

            return {
                "course_id": course_id,
                "course_name": f"{learning_path['title']} - Overview",
                "level": "Overview",
                "sections": [],
                "course_url": f"{self.api.base_url}/course/view.php?id={course_id}",
            }

        except Exception as e:
            print(f"❌ Failed to create overview course: {e}")
            return None

    def _get_timestamp(self) -> str:
        """Get current timestamp for unique naming"""
        import time

        return str(int(time.time()))

    # Content generation methods
    def _get_setup_guide_content(self) -> str:
        return """# Python Installation and Setup Guide

## 1. Installing Python

### Windows:
1. Visit https://python.org/downloads/
2. Download Python 3.11+ installer
3. Run installer with "Add to PATH" checked
4. Verify: Open Command Prompt, type `python --version`

### macOS:
1. Install via Homebrew: `brew install python3`
2. Or download from python.org
3. Verify: `python3 --version`

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip
```

## 2. Setting up Development Environment

### Recommended: VS Code
1. Download from https://code.visualstudio.com/
2. Install Python extension
3. Configure Python interpreter

### Alternative: PyCharm Community
1. Download from https://jetbrains.com/pycharm/
2. Create new Python project

## 3. Your First Program

Create a file called `hello.py`:

```python
print("Hello, Python!")
print("Welcome to your programming journey!")

name = input("What's your name? ")
print(f"Nice to meet you, {name}!")
```

Run it: `python hello.py`

## 4. Package Management

Install packages with pip:
```bash
pip install requests
pip install matplotlib
pip list  # See installed packages
```

## 5. Virtual Environments (Recommended)

```bash
python -m venv myproject
# Windows: myproject\\Scripts\\activate
# Mac/Linux: source myproject/bin/activate
```

🎉 You're ready to start coding in Python!
"""

    def _get_basics_code_content(self) -> str:
        return """# Python Basics - Essential Concepts

# 1. Variables and Data Types
name = "Alice"           # String
age = 25                 # Integer  
height = 5.6             # Float
is_student = True        # Boolean

print(f"Name: {name}, Age: {age}, Height: {height}ft")

# 2. Basic Operations
x = 10
y = 3

print(f"Addition: {x + y}")
print(f"Division: {x / y}")
print(f"Integer Division: {x // y}")
print(f"Remainder: {x % y}")
print(f"Power: {x ** y}")

# 3. String Operations
message = "Python is awesome!"
print(message.upper())
print(message.lower())
print(message.replace("awesome", "fantastic"))
print(len(message))

# 4. User Input
user_name = input("Enter your name: ")
user_age = int(input("Enter your age: "))

print(f"Hello {user_name}, you are {user_age} years old!")

# 5. Comments
# This is a single line comment

\"\"\"
This is a 
multi-line comment
or docstring
\"\"\"

# Practice Exercise:
# Create variables for your favorite movie, year released, and rating
# Print them in a formatted string

favorite_movie = "The Matrix"
release_year = 1999
rating = 9.0

print(f"My favorite movie is {favorite_movie}, released in {release_year} with rating {rating}/10")
"""

    def _get_control_flow_content(self) -> str:
        return """# Control Flow in Python

# 1. If Statements
age = int(input("Enter your age: "))

if age >= 18:
    print("You are an adult!")
elif age >= 13:
    print("You are a teenager!")
else:
    print("You are a child!")

# 2. For Loops
print("\\nCounting to 5:")
for i in range(1, 6):
    print(f"Count: {i}")

# Loop through a list
fruits = ["apple", "banana", "orange"]
print("\\nFruits:")
for fruit in fruits:
    print(f"- {fruit}")

# 3. While Loops
print("\\nCountdown:")
countdown = 5
while countdown > 0:
    print(f"{countdown}...")
    countdown -= 1
print("Blast off! 🚀")

# 4. Break and Continue
print("\\nNumbers 1-10 (skipping 5):")
for num in range(1, 11):
    if num == 5:
        continue  # Skip 5
    if num == 8:
        break     # Stop at 8
    print(num)

# 5. Nested Loops
print("\\nMultiplication Table (3x3):")
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} x {j} = {i * j}")
    print()  # Empty line

# Practice Project: Simple Guessing Game
import random

secret_number = random.randint(1, 10)
max_attempts = 3
attempts = 0

print("\\n🎯 Guessing Game!")
print("I'm thinking of a number between 1 and 10.")
print(f"You have {max_attempts} attempts.")

while attempts < max_attempts:
    guess = int(input("Enter your guess: "))
    attempts += 1
    
    if guess == secret_number:
        print(f"🎉 Congratulations! You got it in {attempts} attempts!")
        break
    elif guess < secret_number:
        print("Too low!")
    else:
        print("Too high!")
    
    if attempts < max_attempts:
        print(f"Attempts remaining: {max_attempts - attempts}")
else:
    print(f"😢 Game over! The number was {secret_number}")
"""

    def _get_data_structures_content(self) -> str:
        return """# Python Data Structures

# 1. Lists - Ordered, mutable collections
students = ["Alice", "Bob", "Charlie", "Diana"]
print("Students:", students)

# List operations
students.append("Eve")           # Add to end
students.insert(1, "Frank")      # Insert at position
students.remove("Bob")           # Remove by value
print("After changes:", students)

# List comprehension
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
print("Squares:", squares)

# 2. Tuples - Ordered, immutable collections  
coordinates = (10, 20)
rgb_color = (255, 128, 0)
print(f"Point: {coordinates}, Color: {rgb_color}")

# 3. Dictionaries - Key-value pairs
student_grades = {
    "Alice": 95,
    "Bob": 87,
    "Charlie": 92,
    "Diana": 88
}

print("Grades:", student_grades)
print(f"Alice's grade: {student_grades['Alice']}")

# Add new grade
student_grades["Eve"] = 91
print("Updated grades:", student_grades)

# Dictionary methods
print("Students:", list(student_grades.keys()))
print("Grades:", list(student_grades.values()))

# 4. Sets - Unique values, unordered
fruits = {"apple", "banana", "orange", "apple"}  # Duplicate ignored
print("Fruits:", fruits)

vegetables = {"carrot", "broccoli", "spinach"}
print("Vegetables:", vegetables)

# Set operations
all_foods = fruits.union(vegetables)
print("All foods:", all_foods)

# 5. Mini-Project: Student Grade Calculator
class GradeCalculator:
    def __init__(self):
        self.students = {}
    
    def add_student(self, name, grades):
        self.students[name] = grades
    
    def calculate_average(self, name):
        if name in self.students:
            grades = self.students[name]
            return sum(grades) / len(grades)
        return None
    
    def get_class_average(self):
        all_grades = []
        for grades in self.students.values():
            all_grades.extend(grades)
        return sum(all_grades) / len(all_grades) if all_grades else 0
    
    def get_top_student(self):
        best_student = None
        best_average = 0
        
        for student, grades in self.students.items():
            avg = sum(grades) / len(grades)
            if avg > best_average:
                best_average = avg
                best_student = student
        
        return best_student, best_average

# Example usage
calculator = GradeCalculator()
calculator.add_student("Alice", [95, 92, 88, 96])
calculator.add_student("Bob", [87, 85, 91, 89])
calculator.add_student("Charlie", [92, 94, 89, 95])

print("\\n📊 Grade Calculator Results:")
for student in calculator.students.keys():
    avg = calculator.calculate_average(student)
    print(f"{student}: {avg:.1f}%")

class_avg = calculator.get_class_average()
print(f"\\nClass Average: {class_avg:.1f}%")

top_student, top_avg = calculator.get_top_student()
print(f"Top Student: {top_student} ({top_avg:.1f}%)")
"""

    def _get_project_requirements(self) -> str:
        return """# Final Project: Personal Expense Tracker

## 🎯 Project Overview
Create a command-line expense tracking application that helps users manage their personal finances.

## 📋 Requirements

### Core Features (Must Have)
1. **Add Expenses**: Record expense with date, category, amount, and description
2. **View Expenses**: Display all expenses or filter by date/category
3. **Categories**: Support categories like Food, Transport, Entertainment, etc.
4. **Summary**: Show total expenses and breakdown by category
5. **Data Persistence**: Save/load expenses from a file

### Advanced Features (Nice to Have)
1. **Budget Tracking**: Set monthly budgets and track remaining amounts
2. **Data Visualization**: Simple text-based charts showing spending patterns
3. **Search**: Find expenses by description or amount range
4. **Export**: Generate CSV reports

## 🛠️ Technical Requirements
- Use all major Python concepts learned in the course
- Implement proper error handling
- Include user-friendly menu system
- Add comments and documentation
- Follow Python naming conventions

## 📁 Project Structure
```
expense_tracker/
├── main.py              # Main application entry point
├── expense.py           # Expense class definition  
├── tracker.py           # ExpenseTracker class
├── utils.py             # Utility functions
├── data/
│   └── expenses.json    # Data storage file
└── README.md            # Project documentation
```

## 🚀 Getting Started
1. Create the project directory structure
2. Define the Expense class with attributes: date, category, amount, description
3. Create ExpenseTracker class with methods for CRUD operations
4. Implement the main menu loop
5. Add file I/O for data persistence
6. Test thoroughly with different scenarios

## 📊 Sample Output
```
=== Personal Expense Tracker ===
1. Add Expense
2. View All Expenses  
3. View by Category
4. Monthly Summary
5. Set Budget
6. Export to CSV
7. Exit

Enter choice: 1

Add New Expense:
Date (YYYY-MM-DD): 2024-01-15
Category: Food
Amount: 25.50
Description: Lunch at cafe
✅ Expense added successfully!
```

## 🎓 Learning Objectives
- Apply variables, data types, and operators
- Use control structures (if/else, loops)
- Work with data structures (lists, dictionaries)
- Implement functions and classes
- Handle user input and validation
- Perform file operations
- Practice error handling

## 📝 Submission Guidelines
1. Complete source code files
2. Sample data file with test expenses
3. README.md with setup and usage instructions
4. Brief reflection document on challenges faced and solutions

## 🏆 Evaluation Criteria
- **Functionality** (40%): All core features work correctly
- **Code Quality** (30%): Clean, readable, well-commented code
- **User Experience** (20%): Intuitive interface and error handling
- **Documentation** (10%): Clear README and code comments

## 💡 Tips for Success
- Start with a simple version and add features incrementally
- Test each feature before moving to the next
- Use meaningful variable and function names
- Don't hesitate to ask for help if stuck
- Have fun and be creative!

🎉 Good luck with your final project!
"""

    async def run_comprehensive_demo(self):
        """Run the complete comprehensive course structure demo"""

        print("🌟 COMPREHENSIVE COURSE STRUCTURE DEMO")
        print("=" * 70)
        print("Creating a complete learning ecosystem with multiple courses,")
        print("advanced section management, and rich content integration.")
        print("=" * 70)

        try:
            # Create the complete learning path
            result = await self.create_complete_learning_path()

            # Display results
            print(f"\n🎉 LEARNING PATH CREATION COMPLETED!")
            print(f"=" * 70)
            print(f"📚 Learning Path: {result['learning_path']['title']}")
            print(f"🎓 Total Courses: {result['total_courses']}")
            print(f"📖 Total Sections: {result['total_sections']}")

            print(f"\n📋 Created Courses:")
            for i, course in enumerate(result["created_courses"], 1):
                print(f"   {i}. {course['course_name']} ({course['level']})")
                print(f"      📊 Sections: {len(course['sections'])}")
                print(f"      🌐 URL: {course['course_url']}")
                print()

            print(f"🎯 Quick Access URLs:")
            for course in result["created_courses"]:
                print(f"   • {course['course_name']}: {course['course_url']}")

            return result

        except Exception as e:
            print(f"❌ Comprehensive demo failed: {e}")
            import traceback

            traceback.print_exc()
            return None


async def main():
    """Main function to run the comprehensive demo"""

    # Get environment variables
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_TOKEN", "b2021a7a41309b8c58ad026a751d0cd0")

    print(f"🔗 Connecting to: {moodle_url}")
    print(f"🔑 Using token: {moodle_token[:10]}...")

    # Create comprehensive course builder
    builder = ComprehensiveCourseBuilder(moodle_url, moodle_token)

    # Run the demo
    result = await builder.run_comprehensive_demo()

    if result:
        print(f"\n✨ Demo completed successfully!")
        print(f"   Check your Moodle instance to explore the created courses.")
    else:
        print(f"\n❌ Demo failed - check error messages above.")


if __name__ == "__main__":
    # Set default environment variables if not provided
    if not os.getenv("MOODLE_TOKEN"):
        os.environ["MOODLE_TOKEN"] = "b2021a7a41309b8c58ad026a751d0cd0"

    if not os.getenv("MOODLE_URL"):
        os.environ["MOODLE_URL"] = "http://localhost:8080"

    print("🌟 MoodleClaude Comprehensive Course Structure Demo")
    print(
        "📚 Creating a complete learning ecosystem with multiple interconnected courses"
    )
    print("⚡ Starting demo...\n")

    # Run the demo
    asyncio.run(main())
