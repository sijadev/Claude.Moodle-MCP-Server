"""
Adaptive Content Processor for Intelligent Course Creation
Automatically detects content limits, adapts chunking strategies, and manages session state
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from src.models.models import ChatContent, CourseStructure
from src.core.content_chunker import ContentChunker
from src.core.content_parser import ChatContentParser

logger = logging.getLogger(__name__)

class ProcessingStrategy(Enum):
    """Content processing strategies based on content analysis"""
    SINGLE_PASS = "single_pass"        # Content fits in one request
    INTELLIGENT_CHUNK = "intelligent_chunk"  # Smart sectioning based on content
    PROGRESSIVE_BUILD = "progressive_build"  # Build course incrementally
    ADAPTIVE_RETRY = "adaptive_retry"   # Adjust limits based on failures

class SessionState(Enum):
    """Session processing states"""
    INITIALIZED = "initialized"
    ANALYZING = "analyzing"
    CHUNKING = "chunking"
    PROCESSING = "processing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class ContentLimits:
    """Adaptive content limits based on runtime detection"""
    max_char_length: int = 8000
    max_sections: int = 10
    max_items_per_section: int = 15
    max_code_blocks: int = 20
    max_topics: int = 25
    confidence_level: float = 0.8  # How confident we are in these limits
    
    def adjust_limits(self, success_rate: float, content_size: int):
        """Dynamically adjust limits based on success rate"""
        if success_rate > 0.9 and content_size > self.max_char_length:
            # Increase limits if we're succeeding with larger content
            self.max_char_length = min(int(self.max_char_length * 1.2), 15000)
            self.max_sections = min(int(self.max_sections * 1.1), 20)
        elif success_rate < 0.6:
            # Decrease limits if we're failing
            self.max_char_length = max(int(self.max_char_length * 0.8), 4000)
            self.max_sections = max(int(self.max_sections * 0.9), 5)
        
        # Update confidence based on data points
        self.confidence_level = min(0.95, self.confidence_level + 0.05)

@dataclass
class ProcessingSession:
    """Manages state for a course creation session"""
    session_id: str
    content_hash: str
    original_content: str
    strategy: ProcessingStrategy
    state: SessionState = SessionState.INITIALIZED
    
    # Progress tracking
    total_chunks: int = 0
    processed_chunks: int = 0
    current_chunk_index: int = 0
    
    # Course creation state
    course_id: Optional[int] = None
    course_name: str = ""
    created_sections: List[Dict[str, Any]] = field(default_factory=list)
    
    # Error tracking and retry logic
    error_count: int = 0
    last_error: Optional[str] = None
    retry_attempts: int = 0
    max_retries: int = 3
    
    # Session metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=2))
    
    # Continuation logic
    needs_continuation: bool = False
    continuation_prompt: str = ""
    next_chunk_hint: str = ""
    
    def update_progress(self, chunk_index: int, success: bool = True):
        """Update session progress"""
        self.current_chunk_index = chunk_index
        if success:
            self.processed_chunks += 1
            self.error_count = 0  # Reset error count on success
        else:
            self.error_count += 1
        
        self.updated_at = datetime.now()
        
        # Check if session needs continuation
        if self.processed_chunks < self.total_chunks:
            self.needs_continuation = True
            self._generate_continuation_prompt()
    
    def _generate_continuation_prompt(self):
        """Generate natural continuation prompt for Claude Desktop"""
        progress_percent = (self.processed_chunks / self.total_chunks) * 100
        
        if progress_percent < 25:
            self.continuation_prompt = f"Great start! I've processed the first section. Please continue with the next part of the content to build upon what we've created so far."
        elif progress_percent < 50:
            self.continuation_prompt = f"Excellent progress! We're about {progress_percent:.0f}% complete. Please provide the next section to continue building your course."
        elif progress_percent < 75:
            self.continuation_prompt = f"We're making great progress! About {progress_percent:.0f}% complete. Please share the next portion of content."
        else:
            self.continuation_prompt = f"Almost there! We're {progress_percent:.0f}% complete. Please provide the final sections to complete your course."
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.now() > self.expires_at
    
    def can_retry(self) -> bool:
        """Check if we can retry after an error"""
        return self.retry_attempts < self.max_retries and self.error_count < 5


class AdaptiveContentProcessor:
    """
    Intelligent content processor that adapts to Claude Desktop limitations
    and provides seamless user experience for course creation
    """
    
    def __init__(self):
        """Initialize the adaptive processor"""
        self.content_parser = ChatContentParser()
        self.content_chunker = ContentChunker()
        self.content_limits = ContentLimits()
        
        # Session management
        self.active_sessions: Dict[str, ProcessingSession] = {}
        self.session_cleanup_interval = 3600  # 1 hour
        
        # Learning system for adaptive limits
        self.processing_history: List[Dict[str, Any]] = []
        self.success_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_content_size': 0
        }
        
        logger.info("AdaptiveContentProcessor initialized with adaptive learning")
    
    async def analyze_content_complexity(self, content: str) -> Dict[str, Any]:
        """
        Analyze content to determine optimal processing strategy
        
        Args:
            content: The chat content to analyze
            
        Returns:
            Dictionary with analysis results and recommended strategy
        """
        analysis = {
            'content_length': len(content),
            'estimated_sections': 0,
            'code_blocks': 0,
            'topics': 0,
            'complexity_score': 0.0,
            'recommended_strategy': ProcessingStrategy.SINGLE_PASS,
            'estimated_chunks': 1,
            'processing_time_estimate': 30  # seconds
        }
        
        try:
            # Parse content to get structure
            parsed_content = self.content_parser.parse_chat(content)
            
            # Count different content types
            code_items = [item for item in parsed_content.items if item.type == 'code']
            topic_items = [item for item in parsed_content.items if item.type == 'topic']
            
            analysis['code_blocks'] = len(code_items)
            analysis['topics'] = len(topic_items)
            analysis['estimated_sections'] = max(1, (len(parsed_content.items) + 4) // 5)  # ~5 items per section
            
            # Calculate complexity score (0.0 = simple, 1.0 = very complex)
            length_factor = min(1.0, analysis['content_length'] / 15000)
            structure_factor = min(1.0, analysis['estimated_sections'] / 20)
            code_factor = min(1.0, analysis['code_blocks'] / 30)
            topic_factor = min(1.0, analysis['topics'] / 40)
            
            analysis['complexity_score'] = (length_factor + structure_factor + code_factor + topic_factor) / 4
            
            # Determine strategy based on analysis
            if analysis['content_length'] <= self.content_limits.max_char_length and analysis['complexity_score'] < 0.3:
                analysis['recommended_strategy'] = ProcessingStrategy.SINGLE_PASS
                analysis['estimated_chunks'] = 1
            elif analysis['complexity_score'] < 0.6:
                analysis['recommended_strategy'] = ProcessingStrategy.INTELLIGENT_CHUNK
                analysis['estimated_chunks'] = max(2, analysis['estimated_sections'] // 3)
            elif analysis['complexity_score'] < 0.8:
                analysis['recommended_strategy'] = ProcessingStrategy.PROGRESSIVE_BUILD
                analysis['estimated_chunks'] = analysis['estimated_sections']
            else:
                analysis['recommended_strategy'] = ProcessingStrategy.ADAPTIVE_RETRY
                analysis['estimated_chunks'] = analysis['estimated_sections'] + 2
            
            # Estimate processing time
            base_time = 30
            complexity_multiplier = 1 + (analysis['complexity_score'] * 2)
            chunk_multiplier = 1 + (analysis['estimated_chunks'] * 0.5)
            analysis['processing_time_estimate'] = int(base_time * complexity_multiplier * chunk_multiplier)
            
            logger.info(f"Content analysis: {analysis['content_length']} chars, "
                       f"complexity: {analysis['complexity_score']:.2f}, "
                       f"strategy: {analysis['recommended_strategy'].value}")
            
        except Exception as e:
            logger.error(f"Error in content analysis: {e}")
            # Fallback to safe defaults
            if analysis['content_length'] > self.content_limits.max_char_length:
                analysis['recommended_strategy'] = ProcessingStrategy.INTELLIGENT_CHUNK
                analysis['estimated_chunks'] = 3
        
        return analysis
    
    def _analyze_content_complexity_sync(self, content: str) -> Dict[str, Any]:
        """
        Synchronous fallback for content analysis when async is not available
        """
        analysis = {
            'content_length': len(content),
            'estimated_sections': 0,
            'code_blocks': 0,
            'topics': 0,
            'complexity_score': 0.0,
            'recommended_strategy': ProcessingStrategy.SINGLE_PASS,
            'estimated_chunks': 1,
            'processing_time_estimate': 30
        }
        
        try:
            # Simple regex-based analysis for fallback
            import re
            
            # Count code blocks
            code_blocks = len(re.findall(r'```[\s\S]*?```', content))
            analysis['code_blocks'] = code_blocks
            
            # Count sections (lines starting with # or ##)
            sections = len(re.findall(r'^#+\s+', content, re.MULTILINE))
            analysis['estimated_sections'] = sections
            
            # Estimate topics based on structure
            analysis['topics'] = max(sections, len(re.findall(r'\*\*[^*]+\*\*', content)))
            
            # Calculate complexity score
            length_factor = min(analysis['content_length'] / 10000, 1.0)
            structure_factor = min((analysis['estimated_sections'] + analysis['code_blocks']) / 20, 1.0)
            analysis['complexity_score'] = (length_factor + structure_factor) / 2
            
            # Determine strategy
            if analysis['content_length'] > self.content_limits.max_char_length:
                analysis['recommended_strategy'] = ProcessingStrategy.INTELLIGENT_CHUNK
                analysis['estimated_chunks'] = max(2, analysis['content_length'] // self.content_limits.max_char_length + 1)
            elif analysis['complexity_score'] > 0.4:
                analysis['recommended_strategy'] = ProcessingStrategy.INTELLIGENT_CHUNK
                analysis['estimated_chunks'] = 2
                
            logger.info(f"Sync content analysis: {analysis['content_length']} chars, "
                       f"complexity: {analysis['complexity_score']:.2f}, "
                       f"strategy: {analysis['recommended_strategy'].value}")
                       
        except Exception as e:
            logger.error(f"Error in sync content analysis: {e}")
            # Ultra-safe fallback
            if analysis['content_length'] > 8000:
                analysis['recommended_strategy'] = ProcessingStrategy.INTELLIGENT_CHUNK
                analysis['estimated_chunks'] = 3
                
        return analysis
    
    def create_session(self, content: str, course_name: str = "") -> str:
        """
        Create a new processing session
        
        Args:
            content: The content to process
            course_name: Name for the course
            
        Returns:
            Session ID for tracking
        """
        # Generate session ID and content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()
        session_id = f"session_{content_hash[:8]}_{int(datetime.now().timestamp())}"
        
        # Check if we already have a session for this content
        existing_session = self._find_existing_session(content_hash)
        if existing_session and not existing_session.is_expired():
            logger.info(f"Resuming existing session: {existing_session.session_id}")
            return existing_session.session_id
        
        # Analyze content to determine strategy
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an event loop, use create_task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.analyze_content_complexity(content))
                    analysis = future.result()
            else:
                analysis = asyncio.run(self.analyze_content_complexity(content))
        except RuntimeError:
            # Fallback: run synchronously
            analysis = self._analyze_content_complexity_sync(content)
        
        # Create new session
        session = ProcessingSession(
            session_id=session_id,
            content_hash=content_hash,
            original_content=content,
            strategy=analysis['recommended_strategy'],
            total_chunks=analysis['estimated_chunks'],
            course_name=course_name or f"Course from Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Created session {session_id} with strategy {session.strategy.value}")
        return session_id
    
    def _find_existing_session(self, content_hash: str) -> Optional[ProcessingSession]:
        """Find existing session by content hash"""
        for session in self.active_sessions.values():
            if session.content_hash == content_hash and not session.is_expired():
                return session
        return None
    
    async def process_content_chunk(self, session_id: str, chunk_index: int = 0, 
                                   continue_previous: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        Process a specific chunk of content within a session
        
        Args:
            session_id: The session to process
            chunk_index: Which chunk to process (0-based)
            continue_previous: Whether this continues a previous session
            
        Returns:
            Tuple of (success, result_data)
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return False, {"error": "Session not found", "action": "create_new_session"}
        
        if session.is_expired():
            return False, {"error": "Session expired", "action": "create_new_session"}
        
        try:
            session.state = SessionState.PROCESSING
            
            # Determine content to process based on strategy
            content_chunk = await self._get_content_chunk(session, chunk_index)
            
            if not content_chunk:
                return False, {"error": "No content to process"}
            
            # Parse and structure the chunk
            session.state = SessionState.ANALYZING
            parsed_content = self.content_parser.parse_chat(content_chunk)
            
            # Create course structure from parsed content
            course_structure = self._create_course_structure(parsed_content, session)
            
            # Update session progress
            session.update_progress(chunk_index, success=True)
            
            # Generate response based on session state
            response_data = await self._generate_intelligent_response(session, course_structure)
            
            # Update learning metrics
            self._update_success_metrics(len(content_chunk), True)
            
            return True, response_data
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_index} in session {session_id}: {e}")
            session.update_progress(chunk_index, success=False)
            session.last_error = str(e)
            
            # Update learning metrics
            self._update_success_metrics(len(session.original_content), False)
            
            # Determine if we should retry or adapt strategy
            if session.can_retry():
                return await self._handle_retry_logic(session, chunk_index, str(e))
            else:
                session.state = SessionState.FAILED
                return False, {
                    "error": str(e),
                    "action": "manual_intervention_required",
                    "session_id": session_id
                }
    
    async def _get_content_chunk(self, session: ProcessingSession, chunk_index: int) -> str:
        """Get the appropriate content chunk based on session strategy"""
        if session.strategy == ProcessingStrategy.SINGLE_PASS:
            return session.original_content
        
        # Parse content and create logical chunks
        parsed_content = self.content_parser.parse_chat(session.original_content)
        
        if session.strategy == ProcessingStrategy.INTELLIGENT_CHUNK:
            chunks = self._create_intelligent_chunks(parsed_content)
        elif session.strategy == ProcessingStrategy.PROGRESSIVE_BUILD:
            chunks = self._create_progressive_chunks(parsed_content)
        else:  # ADAPTIVE_RETRY
            chunks = self._create_adaptive_chunks(parsed_content)
        
        if chunk_index < len(chunks):
            return chunks[chunk_index]
        
        return ""
    
    def _create_intelligent_chunks(self, parsed_content: ChatContent) -> List[str]:
        """Create intelligent chunks based on content structure"""
        chunks = []
        current_chunk = []
        current_length = 0
        max_chunk_length = int(self.content_limits.max_char_length * 0.8)  # Safety margin
        
        for item in parsed_content.items:
            item_length = len(item.content)
            
            # If adding this item would exceed limit, start new chunk
            if current_length + item_length > max_chunk_length and current_chunk:
                chunks.append(self._reconstruct_chunk_content(current_chunk))
                current_chunk = [item]
                current_length = item_length
            else:
                current_chunk.append(item)
                current_length += item_length
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._reconstruct_chunk_content(current_chunk))
        
        return chunks
    
    def _create_progressive_chunks(self, parsed_content: ChatContent) -> List[str]:
        """Create progressive chunks for incremental course building"""
        # Group by logical sections/topics
        sections = {}
        for item in parsed_content.items:
            # Use first few words as section key
            section_key = " ".join(item.title.split()[:3]) if item.title else "general"
            if section_key not in sections:
                sections[section_key] = []
            sections[section_key].append(item)
        
        # Create chunks from sections
        chunks = []
        for section_name, items in sections.items():
            chunk_content = self._reconstruct_chunk_content(items)
            chunks.append(chunk_content)
        
        return chunks
    
    def _create_adaptive_chunks(self, parsed_content: ChatContent) -> List[str]:
        """Create adaptive chunks that adjust based on previous success/failure"""
        # Start with smaller chunks and adjust based on success rate
        chunk_size = max(2, int(self.content_limits.max_sections * 0.6))
        
        chunks = []
        for i in range(0, len(parsed_content.items), chunk_size):
            chunk_items = parsed_content.items[i:i + chunk_size]
            chunk_content = self._reconstruct_chunk_content(chunk_items)
            chunks.append(chunk_content)
        
        return chunks
    
    def _reconstruct_chunk_content(self, items) -> str:
        """Reconstruct chat-style content from content items"""
        reconstructed = []
        
        for item in items:
            if item.type == 'code':
                reconstructed.append(f"Here's a {item.language} code example:")
                reconstructed.append(f"```{item.language}")
                reconstructed.append(item.content)
                reconstructed.append("```")
                if item.description:
                    reconstructed.append(item.description)
            elif item.type == 'topic':
                reconstructed.append(f"## {item.title}")
                reconstructed.append(item.content)
            
            reconstructed.append("")  # Add spacing
        
        return "\n".join(reconstructed)
    
    def _create_course_structure(self, parsed_content: ChatContent, session: ProcessingSession) -> CourseStructure:
        """Create course structure from parsed content"""
        sections = []
        
        # Group items into sections
        current_section_items = []
        for item in parsed_content.items:
            current_section_items.append(item)
            
            # Create section when we have enough items or reach a natural break
            if len(current_section_items) >= self.content_limits.max_items_per_section:
                section_name = f"Section {len(sections) + 1}"
                section = CourseStructure.Section(
                    name=section_name,
                    description=f"Learning materials for {section_name.lower()}",
                    items=current_section_items.copy()
                )
                sections.append(section)
                current_section_items = []
        
        # Add remaining items as final section
        if current_section_items:
            section_name = f"Section {len(sections) + 1}"
            section = CourseStructure.Section(
                name=section_name,
                description=f"Learning materials for {section_name.lower()}",
                items=current_section_items
            )
            sections.append(section)
        
        return CourseStructure(sections=sections)
    
    async def _generate_intelligent_response(self, session: ProcessingSession, 
                                           course_structure: CourseStructure) -> Dict[str, Any]:
        """Generate intelligent response based on session state and progress"""
        response = {
            "session_id": session.session_id,
            "progress": {
                "completed_chunks": session.processed_chunks,
                "total_chunks": session.total_chunks,
                "percentage": (session.processed_chunks / session.total_chunks) * 100
            },
            "course_structure": course_structure,
            "continuation_needed": session.needs_continuation,
        }
        
        if session.needs_continuation:
            response["continuation_prompt"] = session.continuation_prompt
            response["user_message"] = self._generate_user_friendly_continuation()
        else:
            session.state = SessionState.COMPLETED
            response["user_message"] = f"✅ Course creation completed! Created {len(course_structure.sections)} sections with your content."
            response["final_summary"] = {
                "total_sections": len(course_structure.sections),
                "total_items": sum(len(section.items) for section in course_structure.sections),
                "processing_time": (datetime.now() - session.created_at).total_seconds()
            }
        
        return response
    
    def _generate_user_friendly_continuation(self) -> str:
        """Generate user-friendly message that naturally prompts for continuation"""
        messages = [
            "Perfect! I've processed that section. Please share the next part of your content when you're ready.",
            "Great progress! Ready for the next section of content to continue building your course.",
            "Excellent! I've got that part handled. Please continue with more content when you'd like.",
            "Nice work! I'm ready to process the next portion of your material.",
        ]
        
        import random
        return random.choice(messages)
    
    async def _handle_retry_logic(self, session: ProcessingSession, chunk_index: int, 
                                error: str) -> Tuple[bool, Dict[str, Any]]:
        """Handle intelligent retry logic when processing fails"""
        session.retry_attempts += 1
        
        # Adapt strategy based on error type
        if "too large" in error.lower() or "limit" in error.lower():
            # Content too large - adjust limits and retry with smaller chunks
            self.content_limits.adjust_limits(0.3, len(session.original_content))
            session.strategy = ProcessingStrategy.ADAPTIVE_RETRY
            
            return False, {
                "error": "Content too large, adapting strategy",
                "action": "retry_with_smaller_chunks",
                "session_id": session.session_id,
                "retry_message": "I'm adjusting my approach to handle this content better. Let me try with smaller sections."
            }
        
        elif "timeout" in error.lower():
            # Timeout - suggest breaking up content
            return False, {
                "error": "Processing timeout",
                "action": "break_into_smaller_parts",
                "session_id": session.session_id,
                "retry_message": "This content is quite complex. Try sharing it in smaller parts for better processing."
            }
        
        else:
            # Generic error - provide helpful guidance
            return False, {
                "error": error,
                "action": "manual_review_needed",
                "session_id": session.session_id,
                "retry_message": "I encountered an issue processing this content. Please try rephrasing or breaking it into smaller sections."
            }
    
    def _update_success_metrics(self, content_size: int, success: bool):
        """Update learning metrics for adaptive behavior"""
        self.success_metrics['total_requests'] += 1
        
        if success:
            self.success_metrics['successful_requests'] += 1
        else:
            self.success_metrics['failed_requests'] += 1
        
        # Update running average of content size
        current_avg = self.success_metrics['average_content_size']
        total_requests = self.success_metrics['total_requests']
        self.success_metrics['average_content_size'] = (
            (current_avg * (total_requests - 1) + content_size) / total_requests
        )
        
        # Adapt limits based on success rate
        success_rate = self.success_metrics['successful_requests'] / self.success_metrics['total_requests']
        self.content_limits.adjust_limits(success_rate, content_size)
        
        # Log metrics periodically
        if self.success_metrics['total_requests'] % 10 == 0:
            logger.info(f"Success rate: {success_rate:.2f}, "
                       f"Avg content size: {self.success_metrics['average_content_size']:.0f}, "
                       f"Current limits: {self.content_limits.max_char_length} chars")
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a processing session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "state": session.state.value,
            "progress": {
                "completed_chunks": session.processed_chunks,
                "total_chunks": session.total_chunks,
                "percentage": (session.processed_chunks / session.total_chunks) * 100 if session.total_chunks > 0 else 0
            },
            "course_id": session.course_id,
            "course_name": session.course_name,
            "created_sections_count": len(session.created_sections),
            "needs_continuation": session.needs_continuation,
            "continuation_prompt": session.continuation_prompt if session.needs_continuation else None,
            "error_count": session.error_count,
            "last_error": session.last_error,
            "expires_at": session.expires_at.isoformat(),
            "strategy": session.strategy.value
        }
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get current processing metrics and adaptive learning status"""
        active_session_count = len([s for s in self.active_sessions.values() if not s.is_expired()])
        
        return {
            "success_metrics": self.success_metrics.copy(),
            "current_limits": {
                "max_char_length": self.content_limits.max_char_length,
                "max_sections": self.content_limits.max_sections,
                "confidence_level": self.content_limits.confidence_level
            },
            "active_sessions": active_session_count,
            "total_sessions_created": len(self.active_sessions),
            "learning_status": "adaptive" if self.content_limits.confidence_level > 0.8 else "learning"
        }