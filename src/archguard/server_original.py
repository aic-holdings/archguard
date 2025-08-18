"""
ArchGuard v0 - AI Governance MCP Server
Provides real-time coding guidance for AI agents.
"""

from fastmcp import FastMCP
from .rules_engine import create_rule_engine
from .detectors import create_detection_engine
from .analyzers import LLMAnalyzer, ReportGenerator, ContextExtractor

# Create the ArchGuard MCP server
mcp = FastMCP("ArchGuard")

# Initialize rule engine (will switch to vector engine later)
rule_engine = create_rule_engine("keyword")

# Initialize detection engine with all detectors
detection_engine = create_detection_engine()

# Initialize analysis components
llm_analyzer = LLMAnalyzer()
report_generator = ReportGenerator()
context_extractor = ContextExtractor()

@mcp.tool
def get_guidance(action: str, code: str = "", context: str = "") -> dict:
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
    global _server_context, _server_project
    
    # Build project context for rule engine
    project_context = {
        "server_context": _server_context,
        "project": _server_project
    }
    
    # Use rule engine to find relevant rules
    relevant_rules = rule_engine.find_relevant_rules(
        action=action,
        code=code,
        context=context,
        project_context=project_context
    )
    
    # Extract guidance from rules
    guidance = []
    patterns = []
    rules_applied = []
    
    for rule in relevant_rules[:5]:  # Top 5 most relevant rules
        guidance.append(rule["guidance"])
        rules_applied.append(rule["rule_id"])
        
        # Add any patterns from the rule
        if "patterns" in rule:
            patterns.extend(rule["patterns"])
    
    # Add legacy code analysis (keep existing code analysis logic)
    if code:
        code_lines = len(code.split('\n'))
        if code_lines > 50:
            guidance.append(f"📏 Code length ({code_lines} lines) suggests considering decomposition")
        
        # Check for potential code smells
        if code.count('if') > 10:
            guidance.append("🧩 High cyclomatic complexity detected - consider extracting methods")
        if 'TODO' in code or 'FIXME' in code:
            guidance.append("📝 Address TODO/FIXME comments before finalizing")
        if any(word in code.lower() for word in ['password', 'secret', 'key']) and any(word in code for word in ['"', "'"]):
            guidance.append("🚨 Potential hardcoded secrets detected - use environment variables")
    
    # Add server context-specific guidance
    if _server_context == 'ide-assistant':
        guidance.append("💡 IDE Integration: Consider adding IntelliSense-friendly type hints")
        guidance.append("🔧 IDE Integration: Structure code for better refactoring support")
    elif _server_context == 'agent':
        guidance.append("🤖 Agent Mode: Focus on automated code generation patterns")
        guidance.append("🔄 Agent Mode: Design for programmatic modification")
    
    # Add project-specific guidance if project directory is available
    if _server_project:
        guidance.append(f"📁 Project Context: Working in {_server_project}")
        # TODO: Add project-specific configuration loading from .archguard.toml
    
    # Provide default guidance if no rules matched
    if not guidance:
        guidance.extend([
            "✅ No specific architectural concerns detected",
            "🏗️ Follow established coding standards and best practices",
            "🧪 Consider adding tests for new functionality",
            "📝 Document complex logic and API interfaces"
        ])
    
    # Determine complexity score based on number of rules and priority
    complexity_score = "low"
    if len(relevant_rules) > 3:
        complexity_score = "high"
    elif len(relevant_rules) > 1:
        complexity_score = "medium"
    elif any(rule.get("priority") == "high" for rule in relevant_rules):
        complexity_score = "medium"
    
    return {
        "guidance": guidance,
        "status": "advisory",
        "action": action,
        "complexity_score": complexity_score,
        "patterns": patterns if patterns else ["General Best Practices"],
        "rules_applied": rules_applied,
        "code_analysis": {
            "lines_analyzed": len(code.split('\n')) if code else 0,
            "context_provided": bool(context),
            "rules_matched": len(relevant_rules)
        }
    }

@mcp.tool
def search_rules(query: str, max_results: int = 5) -> dict:
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
    results = rule_engine.search_rules(query, max_results)
    
    return {
        "query": query,
        "total_results": len(results),
        "rules": [
            {
                "rule_id": rule["rule_id"],
                "title": rule["title"],
                "guidance": rule["guidance"],
                "category": rule.get("category", "general"),
                "priority": rule.get("priority", "medium"),
                "search_score": rule.get("search_score", 0),
                "contexts": rule.get("contexts", [])
            }
            for rule in results
        ]
    }

