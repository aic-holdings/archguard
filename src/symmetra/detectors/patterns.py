"""
PatternDetector - Detect common anti-patterns and code smells

Identifies problematic coding patterns that indicate potential
maintainability, performance, or design issues.

Detection Categories:
- Missing error handling (try/catch blocks)
- Code duplication patterns
- Anti-patterns (magic numbers, empty catch blocks)
- Unused imports and variables
- Inconsistent naming conventions
"""

import re
import ast
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
from .base import Detector, DetectedIssue, IssueType, Severity


class PatternDetector(Detector):
    """Detect anti-patterns and code smells"""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        
        # Magic number patterns (excluding common acceptable values)
        self.magic_number_pattern = r'\b(?<![\w.])((?!0|1|2|10|100|1000)\d{2,})\b'
        self.acceptable_numbers = {0, 1, 2, 3, 4, 5, 10, 24, 60, 100, 200, 404, 500, 1000, 1024}
        
        # Duplication threshold
        self.min_duplicate_lines = 5
        self.similarity_threshold = 0.8
    
    def detect(self, code: str, file_path: str, context: Dict[str, Any]) -> List[DetectedIssue]:
        """Detect pattern-related issues in code"""
        issues = []
        language = context.get('language', '').lower()
        
        # Check for missing error handling
        issues.extend(self._check_error_handling(code, file_path, language))
        
        # Check for magic numbers
        issues.extend(self._check_magic_numbers(code, file_path, language))
        
        # Check for code duplication
        issues.extend(self._check_code_duplication(code, file_path, language))
        
        # Language-specific patterns
        if language == 'python':
            issues.extend(self._check_python_patterns(code, file_path))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._check_javascript_patterns(code, file_path))
        else:
            issues.extend(self._check_generic_patterns(code, file_path, language))
        
        return issues
    
    def _check_error_handling(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Check for missing or inadequate error handling"""
        issues = []
        lines = code.split('\n')
        
        # Language-specific error handling patterns
        error_patterns = {
            'python': {
                'risky_operations': [
                    r'open\s*\(',
                    r'requests\.(get|post|put|delete)',
                    r'json\.loads\s*\(',
                    r'int\s*\(',
                    r'float\s*\(',
                ],
                'error_handling': [
                    r'try\s*:',
                    r'except\s+',
                    r'raise\s+',
                ]
            },
            'javascript': {
                'risky_operations': [
                    r'JSON\.parse\s*\(',
                    r'fetch\s*\(',
                    r'parseInt\s*\(',
                    r'parseFloat\s*\(',
                ],
                'error_handling': [
                    r'try\s*{',
                    r'catch\s*\(',
                    r'throw\s+',
                ]
            }
        }
        
        lang_patterns = error_patterns.get(language, error_patterns.get('javascript', {}))
        if not lang_patterns:
            return issues
        
        risky_lines = []
        error_handling_lines = set()
        
        # Find risky operations and error handling
        for line_no, line in enumerate(lines, 1):
            # Skip comments
            if self._is_comment_line(line, language):
                continue
            
            # Check for risky operations
            for pattern in lang_patterns.get('risky_operations', []):
                if re.search(pattern, line):
                    risky_lines.append((line_no, line.strip(), pattern))
            
            # Check for error handling
            for pattern in lang_patterns.get('error_handling', []):
                if re.search(pattern, line):
                    error_handling_lines.add(line_no)
        
        # Find risky operations without nearby error handling
        for line_no, line_content, pattern in risky_lines:
            # Check if there's error handling within 10 lines
            has_error_handling = any(
                abs(eh_line - line_no) <= 10 
                for eh_line in error_handling_lines
            )
            
            if not has_error_handling:
                issues.append(DetectedIssue(
                    type=IssueType.MISSING_ERROR_HANDLING,
                    severity=Severity.MEDIUM,
                    rule_id="PATTERN-001-MISSING-ERROR-HANDLING",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"Risky operation without error handling: {line_content[:50]}...",
                    message="Operation may fail without proper error handling",
                    fix_suggestion=self._get_error_handling_suggestion(language),
                    confidence=0.70,
                    language=language,
                    context={'operation': pattern, 'line_content': line_content}
                ))
        
        return issues
    
    def _is_comment_line(self, line: str, language: str) -> bool:
        """Check if line is a comment"""
        stripped = line.strip()
        if not stripped:
            return True
        
        comment_prefixes = {
            'python': ['#'],
            'javascript': ['//', '/*', '*'],
            'typescript': ['//', '/*', '*'],
            'java': ['//', '/*', '*'],
            'csharp': ['//', '/*', '*'],
        }
        
        prefixes = comment_prefixes.get(language, ['#', '//', '/*', '*'])
        return any(stripped.startswith(prefix) for prefix in prefixes)
    
    def _get_error_handling_suggestion(self, language: str) -> str:
        """Get error handling suggestion for language"""
        suggestions = {
            'python': "Wrap in try/except block and handle specific exceptions",
            'javascript': "Use try/catch block or .catch() for promises",
            'typescript': "Use try/catch block with proper error types",
            'java': "Use try/catch block with specific exception types",
            'csharp': "Use try/catch block with specific exception handling",
        }
        return suggestions.get(language, "Add appropriate error handling")
    
    def _check_magic_numbers(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Check for magic numbers that should be constants"""
        issues = []
        lines = code.split('\n')
        
        for line_no, line in enumerate(lines, 1):
            if self._is_comment_line(line, language):
                continue
            
            # Find potential magic numbers
            numbers = re.finditer(self.magic_number_pattern, line)
            for match in numbers:
                number = int(match.group(1))
                
                # Skip acceptable numbers
                if number in self.acceptable_numbers:
                    continue
                
                # Skip if it's clearly a year, ID, or other meaningful number
                if self._is_meaningful_number(number, line):
                    continue
                
                issues.append(DetectedIssue(
                    type=IssueType.DUPLICATE_CODE,  # Reusing enum for magic numbers
                    severity=Severity.LOW,
                    rule_id="PATTERN-002-MAGIC-NUMBER",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"Magic number {number} in: {line.strip()[:50]}...",
                    message=f"Magic number {number} should be a named constant",
                    fix_suggestion=f"Replace with a named constant: SOME_CONSTANT = {number}",
                    confidence=0.60,
                    language=language,
                    context={'magic_number': number, 'line_content': line.strip()}
                ))
        
        return issues
    
    def _is_meaningful_number(self, number: int, line: str) -> bool:
        """Check if number appears to be meaningful (year, ID, etc.)"""
        line_lower = line.lower()
        
        # Years
        if 1900 <= number <= 2100:
            return True
        
        # Common HTTP status codes
        if number in {200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503}:
            return True
        
        # Port numbers
        if 1 <= number <= 65535 and any(keyword in line_lower for keyword in ['port', 'socket', 'connect']):
            return True
        
        # Array/list indices or sizes that are contextually clear
        if any(keyword in line_lower for keyword in ['index', 'length', 'size', 'count', 'limit']):
            return True
        
        return False
    
    def _check_code_duplication(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Check for duplicated code blocks"""
        issues = []
        lines = code.split('\n')
        
        # Normalize lines (remove whitespace and comments)
        normalized_lines = []
        for line in lines:
            if self._is_comment_line(line, language):
                normalized_lines.append("")
            else:
                # Normalize whitespace
                normalized = re.sub(r'\s+', ' ', line.strip())
                normalized_lines.append(normalized)
        
        # Find duplicate blocks
        duplicates = self._find_duplicate_blocks(normalized_lines, self.min_duplicate_lines)
        
        for block_hash, locations in duplicates.items():
            if len(locations) >= 2:  # At least one duplication
                first_location = locations[0]
                other_locations = locations[1:]
                
                issues.append(DetectedIssue(
                    type=IssueType.DUPLICATE_CODE,
                    severity=Severity.MEDIUM,
                    rule_id="PATTERN-003-CODE-DUPLICATION",
                    file_path=file_path,
                    line_number=first_location[0],
                    evidence=f"Duplicate code block ({first_location[1]} lines) found {len(other_locations)} more time(s)",
                    message=f"Code block duplicated in {len(other_locations)} other location(s)",
                    fix_suggestion="Extract common code into a function or method",
                    confidence=0.85,
                    language=language,
                    context={
                        'block_size': first_location[1],
                        'duplicate_locations': [loc[0] for loc in other_locations],
                        'total_duplicates': len(locations)
                    }
                ))
        
        return issues
    
    def _find_duplicate_blocks(self, lines: List[str], min_lines: int) -> Dict[str, List[Tuple[int, int]]]:
        """Find duplicate code blocks"""
        duplicates = defaultdict(list)
        
        for start_line in range(len(lines) - min_lines + 1):
            for block_size in range(min_lines, min(20, len(lines) - start_line + 1)):
                block = lines[start_line:start_line + block_size]
                
                # Skip blocks that are mostly empty
                significant_lines = [line for line in block if line.strip()]
                if len(significant_lines) < min_lines // 2:
                    continue
                
                # Create hash of the block
                block_hash = hash(tuple(block))
                duplicates[block_hash].append((start_line + 1, block_size))
        
        # Filter out blocks that appear only once
        return {k: v for k, v in duplicates.items() if len(v) > 1}
    
    def _check_python_patterns(self, code: str, file_path: str) -> List[DetectedIssue]:
        """Check Python-specific patterns"""
        issues = []
        
        try:
            tree = ast.parse(code)
            issues.extend(self._check_python_unused_imports(tree, file_path))
            issues.extend(self._check_python_naming_conventions(tree, file_path))
            issues.extend(self._check_python_antipatterns(tree, file_path))
        except SyntaxError:
            pass  # Can't analyze syntactically incorrect code
        
        return issues
    
    def _check_python_unused_imports(self, tree: ast.AST, file_path: str) -> List[DetectedIssue]:
        """Check for unused imports in Python"""
        issues = []
        
        # Collect imports
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno
        
        # Find usage
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Handle module.function patterns
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        # Find unused imports
        for import_name, line_no in imports.items():
            if import_name not in used_names and not import_name.startswith('_'):
                issues.append(DetectedIssue(
                    type=IssueType.DUPLICATE_CODE,  # Reusing enum
                    severity=Severity.LOW,
                    rule_id="PATTERN-004-UNUSED-IMPORT",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"Unused import: {import_name}",
                    message=f"Import '{import_name}' is not used",
                    fix_suggestion="Remove unused import",
                    confidence=0.90,
                    language="python",
                    context={'import_name': import_name}
                ))
        
        return issues
    
    def _check_python_naming_conventions(self, tree: ast.AST, file_path: str) -> List[DetectedIssue]:
        """Check Python naming conventions (PEP 8)"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Function names should be snake_case
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('_'):
                    issues.append(DetectedIssue(
                        type=IssueType.DUPLICATE_CODE,  # Reusing enum
                        severity=Severity.LOW,
                        rule_id="PATTERN-005-NAMING-CONVENTION",
                        file_path=file_path,
                        line_number=node.lineno,
                        evidence=f"Function name: {node.name}",
                        message=f"Function '{node.name}' should use snake_case",
                        fix_suggestion="Use snake_case for function names (PEP 8)",
                        confidence=0.95,
                        language="python",
                        context={'name': node.name, 'type': 'function'}
                    ))
            
            elif isinstance(node, ast.ClassDef):
                # Class names should be PascalCase
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append(DetectedIssue(
                        type=IssueType.DUPLICATE_CODE,  # Reusing enum
                        severity=Severity.LOW,
                        rule_id="PATTERN-005-NAMING-CONVENTION",
                        file_path=file_path,
                        line_number=node.lineno,
                        evidence=f"Class name: {node.name}",
                        message=f"Class '{node.name}' should use PascalCase",
                        fix_suggestion="Use PascalCase for class names (PEP 8)",
                        confidence=0.95,
                        language="python",
                        context={'name': node.name, 'type': 'class'}
                    ))
        
        return issues
    
    def _check_python_antipatterns(self, tree: ast.AST, file_path: str) -> List[DetectedIssue]:
        """Check for Python-specific anti-patterns"""
        issues = []
        
        for node in ast.walk(tree):
            # Empty except blocks
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    issues.append(DetectedIssue(
                        type=IssueType.MISSING_ERROR_HANDLING,
                        severity=Severity.MEDIUM,
                        rule_id="PATTERN-006-EMPTY-EXCEPT",
                        file_path=file_path,
                        line_number=node.lineno,
                        evidence="Empty except block with only pass",
                        message="Empty except block silently ignores errors",
                        fix_suggestion="Handle specific exceptions or log the error",
                        confidence=0.95,
                        language="python",
                        context={'exception_type': getattr(node.type, 'id', 'Exception') if node.type else 'bare except'}
                    ))
            
            # Bare except clauses
            elif isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(DetectedIssue(
                    type=IssueType.MISSING_ERROR_HANDLING,
                    severity=Severity.MEDIUM,
                    rule_id="PATTERN-007-BARE-EXCEPT",
                    file_path=file_path,
                    line_number=node.lineno,
                    evidence="Bare except clause",
                    message="Bare except clause catches all exceptions",
                    fix_suggestion="Catch specific exception types",
                    confidence=0.90,
                    language="python"
                ))
        
        return issues
    
    def _check_javascript_patterns(self, code: str, file_path: str) -> List[DetectedIssue]:
        """Check JavaScript/TypeScript specific patterns"""
        issues = []
        lines = code.split('\n')
        
        # Check for console.log in production code
        for line_no, line in enumerate(lines, 1):
            if 'console.log' in line and not self._is_comment_line(line, 'javascript'):
                issues.append(DetectedIssue(
                    type=IssueType.DUPLICATE_CODE,  # Reusing enum
                    severity=Severity.LOW,
                    rule_id="PATTERN-008-CONSOLE-LOG",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"console.log statement: {line.strip()[:50]}...",
                    message="console.log should not be in production code",
                    fix_suggestion="Remove console.log or use proper logging",
                    confidence=0.80,
                    language="javascript",
                    context={'line_content': line.strip()}
                ))
        
        # Check for == instead of ===
        for line_no, line in enumerate(lines, 1):
            if re.search(r'[^=!]==[^=]', line) and not self._is_comment_line(line, 'javascript'):
                issues.append(DetectedIssue(
                    type=IssueType.DUPLICATE_CODE,  # Reusing enum
                    severity=Severity.LOW,
                    rule_id="PATTERN-009-LOOSE-EQUALITY",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"Loose equality operator: {line.strip()[:50]}...",
                    message="Use strict equality (===) instead of loose equality (==)",
                    fix_suggestion="Replace == with === for strict comparison",
                    confidence=0.85,
                    language="javascript",
                    context={'line_content': line.strip()}
                ))
        
        return issues
    
    def _check_generic_patterns(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Check generic patterns for any language"""
        issues = []
        lines = code.split('\n')
        
        # Check for very long lines
        for line_no, line in enumerate(lines, 1):
            if len(line) > 120 and not self._is_comment_line(line, language):
                issues.append(DetectedIssue(
                    type=IssueType.DUPLICATE_CODE,  # Reusing enum
                    severity=Severity.LOW,
                    rule_id="PATTERN-010-LONG-LINE",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"Line has {len(line)} characters",
                    message="Line exceeds maximum length",
                    fix_suggestion="Break long lines for better readability",
                    confidence=0.95,
                    language=language,
                    context={'line_length': len(line)}
                ))
        
        # Check for TODO/FIXME comments
        for line_no, line in enumerate(lines, 1):
            if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
                issues.append(DetectedIssue(
                    type=IssueType.DUPLICATE_CODE,  # Reusing enum
                    severity=Severity.LOW,
                    rule_id="PATTERN-011-TODO-COMMENT",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"TODO/FIXME comment: {line.strip()[:50]}...",
                    message="TODO/FIXME comment found",
                    fix_suggestion="Address the TODO or create a task",
                    confidence=0.95,
                    language=language,
                    context={'comment_type': 'TODO', 'line_content': line.strip()}
                ))
        
        return issues
    
    def get_supported_languages(self) -> List[str]:
        """Languages supported by pattern detector"""
        return ["python", "javascript", "typescript", "java", "csharp", "all"]
    
    def get_detection_patterns(self) -> Dict[str, str]:
        """Get patterns this detector looks for"""
        return {
            "missing_error_handling": "Operations without try/catch blocks",
            "magic_numbers": "Hardcoded numbers that should be constants",
            "code_duplication": "Duplicate code blocks",
            "unused_imports": "Unused import statements",
            "naming_conventions": "Non-standard naming patterns",
            "antipatterns": "Common anti-patterns and code smells"
        }