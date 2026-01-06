"""
Base class for linting rules

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Abstract base class that all linting rules must inherit from
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Any


class RuleSeverity(Enum):
    """Severity level for rule violations"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class RuleViolation:
    """
    Represents a single rule violation
    
    Attributes:
        file: Path to the file containing the violation
        line: Line number where violation occurs
        column: Column number (optional, depends on linter)
        severity: Severity level of the violation
        message: Human-readable description of the violation
        rule_id: Unique identifier for the rule
        context: Additional context information (optional)
    """
    file: str
    line: int
    column: int
    severity: RuleSeverity
    message: str
    rule_id: str
    context: Optional[str] = None


class BaseRule(ABC):
    """
    Abstract base class for all linting rules
    
    Each rule should:
    - Have a unique rule_id
    - Implement the check() method
    - Define its default severity level
    - Provide a clear description
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize rule with optional configuration
        
        Args:
            config: Optional configuration dictionary for the rule
        """
        self.config = config or {}
        self._enabled = self.config.get('enabled', True)
        self._severity = self._parse_severity(
            self.config.get('severity', self.default_severity())
        )
    
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """
        Unique identifier for this rule (e.g., 'ND_FILE_HDR_MISS')
        
        Returns:
            String identifier for the rule
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of what this rule checks
        
        Returns:
            String description of the rule
        """
        pass
    
    @abstractmethod
    def default_severity(self) -> RuleSeverity:
        """
        Default severity level for violations of this rule
        
        Returns:
            RuleSeverity enum value
        """
        pass
    
    @abstractmethod
    def check(self, file_path: str, file_content: str, context: Any) -> List[RuleViolation]:
        """
        Check file for violations of this rule
        
        Args:
            file_path: Path to the file being checked
            file_content: Content of the file as a string
            context: Additional context (e.g., AST, parsed data)
        
        Returns:
            List of RuleViolation objects found
        """
        pass
    
    @property
    def enabled(self) -> bool:
        """Check if rule is enabled"""
        return self._enabled
    
    @property
    def severity(self) -> RuleSeverity:
        """Get configured severity level"""
        return self._severity
    
    def _parse_severity(self, severity_str) -> RuleSeverity:
        """
        Parse severity string to enum
        
        Args:
            severity_str: Severity as string ("ERROR", "WARNING", "INFO") or RuleSeverity object
        
        Returns:
            RuleSeverity enum value
        """
        # If already a RuleSeverity object, return it
        if isinstance(severity_str, RuleSeverity):
            return severity_str
        
        # Parse string to enum
        if isinstance(severity_str, str):
            severity_upper = severity_str.upper()
            if severity_upper == "ERROR":
                return RuleSeverity.ERROR
            elif severity_upper == "WARNING":
                return RuleSeverity.WARNING
            elif severity_upper == "INFO":
                return RuleSeverity.INFO
        
        # Default fallback
        return self.default_severity()
    
    def create_violation(self, file_path: str, line: int, message: str, 
                        column: int = 0, context: Optional[str] = None) -> RuleViolation:
        """
        Helper method to create a RuleViolation with this rule's configuration
        
        Args:
            file_path: Path to file with violation
            line: Line number
            message: Violation message
            column: Column number (default: 0)
            context: Additional context (default: None)
        
        Returns:
            Configured RuleViolation object
        """
        return RuleViolation(
            file=file_path,
            line=line,
            column=column,
            severity=self.severity,
            message=message,
            rule_id=self.rule_id,
            context=context
        )
    
    def _extract_preceding_comments(self, file_content: str, start_line: int, 
                                    context: any = None, max_lines: int = 50) -> List[str]:
        """
        Extract comments preceding a given line number using Verible parser tokens.
        
        This method uses Verible's rawtokens (if available) to accurately extract
        comments, which properly handles all comment types:
        - Single-line comments: // ...
        - Multiline block comments: /* ... */
        - Multiline block comments with continuation lines: /* ... * ... */
        - Mixed comment styles
        
        If rawtokens are not available, falls back to text-based parsing.
        
        Args:
            file_content: Full content of the file as a string
            start_line: Line number to start searching backwards from (1-indexed)
            context: AST context object (should have rawtokens attribute if available)
            max_lines: Maximum number of lines to search backwards (default: 50)
        
        Returns:
            List of comment lines in forward order (earliest to latest)
        """
        # Try to use Verible rawtokens if available
        if context and hasattr(context, 'rawtokens') and context.rawtokens:
            return self._extract_comments_from_rawtokens(context, start_line, file_content)
        
        # Fallback to text-based parsing if rawtokens not available
        return self._extract_comments_from_text(file_content, start_line, max_lines)
    
    def _extract_comments_from_rawtokens(self, context: any, start_line: int, 
                                        file_content: str) -> List[str]:
        """
        Extract comments using Verible rawtokens.
        
        This method finds all comment tokens that appear before the target line
        and extracts their text content. Verible's parser correctly identifies
        all comment types including multiline block comments.
        
        Args:
            context: AST context with rawtokens and file_bytes
            start_line: Target line number (1-indexed)
            file_content: Full file content (for calculating byte offset)
        
        Returns:
            List of comment lines in forward order
        """
        if not context or not hasattr(context, 'rawtokens') or not context.rawtokens:
            return []
        
        if not hasattr(context, 'file_bytes') or not context.file_bytes:
            return []
        
        # Convert start_line to byte offset for the start of the target line
        lines = file_content.split('\n')
        if start_line < 1 or start_line > len(lines):
            return []
        
        # Calculate byte offset for start of target line
        # Need to account for newlines (which are \n = 1 byte in UTF-8)
        target_byte_offset = 0
        for i in range(start_line - 1):
            target_byte_offset += len(lines[i].encode('utf-8')) + 1  # +1 for newline
        
        # Find all comment tokens that end before the target line
        # Verible comment token tags: TK_EOL_COMMENT (//), TK_COMMENT_BLOCK (/* */)
        comment_tokens = []
        for token in context.rawtokens:
            # Check if this is a comment token
            # Verible uses tags like "TK_EOL_COMMENT" or "TK_COMMENT_BLOCK"
            tag = token.tag if hasattr(token, 'tag') else str(token)
            tag_upper = tag.upper()
            
            # Check for comment tokens (Verible uses various comment token tags)
            is_comment = ('COMMENT' in tag_upper or 
                         tag in ['TK_EOL_COMMENT', 'TK_COMMENT_BLOCK', 
                                'TK_COMMENT', 'EOL_COMMENT', 'COMMENT_BLOCK'])
            
            if is_comment:
                # Check if this comment ends before our target line
                token_end = token.end if hasattr(token, 'end') else None
                if token_end is not None and token_end <= target_byte_offset:
                    comment_tokens.append(token)
        
        # Sort by end position (ascending) to get them in forward order
        comment_tokens.sort(key=lambda t: t.end if hasattr(t, 'end') else 0)
        
        # Extract comment text and preserve multiline structure
        comments = []
        for token in comment_tokens:
            # Get token text
            token_text = token.text if hasattr(token, 'text') else ""
            if not token_text:
                # Fallback: extract from file_bytes
                if hasattr(token, 'start') and hasattr(token, 'end'):
                    try:
                        token_text = context.file_bytes[token.start:token.end].decode('utf-8')
                    except:
                        continue
            
            if not token_text:
                continue
            
            # For multiline block comments, split into lines and clean each line
            # For single-line comments, just clean the marker
            lines = token_text.split('\n')
            for line in lines:
                stripped = line.strip()
                
                # Handle empty lines in block comments
                if not stripped:
                    # Only include empty lines if we're in a block comment
                    # (single-line comments don't have empty lines)
                    if '/*' in token_text or '*/' in token_text:
                        comments.append("")
                    continue
                
                # Remove comment markers while preserving content
                # Single-line comment: remove //
                if stripped.startswith('//'):
                    comment_line = stripped[2:].strip()
                    if comment_line:
                        comments.append(comment_line)
                # Block comment start: remove /*
                elif stripped.startswith('/*'):
                    comment_line = stripped[2:].strip()
                    # Remove */ if present (single-line block comment)
                    if comment_line.endswith('*/'):
                        comment_line = comment_line[:-2].strip()
                    if comment_line:
                        comments.append(comment_line)
                # Block comment end: remove */
                elif stripped.endswith('*/'):
                    comment_line = stripped[:-2].strip()
                    if comment_line:
                        comments.append(comment_line)
                # Block comment continuation: remove leading * (if present)
                elif stripped.startswith('*') and not stripped.startswith('*/'):
                    comment_line = stripped[1:].strip()
                    if comment_line:
                        comments.append(comment_line)
                # Block comment content (no marker, or content after *)
                else:
                    comments.append(stripped)
        
        return comments
    
    def _extract_comments_from_text(self, file_content: str, start_line: int, 
                                   max_lines: int = 50) -> List[str]:
        """
        Fallback method: Extract comments using text-based parsing.
        
        This is used when Verible rawtokens are not available.
        """
        lines = file_content.split('\n')
        comments = []
        
        # Track if we're currently collecting a multiline block comment
        collecting_block_comment = False
        
        # Start from the line before the target (start_line is 1-indexed)
        start_idx = start_line - 1
        
        # Iterate backwards from start_line
        for i in range(start_idx - 1, max(0, start_idx - max_lines) - 1, -1):
            if i < 0 or i >= len(lines):
                break
                
            line = lines[i]
            stripped = line.strip()
            
            # Handle empty lines
            if not stripped:
                if collecting_block_comment:
                    comments.insert(0, "")
                else:
                    continue
                continue
            
            # Check for single-line comment (//)
            if stripped.startswith('//'):
                comments.insert(0, stripped)
                collecting_block_comment = False
                continue
            
            # Check for end of block comment (*/)
            if '*/' in stripped:
                end_idx = stripped.find('*/')
                comment_part = stripped[:end_idx + 2].strip()
                if comment_part:
                    comments.insert(0, comment_part)
                
                if '/*' in stripped:
                    start_idx_comment = stripped.find('/*')
                    if start_idx_comment < end_idx:
                        collecting_block_comment = False
                    else:
                        collecting_block_comment = True
                else:
                    collecting_block_comment = True
                continue
            
            # Check for start of block comment (/*)
            if '/*' in stripped:
                start_idx_comment = stripped.find('/*')
                comment_part = stripped[start_idx_comment:].strip()
                
                if '*/' in comment_part:
                    comments.insert(0, comment_part)
                    collecting_block_comment = False
                else:
                    comments.insert(0, comment_part)
                    collecting_block_comment = False
                continue
            
            # If we're collecting a block comment, include continuation lines
            if collecting_block_comment:
                comments.insert(0, stripped)
                continue
            
            # If we get here, this is not a comment line
            break
        
        return comments
    
    def _has_naturaldocs_keyword(self, comments: list, keywords: list) -> bool:
        """
        Check if comments contain any of the NaturalDocs keywords.
        
        Since comment markers (//, /*, */, *) are already stripped during extraction,
        this method searches for keywords directly without requiring comment markers.
        
        Args:
            comments: List of comment lines (with markers already removed)
            keywords: List of keywords to search for (e.g., ['Package', 'Class'])
        
        Returns:
            True if any keyword is found, False otherwise
        """
        import re
        comment_text = ' '.join(comments)
        for keyword in keywords:
            # Search for keyword followed by colon (e.g., "Package:", "Class:")
            # The comment markers have already been stripped, so we just need to match
            # the keyword and colon, possibly with whitespace
            pattern = r'\b' + re.escape(keyword) + r'\s*:'
            if re.search(pattern, comment_text, re.IGNORECASE):
                return True
        return False

