#!/usr/bin/env python3
"""
Command System for MoodleClaude
Implements Command pattern for session operations with undo support
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from .dependency_injection import ServiceLifetime, service
from .event_system import publish_session_failed
from .interfaces import (
    CommandResult,
    IContentProcessor,
    IEventPublisher,
    IMoodleClient,
    ISessionCommand,
)

logger = logging.getLogger(__name__)


class CommandStatus(Enum):
    """Command execution status"""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    UNDONE = "undone"


class CommandContext:
    """Context information for command execution"""

    def __init__(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.metadata = metadata or {}
        self.execution_id = str(uuid.uuid4())
        self.timestamp = datetime.now()


class BaseCommand(ISessionCommand):
    """Base class for all commands"""

    def __init__(self, context: CommandContext):
        self.context = context
        self.command_id = str(uuid.uuid4())
        self.status = CommandStatus.PENDING
        self.created_at = datetime.now()
        self.executed_at: Optional[datetime] = None
        self.execution_time: Optional[float] = None
        self.result: Optional[CommandResult] = None
        self.error: Optional[Exception] = None

    async def execute(self, session_data: Dict[str, Any]) -> CommandResult:
        """Execute the command with timing and error handling"""
        self.status = CommandStatus.EXECUTING
        self.executed_at = datetime.now()

        try:
            start_time = datetime.now()
            result = await self._execute_impl(session_data)
            end_time = datetime.now()

            self.execution_time = (end_time - start_time).total_seconds()
            self.result = result
            self.status = (
                CommandStatus.COMPLETED if result.success else CommandStatus.FAILED
            )

            logger.debug(
                f"Command {self.__class__.__name__} executed in {self.execution_time:.3f}s"
            )
            return result

        except Exception as e:
            self.error = e
            self.status = CommandStatus.FAILED
            logger.error(f"Command {self.__class__.__name__} failed: {e}")

            return CommandResult(
                success=False,
                message=f"Command execution failed: {str(e)}",
                data={"command_id": self.command_id, "error": str(e)},
            )

    async def undo(self, session_data: Dict[str, Any]) -> CommandResult:
        """Undo the command if possible"""
        if self.status != CommandStatus.COMPLETED:
            return CommandResult(
                success=False,
                message="Cannot undo command that was not successfully completed",
            )

        try:
            result = await self._undo_impl(session_data)
            if result.success:
                self.status = CommandStatus.UNDONE
            return result

        except Exception as e:
            logger.error(f"Failed to undo command {self.__class__.__name__}: {e}")
            return CommandResult(
                success=False,
                message=f"Undo failed: {str(e)}",
                data={"command_id": self.command_id, "error": str(e)},
            )

    async def _execute_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Implement the actual command logic"""
        raise NotImplementedError("Subclasses must implement _execute_impl")

    async def _undo_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Implement the undo logic (optional)"""
        return CommandResult(
            success=False, message=f"Undo not supported for {self.__class__.__name__}"
        )

    def get_info(self) -> Dict[str, Any]:
        """Get command information"""
        return {
            "command_id": self.command_id,
            "command_type": self.__class__.__name__,
            "status": self.status.value,
            "session_id": self.context.session_id,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_time": self.execution_time,
            "success": self.result.success if self.result else None,
            "error": str(self.error) if self.error else None,
        }


class CreateCourseCommand(BaseCommand):
    """Command to create a Moodle course"""

    def __init__(
        self,
        context: CommandContext,
        moodle_client: IMoodleClient,
        course_name: str,
        course_description: str = "",
    ):
        super().__init__(context)
        self.moodle_client = moodle_client
        self.course_name = course_name
        self.course_description = course_description
        self.created_course_id: Optional[int] = None

    async def _execute_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Create the Moodle course"""
        try:
            course_id = await self.moodle_client.create_course(
                name=self.course_name, description=self.course_description
            )

            self.created_course_id = course_id

            return CommandResult(
                success=True,
                message=f"Course '{self.course_name}' created successfully",
                data={
                    "course_id": course_id,
                    "course_name": self.course_name,
                    "command_id": self.command_id,
                },
            )

        except Exception as e:
            logger.error(f"Failed to create course '{self.course_name}': {e}")
            raise

    async def _undo_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Delete the created course (if supported by Moodle client)"""
        if not self.created_course_id:
            return CommandResult(success=False, message="No course ID to undo")

        # Note: This would require implementing course deletion in the Moodle client
        # For now, we just log the undo attempt
        logger.warning(
            f"Undo requested for course creation (ID: {self.created_course_id}). Manual cleanup may be required."
        )

        return CommandResult(
            success=True,
            message=f"Course creation undo logged (manual cleanup may be required for course ID: {self.created_course_id})",
            data={"course_id": self.created_course_id},
        )


class CreateCourseStructureCommand(BaseCommand):
    """Command to create course structure with sections and activities"""

    def __init__(
        self,
        context: CommandContext,
        moodle_client: IMoodleClient,
        course_id: int,
        sections_data: List[Dict[str, Any]],
    ):
        super().__init__(context)
        self.moodle_client = moodle_client
        self.course_id = course_id
        self.sections_data = sections_data
        self.created_sections: List[int] = []

    async def _execute_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Create the course structure"""
        try:
            result = await self.moodle_client.create_course_structure(
                course_id=self.course_id, sections_data=self.sections_data
            )

            # Extract created section IDs for undo support
            if "sections" in result:
                self.created_sections = [
                    s.get("id") for s in result["sections"] if s.get("id")
                ]

            return CommandResult(
                success=True,
                message=f"Course structure created with {len(self.sections_data)} sections",
                data={
                    "course_id": self.course_id,
                    "sections_created": len(self.sections_data),
                    "structure_result": result,
                    "command_id": self.command_id,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to create course structure for course {self.course_id}: {e}"
            )
            raise

    async def _undo_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Undo course structure creation (limited support)"""
        logger.warning(
            f"Undo requested for course structure creation (Course ID: {self.course_id}). Manual cleanup may be required."
        )

        return CommandResult(
            success=True,
            message=f"Course structure creation undo logged (manual cleanup may be required for course ID: {self.course_id})",
            data={"course_id": self.course_id, "sections": self.created_sections},
        )


class ProcessContentCommand(BaseCommand):
    """Command to process content using content processor"""

    def __init__(
        self,
        context: CommandContext,
        content_processor: IContentProcessor,
        content: str,
    ):
        super().__init__(context)
        self.content_processor = content_processor
        self.content = content
        self.session_id_created: Optional[str] = None

    async def _execute_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Process the content"""
        try:
            session_id = await self.content_processor.create_session(
                content=self.content,
                course_name=session_data.get("course_name", "Untitled Course"),
            )

            self.session_id_created = session_id

            return CommandResult(
                success=True,
                message="Content processing session created",
                data={
                    "session_id": session_id,
                    "content_length": len(self.content),
                    "command_id": self.command_id,
                },
            )

        except Exception as e:
            logger.error(f"Failed to process content: {e}")
            raise


class ValidateCourseCommand(BaseCommand):
    """Command to validate course creation"""

    def __init__(
        self,
        context: CommandContext,
        moodle_client: IMoodleClient,
        course_id: int,
        expected_sections: int,
    ):
        super().__init__(context)
        self.moodle_client = moodle_client
        self.course_id = course_id
        self.expected_sections = expected_sections

    async def _execute_impl(self, session_data: Dict[str, Any]) -> CommandResult:
        """Validate the course"""
        try:
            sections = await self.moodle_client.get_course_sections(self.course_id)
            actual_sections = len(sections)

            is_valid = actual_sections >= self.expected_sections

            return CommandResult(
                success=is_valid,
                message=f"Course validation {'passed' if is_valid else 'failed'}",
                data={
                    "course_id": self.course_id,
                    "expected_sections": self.expected_sections,
                    "actual_sections": actual_sections,
                    "validation_passed": is_valid,
                    "command_id": self.command_id,
                },
            )

        except Exception as e:
            logger.error(f"Failed to validate course {self.course_id}: {e}")
            raise


@service(ISessionCommand, ServiceLifetime.TRANSIENT)
class CommandExecutor:
    """
    Command executor that manages command execution with history and undo support
    """

    def __init__(self, event_publisher: Optional[IEventPublisher] = None):
        self.event_publisher = event_publisher
        self._command_history: List[BaseCommand] = []
        self._max_history = 100

    async def execute_command(
        self, command: BaseCommand, session_data: Dict[str, Any]
    ) -> CommandResult:
        """
        Execute a command and add it to history

        Args:
            command: The command to execute
            session_data: Session data context
        """
        try:
            result = await command.execute(session_data)

            # Add to history
            self._add_to_history(command)

            # Publish event if command failed
            if not result.success and self.event_publisher:
                await publish_session_failed(
                    self.event_publisher,
                    command.context.session_id,
                    {
                        "command_type": command.__class__.__name__,
                        "command_id": command.command_id,
                        "error": result.message,
                    },
                )

            return result

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            if self.event_publisher:
                await publish_session_failed(
                    self.event_publisher,
                    command.context.session_id,
                    {
                        "command_type": command.__class__.__name__,
                        "command_id": command.command_id,
                        "error": str(e),
                    },
                )
            raise

    async def execute_commands(
        self, commands: List[BaseCommand], session_data: Dict[str, Any]
    ) -> List[CommandResult]:
        """
        Execute multiple commands in sequence

        Args:
            commands: List of commands to execute
            session_data: Session data context
        """
        results = []

        for command in commands:
            try:
                result = await self.execute_command(command, session_data)
                results.append(result)

                # Stop on first failure if command is critical
                if not result.success and getattr(command, "critical", True):
                    logger.warning(
                        f"Critical command failed, stopping execution: {command.__class__.__name__}"
                    )
                    break

            except Exception as e:
                logger.error(f"Command execution failed, stopping: {e}")
                results.append(
                    CommandResult(
                        success=False,
                        message=f"Command execution failed: {str(e)}",
                        data={
                            "command_type": command.__class__.__name__,
                            "error": str(e),
                        },
                    )
                )
                break

        return results

    async def undo_last_command(self, session_data: Dict[str, Any]) -> CommandResult:
        """Undo the last executed command"""
        if not self._command_history:
            return CommandResult(success=False, message="No commands to undo")

        last_command = self._command_history[-1]
        if last_command.status != CommandStatus.COMPLETED:
            return CommandResult(
                success=False, message="Last command was not successfully completed"
            )

        result = await last_command.undo(session_data)
        return result

    async def undo_commands_for_session(
        self, session_id: str, session_data: Dict[str, Any]
    ) -> List[CommandResult]:
        """Undo all commands for a specific session"""
        session_commands = [
            cmd for cmd in self._command_history if cmd.context.session_id == session_id
        ]
        session_commands.reverse()  # Undo in reverse order

        results = []
        for command in session_commands:
            if command.status == CommandStatus.COMPLETED:
                result = await command.undo(session_data)
                results.append(result)

        return results

    def get_command_history(
        self, session_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get command execution history"""
        commands = self._command_history

        if session_id:
            commands = [cmd for cmd in commands if cmd.context.session_id == session_id]

        # Return latest commands up to limit
        recent_commands = commands[-limit:] if limit > 0 else commands
        return [cmd.get_info() for cmd in recent_commands]

    def get_statistics(self) -> Dict[str, Any]:
        """Get command execution statistics"""
        if not self._command_history:
            return {"total_commands": 0}

        total = len(self._command_history)
        completed = sum(
            1 for cmd in self._command_history if cmd.status == CommandStatus.COMPLETED
        )
        failed = sum(
            1 for cmd in self._command_history if cmd.status == CommandStatus.FAILED
        )

        execution_times = [
            cmd.execution_time for cmd in self._command_history if cmd.execution_time
        ]
        avg_execution_time = (
            sum(execution_times) / len(execution_times) if execution_times else 0
        )

        command_types = {}
        for cmd in self._command_history:
            cmd_type = cmd.__class__.__name__
            command_types[cmd_type] = command_types.get(cmd_type, 0) + 1

        return {
            "total_commands": total,
            "completed_commands": completed,
            "failed_commands": failed,
            "success_rate": (completed / total) * 100 if total > 0 else 0,
            "average_execution_time": avg_execution_time,
            "command_types": command_types,
        }

    def _add_to_history(self, command: BaseCommand) -> None:
        """Add command to history with size limit"""
        self._command_history.append(command)

        # Maintain history size limit
        if len(self._command_history) > self._max_history:
            self._command_history = self._command_history[-self._max_history :]

    def clear_history(self) -> None:
        """Clear command history"""
        self._command_history.clear()
        logger.info("Command history cleared")
