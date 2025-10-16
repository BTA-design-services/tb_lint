"""
Task documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper task documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class TaskDocsRule(BaseRule):
    """
    Rule: Check task documentation
    
    Requirements:
    - Tasks must have 'Function:' documentation (NaturalDocs uses Function for tasks)
    - Only prototypes (extern) require documentation
    - Implementations skip checks if prototype exists
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_TASK_MISS]"
    
    @property
    def description(self) -> str:
        return "Tasks must have 'Function:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check task documentation using AST context
        
        Similar to function checking but for tasks
        """
        violations = []
        
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Collect task prototypes
        task_prototypes = set()
        for node in tree.iter_find_all({'tag': 'kTaskPrototype'}):
            task_name = self._extract_task_name(node)
            if task_name:
                task_prototypes.add(task_name)
                violations.extend(self._check_task_node(
                    node, file_path, file_content, context
                ))
        
        # Check task implementations (skip if prototype exists)
        for node in tree.iter_find_all({'tag': 'kTaskDeclaration'}):
            task_name = self._extract_task_name(node)
            if task_name and task_name not in task_prototypes:
                violations.extend(self._check_task_node(
                    node, file_path, file_content, context
                ))
        
        return violations
    
    def _check_task_node(self, node, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check a single task node for documentation"""
        violations = []
        
        task_name = self._extract_task_name(node)
        start_line = self._get_line_number(context.file_bytes, node.start)
        comments = self._extract_preceding_comments(file_content, start_line - 1)
        
        # NaturalDocs uses 'Function' keyword for tasks
        if not self._has_naturaldocs_keyword(comments, ['Function', 'Func', 'Procedure', 'Proc', 'Method']):
            violations.append(self.create_violation(
                file_path=file_path,
                line=start_line,
                message=f"Task '{task_name}' without 'Function:' documentation (NaturalDocs uses Function for tasks)" 
                       if task_name else "Task without 'Function:' documentation"
            ))
        
        return violations
    
    def _extract_task_name(self, node) -> str:
        """Extract task name from AST node"""
        try:
            for header in node.iter_find_all({'tag': 'kTaskHeader'}):
                for child in header.children:
                    if hasattr(child, 'tag'):
                        if child.tag in ['kUnqualifiedId', 'kQualifiedId']:
                            text = child.text
                            if '::' in text:
                                return text.split('::')[-1].strip()
                            return text.strip()
        except:
            pass
        return ""
    
    def _get_line_number(self, file_bytes: bytes, byte_offset: int) -> int:
        """Convert byte offset to line number"""
        if byte_offset is None:
            return 1
        return file_bytes[:byte_offset].count(b'\n') + 1
    
    def _extract_preceding_comments(self, file_content: str, start_line: int, max_lines: int = 50) -> list:
        """Extract comments before a declaration"""
        lines = file_content.split('\n')
        comments = []
        for i in range(start_line - 1, max(0, start_line - max_lines) - 1, -1):
            line = lines[i].strip()
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                comments.insert(0, line)
            elif not line:
                continue
            else:
                break
        return comments
    
    def _has_naturaldocs_keyword(self, comments: list, keywords: list) -> bool:
        """Check if comments contain any of the NaturalDocs keywords"""
        import re
        comment_text = ' '.join(comments)
        for keyword in keywords:
            if re.search(r'(?://|/\*|\*)\s*' + re.escape(keyword) + r'\s*:', comment_text, re.IGNORECASE):
                return True
        return False

