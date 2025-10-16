"""
File header documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper file header documentation
"""

import re
from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class FileHeaderRule(BaseRule):
    """
    Rule: Check for proper file header documentation
    
    Requirements:
    - File must have 'File:' keyword in first 30 lines
    - Should have 'Company:' field (configurable)
    - Should have 'Author:' field with email (configurable)
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_FILE_HDR_MISS]"
    
    @property
    def description(self) -> str:
        return "File header must contain 'File:' keyword"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check file header documentation
        
        Args:
            file_path: Path to file being checked
            file_content: Content of the file
            context: Not used for this rule
        
        Returns:
            List of violations found
        """
        violations = []
        lines = file_content.split('\n')
        header_lines = lines[:30]  # Check first 30 lines
        header_text = '\n'.join(header_lines)
        
        # Get configuration with empty string defaults
        company_pattern = self.config.get('company_pattern', '')
        company_name = self.config.get('company_name', '')
        email_domain = self.config.get('email_domain', '')
        
        # Check for File: keyword
        if not re.search(r'(?://|/\*|\*)\s*File\s*:', header_text):
            violations.append(self.create_violation(
                file_path=file_path,
                line=1,
                message="Missing 'File:' keyword in header"
            ))
        
        return violations


class CompanyFieldRule(BaseRule):
    """
    Rule: Check for Company field in file header
    
    This is typically a WARNING rather than ERROR
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_COMPANY_MISS]"
    
    @property
    def description(self) -> str:
        return "File header should contain 'Company:' field"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check for Company field in header"""
        violations = []
        lines = file_content.split('\n')
        header_lines = lines[:30]
        header_text = '\n'.join(header_lines)
        
        company_pattern = self.config.get('company_pattern', '')
        company_name = self.config.get('company_name', '')
        
        # Only check if company pattern is configured
        if not company_pattern:
            return violations
        
        # Check for Company field
        company_regex = rf'(?://|/\*|\*)\s*Company\s*:\s*{re.escape(company_pattern)}'
        if not re.search(company_regex, header_text, re.IGNORECASE):
            message = f"Missing or incomplete 'Company: {company_name}' in header" if company_name else f"Missing 'Company:' field with pattern '{company_pattern}'"
            violations.append(self.create_violation(
                file_path=file_path,
                line=1,
                message=message
            ))
        
        return violations


class AuthorFieldRule(BaseRule):
    """
    Rule: Check for Author field with email in file header
    
    This is typically a WARNING rather than ERROR
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_AUTHOR_MISS]"
    
    @property
    def description(self) -> str:
        return "File header should contain 'Author:' field with email"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check for Author field with email"""
        violations = []
        lines = file_content.split('\n')
        header_lines = lines[:30]
        header_text = '\n'.join(header_lines)
        
        email_domain = self.config.get('email_domain', '')
        
        # Only check if email domain is configured
        if not email_domain:
            return violations
        
        # Check for Author with email
        email_regex = rf'(?://|/\*|\*)\s*Author\s*:.*{re.escape(email_domain)}'
        if not re.search(email_regex, header_text):
            violations.append(self.create_violation(
                file_path=file_path,
                line=1,
                message=f"Missing 'Author:' with {email_domain} email"
            ))
        
        return violations

