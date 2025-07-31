#!/usr/bin/env python3
"""
Refactored Service Layer for MoodleClaude
Breaks down the god object pattern into focused, single-responsibility services
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from .interfaces import (
    ICourseCreationService, IAnalyticsService, IMoodleClient, IContentProcessor,
    ISessionRepository, IEventPublisher, SessionEventType
)
from .dependency_injection import service, ServiceLifetime
from .command_system import (
    CommandExecutor, CreateCourseCommand, CreateCourseStructureCommand,
    ProcessContentCommand, ValidateCourseCommand, CommandContext
)
from .event_system import (
    publish_session_created, publish_processing_started, publish_course_created,
    publish_session_completed, publish_session_failed
)

logger = logging.getLogger(__name__)


@service(ICourseCreationService, ServiceLifetime.SINGLETON)
class CourseCreationService(ICourseCreationService):
    """
    High-level service for orchestrating course creation
    
    Responsibilities:
    - Coordinate between content processor, Moodle client, and repository
    - Manage session lifecycle
    - Publish events
    - Handle errors and recovery
    """
    
    def __init__(
        self,
        content_processor: IContentProcessor,
        moodle_client: IMoodleClient,
        session_repository: ISessionRepository,
        event_publisher: IEventPublisher
    ):
        self.content_processor = content_processor
        self.moodle_client = moodle_client
        self.session_repository = session_repository
        self.event_publisher = event_publisher
        self.command_executor = CommandExecutor(event_publisher)
    
    async def create_course_from_content(
        self, 
        content: str, 
        course_name: str, 
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a complete course from chat content
        
        Args:
            content: Chat content to process
            course_name: Name for the course
            options: Additional options (category_id, description, etc.)
        """
        session_id = str(uuid.uuid4())
        context = CommandContext(session_id, options.get("user_id"))
        
        try:
            # Analyze content complexity
            complexity_analysis = await self.content_processor.analyze_content_complexity(content)
            
            # Create initial session data
            session_data = {
                "session_id": session_id,
                "content": content,
                "course_name": course_name,
                "state": "created",
                "strategy": complexity_analysis.get("recommended_strategy", "single_pass"),
                "progress": {"percentage": 0, "completed_chunks": 0, "total_chunks": 1},
                "options": options,
                "complexity_analysis": complexity_analysis,
                "created_at": datetime.now().isoformat()
            }
            
            # Save initial session
            await self.session_repository.save(session_data)
            
            # Publish session created event
            await publish_session_created(self.event_publisher, session_id, {
                "course_name": course_name,
                "content_length": len(content),
                "strategy": session_data["strategy"],
                "complexity_score": complexity_analysis.get("complexity_score", 0)
            })
            
            # Start processing
            await publish_processing_started(self.event_publisher, session_id, {
                "processing_strategy": session_data["strategy"]
            })
            
            # Execute processing pipeline
            commands = [
                ProcessContentCommand(context, self.content_processor, content),
                CreateCourseCommand(context, self.moodle_client, course_name, options.get("description", "")),
            ]
            
            results = await self.command_executor.execute_commands(commands, session_data)
            
            # Check if all commands succeeded
            if all(result.success for result in results):
                # Get course ID from create course command result
                course_id = None
                for result in results:
                    if "course_id" in result.data:
                        course_id = result.data["course_id"]
                        break
                
                if course_id:
                    # Create course structure
                    course_structure_data = await self._build_course_structure_data(session_id)
                    if course_structure_data:
                        structure_command = CreateCourseStructureCommand(
                            context, self.moodle_client, course_id, course_structure_data
                        )
                        structure_result = await self.command_executor.execute_command(structure_command, session_data)
                        
                        if structure_result.success:
                            # Update session with success
                            await self.session_repository.update_session_state(
                                session_id, "completed", 
                                {
                                    "course_id": course_id,
                                    "progress": {"percentage": 100, "completed_chunks": 1, "total_chunks": 1}
                                }
                            )
                            
                            # Publish events
                            await publish_course_created(self.event_publisher, session_id, {
                                "course_id": course_id,
                                "course_name": course_name
                            })
                            
                            await publish_session_completed(self.event_publisher, session_id, {
                                "course_id": course_id,
                                "processing_time": (datetime.now() - datetime.fromisoformat(session_data["created_at"])).total_seconds()
                            })
                            
                            return {
                                "success": True,
                                "session_id": session_id,
                                "course_id": course_id,
                                "course_name": course_name,
                                "message": "Course created successfully"
                            }
            
            # If we get here, something failed
            await self._handle_creation_failure(session_id, results)
            
            return {
                "success": False,
                "session_id": session_id,
                "message": "Course creation failed",
                "errors": [result.message for result in results if not result.success]
            }
        
        except Exception as e:
            logger.error(f"Course creation failed for session {session_id}: {e}")
            await publish_session_failed(self.event_publisher, session_id, {"error": str(e)})
            
            return {
                "success": False,
                "session_id": session_id,
                "message": f"Course creation failed: {str(e)}"
            }
    
    async def continue_course_creation(self, session_id: str, additional_content: str = "") -> Dict[str, Any]:
        """Continue an existing course creation session"""
        try:
            session_data = await self.session_repository.get_by_id(session_id)
            if not session_data:
                return {
                    "success": False,
                    "message": "Session not found or expired"
                }
            
            if session_data["state"] == "completed":
                return {
                    "success": True,
                    "message": "Session already completed",
                    "course_id": session_data.get("course_id")
                }
            
            # Continue processing logic would go here
            # This is a simplified version - full implementation would handle chunked processing
            
            return {
                "success": True,
                "message": "Session continuation not yet implemented",
                "session_id": session_id
            }
        
        except Exception as e:
            logger.error(f"Failed to continue session {session_id}: {e}")
            return {
                "success": False,
                "message": f"Session continuation failed: {str(e)}"
            }
    
    async def validate_course(self, session_id: str, course_id: Optional[int] = None) -> Dict[str, Any]:
        """Validate created course"""
        try:
            session_data = await self.session_repository.get_by_id(session_id)
            if not session_data:
                return {
                    "success": False,
                    "message": "Session not found"
                }
            
            target_course_id = course_id or session_data.get("course_id")
            if not target_course_id:
                return {
                    "success": False,
                    "message": "No course ID available for validation"
                }
            
            # Create validation command
            context = CommandContext(session_id)
            expected_sections = len(session_data.get("course_structure", {}).get("sections", []))
            
            validation_command = ValidateCourseCommand(
                context, self.moodle_client, target_course_id, expected_sections
            )
            
            result = await self.command_executor.execute_command(validation_command, session_data)
            
            return {
                "success": result.success,
                "message": result.message,
                "validation_data": result.data
            }
        
        except Exception as e:
            logger.error(f"Course validation failed for session {session_id}: {e}")
            return {
                "success": False,
                "message": f"Validation failed: {str(e)}"
            }
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session status"""
        try:
            session_data = await self.session_repository.get_by_id(session_id)
            if not session_data:
                return {
                    "success": False,
                    "message": "Session not found"
                }
            
            # Get command history for this session
            command_history = self.command_executor.get_command_history(session_id)
            
            return {
                "success": True,
                "session_data": {
                    "session_id": session_id,
                    "state": session_data["state"],
                    "course_name": session_data["course_name"],
                    "progress": session_data.get("progress", {}),
                    "course_id": session_data.get("course_id"),
                    "created_at": session_data["created_at"],
                    "updated_at": session_data.get("updated_at")
                },
                "command_history": command_history
            }
        
        except Exception as e:
            logger.error(f"Failed to get session status for {session_id}: {e}")
            return {
                "success": False,
                "message": f"Status retrieval failed: {str(e)}"
            }
    
    async def _build_course_structure_data(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Build course structure data from session"""
        try:
            session_data = await self.session_repository.get_by_id(session_id)
            if not session_data:
                return None
            
            # This would typically extract structure from processed content
            # For now, return a simple structure
            return [
                {
                    "name": "Introduction",
                    "description": "Course introduction and overview",
                    "activities": [
                        {
                            "type": "page",
                            "name": "Welcome",
                            "content": "Welcome to the course!"
                        }
                    ]
                }
            ]
        
        except Exception as e:
            logger.error(f"Failed to build course structure for session {session_id}: {e}")
            return None
    
    async def _handle_creation_failure(self, session_id: str, results: List) -> None:
        """Handle course creation failure"""
        error_messages = [result.message for result in results if not result.success]
        
        await self.session_repository.update_session_state(
            session_id, "failed",
            {
                "error_count": len(error_messages),
                "last_error": error_messages[0] if error_messages else "Unknown error"
            }
        )
        
        await publish_session_failed(self.event_publisher, session_id, {
            "errors": error_messages
        })


