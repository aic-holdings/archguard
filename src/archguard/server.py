"""
ArchGuard v0 - AI Governance MCP Server (Refactored)
Provides real-time coding guidance for AI agents.

This is the clean, refactored version with proper separation of concerns.
"""

from fastmcp import FastMCP
from .tools import (
    get_guidance, search_rules, list_rule_categories,
    detect_issues, analyze_code_context, batch_analyze_issues, get_detection_info,
    get_archguard_help, get_rules_resource, get_review_code_prompt
)

# Create the ArchGuard MCP server
mcp = FastMCP("ArchGuard")

# Global variables to store server context and project
_server_context = "desktop-app"
_server_project = None

@mcp.tool
def get_guidance_tool(action: str, code: str = "", context: str = "") -> dict:
    """
    🏗️ Get comprehensive architectural guidance for coding actions
    
    This is ArchGuard's primary tool for providing real-time architectural guidance.
    Use this tool whenever you're about to:
    - Create new files, functions, or components
    - Design APIs, databases, or system architecture  
    - Implement authentication, security, or data handling
    - Refactor existing code or restructure projects
    - Make any significant coding decisions
    
    The tool analyzes your intended action and existing code to provide:
    - 🔒 Security best practices and vulnerability prevention
    - 📐 Architectural patterns and design recommendations  
    - 🎯 Code organization and maintainability guidance
    - ⚡ Performance optimization suggestions
    - 📋 Industry standards and compliance advice
    
    Args:
        action: Describe what you're planning to do (e.g., "create user authentication system", 
                "design REST API for orders", "refactor large component")
        code: Optional existing code to analyze (provide relevant snippets)
        context: Optional additional context about your project, tech stack, or constraints
        
    Returns:
        Comprehensive guidance dictionary with:
        - guidance: List of specific, actionable recommendations
        - status: "advisory" (never blocking your work)
        - action: Your original action for reference
        - complexity_score: Estimated complexity (low/medium/high)
        - patterns: Suggested architectural patterns when applicable
        
    Example usage:
        "Get guidance for implementing user authentication with JWT tokens"
        "Review this 200-line component for architectural improvements"
        "Suggest database schema design for e-commerce orders"
    """
    return get_guidance(action, code, context, _server_context, _server_project)

@mcp.tool  
def search_rules_tool(query: str, max_results: int = 5) -> dict:
    """
    🔍 Search ArchGuard rules by query text
    
    This tool allows you to search through ArchGuard's rule database to find
    specific guidance on architectural patterns, best practices, and design decisions.
    
    Args:
        query: Search query text (searches titles, guidance, keywords, etc.)
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary with matching rules and their relevance scores
    """
    return search_rules(query, max_results)

@mcp.tool
def list_rule_categories_tool() -> dict:
    """
    📋 List all available rule categories
    
    Returns all rule categories available in ArchGuard's rule engine,
    helping you understand what types of guidance are available.
    """
    return list_rule_categories()

@mcp.tool
def detect_issues_tool(code: str, file_path: str = "unknown.py", language: str = None, 
                      report_type: str = "summary", project_context: dict = None) -> dict:
    """
    🔍 Detect specific code issues using hybrid analysis
    
    This tool provides the second mode of ArchGuard - specific issue detection.
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
    return detect_issues(code, file_path, language, report_type, project_context, 
                        _server_context, _server_project)

@mcp.tool
def analyze_code_context_tool(code: str, line_number: int = None, language: str = None, 
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
    return analyze_code_context(code, line_number, language, focus_keywords)

@mcp.tool
def batch_analyze_issues_tool(code: str, file_path: str = "unknown.py", 
                             enable_llm_analysis: bool = False, project_context: dict = None) -> dict:
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
        
    Returns:
        Comprehensive analysis with:
        - detection_results: Standard detection findings
        - llm_analysis: Enhanced analysis with contextual understanding (if enabled)
        - recommendations: Prioritized improvement suggestions
        - patterns: Identified code patterns and issues
        - report_options: Different report formats available
    """
    return batch_analyze_issues(code, file_path, enable_llm_analysis, project_context,
                               _server_context, _server_project)

@mcp.tool
def get_detection_info_tool() -> dict:
    """
    ℹ️ Get information about ArchGuard's detection capabilities
    
    This tool provides details about the detection engine, available detectors,
    supported languages, and detection patterns. Use this to understand what
    types of issues ArchGuard can detect and how the detection system works.
    
    Returns:
        Comprehensive information about:
        - available_detectors: List of all detection modules
        - supported_languages: Programming languages supported
        - detection_patterns: Types of patterns and issues detected
        - statistics: Performance and capability metrics
    """
    return get_detection_info()

@mcp.tool
def get_archguard_help_tool() -> dict:
    """
    📚 Get comprehensive help on using ArchGuard effectively
    
    This tool provides coding agents with detailed instructions on how to best
    utilize ArchGuard's capabilities. Use this tool when you want to understand:
    - How to phrase requests to get the most helpful guidance
    - What types of architectural questions ArchGuard can answer
    - Best practices for integrating ArchGuard into your development workflow
    - Examples of effective ArchGuard interactions
    
    Returns:
        Complete guide on ArchGuard usage, capabilities, and best practices
    """
    return get_archguard_help()

@mcp.resource("archguard://rules")
def get_rules() -> str:
    """
    📋 Access ArchGuard's comprehensive architectural governance rules
    
    This resource provides the complete set of architectural standards and 
    best practices that ArchGuard uses to evaluate code and provide guidance.
    Use this when you need to understand ArchGuard's recommendations or 
    when establishing coding standards for a project.
    
    Contains rules for: security, performance, maintainability, scalability,
    documentation, testing, and general architectural principles.
    """
    return get_rules_resource()

@mcp.prompt  
def review_code(code: str) -> str:
    """
    🔍 Generate comprehensive architectural code review prompt
    
    This prompt template guides thorough code review with focus on architectural
    principles, security, performance, and maintainability. Use this when you
    want to perform a detailed review of code against ArchGuard's standards.
    
    The generated prompt will analyze:
    - Architectural patterns and design principles
    - Security vulnerabilities and best practices
    - Performance optimization opportunities  
    - Code organization and maintainability
    - Testing and documentation completeness
    
    Args:
        code: The code snippet or file content to review
        
    Returns:
        Structured review prompt for comprehensive architectural analysis
    """
    return get_review_code_prompt(code)

def main(context: str = "desktop-app", project: str = None):
    """Main entry point for the MCP server"""
    import sys
    global _server_context, _server_project
    
    print(f"🛡️ Starting ArchGuard MCP Server (Refactored)...", file=sys.stderr)
    print(f"🎯 Context: {context}", file=sys.stderr)
    if project:
        print(f"📁 Project: {project}", file=sys.stderr)
    
    # Store context and project globally
    _server_context = context
    _server_project = project
    
    mcp.run()  # Default: stdio transport

if __name__ == "__main__":
    main()