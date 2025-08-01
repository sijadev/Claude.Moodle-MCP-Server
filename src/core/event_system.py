#!/usr/bin/env python3
"""
Event System for MoodleClaude
Implements Observer pattern for session events and notifications
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime

from .interfaces import IEventPublisher, ISessionObserver, SessionEvent, SessionEventType
from .dependency_injection import service, ServiceLifetime

logger = logging.getLogger(__name__)


@service(IEventPublisher, ServiceLifetime.SINGLETON)
class EventPublisher(IEventPublisher):
    """
    Central event publisher implementing Observer pattern
    
    Features:
    - Async event publishing
    - Multiple observer support
    - Event filtering by type
    - Error handling and recovery
    - Event persistence (optional)
    """
    
    def __init__(self):
        self._observers: Set[ISessionObserver] = set()
        self._type_observers: Dict[SessionEventType, Set[ISessionObserver]] = {}
        self._lock = Lock()
        self._event_history: List[SessionEvent] = []
        self._max_history = 1000
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="event_publisher")
    
    def subscribe(self, observer: ISessionObserver, event_types: Optional[List[SessionEventType]] = None) -> None:
        """
        Subscribe to events
        
        Args:
            observer: The observer to subscribe
            event_types: Specific event types to subscribe to (None = all events)
        """
        with self._lock:
            if event_types is None:
                # Subscribe to all events
                self._observers.add(observer)
                logger.debug(f"Observer {observer.__class__.__name__} subscribed to all events")
            else:
                # Subscribe to specific event types
                for event_type in event_types:
                    if event_type not in self._type_observers:
                        self._type_observers[event_type] = set()
                    self._type_observers[event_type].add(observer)
                logger.debug(f"Observer {observer.__class__.__name__} subscribed to events: {[e.value for e in event_types]}")
    
    def unsubscribe(self, observer: ISessionObserver) -> None:
        """Unsubscribe from all events"""
        with self._lock:
            # Remove from general observers
            self._observers.discard(observer)
            
            # Remove from type-specific observers
            for observers_set in self._type_observers.values():
                observers_set.discard(observer)
            
            logger.debug(f"Observer {observer.__class__.__name__} unsubscribed from all events")
    
    async def publish(self, event: SessionEvent) -> None:
        """
        Publish event to all relevant subscribers
        
        Args:
            event: The event to publish
        """
        # Store event in history
        self._add_to_history(event)
        
        # Get all relevant observers
        observers_to_notify = set()
        
        with self._lock:
            # Add general observers
            observers_to_notify.update(self._observers)
            
            # Add type-specific observers
            if event.event_type in self._type_observers:
                observers_to_notify.update(self._type_observers[event.event_type])
        
        if not observers_to_notify:
            logger.debug(f"No observers for event {event.event_type.value}")
            return
        
        # Notify all observers asynchronously
        tasks = []
        for observer in observers_to_notify:
            task = asyncio.create_task(self._notify_observer_safe(observer, event))
            tasks.append(task)
        
        # Wait for all notifications to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.debug(f"Published event {event.event_type.value} to {len(observers_to_notify)} observers")
    
    async def _notify_observer_safe(self, observer: ISessionObserver, event: SessionEvent) -> None:
        """Safely notify an observer, handling any exceptions"""
        try:
            await observer.on_session_event(event)
        except Exception as e:
            logger.error(f"Error notifying observer {observer.__class__.__name__}: {e}")
    
    def _add_to_history(self, event: SessionEvent) -> None:
        """Add event to history with size limit"""
        with self._lock:
            self._event_history.append(event)
            
            # Maintain history size limit
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
    
    def get_event_history(self, session_id: Optional[str] = None, event_types: Optional[List[SessionEventType]] = None, limit: int = 100) -> List[SessionEvent]:
        """
        Get event history with optional filtering
        
        Args:
            session_id: Filter by session ID
            event_types: Filter by event types
            limit: Maximum number of events to return
        """
        with self._lock:
            events = self._event_history.copy()
        
        # Apply filters
        if session_id:
            events = [e for e in events if e.session_id == session_id]
        
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        
        # Return latest events up to limit
        return events[-limit:] if limit > 0 else events
    
    def get_observer_count(self) -> Dict[str, int]:
        """Get count of observers by type"""
        with self._lock:
            result = {
                "total_observers": len(self._observers),
                "type_specific_observers": {
                    event_type.value: len(observers) 
                    for event_type, observers in self._type_observers.items()
                }
            }
        return result
    
    def clear_history(self) -> None:
        """Clear event history"""
        with self._lock:
            self._event_history.clear()
        logger.info("Event history cleared")
    
    def shutdown(self) -> None:
        """Shutdown the event publisher"""
        self._executor.shutdown(wait=True)
        logger.info("Event publisher shutdown complete")


class LoggingObserver(ISessionObserver):
    """Observer that logs all session events"""
    
    def __init__(self, log_level: int = logging.INFO):
        self.logger = logging.getLogger(f"{__name__}.LoggingObserver")
        self.log_level = log_level
    
    async def on_session_event(self, event: SessionEvent) -> None:
        """Log the session event"""
        self.logger.log(
            self.log_level,
            f"Session Event: {event.event_type.value} | Session: {event.session_id} | Data: {json.dumps(event.data, default=str)}"
        )


class MetricsObserver(ISessionObserver):
    """Observer that collects metrics from session events"""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {
            "total_events": 0,
            "events_by_type": {},
            "sessions_created": 0,
            "sessions_completed": 0,
            "sessions_failed": 0,
            "processing_times": [],
            "error_count": 0
        }
        self._lock = Lock()
    
    async def on_session_event(self, event: SessionEvent) -> None:
        """Collect metrics from session event"""
        with self._lock:
            self._metrics["total_events"] += 1
            
            # Count by event type
            event_type_name = event.event_type.value
            if event_type_name not in self._metrics["events_by_type"]:
                self._metrics["events_by_type"][event_type_name] = 0
            self._metrics["events_by_type"][event_type_name] += 1
            
            # Track specific metrics
            if event.event_type == SessionEventType.SESSION_CREATED:
                self._metrics["sessions_created"] += 1
            
            elif event.event_type == SessionEventType.SESSION_COMPLETED:
                self._metrics["sessions_completed"] += 1
                # Track processing time if available
                if "processing_time" in event.data:
                    self._metrics["processing_times"].append(event.data["processing_time"])
            
            elif event.event_type == SessionEventType.SESSION_FAILED:
                self._metrics["sessions_failed"] += 1
                self._metrics["error_count"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        with self._lock:
            metrics = self._metrics.copy()
            
            # Calculate derived metrics
            if metrics["processing_times"]:
                times = metrics["processing_times"]
                metrics["avg_processing_time"] = sum(times) / len(times)
                metrics["max_processing_time"] = max(times)
                metrics["min_processing_time"] = min(times)
            
            metrics["success_rate"] = (
                metrics["sessions_completed"] / max(metrics["sessions_created"], 1)
            ) * 100
            
            return metrics
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""
        with self._lock:
            self._metrics = {
                "total_events": 0,
                "events_by_type": {},
                "sessions_created": 0,
                "sessions_completed": 0,
                "sessions_failed": 0,
                "processing_times": [],
                "error_count": 0
            }


class DatabaseEventObserver(ISessionObserver):
    """Observer that persists events to database"""
    
    def __init__(self, db_path: str = "data/events.db"):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self) -> None:
        """Setup database tables for event storage"""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS session_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        data TEXT,
                        timestamp TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_events_session_id 
                    ON session_events(session_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_events_event_type 
                    ON session_events(event_type)
                """)
                
                conn.commit()
                logger.debug(f"Event database initialized at {self.db_path}")
        
        except Exception as e:
            logger.error(f"Failed to setup event database: {e}")
    
    async def on_session_event(self, event: SessionEvent) -> None:
        """Persist event to database"""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO session_events (event_type, session_id, data, timestamp) VALUES (?, ?, ?, ?)",
                    (
                        event.event_type.value,
                        event.session_id,
                        json.dumps(event.data, default=str),
                        event.timestamp.isoformat()
                    )
                )
                conn.commit()
        
        except Exception as e:
            logger.error(f"Failed to persist event to database: {e}")
    
    def get_events(self, session_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve events from database"""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                if session_id:
                    cursor = conn.execute(
                        "SELECT * FROM session_events WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                        (session_id, limit)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM session_events ORDER BY created_at DESC LIMIT ?",
                        (limit,)
                    )
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Failed to retrieve events from database: {e}")
            return []


# Utility functions for easy event publishing
async def publish_session_created(publisher: IEventPublisher, session_id: str, data: Dict[str, Any]) -> None:
    """Publish session created event"""
    event = SessionEvent(SessionEventType.SESSION_CREATED, session_id, data)
    await publisher.publish(event)


async def publish_processing_started(publisher: IEventPublisher, session_id: str, data: Dict[str, Any]) -> None:
    """Publish processing started event"""
    event = SessionEvent(SessionEventType.PROCESSING_STARTED, session_id, data)
    await publisher.publish(event)


async def publish_chunk_processed(publisher: IEventPublisher, session_id: str, data: Dict[str, Any]) -> None:
    """Publish chunk processed event"""
    event = SessionEvent(SessionEventType.CHUNK_PROCESSED, session_id, data)
    await publisher.publish(event)


async def publish_course_created(publisher: IEventPublisher, session_id: str, data: Dict[str, Any]) -> None:
    """Publish course created event"""
    event = SessionEvent(SessionEventType.COURSE_CREATED, session_id, data)
    await publisher.publish(event)


async def publish_session_completed(publisher: IEventPublisher, session_id: str, data: Dict[str, Any]) -> None:
    """Publish session completed event"""
    event = SessionEvent(SessionEventType.SESSION_COMPLETED, session_id, data)
    await publisher.publish(event)


async def publish_session_failed(publisher: IEventPublisher, session_id: str, data: Dict[str, Any]) -> None:
    """Publish session failed event"""
    event = SessionEvent(SessionEventType.SESSION_FAILED, session_id, data)
    await publisher.publish(event)