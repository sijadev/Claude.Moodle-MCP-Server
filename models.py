"""
Data models for the MCP Moodle server
Defines the structure for chat content, course organization, and content items
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class ContentType(Enum):
    """Types of content that can be extracted"""
    CODE = "code"
    TOPIC = "topic"
    MIXED = "mixed"

@dataclass
class ContentItem:
    """Represents a single piece of content (code or topic)"""
    type: str  # "code" or "topic"
    title: str
    content: str
    description: Optional[str] = None
    language: Optional[str] = None  # For code items
    topic: Optional[str] = None  # Subject/category
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization"""
        if self.type not in ["code", "topic"]:
            raise ValueError(f"Invalid content type: {self.type}")
        
        # Normalize language name
        if self.language:
            self.language = self.language.lower().strip()
        
        # Ensure content is not empty
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")
        
        # Generate default title if not provided
        if not self.title or not self.title.strip():
            if self.type == "code":
                self.title = f"{self.language.title() if self.language else 'Code'} Example"
            else:
                # Use first few words of content as title
                words = self.content.split()[:6]
                self.title = ' '.join(words) + ("..." if len(words) >= 6 else "")
    
    @property
    def word_count(self) -> int:
        """Get word count of content"""
        return len(self.content.split())
    
    @property
    def line_count(self) -> int:
        """Get line count of content"""
        return len(self.content.splitlines())
    
    @property
    def char_count(self) -> int:
        """Get character count of content"""
        return len(self.content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'description': self.description,
            'language': self.language,
            'topic': self.topic,
            'metadata': self.metadata,
            'stats': {
                'word_count': self.word_count,
                'line_count': self.line_count,
                'char_count': self.char_count
            }
        }

@dataclass
class ChatContent:
    """Represents parsed content from a chat conversation"""
    items: List[ContentItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process content after initialization"""
        # Remove empty items
        self.items = [item for item in self.items if item.content.strip()]
        
        # Update metadata
        self.metadata.update({
            'total_items': len(self.items),
            'code_items': len([item for item in self.items if item.type == "code"]),
            'topic_items': len([item for item in self.items if item.type == "topic"]),
            'languages': list(set(item.language for item in self.items if item.language)),
            'topics': list(set(item.topic for item in self.items if item.topic))
        })
    
    @property
    def code_items(self) -> List[ContentItem]:
        """Get all code items"""
        return [item for item in self.items if item.type == "code"]
    
    @property
    def topic_items(self) -> List[ContentItem]:
        """Get all topic items"""
        return [item for item in self.items if item.type == "topic"]
    
    @property
    def languages(self) -> List[str]:
        """Get unique languages found in code items"""
        return list(set(item.language for item in self.code_items if item.language))
    
    @property
    def topics(self) -> List[str]:
        """Get unique topics found"""
        return list(set(item.topic for item in self.items if item.topic))
    
    def get_items_by_topic(self, topic: str) -> List[ContentItem]:
        """Get all items for a specific topic"""
        return [item for item in self.items if item.topic == topic]
    
    def get_items_by_language(self, language: str) -> List[ContentItem]:
        """Get all code items for a specific language"""
        return [item for item in self.code_items if item.language == language]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'items': [item.to_dict() for item in self.items],
            'metadata': self.metadata,
            'summary': {
                'total_items': len(self.items),
                'code_items': len(self.code_items),
                'topic_items': len(self.topic_items),
                'languages': self.languages,
                'topics': self.topics
            }
        }

@dataclass
class CourseSection:
    """Represents a section within a Moodle course"""
    name: str
    description: str = ""
    items: List[ContentItem] = field(default_factory=list)
    section_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Process section after initialization"""
        # Update metadata
        self.metadata.update({
            'item_count': len(self.items),
            'code_count': len([item for item in self.items if item.type == "code"]),
            'topic_count': len([item for item in self.items if item.type == "topic"]),
            'languages': list(set(item.language for item in self.items if item.language))
        })
    
    @property
    def code_items(self) -> List[ContentItem]:
        """Get code items in this section"""
        return [item for item in self.items if item.type == "code"]
    
    @property
    def topic_items(self) -> List[ContentItem]:
        """Get topic items in this section"""
        return [item for item in self.items if item.type == "topic"]
    
    def add_item(self, item: ContentItem):
        """Add an item to this section"""
        self.items.append(item)
        # Update metadata
        self.__post_init__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'description': self.description,
            'section_id': self.section_id,
            'items': [item.to_dict() for item in self.items],
            'metadata': self.metadata
        }

