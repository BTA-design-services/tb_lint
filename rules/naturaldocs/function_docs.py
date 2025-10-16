"""
Function documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper function documentation
"""

from typing import List, Set
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class FunctionDocsRule(BaseRule):
    """
    Rule: Check function documentation
    
    Requirements:
    - Functions must have 'Function:' documentation
    - Only prototypes (extern) require documentation
    - Implementations skip checks if prototype exists
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_FUNC_MISS]"
    
    @property
    def description(self) -> str:
        return "Functions must have 'Function:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check function documentation using AST context
        
        Args:
            file_path: Path to file being checked
            file_content: Content of the file
            context: AST context with function nodes
        
        Returns:
            List of violations found
        """
        violations = []
        
        # Context should contain AST tree from Verible
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # First pass: collect all function prototypes
        function_prototypes = set()
        
        for node in tree.iter_find_all({'tag': 'kFunctionPrototype'}):
            func_name = self._extract_function_name_from_prototype(node)
            if func_name:
                function_prototypes.add(func_name)
                # Check documentation on prototype
                violations.extend(self._check_function_node(
                    node, file_path, file_content, context, is_prototype=True
                ))
        
        # Check constructor prototypes
        for node in tree.iter_find_all({'tag': 'kClassConstructorPrototype'}):
            func_name = self._extract_function_name_from_prototype(node)
            if func_name:
                function_prototypes.add(func_name)
                violations.extend(self._check_function_node(
                    node, file_path, file_content, context, is_prototype=True
                ))
        
        # Second pass: check function implementations (skip if prototype exists)
        for node in tree.iter_find_all({'tag': 'kFunctionDeclaration'}):
            func_name = self._extract_function_name(node)
            # Skip if prototype exists
            if func_name and func_name not in function_prototypes:
                violations.extend(self._check_function_node(
                    node, file_path, file_content, context, is_prototype=False
                ))
        
        return violations
    
    def _check_function_node(self, node, file_path: str, file_content: str, 
                            context: any, is_prototype: bool) -> List[RuleViolation]:
        """Check a single function node for documentation"""
        violations = []
        
        func_name = self._extract_function_name_from_prototype(node) if is_prototype else self._extract_function_name(node)
        start_line = self._get_line_number(context.file_bytes, node.start)
        
        # Extract preceding comments
        comments = self._extract_preceding_comments(file_content, start_line - 1)
        
        # Check for Function: keyword
        if not self._has_naturaldocs_keyword(comments, ['Function']):
            violations.append(self.create_violation(
                file_path=file_path,
                line=start_line,
                message=f"Function '{func_name}' without 'Function:' documentation" if func_name
                       else "Function without 'Function:' documentation"
            ))
        
        return violations
    
    def _extract_function_name(self, node) -> str:
        """Extract function name from implementation node"""
        try:
            for header in node.iter_find_all({'tag': 'kFunctionHeader'}):
                for qualified_id in header.iter_find_all({'tag': 'kQualifiedId'}):
                    qual_text = qualified_id.text
                    if '::' in qual_text:
                        return qual_text.split('::')[-1].strip()
                    else:
                        return qual_text.strip()
        except:
            pass
        return ""
    
    def _extract_function_name_from_prototype(self, node) -> str:
        """Extract function name from prototype node"""
        try:
            # For constructor prototypes
            if node.tag == 'kClassConstructorPrototype':
                for child in node.children:
                    if isinstance(child, str) and child == 'new':
                        return 'new'
                    if hasattr(child, 'text') and child.text == 'new':
                        return 'new'
            
            # For regular function prototypes
            for header in node.iter_find_all({'tag': 'kFunctionHeader'}):
                for child in header.children:
                    if hasattr(child, 'tag'):
                        if child.tag == 'kUnqualifiedId':
                            return child.text
                        elif child.tag == 'kQualifiedId':
                            if '::' in child.text:
                                return child.text.split('::')[-1]
                            return child.text
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

