#!/usr/bin/env python3
"""
Core interfaces for MoodleClaude architecture
Implements dependency injection and loose coupling patterns
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

# Import existing models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.models import (
    ContentItem, ChatContent, CourseSection, CourseStructure
)


class SessionEventType(Enum):
    """Event types for session management"""
    SESSION_CREATED = "session_created"
    PROCESSING_STARTED = "processing_started"
    CHUNK_PROCESSED = "chunk_processed"
    COURSE_CREATED = "course_created"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"
    VALIDATION_COMPLETED = "validation_completed"


class SessionEvent:
    """Event data structure for session notifications"""
    def __init__(self, event_type: SessionEventType, session_id: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.session_id = session_id
        self.data = data
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "session_id": self.session_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class CommandResult:
    """Result of command execution"""
    def __init__(self, success: bool, message: str = "", data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()


# ================================
# Core Service Interfaces
# ================================

class IMoodleClient(ABC):
    """Interface for Moodle API operations"""
    
    @abstractmethod
    async def create_course(self, name: str, description: str, category_id: int = 1) -> int:
        """Create a new Moodle course"""
        pass
    
    @abstractmethod
    async def create_course_structure(self, course_id: int, sections_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create complete course structure with sections and activities"""
        pass
    
    @abstractmethod
    async def create_section(self, course_id: int, name: str, description: str, position: int) -> int:
        """Create a course section"""
        pass
    
    @abstractmethod
    async def create_page_activity(self, course_id: int, section_id: int, name: str, content: str) -> Dict[str, Any]:
        """Create a page activity"""
        pass
    
    @abstractmethod
    async def create_label_activity(self, course_id: int, section_id: int, content: str) -> Dict[str, Any]:
        """Create a label activity"""
        pass
    
    @abstractmethod
    async def get_courses(self) -> List[Dict[str, Any]]:
        """Get list of courses"""
        pass
    
    @abstractmethod
    async def get_course_sections(self, course_id: int) -> List[Dict[str, Any]]:
        """Get course sections"""
        pass


class IContentParser(ABC):
    """Interface for content parsing operations"""
    
    @abstractmethod
    def parse_chat(self, chat_content: str) -> ChatContent:
        """Parse chat content into structured format"""
        pass
    
    @abstractmethod
    def extract_code_blocks(self, content: str) -> List[ContentItem]:
        """Extract code blocks from content"""
        pass
    
    @abstractmethod
    def extract_topics(self, content: str) -> List[ContentItem]:
        """Extract topics from content"""
        pass


class IContentProcessor(ABC):
    """Interface for content processing operations"""
    
    @abstractmethod
    async def analyze_content_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze content complexity and recommend processing strategy"""
        pass
    
    @abstractmethod
    async def create_session(self, content: str, course_name: str) -> str:
        """Create a new processing session"""
        pass
    
    @abstractmethod
    async def process_content_chunk(self, session_id: str, chunk_index: int, continue_previous: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """Process a single content chunk"""
        pass
    
    @abstractmethod
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing performance metrics"""
        pass


class ISessionRepository(ABC):
    """Interface for session data persistence"""
    
    @abstractmethod
    async def save(self, session_data: Dict[str, Any]) -> None:
        """Save session data"""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session by ID"""
        pass
    
    @abstractmethod
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete session"""
        pass
    
    @abstractmethod
    async def update_session_state(self, session_id: str, state: str, data: Dict[str, Any]) -> bool:
        """Update session state and data"""
        pass


class ISessionObserver(ABC):
    """Interface for session event observers"""
    
    @abstractmethod
    async def on_session_event(self, event: SessionEvent) -> None:
        """Handle session event"""
        pass


class IEventPublisher(ABC):
    """Interface for event publishing"""
    
    @abstractmethod
    def subscribe(self, observer: ISessionObserver) -> None:
        """Subscribe to events"""
        pass
    
    @abstractmethod
    def unsubscribe(self, observer: ISessionObserver) -> None:
        """Unsubscribe from events"""
        pass
    
    @abstractmethod
    async def publish(self, event: SessionEvent) -> None:
        """Publish event to all subscribers"""
        pass


class ISessionCommand(ABC):
    """Interface for session operations commands"""
    
    @abstractmethod
    async def execute(self, session_data: Dict[str, Any]) -> CommandResult:
        """Execute the command"""
        pass
    
    @abstractmethod
    async def undo(self, session_data: Dict[str, Any]) -> CommandResult:
        """Undo the command (if possible)"""
        pass


class ICourseStructureBuilder(ABC):
    """Interface for building course structures"""
    
    @abstractmethod
    def with_name(self, name: str) -> 'ICourseStructureBuilder':
        """Set course name"""
        pass
    
    @abstractmethod
    def with_description(self, description: str) -> 'ICourseStructureBuilder':
        """Set course description"""
        pass
    
    @abstractmethod
    def add_section(self, section: CourseSection) -> 'ICourseStructureBuilder':
        """Add section to course"""
        pass
    
    @abstractmethod
    def build(self) -> CourseStructure:
        """Build the final course structure"""
        pass


class IServiceContainer(ABC):
    """Interface for dependency injection container"""
    
    @abstractmethod
    def register(self, interface_type: type, implementation: Any, singleton: bool = True) -> None:
        """Register a service implementation"""
        pass
    
    @abstractmethod
    def resolve(self, interface_type: type) -> Any:
        """Resolve a service instance"""
        pass
    
    @abstractmethod
    def is_registered(self, interface_type: type) -> bool:
        """Check if service is registered"""
        pass


# ================================
# Application Service Interfaces
# ================================

class ICourseCreationService(ABC):
    """High-level interface for course creation orchestration"""
    
    @abstractmethod
    async def create_course_from_content(self, content: str, course_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete course from chat content"""
        pass
    
    @abstractmethod
    async def continue_course_creation(self, session_id: str, additional_content: str = "") -> Dict[str, Any]:
        """Continue an existing course creation session"""
        pass
    
    @abstractmethod
    async def validate_course(self, session_id: str, course_id: Optional[int] = None) -> Dict[str, Any]:
        """Validate created course"""
        pass
    
    @abstractmethod
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session status"""
        pass


class IAnalyticsService(ABC):
    """Interface for analytics and monitoring"""
    
    @abstractmethod
    async def record_session_metrics(self, session_id: str, metrics: Dict[str, Any]) -> None:
        """Record session performance metrics"""
        pass
    
    @abstractmethod
    async def get_processing_analytics(self, detailed: bool = False) -> Dict[str, Any]:
        """Get processing analytics"""
        pass
    
    @abstractmethod
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        pass


# ================================
# Configuration Interfaces
# ================================

class IConfiguration(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    def get_moodle_url(self) -> str:
        """Get Moodle URL"""
        pass
    
    @abstractmethod
    def get_basic_token(self) -> str:
        """Get basic token"""
        pass
    
    @abstractmethod
    def get_plugin_token(self) -> str:
        """Get plugin token"""
        pass
    
    @abstractmethod
    def is_dual_token_mode(self) -> bool:
        """Check if in dual token mode"""
        pass
    
    @abstractmethod
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration"""
        pass