@service(IAnalyticsService, ServiceLifetime.SINGLETON)
class AnalyticsService(IAnalyticsService):
    """
    Service for collecting and providing analytics
    
    Responsibilities:
    - Track session metrics
    - Provide system health information
    - Generate reports
    """
    
    def __init__(
        self,
        session_repository: ISessionRepository,
        event_publisher: IEventPublisher
    ):
        self.session_repository = session_repository
        self.event_publisher = event_publisher
        self._metrics_cache: Dict[str, Any] = {}
        self._cache_expires: Optional[datetime] = None
    
    async def record_session_metrics(self, session_id: str, metrics: Dict[str, Any]) -> None:
        """Record session performance metrics"""
        try:
            session_data = await self.session_repository.get_by_id(session_id)
            if session_data:
                # Update session with metrics
                current_metrics = session_data.get("metrics", {})
                current_metrics.update(metrics)
                
                await self.session_repository.update_session_state(
                    session_id, session_data["state"],
                    {"metrics": current_metrics}
                )
                
                logger.debug(f"Metrics recorded for session {session_id}")
        
        except Exception as e:
            logger.error(f"Failed to record metrics for session {session_id}: {e}")
    
    async def get_processing_analytics(self, detailed: bool = False) -> Dict[str, Any]:
        """Get processing analytics"""
        try:
            # Check cache
            if self._cache_expires and datetime.now() < self._cache_expires and not detailed:
                return self._metrics_cache
            
            # Get repository statistics
            repo_stats = await self.session_repository.get_session_statistics()
            
            # Get active sessions for analysis
            active_sessions = await self.session_repository.get_active_sessions(limit=1000)
            
            # Calculate analytics
            analytics = {
                "overview": {
                    "total_sessions": repo_stats.get("total_sessions", 0),
                    "active_sessions": repo_stats.get("active_sessions", 0),
                    "recent_activity": repo_stats.get("recent_activity_24h", 0),
                    "success_rate": self._calculate_success_rate(active_sessions)
                },
                "sessions_by_state": repo_stats.get("sessions_by_state", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            if detailed:
                analytics["detailed_metrics"] = await self._get_detailed_metrics(active_sessions)
            
            # Cache results
            self._metrics_cache = analytics
            self._cache_expires = datetime.now().replace(hour=datetime.now().hour + 1)  # Cache for 1 hour
            
            return analytics
        
        except Exception as e:
            logger.error(f"Failed to get processing analytics: {e}")
            return {"error": str(e)}
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            repo_stats = await self.session_repository.get_session_statistics()
            
            # Determine health status
            active_sessions = repo_stats.get("active_sessions", 0)
            error_rate = self._calculate_error_rate(repo_stats.get("sessions_by_state", {}))
            
            health_status = "healthy"
            if error_rate > 0.3:  # More than 30% errors
                health_status = "unhealthy"
            elif error_rate > 0.1:  # More than 10% errors
                health_status = "degraded"
            
            return {
                "status": health_status,
                "active_sessions": active_sessions,
                "error_rate": error_rate,
                "database_accessible": True,  # If we got stats, DB is accessible
                "timestamp": datetime.now().isoformat(),
                "details": repo_stats
            }
        
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_success_rate(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate success rate from sessions"""
        if not sessions:
            return 0.0
        
        completed_sessions = sum(1 for s in sessions if s.get("state") == "completed")
        return (completed_sessions / len(sessions)) * 100
    
    def _calculate_error_rate(self, sessions_by_state: Dict[str, int]) -> float:
        """Calculate error rate from state distribution"""
        total = sum(sessions_by_state.values())
        if total == 0:
            return 0.0
        
        failed_sessions = sessions_by_state.get("failed", 0)
        return failed_sessions / total
    
    async def _get_detailed_metrics(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed analytics metrics"""
        # This would calculate more detailed metrics
        # For now, return basic analysis
        return {
            "session_count": len(sessions),
            "states_distribution": self._analyze_states(sessions),
            "creation_timeline": self._analyze_timeline(sessions)
        }
    
    def _analyze_states(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze session states distribution"""
        states = {}
        for session in sessions:
            state = session.get("state", "unknown")
            states[state] = states.get(state, 0) + 1
        return states
    
    def _analyze_timeline(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze session creation timeline"""
        # Simplified timeline analysis
        now = datetime.now()
        timeline = {
            "last_hour": 0,
            "last_24_hours": 0,
            "last_week": 0
        }
        
        for session in sessions:
            created_at = session.get("created_at", "")
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                hours_ago = (now - created).total_seconds() / 3600
                
                if hours_ago <= 1:
                    timeline["last_hour"] += 1
                if hours_ago <= 24:
                    timeline["last_24_hours"] += 1
                if hours_ago <= 168:  # 7 days
                    timeline["last_week"] += 1
            except:
                pass  # Skip invalid dates
        
        return timeline


class SessionCoordinatorService:
    """
    Service for coordinating complex session operations
    
    Responsibilities:
    - Manage multi-step session workflows
    - Handle session recovery
    - Coordinate between services
    """
    
    def __init__(
        self,
        course_creation_service: ICourseCreationService,
        analytics_service: IAnalyticsService,
        session_repository: ISessionRepository,
        event_publisher: IEventPublisher
    ):
        self.course_creation_service = course_creation_service
        self.analytics_service = analytics_service
        self.session_repository = session_repository
        self.event_publisher = event_publisher
    
    async def recover_failed_sessions(self) -> Dict[str, Any]:
        """Attempt to recover failed sessions"""
        try:
            active_sessions = await self.session_repository.get_active_sessions()
            failed_sessions = [s for s in active_sessions if s.get("state") == "failed"]
            
            recovery_results = []
            for session in failed_sessions:
                # Attempt recovery logic here
                recovery_results.append({
                    "session_id": session["session_id"],
                    "recovery_attempted": True,
                    "success": False  # Would be determined by actual recovery logic
                })
            
            return {
                "sessions_processed": len(failed_sessions),
                "recovery_results": recovery_results
            }
        
        except Exception as e:
            logger.error(f"Session recovery failed: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """Clean up expired sessions"""
        try:
            if hasattr(self.session_repository, 'cleanup_expired_sessions'):
                deleted_count = await self.session_repository.cleanup_expired_sessions()
                return {
                    "sessions_deleted": deleted_count,
                    "cleanup_completed": True
                }
            else:
                return {
                    "message": "Cleanup not supported by repository",
                    "cleanup_completed": False
                }
        
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
            return {"error": str(e)}