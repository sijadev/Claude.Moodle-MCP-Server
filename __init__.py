"""
MoodleClaude package initialization.
Exposes the main classes for easier importing.
"""

from src.clients.enhanced_moodle_claude import (
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