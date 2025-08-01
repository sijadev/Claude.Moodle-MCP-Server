"""
Content chunker for handling large conversations
Splits large content into manageable pieces for course creation
"""

import logging
from typing import Any, Dict, List

from src.models.models import ChatContent, CourseStructure

logger = logging.getLogger(__name__)


class ContentChunker:
    """Handles chunking of large content for course creation"""

    def __init__(self, max_section_size: int = 10, max_content_length: int = 30000):
        """
        Initialize content chunker

        Args:
            max_section_size: Maximum number of items per section
            max_content_length: Maximum character length for content items
        """
        self.max_section_size = max_section_size
        self.max_content_length = max_content_length

    def chunk_course_structure(
        self, course_structure: CourseStructure
    ) -> List[CourseStructure]:
        """
        Split large course structure into smaller chunks

        Args:
            course_structure: Original course structure

        Returns:
            List of smaller course structures
        """
        chunks = []

        for section in course_structure.sections:
            # Split large sections
            if len(section.items) > self.max_section_size:
                logger.info(
                    f"Chunking large section '{section.name}' with {len(section.items)} items"
                )

                # Split items into smaller groups
                item_chunks = []
                for i in range(0, len(section.items), self.max_section_size):
                    chunk_items = section.items[i : i + self.max_section_size]
                    item_chunks.append(chunk_items)

                # Create separate sections for each chunk
                for i, chunk_items in enumerate(item_chunks):
                    chunk_section = CourseStructure.Section(
                        name=f"{section.name} (Part {i+1})",
                        description=f"{section.description} - Part {i+1} of {len(item_chunks)}",
                        items=chunk_items,
                    )

                    chunk_structure = CourseStructure(sections=[chunk_section])
                    chunks.append(chunk_structure)
            else:
                # Check for oversized content items
                processed_items = []
                for item in section.items:
                    if len(item.content) > self.max_content_length:
                        logger.info(
                            f"Chunking large content item '{item.title}' ({len(item.content)} chars)"
                        )

                        # Split large content into smaller pieces
                        content_chunks = self._split_content(
                            item.content, self.max_content_length
                        )

                        for j, content_chunk in enumerate(content_chunks):
                            chunked_item = type(item)(
                                title=f"{item.title} (Part {j+1})",
                                content=content_chunk,
                                type=item.type,
                                language=getattr(item, "language", None),
                                topic=item.topic,
                                description=(
                                    f"{item.description or ''} - Part {j+1} of {len(content_chunks)}"
                                    if item.description
                                    else f"Part {j+1} of {len(content_chunks)}"
                                ),
                            )
                            processed_items.append(chunked_item)
                    else:
                        processed_items.append(item)

                # Create section with processed items
                processed_section = CourseStructure.Section(
                    name=section.name,
                    description=section.description,
                    items=processed_items,
                )

                chunk_structure = CourseStructure(sections=[processed_section])
                chunks.append(chunk_structure)

        logger.info(f"Split course structure into {len(chunks)} chunks")
        return chunks

    def _split_content(self, content: str, max_length: int) -> List[str]:
        """
        Split content into smaller pieces at logical boundaries

        Args:
            content: Content to split
            max_length: Maximum length per chunk

        Returns:
            List of content chunks
        """
        if len(content) <= max_length:
            return [content]

        chunks = []
        current_chunk = ""

        # Try to split at paragraph boundaries first
        paragraphs = content.split("\n\n")

        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit
            if len(current_chunk) + len(paragraph) + 2 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    # Single paragraph is too large, split by sentences
                    sentence_chunks = self._split_by_sentences(paragraph, max_length)
                    chunks.extend(sentence_chunks[:-1])
                    current_chunk = sentence_chunks[-1] if sentence_chunks else ""
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _split_by_sentences(self, text: str, max_length: int) -> List[str]:
        """Split text by sentences when paragraphs are too large"""
        import re

        # Simple sentence boundary detection
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Even single sentence is too large, split by words
                    word_chunks = self._split_by_words(sentence, max_length)
                    chunks.extend(word_chunks[:-1])
                    current_chunk = word_chunks[-1] if word_chunks else ""
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _split_by_words(self, text: str, max_length: int) -> List[str]:
        """Split text by words as last resort"""
        words = text.split()
        chunks = []
        current_chunk = ""

        for word in words:
            if len(current_chunk) + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = word
                else:
                    # Single word is too large, truncate it
                    chunks.append(word[: max_length - 3] + "...")
                    current_chunk = ""
            else:
                if current_chunk:
                    current_chunk += " " + word
                else:
                    current_chunk = word

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
