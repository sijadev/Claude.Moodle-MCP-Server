"""
MoodleClaude package initialization.
Exposes the main classes for easier importing.
"""

import sys
import os

# Add the src directory to the Python path for imports to work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from src.clients.enhanced_moodle_claude import (
        EnhancedMoodleAPI,
        FileUploadConfig,
        MoodleClaudeIntegration,
        SectionConfig,
    )
except ImportError:
    # Fallback for different environment setups
    from clients.enhanced_moodle_claude import (
        EnhancedMoodleAPI,
        FileUploadConfig,
        MoodleClaudeIntegration,
        SectionConfig,
    )

__all__ = [
    'EnhancedMoodleAPI',
    'FileUploadConfig', 
    'MoodleClaudeIntegration',
    'SectionConfig',
]