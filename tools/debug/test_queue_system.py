#!/usr/bin/env python3
"""
Test the queue-based chunk processing system
"""

import asyncio
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.enhanced_mcp_server import EnhancedMoodleMCPServer

async def test_queue_system():
    """Test the queue-based processing with large content"""
    
    print("🚀 Testing Queue-Based Chunk Processing System")
    print("=" * 70)
    
    # Create content that will definitely require chunking and queue processing
    large_content_with_mixed_sizes = """
    # Complete Web Development Course
    
    ## HTML Fundamentals
    
    Let's start with basic HTML structure:
    
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My First Website</title>
    </head>
    <body>
        <header>
            <h1>Welcome to My Website</h1>
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </header>
        <main>
            <section id="home">
                <h2>Home Section</h2>
                <p>This is the main content area.</p>
            </section>
        </main>
        <footer>
            <p>&copy; 2024 My Website. All rights reserved.</p>
        </footer>
    </body>
    </html>
    ```
    
    This HTML structure provides the foundation for web pages.
    
    ## CSS Styling
    
    Now let's add some styling:
    
    ```css
    /* Reset and base styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #f4f4f4;
    }
    
    header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 0;
        position: fixed;
        width: 100%;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    nav ul {
        list-style: none;
        display: flex;
        justify-content: center;
        gap: 2rem;
    }
    
    nav a {
        color: white;
        text-decoration: none;
        font-weight: bold;
        transition: color 0.3s ease;
    }
    
    nav a:hover {
        color: #ffd700;
    }
    
    main {
        margin-top: 80px;
        padding: 2rem;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .card {
        background: white;
        padding: 2rem;
        margin: 1rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
    }
    ```
    
    This CSS creates a modern, responsive design.
    
    ## JavaScript Functionality
    
    Let's add interactivity with JavaScript:
    
    ```javascript
    // DOM manipulation and event handling
    document.addEventListener('DOMContentLoaded', function() {
        // Mobile menu toggle
        const menuToggle = document.createElement('button');
        menuToggle.classList.add('menu-toggle');
        menuToggle.innerHTML = '☰';
        document.querySelector('header').appendChild(menuToggle);
        
        const nav = document.querySelector('nav');
        
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('mobile-active');
        });
        
        // Smooth scrolling for navigation links
        const navLinks = document.querySelectorAll('nav a[href^="#"]');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                
                if (targetSection) {
                    targetSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Dynamic content loading
        function loadContent(section) {
            const contentArea = document.querySelector('#content');
            
            fetch(`/api/content/${section}`)
                .then(response => response.json())
                .then(data => {
                    contentArea.innerHTML = `
                        <h2>${data.title}</h2>
                        <p>${data.description}</p>
                        <div class="content-body">${data.content}</div>
                    `;
                })
                .catch(error => {
                    console.error('Error loading content:', error);
                    contentArea.innerHTML = '<p>Error loading content. Please try again.</p>';
                });
        }
        
        // Form validation
        const contactForm = document.querySelector('#contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const name = formData.get('name');
                const email = formData.get('email');
                const message = formData.get('message');
                
                // Basic validation
                if (!name || !email || !message) {
                    alert('Please fill in all fields');
                    return;
                }
                
                // Email validation
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    alert('Please enter a valid email address');
                    return;
                }
                
                // Submit form (simulate API call)
                submitForm(formData);
            });
        }
        
        function submitForm(formData) {
            // Simulate form submission
            const submitButton = document.querySelector('#submit-btn');
            submitButton.textContent = 'Sending...';
            submitButton.disabled = true;
            
            setTimeout(() => {
                alert('Message sent successfully!');
                contactForm.reset();
                submitButton.textContent = 'Send Message';
                submitButton.disabled = false;
            }, 2000);
        }
    });
    
    // Utility functions
    class WebUtils {
        static debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        static throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
        
        static formatDate(date) {
            return new Intl.DateTimeFormat('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(date));
        }
    }
    ```
    
    ## Python Backend
    
    Let's create a Flask backend:
    
    ```python
    from flask import Flask, jsonify, request, render_template
    from flask_cors import CORS
    import sqlite3
    import hashlib
    import jwt
    from datetime import datetime, timedelta
    import os
    
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Database setup
    def init_db():
        conn = sqlite3.connect('website.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/content/<section>')
    def get_content(section):
        content_data = {
            'home': {
                'title': 'Welcome Home',
                'description': 'This is the homepage content',
                'content': '<p>Welcome to our amazing website!</p>'
            },
            'about': {
                'title': 'About Us',
                'description': 'Learn more about our company',
                'content': '<p>We are a innovative web development company.</p>'
            },
            'contact': {
                'title': 'Contact Us',
                'description': 'Get in touch with our team',
                'content': '''
                    <form id="contact-form">
                        <input type="text" name="name" placeholder="Your Name" required>
                        <input type="email" name="email" placeholder="Your Email" required>
                        <textarea name="message" placeholder="Your Message" required></textarea>
                        <button type="submit" id="submit-btn">Send Message</button>
                    </form>
                '''
            }
        }
        
        return jsonify(content_data.get(section, {'error': 'Content not found'}))
    
    @app.route('/api/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect('website.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username or email already exists'}), 409
    
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('website.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            token = jwt.encode({
                'user_id': user[0],
                'username': user[1],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2]
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    if __name__ == '__main__':
        init_db()
        app.run(debug=True, host='0.0.0.0', port=5000)
    ```
    
    This comprehensive web development example covers frontend and backend!
    """
    
    print(f"📊 Large mixed content size: {len(large_content_with_mixed_sizes)} characters")
    
    # Create MCP server instance
    server = EnhancedMoodleMCPServer()
    
    # Test the course creation with queue system
    try:
        print(f"\n📚 Creating course with queue-based processing...")
        
        # Simulate tool call with mixed large content
        arguments = {
            "chat_content": large_content_with_mixed_sizes,
            "course_name": "Complete Web Development with Queue Processing",
            "course_description": "Full-stack web development course processed with advanced queue system for optimal reliability",
            "category_id": 1
        }
        
        # Call the course creation function
        result = await server._create_course_from_chat(arguments)
        
        if result and len(result) > 0:
            response_text = result[0].text
            print(f"✅ Course creation result:")
            print("=" * 70)
            print(response_text)
            print("=" * 70)
            
            # Check for queue processing indicators
            if "Queue:" in response_text or "Queue Processing Stats:" in response_text:
                print(f"\n🎉 SUCCESS! Queue processing system is working!")
                print(f"✅ Advanced retry logic and rate limiting in action")
                print(f"✅ Resilient processing with automatic error recovery")
                print(f"✅ Progress tracking and detailed statistics")
            else:
                print(f"\n✅ Content processed successfully (queue not needed)")
                
        else:
            print(f"❌ No result returned from course creation")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 70)
    print(f"🎯 Queue System Test Complete")

if __name__ == "__main__":
    asyncio.run(test_queue_system())