@mcp.tool
def list_rule_categories() -> dict:
    """
    📋 List all available rule categories
    
    Returns all rule categories available in ArchGuard's rule engine,
    helping you understand what types of guidance are available.
    """
    all_rules = rule_engine.list_all_rules()
    categories = {}
    
    for rule in all_rules:
        category = rule.get("category", "general")
        if category not in categories:
            categories[category] = {
                "name": category,
                "count": 0,
                "rules": []
            }
        
        categories[category]["count"] += 1
        categories[category]["rules"].append({
            "rule_id": rule["rule_id"],
            "title": rule["title"],
            "priority": rule.get("priority", "medium")
        })
    
    return {
        "total_categories": len(categories),
        "categories": categories
    }

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
    return """
🛡️ ArchGuard Architectural Governance Rules v1.0

📏 CODE ORGANIZATION & STRUCTURE
1. File Size: Keep files under 300 lines for maintainability
2. Function Length: Limit functions to 50 lines or less
3. Class Responsibility: Follow Single Responsibility Principle
4. Module Coupling: Minimize dependencies between modules
5. Naming: Use descriptive, intention-revealing names

🔒 SECURITY STANDARDS
6. Authentication: Use established libraries (OAuth2, Passport, etc.)
7. Password Storage: Never store passwords in plain text - use bcrypt/Argon2
8. Secret Management: Store secrets in environment variables, never in code
9. Input Validation: Sanitize and validate all user inputs
10. HTTPS: Use HTTPS for all authentication and sensitive data
11. Rate Limiting: Implement rate limiting to prevent abuse

🌐 API DESIGN PRINCIPLES
12. RESTful Design: Follow REST conventions for HTTP methods
13. Status Codes: Use appropriate HTTP status codes
14. Documentation: Document all API endpoints with OpenAPI/Swagger
15. Versioning: Plan for API versioning (v1, v2, etc.)
16. Error Handling: Implement consistent error response format

🗄️ DATABASE BEST PRACTICES
17. Soft Deletes: Use deleted_at timestamps instead of hard deletes
18. Indexing: Add indexes for frequently queried fields
19. Relationships: Design proper foreign key constraints
20. Migrations: Version control database schema changes
21. Security: Implement proper database user permissions

⚡ PERFORMANCE & SCALABILITY
22. Caching: Implement appropriate caching strategies
23. Async Processing: Use async operations for heavy tasks
24. Query Optimization: Optimize database queries and use connection pooling
25. Monitoring: Add performance monitoring and logging
26. Load Planning: Design for horizontal scaling

🧪 TESTING & QUALITY
27. Test Coverage: Write tests for critical functionality
28. Test Types: Include unit, integration, and end-to-end tests
29. Code Review: Require peer review before merging
30. Static Analysis: Use linting and static analysis tools

📝 DOCUMENTATION & MAINTAINABILITY
31. Code Comments: Document complex logic and business rules
32. README: Maintain up-to-date project documentation
33. Architecture Docs: Document high-level system architecture
34. Dependencies: Keep dependencies up to date and minimal

🏗️ ARCHITECTURAL PATTERNS
35. Design Patterns: Use appropriate design patterns (Strategy, Factory, etc.)
36. Separation of Concerns: Separate business logic from presentation
37. Dependency Injection: Use DI for loose coupling
38. Configuration: Externalize configuration from code
39. Error Boundaries: Implement proper error handling and recovery
40. Monitoring: Add health checks and observability

These rules are advisory and should be adapted to your specific project needs.
ArchGuard provides guidance based on these principles but never blocks development.
"""

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
    return f"""🛡️ ARCHGUARD ARCHITECTURAL CODE REVIEW

Please perform a comprehensive architectural review of this code:

```
{code}
```

📋 REVIEW CHECKLIST - Please analyze each area:

🏗️ ARCHITECTURAL DESIGN
- Does this code follow Single Responsibility Principle?
- Are there appropriate design patterns being used?
- Is the separation of concerns properly maintained?
- How does this fit into the overall system architecture?

🔒 SECURITY ANALYSIS
- Are there any potential security vulnerabilities?
- Is input validation and sanitization properly implemented?
- Are secrets or sensitive data properly handled?
- Does authentication/authorization follow best practices?

⚡ PERFORMANCE CONSIDERATIONS
- Are there any performance bottlenecks or anti-patterns?
- Is caching being used appropriately?
- Are database queries optimized?
- Is the code scalable for increased load?

📏 CODE ORGANIZATION & QUALITY
- Is the code readable and well-structured?
- Are functions/methods appropriately sized?
- Are variable and function names descriptive?
- Is there proper error handling?

🧪 TESTING & MAINTAINABILITY
- Is this code testable as written?
- Are there areas that need better test coverage?
- Is the code documented sufficiently?
- How easy would this be to modify or extend?

🔧 REFACTORING OPPORTUNITIES
- What specific improvements would you recommend?
- Are there code smells that should be addressed?
- Could this be simplified or made more maintainable?
- What architectural patterns might be beneficial?

Please provide specific, actionable recommendations for each area where improvements are possible.
Focus on architectural guidance rather than just syntax issues.
"""

