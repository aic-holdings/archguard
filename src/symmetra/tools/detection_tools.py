"""
Detection Tools - Specific code issue detection and analysis

This module contains the new hybrid detection tools that find concrete,
actionable issues in code using pattern matching, AST analysis, and LLM enhancement.
"""

from typing import Dict, Any, List, Optional
from ..detectors import create_detection_engine
from ..analyzers import LLMAnalyzer, ReportGenerator, ContextExtractor

# Initialize detection components
detection_engine = create_detection_engine()
llm_analyzer = LLMAnalyzer()
report_generator = ReportGenerator()
context_extractor = ContextExtractor()

def detect_issues(code: str, file_path: str = "unknown.py", language: str = None, 
                 report_type: str = "summary", project_context: dict = None,
                 server_context: str = None, server_project: str = None) -> dict:
    """
    🔍 Detect specific code issues using hybrid analysis
    
    This tool provides the second mode of Symmetra - specific issue detection.
    Unlike get_guidance() which provides general architectural advice, this tool
    performs deep analysis to find concrete, actionable issues in your code.
    
    The detection system uses multiple techniques:
    - Pattern-based detection for common issues (secrets, SQL injection, etc.)
    - AST analysis for code structure problems (large functions, complexity)
    - Contextual analysis for project-specific concerns
    
    Args:
        code: Source code to analyze for issues
        file_path: Path to the file (helps with language detection and context)
        language: Programming language (auto-detected if not provided)
        report_type: Format of results ("summary", "ide_assistant", "agent", "desktop_app", "security_audit")
        project_context: Additional project context (environment, framework, etc.)
        server_context: Server context (ide-assistant, agent, desktop-app)
        server_project: Project directory path
        
    Returns:
        Comprehensive detection results with:
        - issues: List of detected issues with severity, confidence, and fix suggestions
        - analysis_summary: Overall analysis results and metrics
        - guidance: Prioritized recommendations based on findings
        - report: Formatted report based on specified report_type
        
    Example usage:
        "Check this authentication function for security vulnerabilities"
        "Analyze this 500-line file for maintainability issues"
        "Scan this API endpoint for common code problems"
    """
    if project_context is None:
        project_context = {}
    
    # Add global context
    project_context.update({
        "server_context": server_context,
        "project": server_project,
        "language": language
    })
    
    # Run detection analysis
    result = detection_engine.analyze_code(code, file_path, project_context)
    
    # Generate formatted report
    report = report_generator.generate_report(result, report_type=report_type, context=project_context)
    
    return {
        "detection_results": {
            "file_path": result.file_path,
            "language": result.language,
            "total_lines": result.total_lines,
            "status": result.status,
            "complexity_score": result.complexity_score,
            "analysis_time_ms": result.analysis_time_ms
        },
        "issues": [
            {
                "type": issue.type.value,
                "severity": issue.severity.value,
                "line_number": issue.line_number,
                "message": issue.message,
                "evidence": issue.evidence,
                "fix_suggestion": issue.fix_suggestion,
                "confidence": issue.confidence,
                "rule_id": issue.rule_id
            }
            for issue in result.issues
        ],
        "analysis_summary": {
            "total_issues": len(result.issues),
            "issue_breakdown": result.issue_count_by_severity,
            "critical_issues": len(result.critical_issues),
            "high_priority_issues": len(result.high_issues),
            "has_blocking_issues": result.has_blocking_issues,
            "detectors_run": result.detectors_run,
            "patterns_checked": result.patterns_checked
        },
        "guidance": result.guidance,
        "formatted_report": report,
        "next_steps": {
            "immediate_action": "Fix critical issues first" if result.critical_issues else "Review high-priority issues",
            "estimated_effort": f"{len(result.critical_issues) * 20 + len(result.high_issues) * 15} minutes",
            "testing_needed": len(result.issues) > 0
        }
    }

def analyze_code_context(code: str, line_number: int = None, language: str = None, 
                        focus_keywords: list = None) -> dict:
    """
    🎯 Extract and analyze code context around specific areas
    
    This tool provides intelligent context extraction for better understanding
    of code structure and relationships. Useful for understanding the environment
    around detected issues or when analyzing specific code sections.
    
    Args:
        code: Source code to analyze
        line_number: Specific line to focus on (1-indexed)
        language: Programming language for better parsing
        focus_keywords: Keywords to highlight in the context
        
    Returns:
        Detailed context analysis with:
        - context_lines: Code lines with metadata and highlighting
        - structure_info: Function/class/block context information
        - formatted_context: Human-readable context display
        - summary: Natural language description of the context
    """
    if focus_keywords is None:
        focus_keywords = []
    
    if line_number is None:
        # If no specific line, analyze the middle of the code
        lines = code.split('\n')
        line_number = len(lines) // 2
    
    context_result = context_extractor.extract_context(
        code=code,
        line_number=line_number,
        language=language,
        focus_keywords=focus_keywords
    )
    
    # Also extract function context if available
    function_context = context_extractor.extract_function_context(
        code=code,
        line_number=line_number,
        language=language
    )
    
    return {
        "context_analysis": context_result,
        "function_context": function_context,
        "metadata": {
            "total_lines": len(code.split('\n')),
            "focus_line": line_number,
            "language": language,
            "keywords_highlighted": len(focus_keywords)
        }
    }