@dataclass
class CourseStructure:
    """Represents the complete structure of a Moodle course"""
    sections: List[CourseSection] = field(default_factory=list)
    course_id: Optional[int] = None
    name: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Inner class for backward compatibility
    @dataclass
    class Section:
        """Backward compatibility class"""
        name: str
        description: str = ""
        items: List[ContentItem] = field(default_factory=list)
        
        def to_course_section(self) -> CourseSection:
            """Convert to CourseSection"""
            return CourseSection(
                name=self.name,
                description=self.description,
                items=self.items
            )
    
    def __post_init__(self):
        """Process course structure after initialization"""
        # Convert Section objects to CourseSection if needed
        converted_sections = []
        for section in self.sections:
            if isinstance(section, CourseStructure.Section):
                converted_sections.append(section.to_course_section())
            else:
                converted_sections.append(section)
        self.sections = converted_sections
        
        # Update metadata
        total_items = sum(len(section.items) for section in self.sections)
        total_code = sum(len(section.code_items) for section in self.sections)
        total_topics = sum(len(section.topic_items) for section in self.sections)
        all_languages = set()
        all_topics = set()
        
        for section in self.sections:
            for item in section.items:
                if item.language:
                    all_languages.add(item.language)
                if item.topic:
                    all_topics.add(item.topic)
        
        self.metadata.update({
            'section_count': len(self.sections),
            'total_items': total_items,
            'total_code_items': total_code,
            'total_topic_items': total_topics,
            'languages': list(all_languages),
            'topics': list(all_topics)
        })
    
    @property
    def total_items(self) -> int:
        """Get total number of items across all sections"""
        return sum(len(section.items) for section in self.sections)
    
    @property
    def total_code_items(self) -> int:
        """Get total number of code items"""
        return sum(len(section.code_items) for section in self.sections)
    
    @property
    def total_topic_items(self) -> int:
        """Get total number of topic items"""
        return sum(len(section.topic_items) for section in self.sections)
    
    @property
    def languages(self) -> List[str]:
        """Get all unique languages across the course"""
        languages = set()
        for section in self.sections:
            for item in section.code_items:
                if item.language:
                    languages.add(item.language)
        return list(languages)
    
    @property
    def topics(self) -> List[str]:
        """Get all unique topics across the course"""
        topics = set()
        for section in self.sections:
            for item in section.items:
                if item.topic:
                    topics.add(item.topic)
        return list(topics)
    
    def add_section(self, section: CourseSection):
        """Add a section to the course"""
        self.sections.append(section)
        self.__post_init__()  # Update metadata
    
    def get_section_by_name(self, name: str) -> Optional[CourseSection]:
        """Get section by name"""
        for section in self.sections:
            if section.name == name:
                return section
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'course_id': self.course_id,
            'name': self.name,
            'description': self.description,
            'sections': [section.to_dict() for section in self.sections],
            'metadata': self.metadata,
            'summary': {
                'section_count': len(self.sections),
                'total_items': self.total_items,
                'total_code_items': self.total_code_items,
                'total_topic_items': self.total_topic_items,
                'languages': self.languages,
                'topics': self.topics
            }
        }

@dataclass
class MoodleActivity:
    """Represents a Moodle activity"""
    id: Optional[int] = None
    name: str = ""
    type: str = ""  # page, resource, label, etc.
    content: str = ""
    course_id: Optional[int] = None
    section_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'content': self.content,
            'course_id': self.course_id,
            'section_id': self.section_id,
            'metadata': self.metadata
        }

# Type aliases for convenience
ContentItems = List[ContentItem]
CourseSections = List[CourseSection]
