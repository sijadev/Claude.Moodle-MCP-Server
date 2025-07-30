"""
Content Parser for extracting code examples and topic descriptions from Claude chats
Handles parsing of chat messages to identify code blocks and topics
"""

import ast
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from src.core.constants import Messages, ContentTypes
from src.models.models import ChatContent, ContentItem

logger = logging.getLogger(__name__)


class ChatContentParser:
    """Parser for extracting structured content from Claude chat conversations"""

    def __init__(self):
        # Language detection patterns
        self.language_patterns = {
            "python": [
                r"def\s+\w+",
                r"import\s+\w+",
                r"from\s+\w+\s+import",
                r"if\s+__name__\s*==",
                r"class\s+\w+",
            ],
            "javascript": [
                r"function\s+\w+",
                r"const\s+\w+",
                r"let\s+\w+",
                r"var\s+\w+",
                r"=>",
                r"console\.log",
            ],
            "typescript": [
                r"interface\s+\w+",
                r"type\s+\w+",
                r":\s*\w+\[\]",
                r"async\s+function",
                r"Promise<",
            ],
            "java": [
                r"public\s+class",
                r"private\s+\w+",
                r"public\s+static\s+void\s+main",
                r"@\w+",
                r"System\.out",
            ],
            "cpp": [
                r"#include\s*<",
                r"int\s+main\s*\(",
                r"std::",
                r"cout\s*<<",
                r"endl",
            ],
            "c": [r"#include\s*<", r"int\s+main\s*\(", r"printf\s*\(", r"malloc\s*\("],
            "html": [r"<html", r"<div", r"<span", r"<!DOCTYPE", r"<body"],
            "css": [
                r"\.\w+\s*{",
                r"#\w+\s*{",
                r"@media",
                r"font-family:",
                r"background-color:",
            ],
            "sql": [
                r"SELECT\s+",
                r"FROM\s+",
                r"WHERE\s+",
                r"INSERT\s+INTO",
                r"CREATE\s+TABLE",
            ],
            "bash": [r"#!/bin/bash", r"\$\w+", r"echo\s+", r"grep\s+", r"awk\s+"],
            "json": [r'{\s*"', r':\s*"', r"}\s*,", r"\[\s*{"],
            "yaml": [r":\s*$", r"-\s+\w+", r"^\s*\w+:\s*\w+"],
            "xml": [r"<\?xml", r"<\w+[^>]*>", r"</\w+>"],
            "go": [r"package\s+\w+", r"func\s+\w+", r"import\s*\(", r"go\s+func"],
            "rust": [r"fn\s+\w+", r"let\s+\w+", r"match\s+\w+", r"impl\s+\w+"],
            "php": [r"<\?php", r"\$\w+", r"function\s+\w+", r"echo\s+"],
            "ruby": [r"def\s+\w+", r"class\s+\w+", r"puts\s+", r"@\w+"],
            "swift": [r"func\s+\w+", r"let\s+\w+", r"var\s+\w+", r"import\s+\w+"],
            "kotlin": [r"fun\s+\w+", r"val\s+\w+", r"var\s+\w+", r"class\s+\w+"],
            "r": [r"<-", r"library\s*\(", r"data\.frame", r"ggplot"],
            "matlab": [r"function\s+\w+", r"end\s*$", r"plot\s*\(", r"fprintf"],
            "scala": [r"def\s+\w+", r"val\s+\w+", r"object\s+\w+", r"case\s+class"],
        }

        # Topic keywords that indicate educational content
        self.topic_keywords = [
            "explanation",
            "tutorial",
            "guide",
            "overview",
            "introduction",
            "concept",
            "theory",
            "definition",
            "principle",
            "fundamental",
            "basic",
            "advanced",
            "example",
            "demonstration",
            "illustration",
            "summary",
            "conclusion",
            "key points",
            "important",
            "note that",
        ]

        # Code block patterns - more flexible with whitespace
        self.code_block_pattern = re.compile(r"```(\w+)?\s*(.*?)\s*```", re.DOTALL | re.MULTILINE)

        # Inline code pattern
        self.inline_code_pattern = re.compile(r"`([^`\n]+)`")

        # Topic section patterns
        self.topic_section_patterns = [
            re.compile(r"^#{1,3}\s+(.+)$", re.MULTILINE),  # Markdown headers
            re.compile(r"^(.+):$", re.MULTILINE),  # Colon-ended lines
            re.compile(r"^\*\*(.+)\*\*$", re.MULTILINE),  # Bold text lines
        ]

    def parse_chat(self, chat_content: str) -> ChatContent:
        """
        Parse chat content and extract code examples and topics

        Args:
            chat_content: Raw chat conversation content

        Returns:
            ChatContent object with extracted items
        """
        logger.info(Messages.PARSING_STARTED)

        # Split content into messages (assuming messages are separated by patterns)
        messages = self._split_into_messages(chat_content)

        items = []
        current_topic = None

        for message in messages:
            # Extract code blocks
            code_items = self._extract_code_blocks(message, current_topic)
            items.extend(code_items)

            # Extract topic descriptions
            topic_items = self._extract_topic_descriptions(message)
            items.extend(topic_items)

            # Update current topic context
            detected_topic = self._detect_topic_context(message)
            if detected_topic:
                current_topic = detected_topic

        # Post-process to remove duplicates and organize
        items = self._deduplicate_and_organize(items)

        logger.info(Messages.PARSING_COMPLETED.format(count=len(items)))
        return ChatContent(items=items)

    def _split_into_messages(self, content: str) -> List[str]:
        """Split content into individual messages"""
        # Try to detect message boundaries
        patterns = [
            r"\n\n(?=\w)",  # Double newline followed by word
            r"\n(?=Human:|Assistant:|Claude:)",  # Chat participant indicators
            r"\n(?=\d+\.)",  # Numbered items
            r"\n(?=-{3,})",  # Horizontal rules
        ]

        # Split by the most appropriate pattern
        for pattern in patterns:
            split_content = re.split(pattern, content)
            if len(split_content) > 1:
                return [msg.strip() for msg in split_content if msg.strip()]

        # Fallback: split by paragraphs
        return [para.strip() for para in content.split("\n\n") if para.strip()]

    def _extract_code_blocks(
        self, message: str, current_topic: Optional[str] = None
    ) -> List[ContentItem]:
        """Extract code blocks from a message"""
        code_items = []

        # Extract fenced code blocks
        for match in self.code_block_pattern.finditer(message):
            language = match.group(1) or "text"
            code_content = match.group(2).strip()

            if not code_content:
                continue

            # Auto-detect language if not specified
            if language == "text" or not language:
                language = self._detect_language(code_content)

            # Generate title and description
            title, description = self._generate_code_metadata(code_content, language, message)

            code_item = ContentItem(
                type="code",
                title=title,
                content=code_content,
                description=description,
                language=language,
                topic=current_topic or self._infer_topic_from_context(message),
            )

            code_items.append(code_item)

        # Extract significant inline code snippets
        inline_code_items = self._extract_inline_code(message, current_topic)
        code_items.extend(inline_code_items)

        return code_items

    def _extract_inline_code(
        self, message: str, current_topic: Optional[str] = None
    ) -> List[ContentItem]:
        """Extract significant inline code snippets"""
        inline_items = []

        for match in self.inline_code_pattern.finditer(message):
            code_content = match.group(1).strip()

            # Only include substantial inline code (not single words or short snippets)
            if len(code_content) < 10 or len(code_content.split()) < 3:
                continue

            # Skip if it looks like a variable name or simple reference
            if re.match(r"^\w+$", code_content) or code_content.count(" ") == 0:
                continue

            language = self._detect_language(code_content)
            title, description = self._generate_code_metadata(code_content, language, message)

            inline_item = ContentItem(
                type="code",
                title=f"Inline: {title}",
                content=code_content,
                description=description,
                language=language,
                topic=current_topic or self._infer_topic_from_context(message),
            )

            inline_items.append(inline_item)

        return inline_items

    def _detect_language(self, code: str) -> str:
        """Detect programming language from code content"""
        code_lower = code.lower()

        # Score each language based on pattern matches
        scores = {}
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, code, re.IGNORECASE | re.MULTILINE))
                score += matches

            if score > 0:
                scores[language] = score

        # Return language with highest score
        if scores:
            return max(scores.keys(), key=lambda k: scores[k])

        return "text"

    def _generate_code_metadata(self, code: str, language: str, context: str) -> Tuple[str, str]:
        """Generate title and description for code"""
        lines = code.strip().split("\n")

        # Try to extract title from context
        title = self._extract_title_from_context(context, code)

        if not title:
            # Generate title based on code content
            if language == "python":
                title = self._extract_python_title(code)
            elif language in ["javascript", "typescript"]:
                title = self._extract_js_title(code)
            elif language == "java":
                title = self._extract_java_title(code)
            else:
                # Generic title generation
                if len(lines) == 1:
                    title = f"{language.title()} One-liner"
                else:
                    title = f"{language.title()} Code Block"

        # Generate description
        description = self._generate_code_description(code, language, context)

        return title, description

    def _extract_title_from_context(self, context: str, code: str) -> Optional[str]:
        """Extract title from surrounding context"""
        # Look for patterns like "Here's a function that..." or "This code does..."
        patterns = [
            r"(?:here's|this is|here is)\s+(?:a|an|the)\s+([^.]+?)\s+(?:that|which|to)",
            r"(?:function|method|class|script)\s+(?:called|named)\s+(\w+)",
            r"(?:example|sample)\s+(?:of|for)\s+([^.]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        return None

    def _extract_python_title(self, code: str) -> str:
        """Extract title from Python code"""
        # Try to parse and extract function/class names
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    return f"Function: {node.name}"
                elif isinstance(node, ast.ClassDef):
                    return f"Class: {node.name}"
        except:
            pass

        # Fallback to first line or generic title
        first_line = code.split("\n")[0].strip()
        if first_line.startswith("def "):
            func_name = re.search(r"def\s+(\w+)", first_line)
            if func_name:
                return f"Function: {func_name.group(1)}"
        elif first_line.startswith("class "):
            class_name = re.search(r"class\s+(\w+)", first_line)
            if class_name:
                return f"Class: {class_name.group(1)}"

        return "Python Code"

    def _extract_js_title(self, code: str) -> str:
        """Extract title from JavaScript/TypeScript code"""
        # Look for function declarations
        func_match = re.search(r"function\s+(\w+)", code)
        if func_match:
            return f"Function: {func_match.group(1)}"

        # Look for arrow functions assigned to variables
        arrow_match = re.search(r"(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>", code)
        if arrow_match:
            return f"Function: {arrow_match.group(1)}"

        # Look for class declarations
        class_match = re.search(r"class\s+(\w+)", code)
        if class_match:
            return f"Class: {class_match.group(1)}"

        return "JavaScript Code"

    def _extract_java_title(self, code: str) -> str:
        """Extract title from Java code"""
        # Look for class declarations
        class_match = re.search(r"(?:public\s+)?class\s+(\w+)", code)
        if class_match:
            return f"Class: {class_match.group(1)}"

        # Look for method declarations
        method_match = re.search(
            r"(?:public|private|protected)?\s*(?:static\s+)?[A-Za-z<>\[\]]+\s+(\w+)\s*\(",
            code,
        )
        if method_match:
            return f"Method: {method_match.group(1)}"

        return "Java Code"

    def _generate_code_description(self, code: str, language: str, context: str) -> str:
        """Generate description for code"""
        lines = code.strip().split("\n")
        line_count = len(lines)

        # Extract comments from code
        comments = self._extract_comments(code, language)

        # Build description
        description_parts = []

        if comments:
            description_parts.append(f"Description: {comments[0]}")

        description_parts.append(f"Language: {language.title()}")
        description_parts.append(f"Lines of code: {line_count}")

        # Add context if available
        if context and len(context) > len(code):
            context_snippet = context.replace(code, "").strip()[:100]
            if context_snippet:
                description_parts.append(f"Context: {context_snippet}...")

        return " | ".join(description_parts)

    def _extract_comments(self, code: str, language: str) -> List[str]:
        """Extract comments from code"""
        comments = []

        comment_patterns = {
            "python": [r"#\s*(.+)"],
            "javascript": [r"//\s*(.+)", r"/\*\s*(.*?)\s*\*/"],
            "typescript": [r"//\s*(.+)", r"/\*\s*(.*?)\s*\*/"],
            "java": [r"//\s*(.+)", r"/\*\s*(.*?)\s*\*/"],
            "cpp": [r"//\s*(.+)", r"/\*\s*(.*?)\s*\*/"],
            "c": [r"//\s*(.+)", r"/\*\s*(.*?)\s*\*/"],
            "css": [r"/\*\s*(.*?)\s*\*/"],
            "html": [r"<!--\s*(.*?)\s*-->"],
            "sql": [r"--\s*(.+)"],
            "bash": [r"#\s*(.+)"],
        }

        if language in comment_patterns:
            for pattern in comment_patterns[language]:
                matches = re.findall(pattern, code, re.DOTALL)
                comments.extend([match.strip() for match in matches if match.strip()])

        return comments

    def _extract_topic_descriptions(self, message: str) -> List[ContentItem]:
        """Extract topic descriptions and explanations"""
        topic_items = []

        # Look for educational content patterns
        paragraphs = message.split("\n\n")

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph or len(paragraph) < 50:  # Skip short paragraphs
                continue

            # Skip code blocks
            if "```" in paragraph or paragraph.startswith("`"):
                continue

            # Check if paragraph contains topic-related keywords
            if self._is_topic_description(paragraph):
                title = self._extract_topic_title(paragraph)
                topic = self._infer_topic_from_content(paragraph)

                topic_item = ContentItem(
                    type="topic",
                    title=title,
                    content=paragraph,
                    description=(
                        f"Educational content about {topic}" if topic else "Topic description"
                    ),
                    language=None,
                    topic=topic,
                )

                topic_items.append(topic_item)

        return topic_items

    def _is_topic_description(self, text: str) -> bool:
        """Check if text is a topic description"""
        text_lower = text.lower()

        # Check for topic keywords
        keyword_count = sum(1 for keyword in self.topic_keywords if keyword in text_lower)

        # Check for explanatory phrases
        explanatory_phrases = [
            "this means",
            "in other words",
            "for example",
            "that is",
            "it works by",
            "the idea is",
            "the concept",
            "basically",
            "essentially",
            "fundamentally",
            "the purpose",
            "the goal",
        ]

        phrase_count = sum(1 for phrase in explanatory_phrases if phrase in text_lower)

        # Heuristic: if text has educational keywords or explanatory phrases
        return keyword_count > 0 or phrase_count > 0 or self._has_educational_structure(text)

    def _has_educational_structure(self, text: str) -> bool:
        """Check if text has educational structure"""
        # Look for numbered lists, bullet points, step-by-step instructions
        patterns = [
            r"^\d+\.",  # Numbered lists
            r"^\s*[-*•]",  # Bullet points
            r"first|second|third|finally|next|then",  # Sequential words
            r"step \d+",  # Step references
        ]

        for pattern in patterns:
            if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                return True

        return False

    def _extract_topic_title(self, content: str) -> str:
        """Extract title from topic content"""
        # Try to extract from first sentence
        first_sentence = content.split(".")[0].strip()

        # Look for header-like patterns
        for pattern in self.topic_section_patterns:
            match = pattern.search(content)
            if match:
                return match.group(1).strip()

        # Fallback: use first few words
        words = first_sentence.split()[:6]
        title = " ".join(words)

        if len(title) > 50:
            title = title[:50] + "..."

        return title or "Topic Description"

    def _detect_topic_context(self, message: str) -> Optional[str]:
        """Detect the main topic being discussed"""
        # Look for explicit topic declarations
        topic_patterns = [
            r"(?:about|regarding|concerning)\s+([^.]+)",
            r"(?:topic|subject|theme):\s*([^.\n]+)",
            r"(?:let\'s discuss|talking about|focusing on)\s+([^.]+)",
        ]

        for pattern in topic_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return self._infer_topic_from_content(message)

    def _infer_topic_from_context(self, context: str) -> Optional[str]:
        """Infer topic from surrounding context"""
        return self._infer_topic_from_content(context)

    def _infer_topic_from_content(self, content: str) -> Optional[str]:
        """Infer topic from content using keyword analysis"""
        content_lower = content.lower()

        # Technology and programming topics
        tech_topics = {
            "web development": [
                "html",
                "css",
                "javascript",
                "react",
                "vue",
                "angular",
                "frontend",
                "backend",
            ],
            "python programming": ["python", "django", "flask", "pandas", "numpy"],
            "data science": [
                "machine learning",
                "data analysis",
                "statistics",
                "pandas",
                "numpy",
            ],
            "database": ["sql", "database", "mysql", "postgresql", "mongodb"],
            "mobile development": ["android", "ios", "swift", "kotlin", "react native"],
            "devops": ["docker", "kubernetes", "ci/cd", "deployment", "aws", "cloud"],
            "algorithms": [
                "algorithm",
                "sorting",
                "searching",
                "complexity",
                "data structure",
            ],
        }

        # Score topics based on keyword matches
        topic_scores = {}
        for topic, keywords in tech_topics.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                topic_scores[topic] = score

        # Return highest scoring topic
        if topic_scores:
            return max(topic_scores.keys(), key=lambda k: topic_scores[k])

        return None

    def _deduplicate_and_organize(self, items: List[ContentItem]) -> List[ContentItem]:
        """Remove duplicates and organize content items"""
        # Remove duplicate code blocks
        seen_code = set()
        unique_items = []

        for item in items:
            if item.type == "code":
                # Create hash of code content for deduplication
                code_hash = hash(item.content.strip())
                if code_hash not in seen_code:
                    seen_code.add(code_hash)
                    unique_items.append(item)
            else:
                # For topics, check for similar content
                is_duplicate = False
                for existing_item in unique_items:
                    if existing_item.type == "topic" and self._are_similar_topics(
                        item.content, existing_item.content
                    ):
                        is_duplicate = True
                        break

                if not is_duplicate:
                    unique_items.append(item)

        return unique_items

    def _are_similar_topics(self, content1: str, content2: str, threshold: float = 0.8) -> bool:
        """Check if two topic contents are similar"""
        # Simple similarity check based on word overlap
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return False

        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))

        similarity = overlap / union if union > 0 else 0
        return similarity >= threshold
