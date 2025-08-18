"""
Detection Engine - Coordinates all detectors and provides unified analysis

The main engine that runs all enabled detectors and provides
comprehensive code analysis with prioritized results.

Architecture:
1. Run all applicable detectors on code
2. Collect and prioritize issues
3. Generate actionable guidance
4. Provide comprehensive analysis results
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from .base import Detector, DetectedIssue, DetectionResult, Severity


class DetectionEngine:
    """Main engine for running code detection analysis"""
    
    def __init__(self, detectors: List[Detector]):
        self.detectors = detectors
        self.total_patterns_checked = 0
    
    def analyze_code(self, code: str, file_path: str, context: Optional[Dict[str, Any]] = None) -> DetectionResult:
        """
        Run comprehensive detection analysis on code.
        
        Args:
            code: Source code to analyze
            file_path: Path to the file being analyzed
            context: Additional context (language, project info, etc.)
            
        Returns:
            DetectionResult with all issues found and guidance
        """
        if context is None:
            context = {}
        
        start_time = time.time()
        
        # Initialize result
        result = DetectionResult(
            file_path=file_path,
            language=context.get('language'),
            total_lines=len(code.split('\n'))
        )
        
        # Detect language if not provided
        if not result.language:
            result.language = self._detect_language(file_path, code)
            context['language'] = result.language
        
        # Run all applicable detectors
        all_issues = []
        detectors_run = []
        
        for detector in self.detectors:
            if detector.should_run(file_path, result.language, context):
                try:
                    detector_issues = detector.detect(code, file_path, context)
                    all_issues.extend(detector_issues)
                    detectors_run.append(detector.name)
                    
                    # Count patterns checked
                    patterns = detector.get_detection_patterns()
                    self.total_patterns_checked += len(patterns)
                    
                except Exception as e:
                    # Log detector error but continue with other detectors
                    print(f"Warning: {detector.name} failed: {e}")
        
        # Store analysis metadata
        result.detectors_run = detectors_run
        result.patterns_checked = self.total_patterns_checked
        result.analysis_time_ms = (time.time() - start_time) * 1000
        
        # Process and prioritize issues
        result.issues = self._prioritize_issues(all_issues)
        
        # Determine overall status
        result.status = self._determine_status(result.issues)
        
        # Generate guidance
        result.guidance = self._generate_guidance(result.issues, context)
        
        # Calculate complexity score
        result.complexity_score = self._calculate_complexity_score(result.issues, result.total_lines)
        
        return result
    
    def _detect_language(self, file_path: str, code: str) -> Optional[str]:
        """Detect programming language from file extension and content"""
        file_lower = file_path.lower()
        
        # File extension mapping
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.rs': 'rust',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.sh': 'bash',
            '.ps1': 'powershell'
        }
        
        for ext, lang in extension_map.items():
            if file_path.endswith(ext):
                return lang
        
        # Content-based detection fallbacks
        code_lower = code.lower()
        
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function ' in code and ('var ' in code or 'let ' in code or 'const ' in code):
            return 'javascript'
        elif 'public class ' in code and 'import java' in code:
            return 'java'
        elif 'using ' in code and 'namespace ' in code:
            return 'csharp'
        
        return None
    
    def _prioritize_issues(self, issues: List[DetectedIssue]) -> List[DetectedIssue]:
        """Prioritize issues by severity, confidence, and type"""
        
        def priority_score(issue: DetectedIssue) -> Tuple[int, float, str]:
            """Calculate priority score for sorting"""
            severity_scores = {
                Severity.CRITICAL: 4,
                Severity.HIGH: 3,
                Severity.MEDIUM: 2,
                Severity.LOW: 1
            }
            
            # Primary: severity (higher is more important)
            severity_score = severity_scores.get(issue.severity, 0)
            
            # Secondary: confidence (higher is more important)
            confidence_score = issue.confidence
            
            # Tertiary: issue type (security issues first)
            type_priority = {
                'hardcoded_secret': 'A',
                'sql_injection_risk': 'B',
                'insecure_protocol': 'C',
                'missing_error_handling': 'D',
                'large_file': 'E',
                'large_function': 'F',
                'god_object': 'G',
                'deep_nesting': 'H',
                'duplicate_code': 'I'
            }
            
            type_score = type_priority.get(issue.type.value, 'Z')
            
            # For reverse sorting, negate the type score priority (A should come first in reverse sort)
            return (severity_score, confidence_score, ord('Z') - ord(type_score))
        
        # Sort by priority (reverse for descending order)
        return sorted(issues, key=priority_score, reverse=True)
    
    def _determine_status(self, issues: List[DetectedIssue]) -> str:
        """Determine overall analysis status"""
        if not issues:
            return "clean"
        
        critical_count = sum(1 for issue in issues if issue.severity == Severity.CRITICAL)
        high_count = sum(1 for issue in issues if issue.severity == Severity.HIGH)
        
        if critical_count > 0:
            return "critical_issues"
        elif high_count > 0:
            return "high_issues"
        else:
            return "issues_found"
    
    def _generate_guidance(self, issues: List[DetectedIssue], context: Dict[str, Any]) -> List[str]:
        """Generate actionable guidance based on detected issues"""
        guidance = []
        
        if not issues:
            guidance.extend([
                "✅ No issues detected in this code",
                "🏗️ Code appears to follow good practices",
                "🚀 Ready for review and deployment"
            ])
            return guidance
        
        # Count issues by severity
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        high_issues = [i for i in issues if i.severity == Severity.HIGH]
        medium_issues = [i for i in issues if i.severity == Severity.MEDIUM]
        low_issues = [i for i in issues if i.severity == Severity.LOW]
        
        # Critical issues - immediate action required
        if critical_issues:
            guidance.append(f"🚨 {len(critical_issues)} critical issue(s) found - fix immediately!")
            
            # Show first few critical issues
            for issue in critical_issues[:3]:
                guidance.append(f"   🔴 Line {issue.line_number}: {issue.message}")
                guidance.append(f"      💡 {issue.fix_suggestion}")
        
        # High priority issues
        if high_issues:
            guidance.append(f"⚠️ {len(high_issues)} high-priority issue(s) need attention")
            
            # Group by type for better organization
            high_by_type = {}
            for issue in high_issues:
                issue_type = issue.type.value
                if issue_type not in high_by_type:
                    high_by_type[issue_type] = []
                high_by_type[issue_type].append(issue)
            
            # Show grouped high issues
            for issue_type, type_issues in list(high_by_type.items())[:2]:
                example_issue = type_issues[0]
                count = len(type_issues)
                type_name = issue_type.replace('_', ' ').title()
                
                if count == 1:
                    guidance.append(f"   🟡 {type_name}: Line {example_issue.line_number}")
                else:
                    guidance.append(f"   🟡 {type_name}: {count} occurrences (starting line {example_issue.line_number})")
                guidance.append(f"      💡 {example_issue.fix_suggestion}")
        
        # Summary of other issues
        if medium_issues:
            guidance.append(f"📋 {len(medium_issues)} medium-priority improvement(s) available")
        
        if low_issues:
            guidance.append(f"📝 {len(low_issues)} minor improvement(s) suggested")
        
        # Context-specific advice
        context_advice = self._get_context_advice(issues, context)
        if context_advice:
            guidance.extend(context_advice)
        
        # General recommendations
        total_issues = len(issues)
        if total_issues > 10:
            guidance.append("🎯 Focus on critical and high-priority issues first")
        
        if any(issue.type.value == 'large_file' for issue in issues):
            guidance.append("🔨 Consider refactoring large files for better maintainability")
        
        return guidance
    
    def _get_context_advice(self, issues: List[DetectedIssue], context: Dict[str, Any]) -> List[str]:
        """Get context-specific advice"""
        advice = []
        environment = context.get('environment', '').lower()
        project_type = context.get('project_type', '').lower()
        
        # Environment-specific advice
        if environment == 'production':
            critical_count = sum(1 for issue in issues if issue.severity == Severity.CRITICAL)
            if critical_count > 0:
                advice.append("🚫 Critical issues found - do not deploy to production")
        
        # Project type specific advice
        if project_type in ['api', 'web service']:
            security_issues = [i for i in issues if 'secret' in i.type.value or 'injection' in i.type.value]
            if security_issues:
                advice.append("🔐 Security issues in API code require immediate attention")
        
        # File type specific advice
        if any('test' in issue.file_path.lower() for issue in issues):
            advice.append("🧪 Issues in test files may affect test reliability")
        
        return advice
    
    def _calculate_complexity_score(self, issues: List[DetectedIssue], total_lines: int) -> str:
        """Calculate overall complexity score"""
        if not issues:
            return "low"
        
        # Calculate weighted issue score
        severity_weights = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 5,
            Severity.MEDIUM: 2,
            Severity.LOW: 1
        }
        
        total_score = sum(severity_weights.get(issue.severity, 0) for issue in issues)
        
        # Normalize by file size
        normalized_score = total_score / max(total_lines / 100, 1)  # Per 100 lines
        
        if normalized_score >= 10:
            return "high"
        elif normalized_score >= 5:
            return "medium"
        else:
            return "low"
    
    def get_detector_info(self) -> List[Dict[str, Any]]:
        """Get information about all registered detectors"""
        return [detector.get_detector_info() for detector in self.detectors]
    
    def enable_detector(self, detector_name: str) -> bool:
        """Enable a specific detector"""
        for detector in self.detectors:
            if detector.name == detector_name:
                detector.enabled = True
                return True
        return False
    
    def disable_detector(self, detector_name: str) -> bool:
        """Disable a specific detector"""
        for detector in self.detectors:
            if detector.name == detector_name:
                detector.enabled = False
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        enabled_detectors = [d for d in self.detectors if d.enabled]
        
        return {
            "total_detectors": len(self.detectors),
            "enabled_detectors": len(enabled_detectors),
            "detector_names": [d.name for d in enabled_detectors],
            "total_patterns_checked": self.total_patterns_checked,
            "supported_languages": list(set(
                lang for detector in enabled_detectors 
                for lang in detector.get_supported_languages()
            ))
        }