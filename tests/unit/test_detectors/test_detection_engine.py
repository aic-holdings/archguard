"""
Unit tests for DetectionEngine

Tests the coordination of multiple detectors and result prioritization.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.symmetra.detectors.engine import DetectionEngine
from src.symmetra.detectors.base import Detector, DetectedIssue, Severity, IssueType


class MockDetector(Detector):
    """Mock detector for testing"""
    
    def __init__(self, name, issues=None, should_run_result=True, patterns=None):
        super().__init__()
        self.name = name
        self._issues = issues or []
        self._should_run_result = should_run_result
        self._patterns = patterns or ["mock_pattern"]
    
    def detect(self, code, file_path, context):
        return self._issues
    
    def should_run(self, file_path, language, context):
        return self._should_run_result
    
    def get_detection_patterns(self):
        return self._patterns
    
    def get_supported_languages(self):
        return ["python", "javascript"]


class TestDetectionEngine:
    """Test DetectionEngine functionality"""
    
    def setup_method(self):
        """Set up test instances"""
        self.mock_detector1 = MockDetector("MockDetector1")
        self.mock_detector2 = MockDetector("MockDetector2")
        self.engine = DetectionEngine([self.mock_detector1, self.mock_detector2])
    
    def test_engine_initialization(self):
        """Test engine initializes with detectors"""
        assert len(self.engine.detectors) == 2
        assert self.engine.total_patterns_checked == 0
    
    def test_analyze_code_basic(self):
        """Test basic code analysis"""
        code = "print('hello world')"
        result = self.engine.analyze_code(code, "test.py")
        
        assert result.file_path == "test.py"
        assert result.total_lines == 1
        assert result.language == "python"  # Should auto-detect
        assert result.status == "clean"  # No issues from mock detectors
        assert len(result.issues) == 0
        assert result.analysis_time_ms > 0
    
    def test_language_detection(self):
        """Test automatic language detection"""
        test_cases = [
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.ts", "typescript"),
            ("test.java", "java"),
            ("test.cs", "csharp"),
            ("test.unknown", None)
        ]
        
        for file_path, expected_language in test_cases:
            result = self.engine.analyze_code("code", file_path)
            if expected_language:
                assert result.language == expected_language
            # Note: content-based detection tested separately
    
    def test_content_based_language_detection(self):
        """Test language detection from code content"""
        test_cases = [
            ("def function():\n    import os", "python"),
            ("function test() {\n    var x = 1;\n}", "javascript"),
            ("public class Test {\n    import java.util.*;\n}", "java"),
            ("using System;\nnamespace Test {", "csharp")
        ]
        
        for code, expected_language in test_cases:
            result = self.engine.analyze_code(code, "unknown_file")
            assert result.language == expected_language
    
    def test_detector_should_run_filtering(self):
        """Test that only appropriate detectors run"""
        # Create detector that shouldn't run
        no_run_detector = MockDetector("NoRunDetector", should_run_result=False)
        engine = DetectionEngine([self.mock_detector1, no_run_detector])
        
        result = engine.analyze_code("code", "test.py")
        
        # Should only run mock_detector1
        assert "MockDetector1" in result.detectors_run
        assert "NoRunDetector" not in result.detectors_run
    
    def test_issue_detection_and_collection(self):
        """Test detection and collection of issues from multiple detectors"""
        # Create issues for detectors to return
        issue1 = DetectedIssue(
            type=IssueType.HARDCODED_SECRET,
            severity=Severity.CRITICAL,
            rule_id="SEC001",
            file_path="test.py",
            line_number=1,
            evidence="api_key = 'secret'",
            message="Hardcoded secret detected"
        )
        
        issue2 = DetectedIssue(
            type=IssueType.LARGE_FILE,
            severity=Severity.MEDIUM,
            rule_id="SIZE001",
            file_path="test.py", 
            line_number=1,
            evidence="File too large",
            message="File exceeds size limit"
        )
        
        detector1 = MockDetector("SecurityDetector", [issue1])
        detector2 = MockDetector("SizeDetector", [issue2])
        engine = DetectionEngine([detector1, detector2])
        
        result = engine.analyze_code("code", "test.py")
        
        assert len(result.issues) == 2
        assert result.status == "critical_issues"  # Due to critical issue
        assert len(result.critical_issues) == 1
        assert len(result.high_issues) == 0
    
    def test_issue_prioritization(self):
        """Test that issues are prioritized correctly"""
        # Create issues with different severities
        critical_issue = DetectedIssue(
            type=IssueType.HARDCODED_SECRET,
            severity=Severity.CRITICAL,
            rule_id="SEC001",
            file_path="test.py",
            line_number=3,
            evidence="critical",
            message="Critical issue",
            confidence=0.9
        )
        
        high_issue = DetectedIssue(
            type=IssueType.SQL_INJECTION_RISK,
            severity=Severity.HIGH,
            rule_id="SEC002", 
            file_path="test.py",
            line_number=2,
            evidence="high",
            message="High issue",
            confidence=0.8
        )
        
        medium_issue = DetectedIssue(
            type=IssueType.LARGE_FILE,
            severity=Severity.MEDIUM,
            rule_id="SIZE001",
            file_path="test.py",
            line_number=1,
            evidence="medium",
            message="Medium issue",
            confidence=0.7
        )
        
        detector = MockDetector("TestDetector", [medium_issue, critical_issue, high_issue])
        engine = DetectionEngine([detector])
        
        result = engine.analyze_code("code", "test.py")
        
        # Should be ordered: critical, high, medium
        assert result.issues[0].severity == Severity.CRITICAL
        assert result.issues[1].severity == Severity.HIGH
        assert result.issues[2].severity == Severity.MEDIUM
    
    def test_confidence_based_prioritization(self):
        """Test prioritization considers confidence scores"""
        # Two issues with same severity but different confidence
        high_confidence_issue = DetectedIssue(
            type=IssueType.HARDCODED_SECRET,
            severity=Severity.HIGH,
            rule_id="SEC001",
            file_path="test.py",
            line_number=1,
            evidence="high confidence",
            message="High confidence issue",
            confidence=0.95
        )
        
        low_confidence_issue = DetectedIssue(
            type=IssueType.HARDCODED_SECRET,
            severity=Severity.HIGH,
            rule_id="SEC002",
            file_path="test.py",
            line_number=2,
            evidence="low confidence",
            message="Low confidence issue",
            confidence=0.6
        )
        
        detector = MockDetector("TestDetector", [low_confidence_issue, high_confidence_issue])
        engine = DetectionEngine([detector])
        
        result = engine.analyze_code("code", "test.py")
        
        # High confidence should come first
        assert result.issues[0].confidence == 0.95
        assert result.issues[1].confidence == 0.6
    
    def test_type_based_prioritization(self):
        """Test prioritization considers issue types (security first)"""
        security_issue = DetectedIssue(
            type=IssueType.HARDCODED_SECRET,
            severity=Severity.MEDIUM,
            rule_id="SEC001",
            file_path="test.py",
            line_number=1,
            evidence="security",
            message="Security issue",
            confidence=0.8
        )
        
        size_issue = DetectedIssue(
            type=IssueType.LARGE_FILE,
            severity=Severity.MEDIUM,
            rule_id="SIZE001",
            file_path="test.py",
            line_number=1,
            evidence="size",
            message="Size issue",
            confidence=0.8
        )
        
        detector = MockDetector("TestDetector", [size_issue, security_issue])
        engine = DetectionEngine([detector])
        
        result = engine.analyze_code("code", "test.py")
        
        # Security issue should come first even with same severity/confidence
        assert result.issues[0].type == IssueType.HARDCODED_SECRET
        assert result.issues[1].type == IssueType.LARGE_FILE
    
    def test_status_determination(self):
        """Test status determination based on issue severity"""
        test_cases = [
            ([], "clean"),
            ([Severity.LOW], "issues_found"),
            ([Severity.MEDIUM], "issues_found"),
            ([Severity.HIGH], "high_issues"),
            ([Severity.CRITICAL], "critical_issues"),
            ([Severity.HIGH, Severity.MEDIUM], "high_issues"),
            ([Severity.CRITICAL, Severity.HIGH], "critical_issues")
        ]
        
        for severities, expected_status in test_cases:
            issues = [
                DetectedIssue(
                    type=IssueType.HARDCODED_SECRET,
                    severity=severity,
                    rule_id=f"TEST{i}",
                    file_path="test.py",
                    line_number=i+1,
                    evidence=f"evidence{i}",
                    message=f"message{i}"
                )
                for i, severity in enumerate(severities)
            ]
            
            detector = MockDetector("TestDetector", issues)
            engine = DetectionEngine([detector])
            
            result = engine.analyze_code("code", "test.py")
            assert result.status == expected_status
    
    def test_guidance_generation(self):
        """Test guidance generation based on detected issues"""
        critical_issue = DetectedIssue(
            type=IssueType.HARDCODED_SECRET,
            severity=Severity.CRITICAL,
            rule_id="SEC001",
            file_path="test.py",
            line_number=1,
            evidence="api_key = 'secret'",
            message="Hardcoded secret detected"
        )
        
        detector = MockDetector("TestDetector", [critical_issue])
        engine = DetectionEngine([detector])
        
        result = engine.analyze_code("code", "test.py")
        
        assert len(result.guidance) > 0
        guidance_text = " ".join(result.guidance).lower()
        assert "critical" in guidance_text
        assert "fix" in guidance_text or "address" in guidance_text
    
    def test_context_specific_guidance(self):
        """Test context-specific guidance generation"""
        issue = DetectedIssue(
            type=IssueType.HARDCODED_SECRET,
            severity=Severity.CRITICAL,
            rule_id="SEC001",
            file_path="test.py",
            line_number=1,
            evidence="secret",
            message="Secret detected"
        )
        
        detector = MockDetector("TestDetector", [issue])
        engine = DetectionEngine([detector])
        
        # Test production environment context
        prod_context = {"environment": "production", "project_type": "api"}
        result = engine.analyze_code("code", "test.py", prod_context)
        
        guidance_text = " ".join(result.guidance).lower()
        assert "production" in guidance_text or "deploy" in guidance_text
    
    def test_complexity_score_calculation(self):
        """Test complexity score calculation"""
        test_cases = [
            ([], "low"),
            ([Severity.LOW] * 5, "low"),
            ([Severity.MEDIUM] * 3, "medium"),
            ([Severity.HIGH] * 2, "medium"),
            ([Severity.CRITICAL], "high"),
            ([Severity.CRITICAL, Severity.HIGH] * 3, "high")
        ]
        
        for severities, expected_complexity in test_cases:
            issues = [
                DetectedIssue(
                    type=IssueType.HARDCODED_SECRET,
                    severity=severity,
                    rule_id=f"TEST{i}",
                    file_path="test.py",
                    line_number=i+1,
                    evidence=f"evidence{i}",
                    message=f"message{i}"
                )
                for i, severity in enumerate(severities)
            ]
            
            detector = MockDetector("TestDetector", issues)
            engine = DetectionEngine([detector])
            
            result = engine.analyze_code("code", "test.py")
            assert result.complexity_score == expected_complexity
    
    def test_detector_error_handling(self):
        """Test handling of detector errors"""
        # Create detector that raises exception
        failing_detector = Mock()
        failing_detector.name = "FailingDetector"
        failing_detector.should_run.return_value = True
        failing_detector.detect.side_effect = Exception("Detector failed")
        failing_detector.get_detection_patterns.return_value = ["pattern"]
        
        working_detector = MockDetector("WorkingDetector")
        engine = DetectionEngine([failing_detector, working_detector])
        
        # Should not crash, should continue with working detector
        result = engine.analyze_code("code", "test.py")
        
        assert "WorkingDetector" in result.detectors_run
        assert "FailingDetector" not in result.detectors_run
        # Should still produce valid result
        assert result.status in ["clean", "issues_found", "high_issues", "critical_issues"]
    
    def test_patterns_counting(self):
        """Test that pattern counting works correctly"""
        detector1 = MockDetector("Detector1", patterns=["pattern1", "pattern2"])
        detector2 = MockDetector("Detector2", patterns=["pattern3", "pattern4", "pattern5"])
        engine = DetectionEngine([detector1, detector2])
        
        engine.analyze_code("code", "test.py")
        
        assert engine.total_patterns_checked == 5  # 2 + 3 patterns
    
    def test_get_detector_info(self):
        """Test getting detector information"""
        info = self.engine.get_detector_info()
        
        assert len(info) == 2
        assert info[0]["name"] == "MockDetector1"
        assert info[1]["name"] == "MockDetector2"
    
    def test_detector_enable_disable(self):
        """Test enabling and disabling detectors"""
        assert self.engine.enable_detector("MockDetector1") is True
        assert self.engine.disable_detector("MockDetector1") is True
        assert self.engine.enable_detector("NonExistentDetector") is False
        assert self.engine.disable_detector("NonExistentDetector") is False
    
    def test_get_statistics(self):
        """Test getting engine statistics"""
        stats = self.engine.get_statistics()
        
        assert stats["total_detectors"] == 2
        assert stats["enabled_detectors"] == 2
        assert "MockDetector1" in stats["detector_names"]
        assert "MockDetector2" in stats["detector_names"]
        assert set(stats["supported_languages"]) == {"python", "javascript"}
        assert stats["total_patterns_checked"] >= 0
    
    def test_empty_code_handling(self):
        """Test handling of empty code"""
        result = self.engine.analyze_code("", "empty.py")
        
        assert result.total_lines == 1  # Empty string splits to 1 line
        assert result.status == "clean"
        assert len(result.issues) == 0
    
    def test_large_code_handling(self):
        """Test handling of large code files"""
        large_code = "\n".join([f"line {i}" for i in range(1000)])
        result = self.engine.analyze_code(large_code, "large.py")
        
        assert result.total_lines == 1000
        assert result.analysis_time_ms > 0
        # Should complete without errors