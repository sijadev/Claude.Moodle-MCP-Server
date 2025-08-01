#!/usr/bin/env python3
"""
Context-Aware Processing System for MoodleClaude
Enhances content processing by maintaining conversation context and user preferences
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """User preferences for content processing"""
    preferred_course_format: str = "topics"  # topics, weeks, social
    default_section_names: List[str] = field(default_factory=lambda: ["Overview", "Content", "Activities", "Resources"])
    content_chunking_strategy: str = "intelligent"  # simple, intelligent, progressive
    activity_types_preference: List[str] = field(default_factory=lambda: ["page", "label", "file"])
    language_preference: str = "en"
    max_section_size: int = 10
    enable_automatic_categorization: bool = True
    include_code_examples: bool = True
    generate_summaries: bool = True


@dataclass
class ConversationTurn:
    """Single turn in conversation history"""
    timestamp: datetime = field(default_factory=datetime.now)
    user_input: str = ""
    context_type: str = "general"  # general, follow_up, clarification, error_recovery
    extracted_intent: str = ""
    content_topics: List[str] = field(default_factory=list)
    mentioned_entities: List[str] = field(default_factory=list)
    user_sentiment: str = "neutral"  # positive, negative, neutral, frustrated
    processing_outcome: str = "pending"  # success, failure, partial, pending


@dataclass
class ConversationContext:
    """Complete conversation context"""
    session_id: str
    user_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    conversation_history: deque = field(default_factory=lambda: deque(maxlen=20))
    accumulated_topics: set = field(default_factory=set)
    user_preferences: UserPreferences = field(default_factory=UserPreferences)
    current_course_context: Optional[Dict] = None
    error_recovery_attempts: int = 0
    success_count: int = 0
    total_interactions: int = 0


class ContextAwareProcessor:
    """
    Processes content with awareness of conversation context and user preferences
    """
    
    def __init__(self, max_contexts: int = 100):
        self.contexts: Dict[str, ConversationContext] = {}
        self.max_contexts = max_contexts
        self.global_statistics = {
            "total_sessions": 0,
            "successful_processes": 0,
            "failed_processes": 0,
            "most_common_topics": defaultdict(int),
            "average_session_length": 0.0
        }
        
        # Intent recognition patterns
        self.intent_patterns = {
            "create_course": ["create", "make", "build", "generate", "course"],
            "modify_course": ["modify", "change", "update", "edit", "fix"],
            "add_content": ["add", "include", "insert", "append"],
            "remove_content": ["remove", "delete", "exclude", "take out"],
            "explain": ["explain", "describe", "what is", "how does"],
            "troubleshoot": ["error", "problem", "issue", "not working", "failed"]
        }
        
        # Topic extraction keywords
        self.topic_keywords = {
            "programming": ["code", "programming", "function", "class", "variable", "algorithm"],
            "mathematics": ["math", "equation", "formula", "calculate", "number", "algebra"],
            "science": ["experiment", "theory", "hypothesis", "research", "data", "analysis"],
            "language": ["grammar", "vocabulary", "writing", "literature", "essay", "text"],
            "business": ["management", "strategy", "marketing", "finance", "business", "company"],
            "technology": ["computer", "software", "hardware", "internet", "digital", "tech"]
        }
    
    def get_or_create_context(self, session_id: str, user_id: Optional[str] = None) -> ConversationContext:
        """Get existing context or create new one"""
        if session_id not in self.contexts:
            # Clean up old contexts if at limit
            if len(self.contexts) >= self.max_contexts:
                self._cleanup_old_contexts()
            
            self.contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id
            )
            self.global_statistics["total_sessions"] += 1
        
        # Update last activity
        self.contexts[session_id].last_activity = datetime.now()
        return self.contexts[session_id]
    
    def _cleanup_old_contexts(self):
        """Remove oldest contexts when limit is reached"""
        # Sort by last activity and remove oldest 25%
        sorted_contexts = sorted(
            self.contexts.items(),
            key=lambda x: x[1].last_activity
        )
        
        contexts_to_remove = len(sorted_contexts) // 4
        for session_id, _ in sorted_contexts[:contexts_to_remove]:
            del self.contexts[session_id]
        
        logger.info(f"Cleaned up {contexts_to_remove} old conversation contexts")
    
    def extract_intent(self, user_input: str) -> str:
        """Extract user intent from input"""
        user_input_lower = user_input.lower()
        
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return "general"
        
        # Return highest scoring intent
        return max(intent_scores, key=intent_scores.get)
    
    def extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        content_lower = content.lower()
        detected_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches >= 2:  # Require at least 2 keyword matches
                detected_topics.append(topic)
        
        return detected_topics
    
    def extract_entities(self, content: str) -> List[str]:
        """Extract mentioned entities (simplified implementation)"""
        entities = []
        
        # Simple entity extraction - in real implementation, use NLP library
        words = content.split()
        for i, word in enumerate(words):
            # Capitalized words that aren't at sentence start
            if (word[0].isupper() and i > 0 and 
                words[i-1][-1] not in '.!?' and
                len(word) > 2 and word.isalpha()):
                entities.append(word)
        
        return list(set(entities))  # Remove duplicates
    
    def detect_sentiment(self, user_input: str) -> str:
        """Detect user sentiment (simplified)"""
        positive_words = ["good", "great", "excellent", "perfect", "amazing", "love", "like"]
        negative_words = ["bad", "terrible", "awful", "hate", "frustrated", "annoying", "failed"]
        
        user_input_lower = user_input.lower()
        
        positive_count = sum(1 for word in positive_words if word in user_input_lower)
        negative_count = sum(1 for word in negative_words if word in user_input_lower)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    def add_conversation_turn(self, session_id: str, user_input: str, 
                            processing_outcome: str = "pending") -> ConversationTurn:
        """Add a new conversation turn"""
        context = self.get_or_create_context(session_id)
        
        # Extract information from user input
        intent = self.extract_intent(user_input)
        topics = self.extract_topics(user_input)
        entities = self.extract_entities(user_input)
        sentiment = self.detect_sentiment(user_input)
        
        # Determine context type based on conversation history
        context_type = self._determine_context_type(context, intent, sentiment)
        
        turn = ConversationTurn(
            user_input=user_input,
            context_type=context_type,
            extracted_intent=intent,
            content_topics=topics,
            mentioned_entities=entities,
            user_sentiment=sentiment,
            processing_outcome=processing_outcome
        )
        
        # Add to context
        context.conversation_history.append(turn)
        context.accumulated_topics.update(topics)
        context.total_interactions += 1
        
        # Update global statistics
        for topic in topics:
            self.global_statistics["most_common_topics"][topic] += 1
        
        return turn
    
    def _determine_context_type(self, context: ConversationContext, 
                              intent: str, sentiment: str) -> str:
        """Determine the type of context for this turn"""
        if not context.conversation_history:
            return "general"
        
        last_turn = context.conversation_history[-1]
        
        # Error recovery context
        if (last_turn.processing_outcome == "failure" or 
            sentiment == "negative" or
            intent == "troubleshoot"):
            return "error_recovery"
        
        # Follow-up context
        if (intent == last_turn.extracted_intent or
            any(topic in context.accumulated_topics for topic in 
                getattr(last_turn, 'content_topics', []))):
            return "follow_up"
        
        # Clarification context
        if intent == "explain" or len(context.conversation_history) > 1:
            return "clarification"
        
        return "general"
    
    def get_contextual_suggestions(self, session_id: str) -> Dict[str, Any]:
        """Get contextual suggestions based on conversation history"""
        context = self.contexts.get(session_id)
        if not context:
            return {"suggestions": [], "reasoning": "No context available"}
        
        suggestions = []
        reasoning = []
        
        # Recent error recovery suggestions
        recent_failures = [
            turn for turn in list(context.conversation_history)[-5:]
            if turn.processing_outcome == "failure"
        ]
        
        if recent_failures:
            suggestions.append("Try breaking down your content into smaller chunks")
            suggestions.append("Check if all required information is provided")
            reasoning.append("Detected recent processing failures")
        
        # Topic-based suggestions
        if context.accumulated_topics:
            most_common_topic = max(
                context.accumulated_topics,
                key=lambda t: self.global_statistics["most_common_topics"][t]
            )
            suggestions.append(f"Consider organizing content around {most_common_topic}")
            reasoning.append(f"User frequently discusses {most_common_topic}")
        
        # Preference-based suggestions
        prefs = context.user_preferences
        if prefs.generate_summaries:
            suggestions.append("Add section summaries for better organization")
        
        if prefs.include_code_examples and "programming" in context.accumulated_topics:
            suggestions.append("Include practical code examples in activities")
        
        return {
            "suggestions": suggestions[:3],  # Top 3 suggestions
            "reasoning": reasoning,
            "context_quality": self._assess_context_quality(context)
        }
    
    def _assess_context_quality(self, context: ConversationContext) -> str:
        """Assess the quality of context information"""
        score = 0
        
        # Conversation length
        if len(context.conversation_history) >= 3:
            score += 2
        elif len(context.conversation_history) >= 1:
            score += 1
        
        # Topic diversity
        if len(context.accumulated_topics) >= 3:
            score += 2
        elif len(context.accumulated_topics) >= 1:
            score += 1
        
        # Success rate
        if context.total_interactions > 0:
            success_rate = context.success_count / context.total_interactions
            if success_rate >= 0.8:
                score += 2
            elif success_rate >= 0.5:
                score += 1
        
        # Recent activity
        if (datetime.now() - context.last_activity).seconds < 300:  # 5 minutes
            score += 1
        
        if score >= 6:
            return "excellent"
        elif score >= 4:
            return "good"
        elif score >= 2:
            return "fair"
        else:
            return "poor"
    
    def update_processing_outcome(self, session_id: str, outcome: str):
        """Update the outcome of the last processing attempt"""
        context = self.contexts.get(session_id)
        if not context or not context.conversation_history:
            return
        
        last_turn = context.conversation_history[-1]
        last_turn.processing_outcome = outcome
        
        # Update context statistics
        if outcome == "success":
            context.success_count += 1
            self.global_statistics["successful_processes"] += 1
        elif outcome == "failure":
            context.error_recovery_attempts += 1
            self.global_statistics["failed_processes"] += 1
    
    def get_adaptive_processing_strategy(self, session_id: str, content: str) -> Dict[str, Any]:
        """Get adaptive processing strategy based on context"""
        context = self.contexts.get(session_id)
        
        strategy = {
            "chunking_method": "intelligent",
            "max_chunk_size": 5000,
            "include_summaries": True,
            "activity_types": ["page", "label"],
            "processing_priority": "balanced",  # speed, quality, balanced
            "error_tolerance": "medium"  # low, medium, high
        }
        
        if not context:
            return strategy
        
        # Adjust based on user preferences
        prefs = context.user_preferences
        strategy["chunking_method"] = prefs.content_chunking_strategy
        strategy["include_summaries"] = prefs.generate_summaries
        strategy["activity_types"] = prefs.activity_types_preference
        
        # Adjust based on conversation history
        if context.error_recovery_attempts > 2:
            # User has had multiple failures - be more conservative
            strategy["max_chunk_size"] = 2000
            strategy["processing_priority"] = "quality"
            strategy["error_tolerance"] = "high"
        
        # Adjust based on content complexity
        content_length = len(content)
        content_topics = self.extract_topics(content)
        
        if content_length > 10000 or len(content_topics) > 3:
            strategy["chunking_method"] = "progressive"
            strategy["processing_priority"] = "balanced"
        
        # Recent success pattern
        recent_successes = [
            turn for turn in list(context.conversation_history)[-3:]
            if turn.processing_outcome == "success"
        ]
        
        if len(recent_successes) >= 2:
            # User is having success - can be more aggressive
            strategy["max_chunk_size"] = 7000
            strategy["processing_priority"] = "speed"
        
        return strategy
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation context"""
        context = self.contexts.get(session_id)
        if not context:
            return {"error": "Context not found"}
        
        session_duration = datetime.now() - context.start_time
        
        return {
            "session_id": session_id,
            "session_duration_minutes": session_duration.total_seconds() / 60,
            "total_interactions": context.total_interactions,
            "success_count": context.success_count,
            "success_rate": context.success_count / max(context.total_interactions, 1),
            "accumulated_topics": list(context.accumulated_topics),
            "error_recovery_attempts": context.error_recovery_attempts,
            "last_activity": context.last_activity.isoformat(),
            "context_quality": self._assess_context_quality(context),
            "user_preferences": {
                "course_format": context.user_preferences.preferred_course_format,
                "chunking_strategy": context.user_preferences.content_chunking_strategy,
                "generate_summaries": context.user_preferences.generate_summaries
            }
        }
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global processing statistics"""
        total_processes = (self.global_statistics["successful_processes"] + 
                          self.global_statistics["failed_processes"])
        
        return {
            "total_sessions": self.global_statistics["total_sessions"],
            "active_sessions": len(self.contexts),
            "total_processes": total_processes,
            "success_rate": (self.global_statistics["successful_processes"] / 
                           max(total_processes, 1) * 100),
            "most_common_topics": dict(
                sorted(self.global_statistics["most_common_topics"].items(),
                      key=lambda x: x[1], reverse=True)[:5]
            ),
            "context_quality_distribution": self._get_context_quality_distribution()
        }
    
    def _get_context_quality_distribution(self) -> Dict[str, int]:
        """Get distribution of context qualities"""
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for context in self.contexts.values():
            quality = self._assess_context_quality(context)
            distribution[quality] += 1
        
        return distribution


# Example usage and testing
if __name__ == "__main__":
    processor = ContextAwareProcessor()
    
    # Simulate a conversation
    session_id = "test_session_123"
    
    # User starts with course creation
    processor.add_conversation_turn(
        session_id,
        "I want to create a course about Python programming with code examples",
        "success"
    )
    
    # Follow-up question
    processor.add_conversation_turn(
        session_id,
        "Can you add more advanced topics like decorators and generators?",
        "success"
    )
    
    # User has an issue
    processor.add_conversation_turn(
        session_id,
        "The course creation failed, what went wrong?",
        "failure"
    )
    
    # Get contextual suggestions
    suggestions = processor.get_contextual_suggestions(session_id)
    print("Contextual Suggestions:")
    print(json.dumps(suggestions, indent=2))
    
    # Get adaptive strategy
    strategy = processor.get_adaptive_processing_strategy(
        session_id,
        "Here's a long piece of content about advanced Python programming..."
    )
    print("\nAdaptive Processing Strategy:")
    print(json.dumps(strategy, indent=2))
    
    # Get context summary
    summary = processor.get_context_summary(session_id)
    print("\nContext Summary:")
    print(json.dumps(summary, indent=2, default=str))