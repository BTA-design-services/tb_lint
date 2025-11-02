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

    Providing an explicit template in this docstring equips contributors with
    the practical knowledge requested in the API documentation brief.

    Example:
        Implementing a rule that flags TODO comments::

            class NoTodoRule(BaseRule):
                @property
                def rule_id(self) -> str:
                    return "[STYLE_NO_TODO]"

                @property
                def description(self) -> str:
                    return "Disallow lingering TODO comments"

                def default_severity(self) -> RuleSeverity:
                    return RuleSeverity.WARNING

                def check(self, file_path: str, file_content: str, context: Any) -> List[RuleViolation]:
                    violations = []
                    for idx, line in enumerate(file_content.splitlines(), start=1):
                        if "TODO" in line:
                            violations.append(self.create_violation(file_path, idx, "Remove TODO markers before check-in"))
                    return violations
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

