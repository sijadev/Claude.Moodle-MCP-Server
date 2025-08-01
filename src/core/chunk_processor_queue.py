"""
Queue-based chunk processor for handling large content processing
Provides retry logic, rate limiting, and async processing
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from src.models.models import CourseStructure

logger = logging.getLogger(__name__)


class ChunkStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class ChunkTask:
    """Represents a chunk processing task"""

    chunk_id: str
    course_id: int
    chunk_data: List[Dict[str, Any]]
    priority: int = 1
    max_retries: int = 3
    retry_count: int = 0
    status: ChunkStatus = ChunkStatus.PENDING
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class ChunkProcessorQueue:
    """Queue-based processor for course content chunks"""

    def __init__(self, max_concurrent: int = 2, rate_limit_delay: float = 1.0):
        """
        Initialize chunk processor queue

        Args:
            max_concurrent: Maximum number of chunks to process concurrently
            rate_limit_delay: Delay between chunk processing to avoid rate limits
        """
        self.max_concurrent = max_concurrent
        self.rate_limit_delay = rate_limit_delay
        self.queue: List[ChunkTask] = []
        self.processing: Dict[str, ChunkTask] = {}
        self.completed: Dict[str, ChunkTask] = {}
        self.failed: Dict[str, ChunkTask] = {}
        self._processing_lock = asyncio.Lock()
        self.last_process_time = 0.0

    async def add_chunks(
        self, course_id: int, chunks_data: List[List[Dict[str, Any]]]
    ) -> List[str]:
        """
        Add chunks to the processing queue

        Args:
            course_id: Course ID
            chunks_data: List of chunk data (each chunk is a list of sections)

        Returns:
            List of chunk IDs
        """
        chunk_ids = []

        for i, chunk_data in enumerate(chunks_data):
            chunk_id = f"course_{course_id}_chunk_{i+1}"

            # Prioritize smaller chunks (they're more likely to succeed)
            total_activities = sum(
                len(section.get("activities", [])) for section in chunk_data
            )
            priority = 10 - min(
                total_activities, 9
            )  # Higher priority for smaller chunks

            task = ChunkTask(
                chunk_id=chunk_id,
                course_id=course_id,
                chunk_data=chunk_data,
                priority=priority,
            )

            self.queue.append(task)
            chunk_ids.append(chunk_id)

        # Sort queue by priority (higher priority first)
        self.queue.sort(key=lambda x: (-x.priority, x.created_at))

        logger.info(
            f"Added {len(chunks_data)} chunks to processing queue for course {course_id}"
        )
        return chunk_ids

    async def process_queue(
        self, plugin_client, progress_callback=None
    ) -> Dict[str, Any]:
        """
        Process all chunks in the queue

        Args:
            plugin_client: Enhanced Moodle client for processing
            progress_callback: Optional callback for progress updates

        Returns:
            Processing summary
        """
        logger.info(f"Starting queue processing with {len(self.queue)} chunks")

        # Create semaphore for concurrent processing
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Start processing tasks
        tasks = []
        while self.queue or self.processing:
            # Start new tasks if we have capacity and pending chunks
            while len(self.processing) < self.max_concurrent and self.queue:
                chunk_task = self.queue.pop(0)
                task = asyncio.create_task(
                    self._process_chunk_with_semaphore(
                        semaphore, chunk_task, plugin_client
                    )
                )
                tasks.append(task)
                self.processing[chunk_task.chunk_id] = chunk_task

            # Wait a bit for tasks to complete
            if tasks:
                done, pending = await asyncio.wait(
                    tasks, timeout=0.1, return_when=asyncio.FIRST_COMPLETED
                )

                # Remove completed tasks
                for task in done:
                    if task in tasks:
                        tasks.remove(task)

                # Update progress if callback provided
                if progress_callback:
                    total_chunks = (
                        len(self.completed)
                        + len(self.failed)
                        + len(self.processing)
                        + len(self.queue)
                    )
                    completed_chunks = len(self.completed) + len(self.failed)
                    await progress_callback(completed_chunks, total_chunks)

            # Break if no more work to do
            if not self.queue and not self.processing:
                break

            # Small delay to prevent busy waiting
            await asyncio.sleep(0.1)

        # Wait for any remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return self._generate_summary()

    async def _process_chunk_with_semaphore(
        self, semaphore: asyncio.Semaphore, chunk_task: ChunkTask, plugin_client
    ):
        """Process a single chunk with semaphore control"""
        async with semaphore:
            await self._process_single_chunk(chunk_task, plugin_client)

    async def _process_single_chunk(self, chunk_task: ChunkTask, plugin_client):
        """Process a single chunk"""
        chunk_task.status = ChunkStatus.PROCESSING
        chunk_task.started_at = time.time()

        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_process_time
            if time_since_last < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - time_since_last)

            self.last_process_time = time.time()

            logger.info(
                f"Processing chunk {chunk_task.chunk_id} (attempt {chunk_task.retry_count + 1})"
            )

            # Process the chunk
            result = await plugin_client.create_course_structure(
                chunk_task.course_id, chunk_task.chunk_data
            )

            if result.get("success"):
                chunk_task.status = ChunkStatus.COMPLETED
                chunk_task.result = result
                chunk_task.completed_at = time.time()

                # Move to completed
                async with self._processing_lock:
                    if chunk_task.chunk_id in self.processing:
                        del self.processing[chunk_task.chunk_id]
                    self.completed[chunk_task.chunk_id] = chunk_task

                logger.info(f"✅ Chunk {chunk_task.chunk_id} completed successfully")

            else:
                await self._handle_chunk_failure(
                    chunk_task, result.get("message", "Unknown error")
                )

        except Exception as e:
            await self._handle_chunk_failure(chunk_task, str(e))

    async def _handle_chunk_failure(self, chunk_task: ChunkTask, error_message: str):
        """Handle chunk processing failure"""
        chunk_task.retry_count += 1
        chunk_task.error_message = error_message

        if chunk_task.retry_count < chunk_task.max_retries:
            # Retry with exponential backoff
            chunk_task.status = ChunkStatus.RETRY
            delay = min(2**chunk_task.retry_count, 30)  # Max 30 seconds

            logger.warning(
                f"⚠️ Chunk {chunk_task.chunk_id} failed, retrying in {delay}s (attempt {chunk_task.retry_count + 1}/{chunk_task.max_retries})"
            )

            # Schedule retry
            await asyncio.sleep(delay)
            chunk_task.status = ChunkStatus.PENDING

            # Re-add to queue with lower priority
            chunk_task.priority = max(1, chunk_task.priority - 1)

            async with self._processing_lock:
                if chunk_task.chunk_id in self.processing:
                    del self.processing[chunk_task.chunk_id]
                self.queue.append(chunk_task)
                self.queue.sort(key=lambda x: (-x.priority, x.created_at))
        else:
            # Max retries reached
            chunk_task.status = ChunkStatus.FAILED
            chunk_task.completed_at = time.time()

            async with self._processing_lock:
                if chunk_task.chunk_id in self.processing:
                    del self.processing[chunk_task.chunk_id]
                self.failed[chunk_task.chunk_id] = chunk_task

            logger.error(
                f"❌ Chunk {chunk_task.chunk_id} failed permanently after {chunk_task.max_retries} attempts: {error_message}"
            )

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate processing summary"""
        total_chunks = len(self.completed) + len(self.failed)
        successful_chunks = len(self.completed)

        # Aggregate results from successful chunks
        total_sections = 0
        total_activities = 0
        successful_activities = 0

        for chunk_task in self.completed.values():
            if chunk_task.result:
                sections = chunk_task.result.get("sections", [])
                total_sections += len(sections)

                for section in sections:
                    section_activities = section.get("activities", [])
                    total_activities += len(section_activities)
                    successful_activities += sum(
                        1 for a in section_activities if a.get("success")
                    )

        # Calculate processing times
        processing_times = []
        for chunk_task in list(self.completed.values()) + list(self.failed.values()):
            if chunk_task.started_at and chunk_task.completed_at:
                processing_times.append(chunk_task.completed_at - chunk_task.started_at)

        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        summary = {
            "total_chunks": total_chunks,
            "successful_chunks": successful_chunks,
            "failed_chunks": len(self.failed),
            "success_rate": successful_chunks / total_chunks if total_chunks > 0 else 0,
            "total_sections": total_sections,
            "total_activities": total_activities,
            "successful_activities": successful_activities,
            "activity_success_rate": (
                successful_activities / total_activities if total_activities > 0 else 0
            ),
            "average_processing_time": avg_processing_time,
            "failed_chunk_details": [
                {
                    "chunk_id": task.chunk_id,
                    "error": task.error_message,
                    "retry_count": task.retry_count,
                }
                for task in self.failed.values()
            ],
        }

        return summary

    def get_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            "pending": len(self.queue),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "queue_tasks": [
                {
                    "chunk_id": task.chunk_id,
                    "priority": task.priority,
                    "status": task.status.value,
                    "retry_count": task.retry_count,
                }
                for task in self.queue
            ],
        }
