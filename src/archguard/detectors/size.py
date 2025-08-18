"""
SizeDetector - Detect file and function size issues

Identifies code organization issues based on size metrics that indicate
potential maintainability and complexity problems.

Detection Categories:
- Large files (>500 lines)
- Large functions/methods (>50 lines)
- God objects (classes with too many responsibilities)
- Deep nesting levels (>4 levels)
- Long parameter lists (>5 parameters)
"""

import re
import ast
from typing import List, Dict, Any, Optional, Tuple
from .base import Detector, DetectedIssue, IssueType, Severity


class SizeDetector(Detector):
    """Detect size-related code organization issues"""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        
        # Configurable thresholds
        self.thresholds = {
            'max_file_lines': 500,
            'warning_file_lines': 300,
            'max_function_lines': 50,
            'warning_function_lines': 30,
            'max_class_methods': 20,
            'warning_class_methods': 15,
            'max_nesting_depth': 4,
            'max_parameters': 5,
            'max_cyclomatic_complexity': 10
        }
    
    def detect(self, code: str, file_path: str, context: Dict[str, Any]) -> List[DetectedIssue]:
        """Detect size-related issues in code"""
        issues = []
        language = context.get('language', '').lower()
        
        # Check file size
        issues.extend(self._check_file_size(code, file_path, language))
        
        # Language-specific analysis
        if language == 'python':
            issues.extend(self._analyze_python_code(code, file_path))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._analyze_javascript_code(code, file_path))
        else:
            # Generic analysis for other languages
            issues.extend(self._analyze_generic_code(code, file_path, language))
        
        return issues
    
    def _check_file_size(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Check if file is too large"""
        issues = []
        lines = code.split('\n')
        total_lines = len(lines)
        
        # Count non-empty, non-comment lines
        significant_lines = self._count_significant_lines(lines, language)
        
        if total_lines > self.thresholds['max_file_lines']:
            severity = Severity.HIGH
            confidence = 0.90
        elif total_lines > self.thresholds['warning_file_lines']:
            severity = Severity.MEDIUM
            confidence = 0.75
        else:
            return issues
        
        # Calculate splitting suggestions
        split_suggestions = self._analyze_file_structure(code, language)
        
        issues.append(DetectedIssue(
            type=IssueType.LARGE_FILE,
            severity=severity,
            rule_id="SIZE-001-LARGE-FILE",
            file_path=file_path,
            line_number=1,
            evidence=f"File has {total_lines} lines ({significant_lines} significant)",
            message=f"File is too large ({total_lines} lines)",
            fix_suggestion=self._get_file_split_suggestion(split_suggestions, total_lines),
            confidence=confidence,
            language=language,
            context={
                'total_lines': total_lines,
                'significant_lines': significant_lines,
                'split_suggestions': split_suggestions
            }
        ))
        
        return issues
    
    def _count_significant_lines(self, lines: List[str], language: str) -> int:
        """Count non-empty, non-comment lines"""
        comment_patterns = {
            'python': [r'^\s*#'],
            'javascript': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'typescript': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'java': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'csharp': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'default': [r'^\s*#', r'^\s*//', r'^\s*/\*', r'^\s*\*']
        }
        
        patterns = comment_patterns.get(language, comment_patterns['default'])
        significant_count = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:  # Empty line
                continue
            
            is_comment = any(re.match(pattern, line) for pattern in patterns)
            if not is_comment:
                significant_count += 1
        
        return significant_count
    
    def _analyze_file_structure(self, code: str, language: str) -> List[str]:
        """Analyze file structure to suggest splitting points"""
        suggestions = []
        
        if language == 'python':
            suggestions = self._analyze_python_structure(code)
        elif language in ['javascript', 'typescript']:
            suggestions = self._analyze_javascript_structure(code)
        else:
            suggestions = self._analyze_generic_structure(code)
        
        return suggestions
    
    def _analyze_python_structure(self, code: str) -> List[str]:
        """Analyze Python file structure for splitting suggestions"""
        suggestions = []
        
        try:
            tree = ast.parse(code)
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(node)
            
            # Suggest splitting by classes
            if len(classes) > 3:
                suggestions.append(f"Split into separate files by class: {', '.join(classes[:3])}...")
            
            # Suggest splitting by functionality
            if len(functions) > 10:
                suggestions.append(f"Group related functions into modules ({len(functions)} functions found)")
            
            # Check for mixed concerns
            if classes and len(functions) > 5:
                suggestions.append("Separate classes and utility functions into different files")
                
        except SyntaxError:
            suggestions.append("Fix syntax errors, then consider splitting by logical sections")
        
        return suggestions
    
    def _analyze_javascript_structure(self, code: str) -> List[str]:
        """Analyze JavaScript/TypeScript structure"""
        suggestions = []
        lines = code.split('\n')
        
        # Look for classes, functions, and exports
        classes = re.findall(r'class\s+(\w+)', code, re.IGNORECASE)
        functions = re.findall(r'function\s+(\w+)|const\s+(\w+)\s*=\s*\(', code)
        exports = re.findall(r'export\s+', code)
        
        if len(classes) > 2:
            suggestions.append(f"Split classes into separate files: {', '.join(classes[:3])}")
        
        if len(functions) > 8:
            suggestions.append("Group related functions into modules")
        
        if len(exports) > 10:
            suggestions.append("Consider using barrel exports or splitting exports")
        
        return suggestions
    
    def _analyze_generic_structure(self, code: str) -> List[str]:
        """Generic structure analysis for unknown languages"""
        suggestions = []
        lines = code.split('\n')
        
        # Look for common patterns
        class_like = len(re.findall(r'\b(class|struct|interface)\s+\w+', code, re.IGNORECASE))
        function_like = len(re.findall(r'\b(function|def|fun|func|method)\s+\w+', code, re.IGNORECASE))
        
        if class_like > 2:
            suggestions.append("Consider splitting classes into separate files")
        
        if function_like > 10:
            suggestions.append("Group related functions into separate modules")
        
        suggestions.append("Split by logical responsibility or feature")
        
        return suggestions
    
    def _get_file_split_suggestion(self, split_suggestions: List[str], total_lines: int) -> str:
        """Generate file splitting suggestion"""
        if split_suggestions:
            return f"Split file: {split_suggestions[0]}"
        else:
            target_files = (total_lines // self.thresholds['max_file_lines']) + 1
            return f"Split into approximately {target_files} smaller files"
    
    def _analyze_python_code(self, code: str, file_path: str) -> List[DetectedIssue]:
        """Analyze Python-specific size issues"""
        issues = []
        
        try:
            tree = ast.parse(code)
            issues.extend(self._check_python_functions(tree, file_path))
            issues.extend(self._check_python_classes(tree, file_path))
            issues.extend(self._check_python_nesting(tree, file_path))
        except SyntaxError as e:
            # Can't parse, but that's not a size issue
            pass
        
        return issues
    
    def _check_python_functions(self, tree: ast.AST, file_path: str) -> List[DetectedIssue]:
        """Check Python function sizes"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                param_count = len(node.args.args)
                
                # Check function length
                if func_lines > self.thresholds['max_function_lines']:
                    severity = Severity.MEDIUM if func_lines < 100 else Severity.HIGH
                    
                    issues.append(DetectedIssue(
                        type=IssueType.LARGE_FUNCTION,
                        severity=severity,
                        rule_id="SIZE-002-LARGE-FUNCTION",
                        file_path=file_path,
                        line_number=node.lineno,
                        evidence=f"Function '{node.name}' has {func_lines} lines",
                        message=f"Function '{node.name}' is too long ({func_lines} lines)",
                        fix_suggestion="Break into smaller, focused functions",
                        confidence=0.90,
                        language="python",
                        context={'function_name': node.name, 'lines': func_lines}
                    ))
                
                # Check parameter count
                if param_count > self.thresholds['max_parameters']:
                    issues.append(DetectedIssue(
                        type=IssueType.LARGE_FUNCTION,
                        severity=Severity.MEDIUM,
                        rule_id="SIZE-003-TOO-MANY-PARAMS",
                        file_path=file_path,
                        line_number=node.lineno,
                        evidence=f"Function '{node.name}' has {param_count} parameters",
                        message=f"Function '{node.name}' has too many parameters",
                        fix_suggestion="Use dataclasses, named tuples, or parameter objects",
                        confidence=0.85,
                        language="python",
                        context={'function_name': node.name, 'param_count': param_count}
                    ))
        
        return issues
    
    def _check_python_classes(self, tree: ast.AST, file_path: str) -> List[DetectedIssue]:
        """Check Python class sizes"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                method_count = len(methods)
                
                if method_count > self.thresholds['max_class_methods']:
                    severity = Severity.MEDIUM if method_count < 30 else Severity.HIGH
                    
                    issues.append(DetectedIssue(
                        type=IssueType.GOD_OBJECT,
                        severity=severity,
                        rule_id="SIZE-004-GOD-CLASS",
                        file_path=file_path,
                        line_number=node.lineno,
                        evidence=f"Class '{node.name}' has {method_count} methods",
                        message=f"Class '{node.name}' has too many methods (God Object)",
                        fix_suggestion="Split into multiple classes with single responsibilities",
                        confidence=0.80,
                        language="python",
                        context={'class_name': node.name, 'method_count': method_count}
                    ))
        
        return issues
    
    def _check_python_nesting(self, tree: ast.AST, file_path: str) -> List[DetectedIssue]:
        """Check for deep nesting in Python code"""
        issues = []
        
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_depth = 0
                self.max_depth = 0
                self.deep_locations = []
                self.current_function = None
            
            def visit_FunctionDef(self, node):
                old_function = self.current_function
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = old_function
            
            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)
            
            def visit_If(self, node):
                self._visit_nesting_node(node)
            
            def visit_For(self, node):
                self._visit_nesting_node(node)
            
            def visit_While(self, node):
                self._visit_nesting_node(node)
            
            def visit_With(self, node):
                self._visit_nesting_node(node)
            
            def visit_Try(self, node):
                self._visit_nesting_node(node)
            
            def _visit_nesting_node(self, node):
                self.current_depth += 1
                if self.current_depth > self.max_depth:
                    self.max_depth = self.current_depth
                
                if self.current_depth > 4:  # Threshold for deep nesting
                    self.deep_locations.append((
                        node.lineno, 
                        self.current_depth, 
                        self.current_function or "module level"
                    ))
                
                self.generic_visit(node)
                self.current_depth -= 1
        
        visitor = NestingVisitor()
        visitor.visit(tree)
        
        for line_no, depth, location in visitor.deep_locations:
            issues.append(DetectedIssue(
                type=IssueType.DEEP_NESTING,
                severity=Severity.MEDIUM,
                rule_id="SIZE-005-DEEP-NESTING",
                file_path=file_path,
                line_number=line_no,
                evidence=f"Nesting depth of {depth} in {location}",
                message=f"Code is nested too deeply ({depth} levels)",
                fix_suggestion="Extract nested logic into separate functions",
                confidence=0.85,
                language="python",
                context={'nesting_depth': depth, 'location': location}
            ))
        
        return issues
    
    def _analyze_javascript_code(self, code: str, file_path: str) -> List[DetectedIssue]:
        """Analyze JavaScript/TypeScript size issues"""
        issues = []
        lines = code.split('\n')
        
        # Find functions and check their sizes
        issues.extend(self._check_javascript_functions(code, file_path))
        
        # Check for deep nesting
        issues.extend(self._check_javascript_nesting(code, file_path))
        
        return issues
    
    def _check_javascript_functions(self, code: str, file_path: str) -> List[DetectedIssue]:
        """Check JavaScript function sizes"""
        issues = []
        lines = code.split('\n')
        
        # Find function definitions
        function_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
            r'(\w+)\s*:\s*function\s*\(',
            r'(\w+)\s*=>\s*{',
        ]
        
        current_function = None
        function_start = 0
        brace_count = 0
        
        for line_no, line in enumerate(lines, 1):
            # Look for function start
            if current_function is None:
                for pattern in function_patterns:
                    match = re.search(pattern, line)
                    if match:
                        current_function = match.group(1)
                        function_start = line_no
                        brace_count = line.count('{') - line.count('}')
                        break
            else:
                # Track braces to find function end
                brace_count += line.count('{') - line.count('}')
                
                if brace_count <= 0:
                    # Function ended
                    func_lines = line_no - function_start + 1
                    
                    if func_lines > self.thresholds['max_function_lines']:
                        severity = Severity.MEDIUM if func_lines < 100 else Severity.HIGH
                        
                        issues.append(DetectedIssue(
                            type=IssueType.LARGE_FUNCTION,
                            severity=severity,
                            rule_id="SIZE-002-LARGE-FUNCTION",
                            file_path=file_path,
                            line_number=function_start,
                            evidence=f"Function '{current_function}' has {func_lines} lines",
                            message=f"Function '{current_function}' is too long",
                            fix_suggestion="Break into smaller, focused functions",
                            confidence=0.85,
                            language="javascript",
                            context={'function_name': current_function, 'lines': func_lines}
                        ))
                    
                    current_function = None
        
        return issues
    
    def _check_javascript_nesting(self, code: str, file_path: str) -> List[DetectedIssue]:
        """Check for deep nesting in JavaScript"""
        issues = []
        lines = code.split('\n')
        
        nesting_keywords = ['if', 'for', 'while', 'switch', 'try', 'function']
        current_depth = 0
        max_depth = 0
        
        for line_no, line in enumerate(lines, 1):
            # Count opening braces and nesting keywords
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Check for nesting keywords
            for keyword in nesting_keywords:
                if re.search(rf'\b{keyword}\b', line):
                    current_depth += 1
                    break
            
            current_depth += open_braces - close_braces
            
            if current_depth > max_depth:
                max_depth = current_depth
            
            if current_depth > self.thresholds['max_nesting_depth']:
                issues.append(DetectedIssue(
                    type=IssueType.DEEP_NESTING,
                    severity=Severity.MEDIUM,
                    rule_id="SIZE-005-DEEP-NESTING",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"Nesting depth of {current_depth}",
                    message=f"Code is nested too deeply ({current_depth} levels)",
                    fix_suggestion="Extract nested logic into separate functions",
                    confidence=0.75,
                    language="javascript",
                    context={'nesting_depth': current_depth}
                ))
        
        return issues
    
    def _analyze_generic_code(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Generic size analysis for unknown languages"""
        issues = []
        lines = code.split('\n')
        
        # Look for very long lines
        for line_no, line in enumerate(lines, 1):
            if len(line) > 120:  # Very long line threshold
                issues.append(DetectedIssue(
                    type=IssueType.LARGE_FUNCTION,  # Reusing enum
                    severity=Severity.LOW,
                    rule_id="SIZE-006-LONG-LINE",
                    file_path=file_path,
                    line_number=line_no,
                    evidence=f"Line has {len(line)} characters",
                    message="Line is too long",
                    fix_suggestion="Break long lines for better readability",
                    confidence=0.90,
                    language=language,
                    context={'line_length': len(line)}
                ))
        
        return issues
    
    def get_supported_languages(self) -> List[str]:
        """Languages supported by size detector"""
        return ["python", "javascript", "typescript", "java", "csharp", "all"]
    
    def get_detection_patterns(self) -> Dict[str, str]:
        """Get patterns this detector looks for"""
        return {
            "large_files": f"Files over {self.thresholds['max_file_lines']} lines",
            "large_functions": f"Functions over {self.thresholds['max_function_lines']} lines",
            "god_objects": f"Classes with over {self.thresholds['max_class_methods']} methods",
            "deep_nesting": f"Code nested over {self.thresholds['max_nesting_depth']} levels",
            "too_many_parameters": f"Functions with over {self.thresholds['max_parameters']} parameters"
        }