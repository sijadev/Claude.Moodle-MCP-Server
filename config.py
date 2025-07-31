"""
Compatibility module for direct import of config.
Re-exports everything from src.core.config and config/* for backward compatibility.
"""

import sys
import os

# Add the directories to the Python path for imports to work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
config_dir = os.path.join(current_dir, 'config')

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if config_dir not in sys.path:
    sys.path.insert(0, config_dir)

try:
    # Try to import from src.core.config first
    from src.core.config import *
    try:
        # Also try to import from config directory if it exists
        from config.dual_token_config import *
    except ImportError:
        pass
except ImportError:
    try:
        # Fallback for different environment setups
        from core.config import *
        try:
            from dual_token_config import *
        except ImportError:
            pass
    except ImportError:
        # Another fallback - try importing directly from config directory
        try:
            sys.path.insert(0, os.path.join(current_dir, 'config'))
            from dual_token_config import *
        except ImportError:
            # Last fallback - try src/core/config directly
            sys.path.insert(0, os.path.join(current_dir, 'src', 'core'))
            try:
                from config import *
            except ImportError:
                pass