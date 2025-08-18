"""
Base classes for ArchGuard detection system.

Provides the foundation for all detectors with consistent interfaces
and data structures for issue reporting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"  # Security vulnerabilities, data loss risk
    HIGH = "high"         # Architecture issues, performance problems
    MEDIUM = "medium"     # Best practices, maintainability
    LOW = "low"           # Style preferences, minor improvements


class IssueType(Enum):
    """Types of issues that can be detected"""
    HARDCODED_SECRET = "hardcoded_secret"
    SQL_INJECTION_RISK = "sql_injection_risk"
    INSECURE_PROTOCOL = "insecure_protocol"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    LARGE_FILE = "large_file"
    LARGE_FUNCTION = "large_function"
    GOD_OBJECT = "god_object"
    DEEP_NESTING = "deep_nesting"
    MISSING_TESTS = "missing_tests"
    DUPLICATE_CODE = "duplicate_code"


@dataclass
class DetectedIssue:
    """Represents a specific issue found in code"""
    
    # Core identification
    type: IssueType
    severity: Severity
    rule_id: str
    
    # Location information
    file_path: str
    line_number: int
    
    # Issue details (required fields)
    evidence: str  # What was detected
    message: str   # Human-readable description
    
    # Optional location and details
    column_number: Optional[int] = None
    fix_suggestion: str = ""  # How to fix it
    
    # Confidence and metadata
    confidence: float = 1.0  # 0.0 to 1.0
    language: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Pattern matching details
    pattern_matched: Optional[str] = None
    matched_text: Optional[str] = None
    
    def __post_init__(self):
        """Validate the issue after creation"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if self.line_number < 1:
            raise ValueError(f"Line number must be >= 1, got {self.line_number}")
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical issue"""
        return self.severity == Severity.CRITICAL
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence detection"""
        return self.confidence >= 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "evidence": self.evidence,
            "message": self.message,
            "fix_suggestion": self.fix_suggestion,
            "confidence": self.confidence,
            "language": self.language,
            "context": self.context,
            "pattern_matched": self.pattern_matched,
            "matched_text": self.matched_text
        }


@dataclass
class DetectionResult:
    """Results from running detection on code"""
    
    # Detection metadata
    file_path: str
    language: Optional[str] = None
    total_lines: int = 0
    analysis_time_ms: float = 0.0
    
    # Issues found
    issues: List[DetectedIssue] = field(default_factory=list)
    
    # Detection statistics
    detectors_run: List[str] = field(default_factory=list)
    patterns_checked: int = 0
    
    # Status and guidance
    status: str = "clean"  # clean, issues_found, error
    guidance: List[str] = field(default_factory=list)
    complexity_score: str = "low"  # low, medium, high
    
    @property
    def critical_issues(self) -> List[DetectedIssue]:
        """Get all critical issues"""
        return [issue for issue in self.issues if issue.severity == Severity.CRITICAL]
    
    @property
    def high_issues(self) -> List[DetectedIssue]:
        """Get all high severity issues"""
        return [issue for issue in self.issues if issue.severity == Severity.HIGH]
    
    @property
    def issue_count_by_severity(self) -> Dict[str, int]:
        """Count issues by severity"""
        counts = {severity.value: 0 for severity in Severity}
        for issue in self.issues:
            counts[issue.severity.value] += 1
        return counts
    
    @property
    def has_blocking_issues(self) -> bool:
        """Check if there are issues that should block deployment"""
        return len(self.critical_issues) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "total_lines": self.total_lines,
            "analysis_time_ms": self.analysis_time_ms,
            "issues": [issue.to_dict() for issue in self.issues],
            "detectors_run": self.detectors_run,
            "patterns_checked": self.patterns_checked,
            "status": self.status,
            "guidance": self.guidance,
            "complexity_score": self.complexity_score,
            "issue_counts": self.issue_count_by_severity,
            "has_blocking_issues": self.has_blocking_issues
        }


class Detector(ABC):
    """Base class for all ArchGuard detectors"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.name = self.__class__.__name__
    
    @abstractmethod
    def detect(self, code: str, file_path: str, context: Dict[str, Any]) -> List[DetectedIssue]:
        """
        Detect issues in the provided code.
        
        Args:
            code: The source code to analyze
            file_path: Path to the file being analyzed
            context: Additional context (language, project info, etc.)
            
        Returns:
            List of detected issues
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of programming languages this detector supports"""
        pass
    
    @abstractmethod
    def get_detection_patterns(self) -> Dict[str, str]:
        """Get the patterns this detector looks for (for documentation)"""
        pass
    
    def is_language_supported(self, language: Optional[str]) -> bool:
        """Check if this detector supports the given language"""
        if language is None:
            return True  # Assume universal support if language unknown
        
        supported = self.get_supported_languages()
        return "all" in supported or language.lower() in [lang.lower() for lang in supported]
    
    def should_run(self, file_path: str, language: Optional[str], context: Dict[str, Any]) -> bool:
        """Determine if this detector should run on the given file"""
        if not self.enabled:
            return False
        
        return self.is_language_supported(language)
    
    def get_detector_info(self) -> Dict[str, Any]:
        """Get information about this detector"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "supported_languages": self.get_supported_languages(),
            "detection_patterns": self.get_detection_patterns(),
            "description": self.__doc__ or "No description available"
        }


class DetectorRegistry:
    """Registry for managing detector instances"""
    
    def __init__(self):
        self._detectors: Dict[str, Detector] = {}
    
    def register(self, detector: Detector, name: Optional[str] = None):
        """Register a detector"""
        detector_name = name or detector.name
        self._detectors[detector_name] = detector
    
    def get(self, name: str) -> Optional[Detector]:
        """Get a detector by name"""
        return self._detectors.get(name)
    
    def get_all(self) -> List[Detector]:
        """Get all registered detectors"""
        return list(self._detectors.values())
    
    def get_enabled(self) -> List[Detector]:
        """Get all enabled detectors"""
        return [detector for detector in self._detectors.values() if detector.enabled]
    
    def list_names(self) -> List[str]:
        """Get names of all registered detectors"""
        return list(self._detectors.keys())
    
    def enable(self, name: str):
        """Enable a detector"""
        if name in self._detectors:
            self._detectors[name].enabled = True
    
    def disable(self, name: str):
        """Disable a detector"""
        if name in self._detectors:
            self._detectors[name].enabled = False


# Global detector registry
detector_registry = DetectorRegistry()