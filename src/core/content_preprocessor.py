"""
Content preprocessor for Moodle API compatibility
Handles parameter sanitization, encoding issues, and size optimization
"""

import re
import html
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ContentPreprocessor:
    """Preprocesses content for Moodle API compatibility"""
    
    def __init__(self):
        # Response size patterns from log analysis
        self.SUCCESS_RESPONSE_MIN = 300  # 327+ bytes = success
        self.ERROR_RESPONSE_SIZE = 119   # 119 bytes = parameter error
        self.MAX_SINGLE_PARAM_SIZE = 16000  # Conservative limit
        self.MAX_TOTAL_PAYLOAD_SIZE = 32000  # Total request size limit
        
        # Problematic characters from logs
        self.EMOJI_PATTERN = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]')
        self.HIGH_UNICODE_PATTERN = re.compile(r'[^\x00-\x7F\u00A0-\u017F\u0100-\u024F]')
        
    def sanitize_sections_data(self, sections_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitize sections data for Moodle API compatibility
        
        Args:
            sections_data: Raw sections data
            
        Returns:
            Sanitized sections data
        """
        logger.info(f"Preprocessing {len(sections_data)} sections for API compatibility")
        
        sanitized_sections = []
        total_payload_size = 0
        
        for i, section in enumerate(sections_data):
            sanitized_section = self._sanitize_section(section, i)
            
            # Calculate section size
            section_size = self._calculate_section_size(sanitized_section)
            total_payload_size += section_size
            
            # Check if we're approaching total payload limit
            if total_payload_size > self.MAX_TOTAL_PAYLOAD_SIZE:
                logger.warning(f"Payload size limit reached at section {i}. Truncating remaining sections.")
                break
                
            sanitized_sections.append(sanitized_section)
            logger.debug(f"Section {i}: {section_size} bytes, total: {total_payload_size} bytes")
        
        logger.info(f"Preprocessed {len(sanitized_sections)} sections, total size: {total_payload_size} bytes")
        return sanitized_sections
    
    def _sanitize_section(self, section: Dict[str, Any], section_index: int) -> Dict[str, Any]:
        """Sanitize a single section"""
        sanitized = {
            'name': self._sanitize_text(section.get('name', f'Section {section_index + 1}')),
            'summary': self._sanitize_html(section.get('summary', '')),
            'activities': []
        }
        
        for j, activity in enumerate(section.get('activities', [])):
            sanitized_activity = self._sanitize_activity(activity, section_index, j)
            
            # Check activity size
            activity_size = self._calculate_activity_size(sanitized_activity)
            if activity_size > self.MAX_SINGLE_PARAM_SIZE:
                logger.warning(f"Activity {j} in section {section_index} too large ({activity_size} bytes). Truncating.")
                sanitized_activity = self._truncate_activity(sanitized_activity)
            
            sanitized['activities'].append(sanitized_activity)
        
        return sanitized
    
    def _sanitize_activity(self, activity: Dict[str, Any], section_idx: int, activity_idx: int) -> Dict[str, Any]:
        """Sanitize a single activity"""
        activity_type = activity.get('type', 'page')
        
        sanitized = {
            'type': self._sanitize_text(activity_type),
            'name': self._sanitize_text(activity.get('name', f'Activity {activity_idx + 1}')),
            'content': self._sanitize_content(activity.get('content', ''), activity_type),
            'filename': self._sanitize_filename(activity.get('filename', ''))
        }
        
        return sanitized
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize plain text fields"""
        if not text:
            return ''
        
        # Remove emojis and high unicode characters
        text = self.EMOJI_PATTERN.sub('', text)
        text = self.HIGH_UNICODE_PATTERN.sub('?', text)
        
        # HTML escape for safety
        text = html.escape(text, quote=False)
        
        # Limit length for text fields
        if len(text) > 250:
            text = text[:247] + '...'
        
        return text.strip()
    
    def _sanitize_html(self, html_content: str) -> str:
        """Sanitize HTML content"""
        if not html_content:
            return ''
        
        # Remove emojis but preserve HTML structure
        html_content = self.EMOJI_PATTERN.sub('[emoji]', html_content)
        
        # Replace problematic unicode with placeholders
        html_content = self.HIGH_UNICODE_PATTERN.sub('?', html_content)
        
        # Remove potentially problematic HTML attributes
        html_content = re.sub(r'(on\w+)=["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'javascript:', '', html_content, flags=re.IGNORECASE)
        
        return html_content.strip()
    
    def _sanitize_content(self, content: str, activity_type: str) -> str:
        """Sanitize activity content based on type"""
        if not content:
            return ''
        
        if activity_type == 'file':
            # For file content, be more conservative
            content = self.EMOJI_PATTERN.sub('', content)
            content = self.HIGH_UNICODE_PATTERN.sub('?', content)
            # Keep code content readable
            content = content.replace('\r\n', '\n').replace('\r', '\n')
        else:
            # For page content (HTML)
            content = self._sanitize_html(content)
        
        # Apply size limits
        if len(content) > self.MAX_SINGLE_PARAM_SIZE:
            logger.warning(f"Content too large ({len(content)} bytes), truncating to {self.MAX_SINGLE_PARAM_SIZE}")
            content = content[:self.MAX_SINGLE_PARAM_SIZE - 100] + '\n\n[Content truncated due to size limits]'
        
        return content
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename"""
        if not filename:
            return ''
        
        # Remove emojis and special characters
        filename = self.EMOJI_PATTERN.sub('', filename)
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ensure reasonable length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:95] + ('.' + ext if ext else '')
        
        return filename
    
    def _calculate_section_size(self, section: Dict[str, Any]) -> int:
        """Calculate approximate size of a section in bytes"""
        size = len(str(section.get('name', ''))) + len(str(section.get('summary', '')))
        
        for activity in section.get('activities', []):
            size += self._calculate_activity_size(activity)
        
        return size
    
    def _calculate_activity_size(self, activity: Dict[str, Any]) -> int:
        """Calculate approximate size of an activity in bytes"""
        return (
            len(str(activity.get('type', ''))) +
            len(str(activity.get('name', ''))) +
            len(str(activity.get('content', ''))) +
            len(str(activity.get('filename', '')))
        )
    
    def _truncate_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Truncate activity content to fit size limits"""
        content = activity.get('content', '')
        
        if len(content) > self.MAX_SINGLE_PARAM_SIZE:
            # Try to truncate at logical boundaries
            truncate_size = self.MAX_SINGLE_PARAM_SIZE - 200  # Leave room for truncation message
            
            if activity.get('type') == 'page':
                # For HTML, try to truncate at tag boundaries
                truncated = self._truncate_html(content, truncate_size)
            else:
                # For code/text, truncate at line boundaries
                lines = content.split('\n')
                truncated_lines = []
                current_size = 0
                
                for line in lines:
                    if current_size + len(line) + 1 > truncate_size:
                        break
                    truncated_lines.append(line)
                    current_size += len(line) + 1
                
                truncated = '\n'.join(truncated_lines)
            
            activity['content'] = truncated + '\n\n[Content truncated - original content was too large for API limits]'
            logger.info(f"Truncated activity content from {len(content)} to {len(activity['content'])} bytes")
        
        return activity
    
    def _truncate_html(self, html_content: str, max_size: int) -> str:
        """Truncate HTML content while preserving structure"""
        if len(html_content) <= max_size:
            return html_content
        
        # Simple truncation at tag boundaries
        truncated = html_content[:max_size]
        
        # Find the last complete tag
        last_tag_end = truncated.rfind('>')
        if last_tag_end > 0:
            truncated = truncated[:last_tag_end + 1]
        
        return truncated
    
    def get_preprocessing_stats(self, original_data: List[Dict], sanitized_data: List[Dict]) -> Dict[str, Any]:
        """Get preprocessing statistics"""
        original_size = sum(self._calculate_section_size(s) for s in original_data)
        sanitized_size = sum(self._calculate_section_size(s) for s in sanitized_data)
        
        return {
            'original_sections': len(original_data),
            'sanitized_sections': len(sanitized_data),
            'original_size_bytes': original_size,
            'sanitized_size_bytes': sanitized_size,
            'size_reduction_percent': ((original_size - sanitized_size) / original_size * 100) if original_size > 0 else 0,
            'sections_removed': len(original_data) - len(sanitized_data),
            'estimated_success_probability': self._estimate_success_probability(sanitized_size)
        }
    
    def _estimate_success_probability(self, total_size: int) -> float:
        """Estimate success probability based on size and log patterns"""
        if total_size < 1000:
            return 0.95  # Very high success rate for small content
        elif total_size < 5000:
            return 0.85  # Good success rate
        elif total_size < 15000:
            return 0.70  # Moderate success rate
        elif total_size < 30000:
            return 0.50  # Lower success rate
        else:
            return 0.25  # Low success rate for very large content