def batch_analyze_issues(code: str, file_path: str = "unknown.py", 
                        enable_llm_analysis: bool = False, project_context: dict = None,
                        server_context: str = None, server_project: str = None) -> dict:
    """
    🧠 Perform comprehensive batch analysis with optional LLM enhancement
    
    This tool combines detection with intelligent analysis to provide deeper
    insights into code issues. It can optionally use LLM analysis for more
    nuanced understanding and context-specific recommendations.
    
    Args:
        code: Source code to analyze
        file_path: Path to the file being analyzed
        enable_llm_analysis: Whether to include LLM-powered contextual analysis
        project_context: Additional project context and constraints
        server_context: Server context (ide-assistant, agent, desktop-app)
        server_project: Project directory path
        
    Returns:
        Comprehensive analysis with:
        - detection_results: Standard detection findings
        - llm_analysis: Enhanced analysis with contextual understanding (if enabled)
        - recommendations: Prioritized improvement suggestions
        - patterns: Identified code patterns and issues
        - report_options: Different report formats available
    """
    if project_context is None:
        project_context = {}
    
    # Add global context
    project_context.update({
        "server_context": server_context,
        "project": server_project
    })
    
    # Run detection analysis
    result = detection_engine.analyze_code(code, file_path, project_context)
    
    analysis_data = None
    if enable_llm_analysis and result.issues:
        # Perform LLM analysis on detected issues
        analysis_data = llm_analyzer.batch_analyze(result.issues, code, project_context)
    
    # Generate different report formats
    report_formats = {}
    for report_type in ["summary", "ide_assistant", "agent", "desktop_app"]:
        report_formats[report_type] = report_generator.generate_report(
            result, analysis_data, report_type, project_context
        )
    
    return {
        "batch_analysis": {
            "detection_summary": {
                "total_issues": len(result.issues),
                "by_severity": result.issue_count_by_severity,
                "status": result.status,
                "complexity": result.complexity_score
            },
            "issue_categories": [issue.type.value for issue in result.issues],
            "priority_issues": [
                {
                    "type": issue.type.value,
                    "line": issue.line_number,
                    "message": issue.message,
                    "fix": issue.fix_suggestion
                }
                for issue in result.issues[:5]  # Top 5 priority issues
            ]
        },
        "llm_analysis": analysis_data if enable_llm_analysis else None,
        "recommendations": {
            "immediate": [f"Fix {issue.type.value}" for issue in result.critical_issues[:3]],
            "short_term": [f"Address {issue.type.value}" for issue in result.high_issues[:3]],
            "long_term": ["Establish automated code quality checks", "Implement security scanning"]
        },
        "report_formats": report_formats,
        "next_actions": {
            "critical_count": len(result.critical_issues),
            "blocking_deployment": result.has_blocking_issues,
            "estimated_fix_time": f"{len(result.issues) * 15} minutes",
            "testing_required": "Run tests after each fix"
        }
    }

def get_detection_info() -> dict:
    """
    ℹ️ Get information about Symmetra's detection capabilities
    
    This tool provides details about the detection engine, available detectors,
    supported languages, and detection patterns. Use this to understand what
    types of issues Symmetra can detect and how the detection system works.
    
    Returns:
        Comprehensive information about:
        - available_detectors: List of all detection modules
        - supported_languages: Programming languages supported
        - detection_patterns: Types of patterns and issues detected
        - statistics: Performance and capability metrics
    """
    detector_info = detection_engine.get_detector_info()
    statistics = detection_engine.get_statistics()
    
    return {
        "detection_system": {
            "version": "1.0",
            "mode": "hybrid_detection",
            "description": "Multi-tier detection system combining pattern matching, AST analysis, and contextual understanding"
        },
        "available_detectors": detector_info,
        "capabilities": {
            "supported_languages": statistics["supported_languages"],
            "total_detectors": statistics["total_detectors"],
            "enabled_detectors": statistics["enabled_detectors"],
            "patterns_available": statistics["total_patterns_checked"]
        },
        "detection_categories": {
            "security": ["hardcoded_secret", "sql_injection_risk", "insecure_protocol"],
            "maintainability": ["large_file", "large_function", "duplicate_code"],
            "quality": ["missing_error_handling", "god_object", "deep_nesting"],
            "patterns": ["anti_patterns", "code_smells", "architectural_issues"]
        },
        "report_formats": {
            "summary": "Balanced overview with key findings",
            "ide_assistant": "Concise, actionable for IDE integration",
            "agent": "Structured data for automated processing",
            "desktop_app": "Detailed educational explanations",
            "security_audit": "Security-focused compliance reporting"
        },
        "usage_guide": {
            "detect_issues": "Find specific code problems",
            "analyze_code_context": "Understand code structure and relationships",
            "batch_analyze_issues": "Comprehensive analysis with optional LLM enhancement",
            "get_guidance": "General architectural advice (complementary tool)"
        }
    }