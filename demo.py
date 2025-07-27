#!/usr/bin/env python3
"""
Demo script to show MCP Moodle server content extraction functionality
"""

import json
from content_parser import ChatContentParser
from content_formatter import ContentFormatter

# Sample chat content with code examples and topic descriptions
SAMPLE_CHAT = """
Human: I want to learn about Python web development with Flask.