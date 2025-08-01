"""
Intelligent Session Manager for Enhanced MCP Server
Manages course creation sessions with automatic continuation and intelligent responses
"""

import asyncio
import json
import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.clients.moodle_client_enhanced import EnhancedMoodleClient
from src.core.adaptive_content_processor import (
    AdaptiveContentProcessor,
    ProcessingSession,
    SessionState,
)
from src.models.models import CourseStructure

logger = logging.getLogger(__name__)


@dataclass
class SessionDatabase:
    """Database configuration for session persistence"""

    db_path: str = "data/sessions.db"
    backup_interval: int = 3600  # 1 hour
    max_sessions: int = 1000


class IntelligentSessionManager:
    """
    Manages course creation sessions with persistence, validation, and intelligent continuation
    Integrates with the existing MCP server to provide seamless user experience
    """

    def __init__(
        self,
        moodle_client: Optional[EnhancedMoodleClient] = None,
        db_config: Optional[SessionDatabase] = None,
    ):
        """
        Initialize the session manager

        Args:
            moodle_client: Optional Moodle client for course creation
            db_config: Database configuration for session persistence
        """
        self.moodle_client = moodle_client

        # Setup database configuration with environment variable support
        if db_config is None:
            db_path = os.getenv("MOODLE_CLAUDE_DB_PATH", "data/sessions.db")
            backup_interval = int(os.getenv("MOODLE_CLAUDE_BACKUP_INTERVAL", "3600"))
            db_config = SessionDatabase(
                db_path=db_path, backup_interval=backup_interval
            )
        self.db_config = db_config
        self.content_processor = AdaptiveContentProcessor()

        # Initialize database
        self._init_database()

        # Load active sessions from database
        self._load_active_sessions()

        # Start background tasks
        self._background_tasks = set()
        self._start_background_tasks()

        logger.info("IntelligentSessionManager initialized with database persistence")

    def _init_database(self):
        """Initialize SQLite database for session persistence"""
        try:
            # Ensure database directory exists
            db_dir = os.path.dirname(self.db_config.db_path)
            if db_dir:  # Only create directory if path has a directory component
                os.makedirs(db_dir, exist_ok=True)

            with sqlite3.connect(self.db_config.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        content_hash TEXT NOT NULL,
                        original_content TEXT NOT NULL,
                        course_name TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        state TEXT NOT NULL,
                        total_chunks INTEGER NOT NULL,
                        processed_chunks INTEGER NOT NULL,
                        current_chunk_index INTEGER NOT NULL,
                        course_id INTEGER,
                        created_sections TEXT,  -- JSON array
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        retry_attempts INTEGER DEFAULT 0,
                        needs_continuation BOOLEAN DEFAULT FALSE,
                        continuation_prompt TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS session_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        content_size INTEGER NOT NULL,
                        processing_time_seconds REAL NOT NULL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        strategy_used TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS course_validation (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        course_id INTEGER NOT NULL,
                        expected_sections INTEGER NOT NULL,
                        actual_sections INTEGER NOT NULL,
                        validation_status TEXT NOT NULL,
                        validation_errors TEXT,  -- JSON array
                        validated_at TEXT NOT NULL,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                """
                )

                conn.commit()

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _load_active_sessions(self):
        """Load active sessions from database"""
        try:
            with sqlite3.connect(self.db_config.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM sessions
                    WHERE state NOT IN ('completed', 'failed')
                    AND datetime(expires_at) > datetime('now')
                """
                )

                for row in cursor:
                    session_data = dict(row)
                    session_data["created_sections"] = json.loads(
                        session_data["created_sections"] or "[]"
                    )
                    session_data["needs_continuation"] = bool(
                        session_data["needs_continuation"]
                    )

                    # Convert datetime strings back to datetime objects
                    for field in ["created_at", "updated_at", "expires_at"]:
                        session_data[field] = datetime.fromisoformat(
                            session_data[field]
                        )

                    # Convert to ProcessingSession object
                    session = ProcessingSession(**session_data)
                    self.content_processor.active_sessions[session.session_id] = session

                logger.info(
                    f"Loaded {len(self.content_processor.active_sessions)} active sessions from database"
                )

        except Exception as e:
            logger.error(f"Failed to load sessions from database: {e}")

    def _save_session_to_db(self, session: ProcessingSession):
        """Save session to database"""
        try:
            with sqlite3.connect(self.db_config.db_path) as conn:
                session_data = asdict(session)
                session_data["created_sections"] = json.dumps(
                    session_data["created_sections"]
                )
                session_data["needs_continuation"] = int(
                    session_data["needs_continuation"]
                )

                # Convert datetime objects to strings
                for field in ["created_at", "updated_at", "expires_at"]:
                    session_data[field] = session_data[field].isoformat()

                conn.execute(
                    """
                    INSERT OR REPLACE INTO sessions (
                        session_id, content_hash, original_content, course_name, strategy, state,
                        total_chunks, processed_chunks, current_chunk_index, course_id, created_sections,
                        error_count, last_error, retry_attempts, needs_continuation, continuation_prompt,
                        created_at, updated_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session_data["session_id"],
                        session_data["content_hash"],
                        session_data["original_content"],
                        session_data["course_name"],
                        session_data["strategy"],
                        session_data["state"],
                        session_data["total_chunks"],
                        session_data["processed_chunks"],
                        session_data["current_chunk_index"],
                        session_data["course_id"],
                        session_data["created_sections"],
                        session_data["error_count"],
                        session_data["last_error"],
                        session_data["retry_attempts"],
                        session_data["needs_continuation"],
                        session_data["continuation_prompt"],
                        session_data["created_at"],
                        session_data["updated_at"],
                        session_data["expires_at"],
                    ),
                )

                conn.commit()

        except Exception as e:
            logger.error(
                f"Failed to save session {session.session_id} to database: {e}"
            )

    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Cleanup task
        cleanup_task = asyncio.create_task(self._periodic_cleanup())
        self._background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self._background_tasks.discard)

        # Backup task
        backup_task = asyncio.create_task(self._periodic_backup())
        self._background_tasks.add(backup_task)
        backup_task.add_done_callback(self._background_tasks.discard)

    async def _periodic_cleanup(self):
        """Periodically clean up expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.db_config.backup_interval)
                self.content_processor.cleanup_expired_sessions()

                # Clean up database
                with sqlite3.connect(self.db_config.db_path) as conn:
                    conn.execute(
                        """
                        DELETE FROM sessions
                        WHERE datetime(expires_at) < datetime('now', '-1 day')
                    """
                    )
                    conn.commit()

            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

    async def _periodic_backup(self):
        """Periodically backup session data"""
        while True:
            try:
                await asyncio.sleep(self.db_config.backup_interval)

                # Create backup
                backup_path = (
                    f"{self.db_config.db_path}.backup.{int(datetime.now().timestamp())}"
                )

                with sqlite3.connect(self.db_config.db_path) as source:
                    with sqlite3.connect(backup_path) as backup:
                        source.backup(backup)

                logger.info(f"Created session database backup: {backup_path}")

                # Keep only last 5 backups
                import glob

                backups = sorted(glob.glob(f"{self.db_config.db_path}.backup.*"))
                for old_backup in backups[:-5]:
                    os.remove(old_backup)

            except Exception as e:
                logger.error(f"Error in periodic backup: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def create_intelligent_course_session(
        self, content: str, course_name: str = "", continue_previous: bool = False
    ) -> Dict[str, Any]:
        """
        Create an intelligent course creation session with automatic continuation logic

        Args:
            content: The chat content to process
            course_name: Name for the course
            continue_previous: Whether to continue a previous session

        Returns:
            Dictionary with session info and next steps
        """
        try:
            # Create or resume session
            session_id = self.content_processor.create_session(content, course_name)
            session = self.content_processor.active_sessions[session_id]

            # Save session to database
            self._save_session_to_db(session)

            # Analyze content and provide initial response
            analysis = await self.content_processor.analyze_content_complexity(content)

            # Determine initial response based on complexity
            if analysis["recommended_strategy"].value == "single_pass":
                # Simple content - process immediately
                success, result = await self.content_processor.process_content_chunk(
                    session_id, 0
                )

                if success:
                    # Create actual Moodle course if client is available
                    if self.moodle_client:
                        course_result = await self._create_moodle_course(
                            session, result["course_structure"]
                        )
                        result.update(course_result)

                    self._save_session_to_db(session)
                    return {
                        "success": True,
                        "session_id": session_id,
                        "immediate_completion": True,
                        "message": "✅ Your course has been created successfully!",
                        **result,
                    }
                else:
                    return {
                        "success": False,
                        "session_id": session_id,
                        "error": result.get("error"),
                        "message": "I encountered an issue creating your course. Let me try a different approach.",
                        "suggested_action": result.get("action", "retry"),
                    }

            else:
                # Complex content - start chunked processing
                return {
                    "success": True,
                    "session_id": session_id,
                    "immediate_completion": False,
                    "message": self._generate_start_message(analysis),
                    "processing_plan": {
                        "strategy": analysis["recommended_strategy"].value,
                        "estimated_chunks": analysis["estimated_chunks"],
                        "estimated_time": analysis["processing_time_estimate"],
                        "complexity_score": analysis["complexity_score"],
                    },
                    "next_action": "process_first_chunk",
                    "user_friendly_message": self._generate_user_start_message(
                        analysis
                    ),
                }

        except Exception as e:
            logger.error(f"Error creating intelligent course session: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I had trouble analyzing your content. Please try again or break it into smaller parts.",
            }

    def _generate_start_message(self, analysis: Dict[str, Any]) -> str:
        """Generate appropriate start message based on content analysis"""
        complexity = analysis["complexity_score"]
        strategy = analysis["recommended_strategy"].value

        if complexity < 0.3:
            return "I can process this content in one go. Starting course creation..."
        elif complexity < 0.6:
            return f"I'll process this content in {analysis['estimated_chunks']} logical sections for the best results."
        else:
            return f"This is rich, complex content! I'll carefully process it in {analysis['estimated_chunks']} parts to ensure everything is captured properly."

    def _generate_user_start_message(self, analysis: Dict[str, Any]) -> str:
        """Generate user-friendly start message"""
        time_est = analysis["processing_time_estimate"]
        chunks = analysis["estimated_chunks"]

        if chunks == 1:
            return f"Perfect! I'll have your course ready in about {time_est} seconds."
        else:
            return f"I'll process this in {chunks} parts. This should take about {time_est} seconds total. I'll keep you updated on progress!"

    async def continue_session_processing(
        self, session_id: str, additional_content: str = ""
    ) -> Dict[str, Any]:
        """
        Continue processing a session, optionally with additional content

        Args:
            session_id: The session to continue
            additional_content: Optional additional content to process

        Returns:
            Processing result with continuation status
        """
        session = self.content_processor.active_sessions.get(session_id)
        if not session:
            return {
                "success": False,
                "error": "Session not found or expired",
                "action": "create_new_session",
            }

        try:
            # If additional content provided, append to session content
            if additional_content:
                session.original_content += f"\n\n{additional_content}"
                session.updated_at = datetime.now()

            # Process next chunk
            next_chunk_index = session.current_chunk_index + 1
            success, result = await self.content_processor.process_content_chunk(
                session_id, next_chunk_index, continue_previous=True
            )

            if success:
                # Create/update Moodle course if client is available
                if self.moodle_client and "course_structure" in result:
                    course_result = await self._update_moodle_course(
                        session, result["course_structure"]
                    )
                    result.update(course_result)

                # Save updated session
                self._save_session_to_db(session)

                # Record metrics
                await self._record_session_metrics(
                    session_id, len(additional_content), True, ""
                )

                return {"success": True, "session_id": session_id, **result}
            else:
                # Record failure metrics
                await self._record_session_metrics(
                    session_id,
                    len(additional_content),
                    False,
                    result.get("error", "Unknown error"),
                )

                return {"success": False, "session_id": session_id, **result}

        except Exception as e:
            logger.error(f"Error continuing session {session_id}: {e}")
            await self._record_session_metrics(
                session_id, len(additional_content), False, str(e)
            )

            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "message": "I encountered an issue continuing your session. Please try again.",
            }

    async def _create_moodle_course(
        self, session: ProcessingSession, course_structure: CourseStructure
    ) -> Dict[str, Any]:
        """Create actual Moodle course from course structure"""
        if not self.moodle_client:
            return {"moodle_integration": "disabled", "preview_mode": True}

        try:
            # Create course
            course_id = await self.moodle_client.create_course(
                fullname=session.course_name,
                shortname=f"course_{session.session_id[:8]}",
                summary=f"Course created from chat content on {datetime.now().strftime('%Y-%m-%d')}",
            )

            session.course_id = course_id
            created_sections = []

            # Create sections and content
            for section in course_structure.sections:
                try:
                    section_result = await self.moodle_client.create_section(
                        course_id=course_id,
                        section_name=section.name,
                        summary=section.description,
                    )

                    # Add items to section
                    for item in section.items:
                        if item.type == "code":
                            await self.moodle_client.create_page_activity(
                                course_id=course_id,
                                section_id=section_result["id"],
                                name=item.title,
                                content=f"<pre><code class='{item.language}'>{item.content}</code></pre>",
                            )
                        elif item.type == "topic":
                            await self.moodle_client.create_page_activity(
                                course_id=course_id,
                                section_id=section_result["id"],
                                name=item.title,
                                content=item.content,
                            )

                    created_sections.append(section_result)

                except Exception as section_error:
                    logger.error(
                        f"Error creating section '{section.name}': {section_error}"
                    )
                    # Continue with other sections

            session.created_sections.extend(created_sections)

            # Validate course creation
            validation_result = await self._validate_course_creation(
                session, course_structure
            )

            return {
                "moodle_integration": "success",
                "course_id": course_id,
                "course_url": f"{self.moodle_client.base_url}/course/view.php?id={course_id}",
                "created_sections_count": len(created_sections),
                "validation": validation_result,
            }

        except Exception as e:
            logger.error(f"Error creating Moodle course: {e}")
            return {
                "moodle_integration": "failed",
                "error": str(e),
                "fallback_action": "preview_mode",
            }

    async def _update_moodle_course(
        self, session: ProcessingSession, course_structure: CourseStructure
    ) -> Dict[str, Any]:
        """Update existing Moodle course with new sections"""
        if not self.moodle_client or not session.course_id:
            return {"moodle_integration": "disabled"}

        try:
            updated_sections = []

            # Add new sections to existing course
            for section in course_structure.sections:
                section_result = await self.moodle_client.create_section(
                    course_id=session.course_id,
                    section_name=section.name,
                    summary=section.description,
                )

                # Add items to section
                for item in section.items:
                    if item.type == "code":
                        await self.moodle_client.create_page_activity(
                            course_id=session.course_id,
                            section_id=section_result["id"],
                            name=item.title,
                            content=f"<pre><code class='{item.language}'>{item.content}</code></pre>",
                        )
                    elif item.type == "topic":
                        await self.moodle_client.create_page_activity(
                            course_id=session.course_id,
                            section_id=section_result["id"],
                            name=item.title,
                            content=item.content,
                        )

                updated_sections.append(section_result)

            session.created_sections.extend(updated_sections)

            return {
                "moodle_integration": "updated",
                "course_id": session.course_id,
                "new_sections_count": len(updated_sections),
                "total_sections_count": len(session.created_sections),
            }

        except Exception as e:
            logger.error(f"Error updating Moodle course: {e}")
            return {"moodle_integration": "update_failed", "error": str(e)}

    async def _validate_course_creation(
        self, session: ProcessingSession, expected_structure: CourseStructure
    ) -> Dict[str, Any]:
        """Validate that the course was created correctly"""
        if not self.moodle_client or not session.course_id:
            return {"validation": "skipped", "reason": "no_moodle_client"}

        try:
            # Get actual course contents
            course_contents = await self.moodle_client.get_course_contents(
                session.course_id
            )

            expected_sections = len(expected_structure.sections)
            actual_sections = len(course_contents.get("sections", []))

            validation_errors = []

            if actual_sections != expected_sections:
                validation_errors.append(
                    f"Section count mismatch: expected {expected_sections}, got {actual_sections}"
                )

            # Check each section
            for i, expected_section in enumerate(expected_structure.sections):
                if i < len(course_contents.get("sections", [])):
                    actual_section = course_contents["sections"][i]
                    expected_items = len(expected_section.items)
                    actual_items = len(actual_section.get("modules", []))

                    if actual_items != expected_items:
                        validation_errors.append(
                            f"Section '{expected_section.name}' item count mismatch: "
                            f"expected {expected_items}, got {actual_items}"
                        )

            validation_status = "success" if not validation_errors else "warnings"

            # Save validation results to database
            with sqlite3.connect(self.db_config.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO course_validation (
                        session_id, course_id, expected_sections, actual_sections,
                        validation_status, validation_errors, validated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session.session_id,
                        session.course_id,
                        expected_sections,
                        actual_sections,
                        validation_status,
                        json.dumps(validation_errors),
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()

            return {
                "validation": validation_status,
                "expected_sections": expected_sections,
                "actual_sections": actual_sections,
                "errors": validation_errors,
            }

        except Exception as e:
            logger.error(f"Error validating course creation: {e}")
            return {"validation": "failed", "error": str(e)}

    async def _record_session_metrics(
        self, session_id: str, content_size: int, success: bool, error_message: str = ""
    ):
        """Record session processing metrics"""
        try:
            session = self.content_processor.active_sessions.get(session_id)
            processing_time = (
                (datetime.now() - session.updated_at).total_seconds() if session else 0
            )

            with sqlite3.connect(self.db_config.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO session_metrics (
                        session_id, content_size, processing_time_seconds, success,
                        error_message, strategy_used, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session_id,
                        content_size,
                        processing_time,
                        success,
                        error_message,
                        session.strategy.value if session else "unknown",
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error recording session metrics: {e}")

    def get_session_analytics(self) -> Dict[str, Any]:
        """Get comprehensive session analytics"""
        try:
            with sqlite3.connect(self.db_config.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Overall metrics
                overall_metrics = conn.execute(
                    """
                    SELECT
                        COUNT(*) as total_sessions,
                        COUNT(CASE WHEN state = 'completed' THEN 1 END) as completed_sessions,
                        COUNT(CASE WHEN state = 'failed' THEN 1 END) as failed_sessions,
                        AVG(processed_chunks * 1.0 / total_chunks) as avg_completion_rate,
                        AVG(LENGTH(original_content)) as avg_content_size
                    FROM sessions
                """
                ).fetchone()

                # Strategy effectiveness
                strategy_metrics = conn.execute(
                    """
                    SELECT
                        strategy,
                        COUNT(*) as usage_count,
                        AVG(CASE WHEN state = 'completed' THEN 1.0 ELSE 0.0 END) as success_rate
                    FROM sessions
                    GROUP BY strategy
                """
                ).fetchall()

                # Processing metrics
                processing_metrics = conn.execute(
                    """
                    SELECT
                        AVG(processing_time_seconds) as avg_processing_time,
                        AVG(content_size) as avg_content_size,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate
                    FROM session_metrics
                    WHERE timestamp > datetime('now', '-7 days')
                """
                ).fetchone()

                return {
                    "overall": dict(overall_metrics) if overall_metrics else {},
                    "strategy_effectiveness": [dict(row) for row in strategy_metrics],
                    "recent_processing": (
                        dict(processing_metrics) if processing_metrics else {}
                    ),
                    "active_sessions": len(self.content_processor.active_sessions),
                    "processor_metrics": self.content_processor.get_processing_metrics(),
                }

        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            return {"error": str(e)}

    async def cleanup_and_shutdown(self):
        """Clean up resources and shutdown gracefully"""
        logger.info("Shutting down IntelligentSessionManager...")

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Save all active sessions
        for session in self.content_processor.active_sessions.values():
            self._save_session_to_db(session)

        logger.info("IntelligentSessionManager shutdown complete")
