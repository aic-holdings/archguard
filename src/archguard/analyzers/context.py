"""
Context Extractor - Extract relevant code context around issues

Provides intelligent context extraction for better analysis and
understanding of detected issues within their surrounding code.
"""

from typing import List, Dict, Any, Tuple, Optional


class ContextExtractor:
    """Extract and format code context around detected issues"""
    
    def __init__(self, context_radius: int = 5):
        """
        Initialize context extractor.
        
        Args:
            context_radius: Number of lines to include before/after issue
        """
        self.context_radius = context_radius
    
    def extract_context(
        self, 
        code: str, 
        line_number: int, 
        language: Optional[str] = None,
        focus_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract context around a specific line.
        
        Args:
            code: Complete source code
            line_number: Line number of the issue (1-indexed)
            language: Programming language for syntax awareness
            focus_keywords: Keywords to highlight in context
            
        Returns:
            Dictionary with context information
        """
        lines = code.split('\n')
        total_lines = len(lines)
        
        # Calculate context boundaries
        start_line = max(0, line_number - self.context_radius - 1)
        end_line = min(total_lines, line_number + self.context_radius)
        
        # Extract context lines
        context_lines = []
        for i in range(start_line, end_line):
            line_content = lines[i] if i < total_lines else ""
            is_focus_line = (i + 1) == line_number
            
            context_lines.append({
                'line_number': i + 1,
                'content': line_content,
                'is_focus': is_focus_line,
                'indentation': len(line_content) - len(line_content.lstrip()),
                'is_comment': self._is_comment_line(line_content, language),
                'is_blank': not line_content.strip()
            })
        
        # Analyze context structure
        structure_info = self._analyze_context_structure(context_lines, language)
        
        # Highlight relevant keywords
        if focus_keywords:
            self._highlight_keywords(context_lines, focus_keywords)
        
        return {
            'context_lines': context_lines,
            'start_line': start_line + 1,
            'end_line': end_line,
            'focus_line': line_number,
            'structure_info': structure_info,
            'formatted_context': self._format_context(context_lines),
            'summary': self._generate_context_summary(context_lines, structure_info)
        }
    
    def _is_comment_line(self, line: str, language: Optional[str]) -> bool:
        """Check if a line is a comment"""
        if not line.strip():
            return False
        
        comment_patterns = {
            'python': ['#'],
            'javascript': ['//', '/*', '*'],
            'typescript': ['//', '/*', '*'],
            'java': ['//', '/*', '*'],
            'csharp': ['//', '/*', '*'],
            'cpp': ['//', '/*', '*'],
            'c': ['//', '/*', '*'],
            'php': ['//', '/*', '*', '#'],
            'ruby': ['#'],
            'go': ['//', '/*', '*'],
            'rust': ['//', '/*', '*'],
            'swift': ['//', '/*', '*']
        }
        
        if not language:
            # Check for common comment patterns
            patterns = ['//', '/*', '*', '#']
        else:
            patterns = comment_patterns.get(language.lower(), ['//', '#'])
        
        stripped = line.strip()
        return any(stripped.startswith(pattern) for pattern in patterns)
    
    def _analyze_context_structure(
        self, 
        context_lines: List[Dict[str, Any]], 
        language: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze the structural context around the issue"""
        
        structure = {
            'function_context': None,
            'class_context': None,
            'block_context': [],
            'indentation_level': 0,
            'control_structures': []
        }
        
        if not language:
            return structure
        
        # Find containing function and class
        for line_info in reversed(context_lines):
            if line_info['is_focus']:
                structure['indentation_level'] = line_info['indentation']
                continue
            
            content = line_info['content'].strip()
            
            # Function detection (language-specific)
            if language.lower() == 'python':
                if content.startswith('def ') and not structure['function_context']:
                    func_name = self._extract_python_function_name(content)
                    structure['function_context'] = {
                        'name': func_name,
                        'line': line_info['line_number']
                    }
                elif content.startswith('class ') and not structure['class_context']:
                    class_name = self._extract_python_class_name(content)
                    structure['class_context'] = {
                        'name': class_name,
                        'line': line_info['line_number']
                    }
            
            elif language.lower() in ['javascript', 'typescript']:
                if any(pattern in content for pattern in ['function ', 'const ', '=>']) and not structure['function_context']:
                    func_name = self._extract_js_function_name(content)
                    if func_name:
                        structure['function_context'] = {
                            'name': func_name,
                            'line': line_info['line_number']
                        }
                elif 'class ' in content and not structure['class_context']:
                    class_name = self._extract_js_class_name(content)
                    if class_name:
                        structure['class_context'] = {
                            'name': class_name,
                            'line': line_info['line_number']
                        }
        
        # Detect control structures
        for line_info in context_lines:
            content = line_info['content'].strip()
            
            control_keywords = ['if', 'for', 'while', 'try', 'catch', 'switch', 'with']
            for keyword in control_keywords:
                if content.startswith(keyword + ' ') or content.startswith(keyword + '('):
                    structure['control_structures'].append({
                        'type': keyword,
                        'line': line_info['line_number'],
                        'indentation': line_info['indentation']
                    })
        
        return structure
    
    def _extract_python_function_name(self, line: str) -> str:
        """Extract function name from Python def line"""
        import re
        match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
        return match.group(1) if match else 'unknown'
    
    def _extract_python_class_name(self, line: str) -> str:
        """Extract class name from Python class line"""
        import re
        match = re.search(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
        return match.group(1) if match else 'unknown'
    
    def _extract_js_function_name(self, line: str) -> Optional[str]:
        """Extract function name from JavaScript/TypeScript"""
        import re
        
        # function declaration
        match = re.search(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
        if match:
            return match.group(1)
        
        # const/let/var function
        match = re.search(r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
        if match:
            return match.group(1)
        
        # method definition
        match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
        if match and '=>' not in line:
            return match.group(1)
        
        return None
    
    def _extract_js_class_name(self, line: str) -> Optional[str]:
        """Extract class name from JavaScript/TypeScript"""
        import re
        match = re.search(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
        return match.group(1) if match else None
    
    def _highlight_keywords(self, context_lines: List[Dict[str, Any]], keywords: List[str]):
        """Add keyword highlighting information to context lines"""
        for line_info in context_lines:
            line_info['highlighted_keywords'] = []
            content_lower = line_info['content'].lower()
            
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    line_info['highlighted_keywords'].append(keyword)
    
    def _format_context(self, context_lines: List[Dict[str, Any]]) -> str:
        """Format context as a readable string"""
        formatted_lines = []
        
        for line_info in context_lines:
            line_num = line_info['line_number']
            content = line_info['content']
            
            # Add markers for focus line
            if line_info['is_focus']:
                prefix = f"{line_num:3}>>> "
            else:
                prefix = f"{line_num:3}:   "
            
            formatted_lines.append(f"{prefix}{content}")
        
        return '\n'.join(formatted_lines)
    
    def _generate_context_summary(
        self, 
        context_lines: List[Dict[str, Any]], 
        structure_info: Dict[str, Any]
    ) -> str:
        """Generate a human-readable summary of the context"""
        summary_parts = []
        
        # Location context
        if structure_info['function_context']:
            func_name = structure_info['function_context']['name']
            summary_parts.append(f"inside function '{func_name}'")
        
        if structure_info['class_context']:
            class_name = structure_info['class_context']['name']
            summary_parts.append(f"in class '{class_name}'")
        
        # Control structure context
        control_structures = structure_info['control_structures']
        if control_structures:
            recent_controls = [cs['type'] for cs in control_structures[-2:]]
            if recent_controls:
                summary_parts.append(f"within {', '.join(recent_controls)} block(s)")
        
        # Code characteristics
        non_blank_lines = [line for line in context_lines if not line['is_blank']]
        comment_lines = [line for line in context_lines if line['is_comment']]
        
        if len(comment_lines) > len(non_blank_lines) / 2:
            summary_parts.append("in heavily commented section")
        
        # Default summary
        if not summary_parts:
            summary_parts.append("in code block")
        
        return "Located " + ", ".join(summary_parts)
    
    def extract_function_context(
        self, 
        code: str, 
        line_number: int, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract the complete function containing the given line"""
        
        lines = code.split('\n')
        
        # Find function boundaries
        function_start = self._find_function_start(lines, line_number - 1, language)
        function_end = self._find_function_end(lines, function_start, language)
        
        if function_start is None:
            return {
                'found': False,
                'reason': 'No containing function found'
            }
        
        # Extract function lines
        function_lines = lines[function_start:function_end + 1]
        
        # Analyze function
        function_info = self._analyze_function(function_lines, language)
        
        return {
            'found': True,
            'start_line': function_start + 1,
            'end_line': function_end + 1,
            'function_lines': function_lines,
            'function_info': function_info,
            'issue_relative_line': line_number - function_start,
            'formatted_function': '\n'.join(f"{i+function_start+1:3}: {line}" for i, line in enumerate(function_lines))
        }
    
    def _find_function_start(
        self, 
        lines: List[str], 
        current_line: int, 
        language: Optional[str]
    ) -> Optional[int]:
        """Find the start of the function containing the current line"""
        
        if not language:
            return None
        
        function_patterns = {
            'python': [r'^\s*def\s+'],
            'javascript': [r'^\s*function\s+', r'^\s*const\s+\w+\s*=', r'^\s*\w+\s*\(.*\)\s*=>', r'^\s*\w+\s*:\s*function'],
            'typescript': [r'^\s*function\s+', r'^\s*const\s+\w+\s*=', r'^\s*\w+\s*\(.*\)\s*=>', r'^\s*\w+\s*:\s*function'],
            'java': [r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)*\w+\s*\('],
            'csharp': [r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)*\w+\s*\(']
        }
        
        patterns = function_patterns.get(language.lower(), [])
        if not patterns:
            return None
        
        import re
        
        # Search backwards from current line
        for i in range(current_line, -1, -1):
            line = lines[i]
            for pattern in patterns:
                if re.match(pattern, line):
                    return i
        
        return None
    
    def _find_function_end(
        self, 
        lines: List[str], 
        function_start: int, 
        language: Optional[str]
    ) -> int:
        """Find the end of the function starting at function_start"""
        
        if language and language.lower() == 'python':
            # For Python, use indentation to find function end
            if function_start >= len(lines):
                return len(lines) - 1
            
            function_indent = len(lines[function_start]) - len(lines[function_start].lstrip())
            
            for i in range(function_start + 1, len(lines)):
                line = lines[i]
                if line.strip():  # Non-empty line
                    line_indent = len(line) - len(line.lstrip())
                    if line_indent <= function_indent:
                        return i - 1
            
            return len(lines) - 1
        
        else:
            # For brace-based languages, count braces
            brace_count = 0
            found_opening = False
            
            for i in range(function_start, len(lines)):
                line = lines[i]
                
                brace_count += line.count('{') - line.count('}')
                if '{' in line:
                    found_opening = True
                
                if found_opening and brace_count <= 0:
                    return i
            
            return len(lines) - 1
    
    def _analyze_function(self, function_lines: List[str], language: Optional[str]) -> Dict[str, Any]:
        """Analyze function characteristics"""
        
        info = {
            'line_count': len(function_lines),
            'has_parameters': False,
            'has_return': False,
            'complexity_indicators': [],
            'docstring_present': False
        }
        
        function_text = '\n'.join(function_lines)
        
        # Check for parameters
        if '(' in function_lines[0] and ')' in function_lines[0]:
            param_section = function_lines[0].split('(')[1].split(')')[0].strip()
            info['has_parameters'] = bool(param_section and param_section != 'self')
        
        # Check for return statements
        info['has_return'] = any('return ' in line for line in function_lines)
        
        # Complexity indicators
        if function_text.count('if ') > 3:
            info['complexity_indicators'].append('multiple_conditionals')
        
        if function_text.count('for ') + function_text.count('while ') > 2:
            info['complexity_indicators'].append('multiple_loops')
        
        if function_text.count('try:') > 0:
            info['complexity_indicators'].append('exception_handling')
        
        # Check for docstring (Python)
        if language and language.lower() == 'python':
            if len(function_lines) > 1:
                second_line = function_lines[1].strip()
                info['docstring_present'] = second_line.startswith('"""') or second_line.startswith("'''")
        
        return info