"""
Compatibility module for direct import of enhanced_moodle_claude.
Re-exports everything from src.clients.enhanced_moodle_claude for backward compatibility.
"""

import os
import sys

# Add the src directory to the Python path for imports to work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from src.clients.enhanced_moodle_claude import *
except ImportError:
    # Fallback for different environment setups
    from clients.enhanced_moodle_claude import *