@mcp.tool
def detect_issues(code: str, file_path: str = "unknown.py", language: str = None, 
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
    if project_context is None:
        project_context = {}
    
    # Add global context
    project_context.update({
        "server_context": _server_context,
        "project": _server_project,
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

@mcp.tool
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

@mcp.tool
def batch_analyze_issues(code: str, file_path: str = "unknown.py", 
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
    if project_context is None:
        project_context = {}
    
    # Add global context
    project_context.update({
        "server_context": _server_context,
        "project": _server_project
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

@mcp.tool
def get_detection_info() -> dict:
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

@mcp.tool
def get_archguard_help() -> dict:
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
    return {
        "guide": """
🛡️ ARCHGUARD USAGE GUIDE FOR CODING AGENTS

🎯 WHAT ARCHGUARD IS BEST FOR:
ArchGuard is your architectural co-pilot that provides dual-mode assistance:

📋 GUIDANCE MODE (get_guidance):
- Designing secure, scalable systems and APIs
- Following architectural best practices and design patterns
- Code organization and maintainability improvements
- Performance optimization and scalability planning
- Database design and data modeling decisions

🔍 DETECTION MODE (detect_issues):
- Finding specific security vulnerabilities (hardcoded secrets, SQL injection)
- Detecting maintainability issues (large files/functions, code duplication)
- Identifying code quality problems (missing error handling, complexity)
- Providing actionable fix recommendations with confidence scores
- Generating reports for different audiences (IDE, security audit, etc.)

⚡ HOW TO GET THE BEST GUIDANCE:

1. BE SPECIFIC with your requests:
   ✅ "Get guidance for implementing JWT authentication with refresh tokens"
   ✅ "Review this 150-line React component for architectural improvements"
   ❌ "Help me with code" (too vague)

2. PROVIDE CONTEXT when possible:
   - Include relevant code snippets
   - Mention your tech stack or constraints
   - Specify if it's for a startup MVP or enterprise system

3. ASK ABOUT ARCHITECTURE, not just syntax:
   ✅ "What architectural patterns should I use for this microservice?"
   ✅ "How should I structure this database schema for scalability?"
   ❌ "Fix this syntax error" (use a linter instead)

🔧 COMMON USAGE PATTERNS:

📋 Before Writing Code:
- "Get guidance for creating a user management system"
- "Suggest architecture for real-time chat application"
- "Design database schema for e-commerce orders"

🔍 During Code Review:
- "Review this authentication middleware for security issues"
- "Analyze this API design for REST best practices"  
- "Check this component for performance bottlenecks"

🏗️ When Refactoring:
- "Suggest improvements for this 300-line service class"
- "How can I better organize this monolithic module?"
- "What design patterns would help clean up this code?"

📚 AVAILABLE RESOURCES:

🛠️ Tools:
- get_guidance() - Primary architectural guidance tool
- detect_issues() - Specific code issue detection and analysis
- analyze_code_context() - Code structure and context analysis
- batch_analyze_issues() - Comprehensive analysis with LLM enhancement
- get_detection_info() - Information about detection capabilities
- get_archguard_help() - This help guide
- review_code() - Structured code review prompts

📋 Resources:
- archguard://rules - Complete architectural governance rules

🎨 Prompts:
- review_code() - Comprehensive architectural review template

💡 PRO TIPS:

1. Don't just ask "Is this good?" - ask "How can this be more secure/scalable/maintainable?"

2. Include business context: "for a startup" vs "for enterprise" gets different advice

3. Ask about patterns: "What design patterns would improve this?"

4. Think architectural layers: "How should I separate concerns in this module?"

5. Consider future scaling: "Will this approach scale to 10x users?"

6. Security first: Always ask about security implications for auth/data handling

🚀 EXAMPLE INTERACTIONS:

INPUT: "Get guidance for implementing user authentication"
RESULT: Detailed security recommendations, pattern suggestions, implementation tips

INPUT: "Review this database model for performance"  
RESULT: Indexing suggestions, query optimization, scaling considerations

INPUT: "How should I structure a microservices API gateway?"
RESULT: Architectural patterns, security considerations, scaling strategies

Remember: ArchGuard is advisory, not blocking. Use the guidance to make informed
architectural decisions while maintaining full control over your development process.
""",
        "quick_reference": {
            "primary_tool": "get_guidance(action, code, context)",
            "resources": ["archguard://rules"],
            "prompts": ["review_code(code)"],
            "best_for": ["architecture", "security", "performance", "scalability"],
            "not_for": ["syntax errors", "debugging runtime issues", "package management"]
        }
    }

# Global variables to store server context and project
_server_context = "desktop-app"
_server_project = None

def main(context: str = "desktop-app", project: str = None):
    """Main entry point for the MCP server"""
    import sys
    global _server_context, _server_project
    
    print(f"🛡️ Starting ArchGuard MCP Server...", file=sys.stderr)
    print(f"🎯 Context: {context}", file=sys.stderr)
    if project:
        print(f"📁 Project: {project}", file=sys.stderr)
    
    # Store context and project globally
    _server_context = context
    _server_project = project
    
    mcp.run()  # Default: stdio transport

def _get_guidance_impl(action: str, code: str = "", context: str = "") -> dict:
    """Internal implementation of get_guidance for testing"""
    guidance = []
    patterns = []
    complexity_score = "low"
    
    # Analyze action intent and provide comprehensive guidance
    action_lower = action.lower()
    
    # 🏗️ Component/File Creation Guidance
    if any(word in action_lower for word in ["create", "build", "implement", "develop"]):
        if any(word in action_lower for word in ["component", "file", "class", "module"]):
            guidance.extend([
                "📏 Keep files under 300 lines for maintainability",
                "🎯 Follow Single Responsibility Principle - one purpose per file",
                "📁 Use descriptive file names that reflect their purpose",
                "🔄 Consider if this could be split into smaller, focused modules"
            ])
            complexity_score = "medium"
    
    # Add context-specific guidance
    if context:
        if any(word in context.lower() for word in ['microservice', 'distributed']):
            guidance.append("🌐 Design for service independence and fault tolerance")
            patterns.append("Microservices Pattern")
        if any(word in context.lower() for word in ['startup', 'mvp']):
            guidance.append("🚀 Focus on core functionality first, optimize later")
        if any(word in context.lower() for word in ['enterprise', 'large-scale']):
            guidance.append("🏢 Consider governance, compliance, and audit requirements")
    
    # Add server context-specific guidance
    global _server_context, _server_project
    if _server_context == 'ide-assistant':
        guidance.append("💡 IDE Integration: Consider adding IntelliSense-friendly type hints")
        guidance.append("🔧 IDE Integration: Structure code for better refactoring support")
    elif _server_context == 'agent':
        guidance.append("🤖 Agent Mode: Focus on automated code generation patterns")
        guidance.append("🔄 Agent Mode: Design for programmatic modification")
    
    # Add project-specific guidance if project directory is available
    if _server_project:
        guidance.append(f"📁 Project Context: Working in {_server_project}")
    
    # Provide default guidance if no specific patterns detected
    if not guidance:
        guidance.extend([
            "✅ No specific architectural concerns detected",
            "🏗️ Follow established coding standards and best practices",
            "🧪 Consider adding tests for new functionality",
            "📝 Document complex logic and API interfaces"
        ])
    
    return {
        "guidance": guidance,
        "status": "advisory",
        "action": action,
        "complexity_score": complexity_score,
        "patterns": patterns if patterns else ["General Best Practices"],
        "code_analysis": {
            "lines_analyzed": len(code.split('\n')) if code else 0,
            "context_provided": bool(context)
        }
    }

def test_guidance_with_context(action: str, code: str = "", context: str = "", server_context: str = None) -> dict:
    """Test version of get_guidance that allows setting server context"""
    global _server_context, _server_project
    
    # Temporarily set server context if provided
    original_context = _server_context
    if server_context:
        _server_context = server_context
    
    try:
        # Call the guidance function implementation directly
        result = _get_guidance_impl(action, code, context)
        return result
    finally:
        # Restore original context
        _server_context = original_context

if __name__ == "__main__":
    main()