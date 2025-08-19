"""
Help and Documentation Tools

This module contains tools for providing help, documentation, and guidance
on how to effectively use Symmetra's capabilities.
"""

def get_symmetra_help() -> dict:
    """
    📚 Get comprehensive help on using Symmetra effectively
    
    This tool provides coding agents with detailed instructions on how to best
    utilize Symmetra's capabilities. Use this tool when you want to understand:
    - How to phrase requests to get the most helpful guidance
    - What types of architectural questions Symmetra can answer
    - Best practices for integrating Symmetra into your development workflow
    - Examples of effective Symmetra interactions
    
    Returns:
        Complete guide on Symmetra usage, capabilities, and best practices
    """
    return {
        "guide": """
🛡️ SYMMETRA USAGE GUIDE FOR CODING AGENTS

🎯 WHAT SYMMETRA IS BEST FOR:
Symmetra is your architectural co-pilot that provides dual-mode assistance:

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
- get_symmetra_help() - This help guide
- review_code() - Structured code review prompts

📋 Resources:
- symmetra://rules - Complete architectural governance rules

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

Remember: Symmetra is advisory, not blocking. Use the guidance to make informed
architectural decisions while maintaining full control over your development process.
""",
        "quick_reference": {
            "primary_tools": {
                "guidance": "get_guidance(action, code, context)",
                "detection": "detect_issues(code, file_path, language, report_type)",
                "context_analysis": "analyze_code_context(code, line_number, language)",
                "batch_analysis": "batch_analyze_issues(code, file_path, enable_llm_analysis)"
            },
            "resources": ["symmetra://rules"],
            "prompts": ["review_code(code)"],
            "best_for": ["architecture", "security", "performance", "scalability"],
            "not_for": ["syntax errors", "debugging runtime issues", "package management"]
        }
    }

def get_rules_resource() -> str:
    """
    📋 Access Symmetra's comprehensive architectural governance rules
    
    This resource provides the complete set of architectural standards and 
    best practices that Symmetra uses to evaluate code and provide guidance.
    Use this when you need to understand Symmetra's recommendations or 
    when establishing coding standards for a project.
    
    Contains rules for: security, performance, maintainability, scalability,
    documentation, testing, and general architectural principles.
    """
    return """
🛡️ Symmetra Architectural Governance Rules v1.0

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
Symmetra provides guidance based on these principles but never blocks development.
"""

def get_review_code_prompt(code: str) -> str:
    """
    🔍 Generate comprehensive architectural code review prompt
    
    This prompt template guides thorough code review with focus on architectural
    principles, security, performance, and maintainability. Use this when you
    want to perform a detailed review of code against Symmetra's standards.
    
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
    return f"""🛡️ SYMMETRA ARCHITECTURAL CODE REVIEW

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