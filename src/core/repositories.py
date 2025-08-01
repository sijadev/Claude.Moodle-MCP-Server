#!/usr/bin/env python3
"""
Repository Pattern implementation for MoodleClaude
Abstracts data persistence layer with multiple storage backends
"""

import asyncio
import json
import logging
import os
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, List, Optional, Union

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

from .dependency_injection import ServiceLifetime, service
from .interfaces import ISessionRepository

logger = logging.getLogger(__name__)


class RepositoryException(Exception):
    """Base exception for repository operations"""

    pass


@service(ISessionRepository, ServiceLifetime.SINGLETON)
class SQLiteSessionRepository(ISessionRepository):
    """
    SQLite implementation of session repository

    Features:
    - Async operations with aiosqlite
    - JSON serialization for complex data
    - Automatic table creation
    - Connection pooling
    - Transaction support
    """

    def __init__(self, db_path: str = "data/sessions.db"):
        if aiosqlite is None:
            raise ImportError(
                "aiosqlite package is required for SQLiteSessionRepository. "
                "Install with: pip install aiosqlite>=0.21.0"
            )
        self.db_path = db_path
        self._ensure_directory()
        self._connection_lock = Lock()
        self._initialized = False

    def _ensure_directory(self) -> None:
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    async def _initialize_database(self) -> None:
        """Initialize database tables if not exists"""
        if self._initialized:
            return

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Sessions table
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        course_name TEXT NOT NULL,
                        state TEXT NOT NULL DEFAULT 'created',
                        strategy TEXT NOT NULL DEFAULT 'single_pass',
                        progress_data TEXT DEFAULT '{}',
                        course_structure TEXT DEFAULT '{}',
                        course_id INTEGER,
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME
                    )
                """
                )

                # Session chunks table for large content
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS session_chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        chunk_content TEXT NOT NULL,
                        processed BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE,
                        UNIQUE(session_id, chunk_index)
                    )
                """
                )

                # Session metadata table for extended attributes
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS session_metadata (
                        session_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (session_id, key),
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
                    )
                """
                )

                # Create indexes for performance
                await db.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(state)"
                )
                await db.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)"
                )
                await db.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)"
                )
                await db.execute(
                    "CREATE INDEX IF NOT EXISTS idx_session_chunks_session_id ON session_chunks(session_id)"
                )

                await db.commit()
                logger.debug(f"Session database initialized at {self.db_path}")
                self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize session database: {e}")
            raise RepositoryException(f"Database initialization failed: {e}")

    async def save(self, session_data: Dict[str, Any]) -> None:
        """Save session data to database"""
        await self._initialize_database()

        session_id = session_data.get("session_id")
        if not session_id:
            raise RepositoryException("Session ID is required")

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Calculate expiration time (default: 24 hours)
                expires_at = datetime.now() + timedelta(hours=24)
                if "expires_at" in session_data:
                    expires_at = session_data["expires_at"]

                # Upsert main session record
                await db.execute(
                    """
                    INSERT OR REPLACE INTO sessions (
                        session_id, content, course_name, state, strategy,
                        progress_data, course_structure, course_id, error_count,
                        last_error, updated_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                """,
                    (
                        session_id,
                        session_data.get("content", ""),
                        session_data.get("course_name", ""),
                        session_data.get("state", "created"),
                        session_data.get("strategy", "single_pass"),
                        json.dumps(session_data.get("progress", {})),
                        json.dumps(session_data.get("course_structure", {})),
                        session_data.get("course_id"),
                        session_data.get("error_count", 0),
                        session_data.get("last_error"),
                        expires_at,
                    ),
                )

                # Save chunks if present
                chunks = session_data.get("chunks", [])
                if chunks:
                    # Clear existing chunks
                    await db.execute(
                        "DELETE FROM session_chunks WHERE session_id = ?", (session_id,)
                    )

                    # Insert new chunks
                    for i, chunk in enumerate(chunks):
                        await db.execute(
                            """
                            INSERT INTO session_chunks (session_id, chunk_index, chunk_content)
                            VALUES (?, ?, ?)
                        """,
                            (session_id, i, chunk),
                        )

                # Save metadata if present
                metadata = session_data.get("metadata", {})
                if metadata:
                    # Clear existing metadata
                    await db.execute(
                        "DELETE FROM session_metadata WHERE session_id = ?",
                        (session_id,),
                    )

                    # Insert new metadata
                    for key, value in metadata.items():
                        await db.execute(
                            """
                            INSERT INTO session_metadata (session_id, key, value)
                            VALUES (?, ?, ?)
                        """,
                            (session_id, key, json.dumps(value)),
                        )

                await db.commit()
                logger.debug(f"Session {session_id} saved successfully")

        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            raise RepositoryException(f"Save operation failed: {e}")

    async def get_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session by ID"""
        await self._initialize_database()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Get main session data
                cursor = await db.execute(
                    """
                    SELECT * FROM sessions WHERE session_id = ?
                """,
                    (session_id,),
                )

                row = await cursor.fetchone()
                if not row:
                    return None

                # Convert to dict
                session_data = dict(row)

                # Parse JSON fields
                session_data["progress"] = json.loads(
                    session_data.pop("progress_data", "{}")
                )
                session_data["course_structure"] = json.loads(
                    session_data.pop("course_structure", "{}")
                )

                # Get chunks
                cursor = await db.execute(
                    """
                    SELECT chunk_index, chunk_content, processed
                    FROM session_chunks
                    WHERE session_id = ?
                    ORDER BY chunk_index
                """,
                    (session_id,),
                )

                chunks_data = await cursor.fetchall()
                session_data["chunks"] = [row["chunk_content"] for row in chunks_data]
                session_data["chunks_processed"] = [
                    row["processed"] for row in chunks_data
                ]

                # Get metadata
                cursor = await db.execute(
                    """
                    SELECT key, value FROM session_metadata WHERE session_id = ?
                """,
                    (session_id,),
                )

                metadata_rows = await cursor.fetchall()
                metadata = {}
                for row in metadata_rows:
                    metadata[row["key"]] = json.loads(row["value"])
                session_data["metadata"] = metadata

                return session_data

        except Exception as e:
            logger.error(f"Failed to retrieve session {session_id}: {e}")
            raise RepositoryException(f"Retrieval operation failed: {e}")

    async def get_active_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all active (non-expired) sessions"""
        await self._initialize_database()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                cursor = await db.execute(
                    """
                    SELECT session_id, course_name, state, created_at, updated_at, expires_at
                    FROM sessions
                    WHERE expires_at > CURRENT_TIMESTAMP OR expires_at IS NULL
                    ORDER BY updated_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            raise RepositoryException(f"Active sessions query failed: {e}")

    async def delete(self, session_id: str) -> bool:
        """Delete session and all related data"""
        await self._initialize_database()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete from main table (cascades to related tables)
                cursor = await db.execute(
                    "DELETE FROM sessions WHERE session_id = ?", (session_id,)
                )
                await db.commit()

                deleted = cursor.rowcount > 0
                if deleted:
                    logger.debug(f"Session {session_id} deleted successfully")

                return deleted

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise RepositoryException(f"Delete operation failed: {e}")

    async def update_session_state(
        self, session_id: str, state: str, data: Dict[str, Any]
    ) -> bool:
        """Update session state and related data"""
        await self._initialize_database()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Update main session state
                cursor = await db.execute(
                    """
                    UPDATE sessions
                    SET state = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """,
                    (state, session_id),
                )

                # Update additional fields if provided
                if "progress" in data:
                    await db.execute(
                        """
                        UPDATE sessions
                        SET progress_data = ?
                        WHERE session_id = ?
                    """,
                        (json.dumps(data["progress"]), session_id),
                    )

                if "course_structure" in data:
                    await db.execute(
                        """
                        UPDATE sessions
                        SET course_structure = ?
                        WHERE session_id = ?
                    """,
                        (json.dumps(data["course_structure"]), session_id),
                    )

                if "course_id" in data:
                    await db.execute(
                        """
                        UPDATE sessions
                        SET course_id = ?
                        WHERE session_id = ?
                    """,
                        (data["course_id"], session_id),
                    )

                if "error_count" in data:
                    await db.execute(
                        """
                        UPDATE sessions
                        SET error_count = ?, last_error = ?
                        WHERE session_id = ?
                    """,
                        (data["error_count"], data.get("last_error"), session_id),
                    )

                await db.commit()

                updated = cursor.rowcount > 0
                if updated:
                    logger.debug(f"Session {session_id} state updated to {state}")

                return updated

        except Exception as e:
            logger.error(f"Failed to update session {session_id} state: {e}")
            raise RepositoryException(f"Update operation failed: {e}")

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        await self._initialize_database()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    DELETE FROM sessions
                    WHERE expires_at < CURRENT_TIMESTAMP
                """
                )
                await db.commit()

                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired sessions")

                return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            raise RepositoryException(f"Cleanup operation failed: {e}")

    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get repository statistics"""
        await self._initialize_database()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total sessions
                cursor = await db.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = (await cursor.fetchone())[0]

                # Active sessions
                cursor = await db.execute(
                    """
                    SELECT COUNT(*) FROM sessions
                    WHERE expires_at > CURRENT_TIMESTAMP OR expires_at IS NULL
                """
                )
                active_sessions = (await cursor.fetchone())[0]

                # Sessions by state
                cursor = await db.execute(
                    """
                    SELECT state, COUNT(*) as count
                    FROM sessions
                    GROUP BY state
                """
                )
                states = {row[0]: row[1] for row in await cursor.fetchall()}

                # Recent activity (last 24 hours)
                cursor = await db.execute(
                    """
                    SELECT COUNT(*) FROM sessions
                    WHERE updated_at > datetime('now', '-1 day')
                """
                )
                recent_activity = (await cursor.fetchone())[0]

                return {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "expired_sessions": total_sessions - active_sessions,
                    "sessions_by_state": states,
                    "recent_activity_24h": recent_activity,
                    "database_path": self.db_path,
                }

        except Exception as e:
            logger.error(f"Failed to get repository statistics: {e}")
            return {"error": str(e)}


class InMemorySessionRepository(ISessionRepository):
    """
    In-memory implementation for testing and development
    """

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    async def save(self, session_data: Dict[str, Any]) -> None:
        """Save session data in memory"""
        session_id = session_data.get("session_id")
        if not session_id:
            raise RepositoryException("Session ID is required")

        with self._lock:
            # Deep copy to avoid reference issues
            self._sessions[session_id] = json.loads(
                json.dumps(session_data, default=str)
            )

        logger.debug(f"Session {session_id} saved to memory")

    async def get_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session from memory"""
        with self._lock:
            session_data = self._sessions.get(session_id)
            if session_data:
                # Return deep copy
                return json.loads(json.dumps(session_data))
            return None

    async def get_active_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all sessions from memory"""
        with self._lock:
            sessions = list(self._sessions.values())
            # Sort by updated_at if available
            sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return sessions[:limit]

    async def delete(self, session_id: str) -> bool:
        """Delete session from memory"""
        with self._lock:
            deleted = session_id in self._sessions
            if deleted:
                del self._sessions[session_id]
                logger.debug(f"Session {session_id} deleted from memory")
            return deleted

    async def update_session_state(
        self, session_id: str, state: str, data: Dict[str, Any]
    ) -> bool:
        """Update session state in memory"""
        with self._lock:
            if session_id not in self._sessions:
                return False

            self._sessions[session_id]["state"] = state
            self._sessions[session_id]["updated_at"] = datetime.now().isoformat()

            # Update additional data
            for key, value in data.items():
                self._sessions[session_id][key] = value

            logger.debug(f"Session {session_id} state updated to {state} in memory")
            return True

    def clear(self) -> None:
        """Clear all sessions from memory"""
        with self._lock:
            self._sessions.clear()
        logger.info("Memory repository cleared")

    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics from in-memory storage"""
        with self._lock:
            total_sessions = len(self._sessions)
            state_counts = {}

            for session in self._sessions.values():
                state = session.get("state", "unknown")
                state_counts[state] = state_counts.get(state, 0) + 1

            return {
                "total_sessions": total_sessions,
                "sessions_by_state": state_counts,
                "data_source": "in_memory_repository",
            }


class CachedSessionRepository(ISessionRepository):
    """
    Cached repository implementation with write-through caching
    """

    def __init__(self, primary_repo: ISessionRepository, cache_size: int = 100):
        self.primary_repo = primary_repo
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_size = cache_size
        self._lock = Lock()
        self._access_order: List[str] = []  # LRU tracking

    async def save(self, session_data: Dict[str, Any]) -> None:
        """Save to both cache and primary repository"""
        session_id = session_data.get("session_id")
        if not session_id:
            raise RepositoryException("Session ID is required")

        # Save to primary repository first
        await self.primary_repo.save(session_data)

        # Update cache
        with self._lock:
            self.cache[session_id] = json.loads(json.dumps(session_data, default=str))
            self._update_access_order(session_id)
            self._evict_if_needed()

    async def get_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get from cache first, then primary repository"""
        with self._lock:
            if session_id in self.cache:
                self._update_access_order(session_id)
                return json.loads(json.dumps(self.cache[session_id]))

        # Not in cache, get from primary repository
        session_data = await self.primary_repo.get_by_id(session_id)

        if session_data:
            with self._lock:
                self.cache[session_id] = json.loads(
                    json.dumps(session_data, default=str)
                )
                self._update_access_order(session_id)
                self._evict_if_needed()

        return session_data

    async def get_active_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get from primary repository (bypass cache for list operations)"""
        return await self.primary_repo.get_active_sessions(limit)

    async def delete(self, session_id: str) -> bool:
        """Delete from both cache and primary repository"""
        # Delete from primary repository
        deleted = await self.primary_repo.delete(session_id)

        # Remove from cache
        with self._lock:
            if session_id in self.cache:
                del self.cache[session_id]
                if session_id in self._access_order:
                    self._access_order.remove(session_id)

        return deleted

    async def update_session_state(
        self, session_id: str, state: str, data: Dict[str, Any]
    ) -> bool:
        """Update in both cache and primary repository"""
        # Update primary repository
        updated = await self.primary_repo.update_session_state(session_id, state, data)

        # Update cache if present
        with self._lock:
            if session_id in self.cache:
                self.cache[session_id]["state"] = state
                for key, value in data.items():
                    self.cache[session_id][key] = value
                self._update_access_order(session_id)

        return updated

    def _update_access_order(self, session_id: str) -> None:
        """Update LRU access order"""
        if session_id in self._access_order:
            self._access_order.remove(session_id)
        self._access_order.append(session_id)

    def _evict_if_needed(self) -> None:
        """Evict least recently used items if cache is full"""
        while len(self.cache) > self.cache_size:
            if self._access_order:
                lru_session = self._access_order.pop(0)
                self.cache.pop(lru_session, None)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "cache_size": len(self.cache),
                "max_cache_size": self.cache_size,
                "cache_utilization": len(self.cache) / self.cache_size * 100,
            }

    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics (delegate to primary repository)"""
        # Check if primary repository has this method
        if hasattr(self.primary_repo, "get_session_statistics"):
            return await self.primary_repo.get_session_statistics()
        else:
            # Fallback implementation using get_active_sessions
            sessions = await self.get_active_sessions(1000)  # Get up to 1000 sessions

            # Basic statistics
            total_sessions = len(sessions)
            state_counts = {}

            for session in sessions:
                state = session.get("state", "unknown")
                state_counts[state] = state_counts.get(state, 0) + 1

            # Add cache statistics
            cache_stats = self.get_cache_stats()

            return {
                "total_sessions": total_sessions,
                "sessions_by_state": state_counts,
                "cache_statistics": cache_stats,
                "data_source": "cached_repository_fallback",
            }
