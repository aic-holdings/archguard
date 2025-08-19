"""
Symmetra Detection System

Hybrid detection system that combines deterministic pattern matching
with targeted LLM analysis for immediate, actionable code feedback.

Architecture:
- Tier 1: Definitive issues (regex/AST) for high-confidence detection
- Tier 2: Targeted LLM analysis for detected issues with context
- Tier 3: Skip complex semantic analysis (reserved for future)

Usage:
    from symmetra.detectors import create_detection_engine
    
    engine = create_detection_engine()
    result = engine.analyze_code(code, file_path, context)
"""

from .base import Detector, DetectedIssue, DetectionResult
from .security import SecurityDetector
from .size import SizeDetector
from .patterns import PatternDetector
from .engine import DetectionEngine

def create_detection_engine() -> DetectionEngine:
    """Create a detection engine with default detectors"""
    return DetectionEngine([
        SecurityDetector(),
        SizeDetector(),
        PatternDetector()
    ])

__all__ = [
    'Detector',
    'DetectedIssue', 
    'DetectionResult',
    'SecurityDetector',
    'SizeDetector',
    'PatternDetector',
    'DetectionEngine',
    'create_detection_engine'
]