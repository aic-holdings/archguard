"""
ArchGuard v0 - AI Governance MCP Server
Provides real-time coding guidance for AI agents.
"""

from fastmcp import FastMCP

# Create the ArchGuard MCP server
mcp = FastMCP("ArchGuard")

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
    
    # 🔒 Security & Authentication Guidance  
    if any(keyword in action_lower for keyword in ["auth", "password", "login", "security", "token", "jwt", "session"]):
        guidance.extend([
            "🔒 Use established authentication libraries (OAuth2, Passport, etc.)",
            "🔐 Never store passwords in plain text - use bcrypt, Argon2, or similar",
            "🎫 Implement proper session management with secure tokens",
            "🛡️ Add rate limiting to prevent brute force attacks",
            "🌐 Use HTTPS only for authentication endpoints",
            "🔑 Store secrets in environment variables, never in code",
            "⏰ Implement proper token expiration and refresh mechanisms"
        ])
        patterns.extend(["Authentication Pattern", "Security Layer Pattern"])
        complexity_score = "high"
    
    # 🌐 API Design Guidance
    if any(keyword in action_lower for keyword in ["api", "endpoint", "route", "rest", "graphql"]):
        guidance.extend([
            "🌐 Follow RESTful conventions: GET (read), POST (create), PUT (update), DELETE (remove)",
            "📝 Document API endpoints with OpenAPI/Swagger specifications",
            "✅ Implement consistent error handling and status codes",
            "🔍 Add input validation and sanitization",
            "📊 Include proper HTTP status codes (200, 201, 400, 401, 404, 500)",
            "🚀 Consider API versioning strategy (v1, v2) for future changes",
            "⚡ Implement caching headers for performance"
        ])
        patterns.extend(["API Gateway Pattern", "RESTful Service Pattern"])
        complexity_score = "medium"
    
    # 🗄️ Database Design Guidance
    if any(keyword in action_lower for keyword in ["database", "db", "sql", "schema", "table", "collection"]):
        guidance.extend([
            "🗄️ Use soft deletes (deleted_at timestamp) instead of hard deletes",
            "🔍 Add database indexes for frequently queried fields",
            "🔗 Design proper foreign key relationships and constraints",
            "📊 Normalize data to reduce redundancy, but consider denormalization for performance",
            "🔒 Implement database-level security with proper user permissions",
            "⚡ Plan for database migrations and version control",
            "💾 Consider backup and disaster recovery strategies"
        ])
        patterns.extend(["Repository Pattern", "Data Access Layer Pattern"])
        complexity_score = "medium"
    
    # 🧩 Refactoring & Code Quality Guidance
    if any(keyword in action_lower for keyword in ["refactor", "improve", "clean", "optimize"]):
        guidance.extend([
            "🧩 Extract common logic into reusable functions/modules",
            "📋 Add comprehensive tests before refactoring",
            "🏷️ Use meaningful variable and function names",
            "📝 Add clear documentation and comments for complex logic",
            "🔄 Consider design patterns: Strategy, Factory, Observer, etc.",
            "⚡ Profile performance before and after changes"
        ])
        patterns.extend(["Strategy Pattern", "Factory Pattern"])
        complexity_score = "medium"
    
    # 🎯 Frontend/UI Guidance
    if any(keyword in action_lower for keyword in ["frontend", "ui", "component", "react", "vue", "angular"]):
        guidance.extend([
            "🎨 Keep components focused and reusable",
            "📱 Design for mobile responsiveness from the start",
            "♿ Implement accessibility features (ARIA labels, keyboard navigation)",
            "⚡ Optimize bundle size and loading performance",
            "🎭 Separate presentation logic from business logic",
            "🧪 Write component tests for critical user interactions"
        ])
        patterns.extend(["Component Pattern", "Container/Presenter Pattern"])
    
    # 🚀 Performance & Scalability Guidance
    if any(keyword in action_lower for keyword in ["performance", "scale", "optimize", "cache", "load"]):
        guidance.extend([
            "⚡ Implement caching strategies (Redis, Memcached) for frequent data",
            "🔄 Use asynchronous processing for heavy operations",
            "📊 Add monitoring and logging for performance metrics",
            "🚀 Consider horizontal scaling with load balancers",
            "💾 Optimize database queries and use connection pooling",
            "📦 Implement lazy loading for large datasets"
        ])
        patterns.extend(["Caching Pattern", "Circuit Breaker Pattern"])
        complexity_score = "high"
    
    # Analyze provided code for additional insights
    if code:
        code_lines = len(code.split('\n'))
        if code_lines > 50:
            guidance.append(f"📏 Code length ({code_lines} lines) suggests considering decomposition")
            complexity_score = "high" if code_lines > 200 else "medium"
        
        # Check for potential code smells
        if code.count('if') > 10:
            guidance.append("🧩 High cyclomatic complexity detected - consider extracting methods")
        if 'TODO' in code or 'FIXME' in code:
            guidance.append("📝 Address TODO/FIXME comments before finalizing")
        if any(word in code.lower() for word in ['password', 'secret', 'key']) and any(word in code for word in ['"', "'"]):
            guidance.append("🚨 Potential hardcoded secrets detected - use environment variables")
    
    # Provide default guidance if no specific patterns detected
    if not guidance:
        guidance.extend([
            "✅ No specific architectural concerns detected",
            "🏗️ Follow established coding standards and best practices",
            "🧪 Consider adding tests for new functionality",
            "📝 Document complex logic and API interfaces"
        ])
    
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
        # TODO: Add project-specific configuration loading from .archguard.toml
    
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
ArchGuard is your architectural co-pilot that provides real-time guidance on:
- Designing secure, scalable systems and APIs
- Following architectural best practices and design patterns
- Code organization and maintainability improvements
- Security vulnerabilities and hardening recommendations
- Performance optimization and scalability planning
- Database design and data modeling decisions

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