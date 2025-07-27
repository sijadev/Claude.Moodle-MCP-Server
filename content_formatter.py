"""
Content Formatter for Moodle
Handles formatting of code and topic content for Moodle activities
"""

import html
import re
from typing import Optional
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
import markdown

class ContentFormatter:
    """Formatter for creating Moodle-compatible content"""
    
    def __init__(self):
        # Initialize Pygments HTML formatter with Moodle-friendly styling
        self.code_formatter = HtmlFormatter(
            style='default',
            cssclass='code-highlight',
            linenos=True,
            linenostart=1,
            noclasses=False
        )
        
        # CSS styles for code highlighting
        self.code_css = """
        <style>
        .code-container {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            margin: 15px 0;
            overflow: hidden;
        }
        .code-header {
            background-color: #e9ecef;
            padding: 10px 15px;
            border-bottom: 1px solid #dee2e6;
            font-weight: bold;
        }
        .code-content {
            padding: 0;
            max-height: 400px;
            overflow-y: auto;
        }
        .code-highlight {
            margin: 0;
            padding: 15px;
            background-color: #ffffff;
        }
        .code-highlight .linenos {
            background-color: #f8f9fa;
            color: #6c757d;
            padding-right: 10px;
            border-right: 1px solid #e9ecef;
        }
        .code-highlight .code {
            padding-left: 10px;
        }
        .code-download {
            background-color: #f8f9fa;
            padding: 8px 15px;
            border-top: 1px solid #e9ecef;
            text-align: right;
        }
        .topic-content {
            background-color: #fff;
            padding: 20px;
            border-left: 4px solid #007bff;
            margin: 15px 0;
        }
        .topic-content h3 {
            color: #007bff;
            margin-top: 0;
        }
        .topic-meta {
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        .content-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #e9ecef;
            border-radius: 5px;
        }
        </style>
        """
        
        # Markdown extensions for better formatting
        self.markdown_extensions = [
            'codehilite',
            'fenced_code',
            'tables',
            'toc',
            'nl2br'
        ]
    
    def format_code_for_moodle(self, code: str, language: Optional[str] = None, 
                              title: str = "Code Example", description: str = "") -> str:
        """
        Format code content for Moodle page activity
        
        Args:
            code: Source code content
            language: Programming language
            title: Code title
            description: Code description
            
        Returns:
            HTML formatted content for Moodle
        """
        # Get syntax highlighted HTML
        highlighted_code = self._highlight_code(code, language)
        
        # Create file extension for download suggestion
        file_extension = self._get_file_extension(language)
        filename = f"{title.lower().replace(' ', '_')}.{file_extension}"
        
        # Format the complete HTML
        html_content = f"""
        {self.code_css}
        
        <div class="content-section">
            <h2>{html.escape(title)}</h2>
            {f'<p class="topic-meta">{html.escape(description)}</p>' if description else ''}
            
            <div class="code-container">
                <div class="code-header">
                    <span>📄 {html.escape(filename)}</span>
                    <span style="float: right;">
                        <small>{language.title() if language else 'Text'} • {len(code.splitlines())} lines</small>
                    </span>
                </div>
                
                <div class="code-content">
                    {highlighted_code}
                </div>
                
                <div class="code-download">
                    <small>💡 Tip: Right-click the code area and select "Save As" to download this file</small>
                </div>
            </div>
            
            <div class="code-metadata">
                <h4>Code Information</h4>
                <ul>
                    <li><strong>Language:</strong> {language.title() if language else 'Text'}</li>
                    <li><strong>Lines:</strong> {len(code.splitlines())}</li>
                    <li><strong>Characters:</strong> {len(code)}</li>
                    {f'<li><strong>Description:</strong> {html.escape(description)}</li>' if description else ''}
                </ul>
            </div>
            
            <details>
                <summary><strong>Raw Code (for copying)</strong></summary>
                <pre style="background-color: #f8f9fa; padding: 15px; border: 1px solid #e9ecef; margin-top: 10px;"><code>{html.escape(code)}</code></pre>
            </details>
        </div>
        """
        
        return html_content
    
    def format_topic_for_moodle(self, content: str, title: str = "Topic", 
                               description: str = "") -> str:
        """
        Format topic content for Moodle page activity
        
        Args:
            content: Topic content (can be markdown)
            title: Topic title
            description: Topic description
            
        Returns:
            HTML formatted content for Moodle
        """
        # Convert markdown to HTML if content contains markdown
        formatted_content = self._format_markdown_content(content)
        
        # Create HTML layout
        html_content = f"""
        {self.code_css}
        
        <div class="topic-content">
            <h2>📚 {html.escape(title)}</h2>
            {f'<p class="topic-meta"><em>{html.escape(description)}</em></p>' if description else ''}
            
            <div class="content-body">
                {formatted_content}
            </div>
            
            <div class="topic-footer" style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e9ecef;">
                <small class="text-muted">
                    📖 Content length: {len(content)} characters • 
                    ⏱️ Estimated reading time: {self._estimate_reading_time(content)} min
                </small>
            </div>
        </div>
        """
        
        return html_content
    
    def format_mixed_content(self, title: str, items: list, description: str = "") -> str:
        """
        Format mixed content (code + topics) for a single Moodle page
        
        Args:
            title: Page title
            items: List of ContentItem objects
            description: Page description
            
        Returns:
            HTML formatted content
        """
        html_content = f"""
        {self.code_css}
        
        <div class="content-section">
            <h1>📋 {html.escape(title)}</h1>
            {f'<p class="topic-meta">{html.escape(description)}</p>' if description else ''}
            
            <div class="content-summary">
                <h3>Content Overview</h3>
                <ul>
        """
        
        # Add content summary
        code_count = sum(1 for item in items if item.type == "code")
        topic_count = sum(1 for item in items if item.type == "topic")
        
        if code_count > 0:
            html_content += f"<li>💻 {code_count} Code Example{'s' if code_count != 1 else ''}</li>"
        if topic_count > 0:
            html_content += f"<li>📝 {topic_count} Topic Description{'s' if topic_count != 1 else ''}</li>"
        
        html_content += """
                </ul>
            </div>
            
            <hr style="margin: 25px 0;">
        """
        
        # Add individual items
        for i, item in enumerate(items, 1):
            if item.type == "code":
                html_content += f"""
                <div id="item-{i}" class="content-item">
                    <h3>💻 {html.escape(item.title)}</h3>
                    {self._get_embedded_code_html(item.content, item.language, item.description)}
                </div>
                <hr style="margin: 25px 0;">
                """
            elif item.type == "topic":
                html_content += f"""
                <div id="item-{i}" class="content-item">
                    <h3>📝 {html.escape(item.title)}</h3>
                    <div class="topic-content">
                        {self._format_markdown_content(item.content)}
                    </div>
                </div>
                <hr style="margin: 25px 0;">
                """
        
        html_content += "</div>"
        return html_content
    
    def _highlight_code(self, code: str, language: Optional[str] = None) -> str:
        """Apply syntax highlighting to code"""
        try:
            if language:
                # Try to get lexer by language name
                lexer = get_lexer_by_name(language, stripnl=False)
            else:
                # Try to guess lexer from content
                lexer = guess_lexer(code)
            
            # Generate highlighted HTML
            highlighted = highlight(code, lexer, self.code_formatter)
            return highlighted
            
        except ClassNotFound:
            # Fallback to plain text if language not supported
            escaped_code = html.escape(code)
            return f'<pre class="code-highlight"><code>{escaped_code}</code></pre>'
        except Exception as e:
            # Fallback for any other errors
            escaped_code = html.escape(code)
            return f'<pre class="code-highlight"><code>{escaped_code}</code></pre>'
    
    def _get_embedded_code_html(self, code: str, language: Optional[str] = None, 
                               description: str = "") -> str:
        """Get HTML for embedded code (without full page structure)"""
        highlighted_code = self._highlight_code(code, language)
        file_extension = self._get_file_extension(language)
        
        return f"""
        <div class="code-container">
            <div class="code-header">
                <span>📄 Code.{file_extension}</span>
                <span style="float: right;">
                    <small>{language.title() if language else 'Text'} • {len(code.splitlines())} lines</small>
                </span>
            </div>
            
            <div class="code-content">
                {highlighted_code}
            </div>
            
            {f'<div class="code-description" style="padding: 10px 15px; background-color: #f8f9fa; border-top: 1px solid #e9ecef;"><small>{html.escape(description)}</small></div>' if description else ''}
        </div>
        """
    
    def _format_markdown_content(self, content: str) -> str:
        """Convert markdown content to HTML"""
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                content,
                extensions=self.markdown_extensions,
                extension_configs={
                    'codehilite': {
                        'css_class': 'highlight',
                        'use_pygments': True
                    }
                }
            )
            return html_content
        except Exception:
            # Fallback: treat as plain text with basic formatting
            return self._format_plain_text(content)
    
    def _format_plain_text(self, content: str) -> str:
        """Format plain text with basic HTML formatting"""
        # Escape HTML and convert newlines
        formatted = html.escape(content)
        
        # Convert double newlines to paragraphs
        paragraphs = formatted.split('\n\n')
        formatted = ''.join(f'<p>{para.replace(chr(10), "<br>")}</p>' for para in paragraphs if para.strip())
        
        # Basic markdown-like formatting
        formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted)  # Bold
        formatted = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted)  # Italic
        formatted = re.sub(r'`(.*?)`', r'<code>\1</code>', formatted)  # Inline code
        
        return formatted
    
    def _get_file_extension(self, language: Optional[str]) -> str:
        """Get appropriate file extension for language"""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'html': 'html',
            'css': 'css',
            'sql': 'sql',
            'bash': 'sh',
            'shell': 'sh',
            'json': 'json',
            'yaml': 'yml',
            'xml': 'xml',
            'go': 'go',
            'rust': 'rs',
            'php': 'php',
            'ruby': 'rb',
            'swift': 'swift',
            'kotlin': 'kt',
            'r': 'r',
            'matlab': 'm',
            'scala': 'scala',
        }
        
        return extensions.get(language.lower() if language else '', 'txt')
    
    def _estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes (assuming 200 words per minute)"""
        word_count = len(content.split())
        reading_time = max(1, round(word_count / 200))
        return reading_time
    
    def create_course_summary_page(self, course_name: str, sections: list) -> str:
        """Create a summary page for the course"""
        html_content = f"""
        {self.code_css}
        
        <div class="content-section">
            <h1>📚 {html.escape(course_name)} - Course Overview</h1>
            
            <div class="course-summary">
                <h2>Course Structure</h2>
                <p>This course was automatically generated from Claude chat conversations. 
                   It contains organized code examples and topic descriptions extracted from the discussion.</p>
                
                <h3>📋 Content Summary</h3>
                <ul>
                    <li><strong>Total Sections:</strong> {len(sections)}</li>
        """
        
        total_code = sum(len([item for item in section.get('items', []) if item.type == 'code']) for section in sections)
        total_topics = sum(len([item for item in section.get('items', []) if item.type == 'topic']) for section in sections)
        
        html_content += f"""
                    <li><strong>Code Examples:</strong> {total_code}</li>
                    <li><strong>Topic Descriptions:</strong> {total_topics}</li>
                </ul>
                
                <h3>🗂️ Section Overview</h3>
                <ol>
        """
        
        for section in sections:
            items = section.get('items', [])
            code_count = len([item for item in items if item.type == 'code'])
            topic_count = len([item for item in items if item.type == 'topic'])
            
            html_content += f"""
                    <li>
                        <strong>{html.escape(section.get('name', 'Unnamed Section'))}</strong>
                        <ul>
                            <li>💻 {code_count} code example{'s' if code_count != 1 else ''}</li>
                            <li>📝 {topic_count} topic description{'s' if topic_count != 1 else ''}</li>
                        </ul>
                    </li>
            """
        
        html_content += """
                </ol>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #e7f3ff; border-left: 4px solid #007bff;">
                    <h4>🎯 How to Use This Course</h4>
                    <ul>
                        <li>Navigate through sections to explore different topics</li>
                        <li>Code examples are provided with syntax highlighting and download options</li>
                        <li>Topic descriptions provide context and explanations</li>
                        <li>Use the search function to find specific content</li>
                    </ul>
                </div>
            </div>
        </div>
        """
        
        return html_content
