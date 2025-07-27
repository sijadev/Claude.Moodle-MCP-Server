"""
Configuration management for the MCP Moodle server
Handles environment variables and configuration settings
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration settings for the MCP server"""
    
    # Moodle configuration
    moodle_url: str
    moodle_token: str
    moodle_username: Optional[str] = None
    
    # Server configuration
    server_name: str = "moodle-course-creator"
    server_version: str = "1.0.0"
    log_level: str = "INFO"
    
    # Content processing configuration
    max_code_length: int = 10000  # Maximum code length to process
    max_topic_length: int = 5000  # Maximum topic content length
    min_code_lines: int = 2  # Minimum lines for code to be considered
    min_topic_words: int = 10  # Minimum words for topic content
    
    # Course creation defaults
    default_category_id: int = 1
    default_course_format: str = "topics"
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        # Moodle settings (optional for preview mode)
        self.moodle_url = os.getenv("MOODLE_URL", "")
        self.moodle_token = os.getenv("MOODLE_TOKEN", "")
        
        # Optional Moodle settings
        self.moodle_username = os.getenv("MOODLE_USERNAME")
        
        # Server settings
        self.server_name = os.getenv("SERVER_NAME", self.server_name)
        self.server_version = os.getenv("SERVER_VERSION", self.server_version)
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        
        # Content processing settings
        self.max_code_length = int(os.getenv("MAX_CODE_LENGTH", self.max_code_length))
        self.max_topic_length = int(os.getenv("MAX_TOPIC_LENGTH", self.max_topic_length))
        self.min_code_lines = int(os.getenv("MIN_CODE_LINES", self.min_code_lines))
        self.min_topic_words = int(os.getenv("MIN_TOPIC_WORDS", self.min_topic_words))
        
        # Course defaults
        self.default_category_id = int(os.getenv("DEFAULT_CATEGORY_ID", self.default_category_id))
        self.default_course_format = os.getenv("DEFAULT_COURSE_FORMAT", self.default_course_format)
        
        # Configure logging
        self._configure_logging()
        
        logger.info("Configuration loaded successfully")
        logger.debug(f"Moodle URL: {self.moodle_url}")
        logger.debug(f"Server: {self.server_name} v{self.server_version}")
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _configure_logging(self):
        """Configure logging based on log level"""
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        level = log_levels.get(self.log_level.upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set specific loggers
        logging.getLogger('mcp').setLevel(level)
        logging.getLogger('urllib3').setLevel(logging.WARNING)  # Reduce HTTP noise
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    def validate_moodle_connection(self) -> bool:
        """Validate Moodle connection settings"""
        try:
            # Basic URL validation
            if not self.moodle_url.startswith(('http://', 'https://')):
                logger.error("Moodle URL must start with http:// or https://")
                return False
            
            # Basic token validation (should be alphanumeric and reasonably long)
            if len(self.moodle_token) < 32:
                logger.error("Moodle token appears to be too short")
                return False
            
            logger.info("Moodle connection settings appear valid")
            return True
            
        except Exception as e:
            logger.error(f"Error validating Moodle connection: {e}")
            return False
    
    def get_content_limits(self) -> dict:
        """Get content processing limits"""
        return {
            'max_code_length': self.max_code_length,
            'max_topic_length': self.max_topic_length,
            'min_code_lines': self.min_code_lines,
            'min_topic_words': self.min_topic_words
        }
    
    def get_moodle_config(self) -> dict:
        """Get Moodle-specific configuration"""
        return {
            'url': self.moodle_url,
            'token': self.moodle_token,
            'username': self.moodle_username,
            'default_category_id': self.default_category_id,
            'default_course_format': self.default_course_format
        }
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            'server_name': self.server_name,
            'server_version': self.server_version,
            'log_level': self.log_level,
            'moodle_url': self.moodle_url,  # URL is okay to show
            'moodle_token_length': len(self.moodle_token),  # Show length, not actual token
            'content_limits': self.get_content_limits(),
            'course_defaults': {
                'category_id': self.default_category_id,
                'format': self.default_course_format
            }
        }

# Global configuration instance
_config: Optional[Config] = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config

def reload_config():
    """Reload configuration from environment"""
    global _config
    _config = Config()
    logger.info("Configuration reloaded")

# Environment variable documentation
ENV_VARS = {
    'MOODLE_URL': {
        'required': True,
        'description': 'Base URL of your Moodle site (e.g., https://moodle.example.com)',
        'example': 'https://moodle.example.com'
    },
    'MOODLE_TOKEN': {
        'required': True,
        'description': 'Moodle web service token for API access',
        'example': 'abc123def456...'
    },
    'MOODLE_USERNAME': {
        'required': False,
        'description': 'Moodle username (optional, for reference)',
        'example': 'admin'
    },
    'SERVER_NAME': {
        'required': False,
        'description': 'Name of the MCP server',
        'default': 'moodle-course-creator'
    },
    'SERVER_VERSION': {
        'required': False,
        'description': 'Version of the MCP server',
        'default': '1.0.0'
    },
    'LOG_LEVEL': {
        'required': False,
        'description': 'Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)',
        'default': 'INFO'
    },
    'MAX_CODE_LENGTH': {
        'required': False,
        'description': 'Maximum length of code blocks to process',
        'default': '10000'
    },
    'MAX_TOPIC_LENGTH': {
        'required': False,
        'description': 'Maximum length of topic content to process',
        'default': '5000'
    },
    'MIN_CODE_LINES': {
        'required': False,
        'description': 'Minimum number of lines for code to be considered',
        'default': '2'
    },
    'MIN_TOPIC_WORDS': {
        'required': False,
        'description': 'Minimum number of words for topic content',
        'default': '10'
    },
    'DEFAULT_CATEGORY_ID': {
        'required': False,
        'description': 'Default Moodle category ID for new courses',
        'default': '1'
    },
    'DEFAULT_COURSE_FORMAT': {
        'required': False,
        'description': 'Default Moodle course format',
        'default': 'topics'
    }
}

def print_env_help():
    """Print help for environment variables"""
    print("MCP Moodle Server - Environment Variables")
    print("=" * 50)
    
    for var_name, var_info in ENV_VARS.items():
        print(f"\n{var_name}:")
        print(f"  Required: {'Yes' if var_info['required'] else 'No'}")
        print(f"  Description: {var_info['description']}")
        
        if 'default' in var_info:
            print(f"  Default: {var_info['default']}")
        
        if 'example' in var_info:
            print(f"  Example: {var_info['example']}")
    
    print("\n" + "=" * 50)
    print("Set these environment variables before running the server.")

if __name__ == "__main__":
    print_env_help()
