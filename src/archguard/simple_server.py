"""
Simplified ArchGuard MCP Server - AI-First Architecture

This is a much simpler implementation focused on providing excellent
architectural guidance to Claude Code through AI analysis rather than
complex deterministic rule systems.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from .ai_guidance import guidance_engine, secret_detector


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("ArchGuard")


@mcp.tool()
def get_guidance(action: str, code: str = "", context: str = "", project_id: str = None) -> Dict[str, Any]:
    """
    🎯 Get comprehensive architectural guidance for coding actions
    
    This is ArchGuard's primary tool for providing real-time architectural guidance.
    Use this tool whenever you're about to:
    - Create new files, functions, or components
    - Design APIs, databases, or system architecture  
    - Implement authentication, security, or data handling
    - Refactor existing code or restructure projects
    - Make any significant coding decisions
    
    The tool analyzes your intended action and existing code to provide:
    - 🔒 Security best practices and vulnerability prevention
    - 📚 Architectural patterns and design recommendations  
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
    try:
        logger.info(f"Providing guidance for action: {action}")
        response = guidance_engine.get_guidance(action, code, context, project_id)
        return response.to_dict()
        
    except Exception as e:
        logger.error(f"Error in get_guidance: {e}")
        return {
            "guidance": ["Unable to provide guidance at this time"],
            "status": "advisory",
            "action": action,
            "complexity_score": "unknown",
            "patterns": []
        }


@mcp.tool()
def scan_secrets(code: str) -> Dict[str, Any]:
    """
    🔍 Scan code for potential hardcoded secrets and credentials
    
    This tool performs a focused scan for common security issues like:
    - Hardcoded API keys
    - Database passwords in code
    - Authentication tokens
    - GitHub tokens
    - Other sensitive credentials
    
    Args:
        code: The code to scan for potential secrets
        
    Returns:
        Dictionary containing:
        - secrets: List of potential security issues found
        - count: Number of issues detected
        - status: "clean" or "issues_found"
    """
    try:
        logger.info("Scanning code for potential secrets")
        secrets = secret_detector.scan_secrets(code)
        
        return {
            "secrets": secrets,
            "count": len(secrets),
            "status": "clean" if len(secrets) == 0 else "issues_found"
        }
        
    except Exception as e:
        logger.error(f"Error in scan_secrets: {e}")
        return {
            "secrets": [],
            "count": 0,
            "status": "error"
        }


@mcp.tool()
def search_rules(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    🔍 Search ArchGuard rules by query text
    
    This tool allows you to search through ArchGuard's knowledge base to find
    specific guidance on architectural patterns, best practices, and design decisions.
    
    Args:
        query: Search query text (searches architectural patterns and best practices)
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary with matching rules and their relevance
    """
    try:
        logger.info(f"Searching rules for: {query}")
        
        # Simple knowledge base - could be expanded with real search
        knowledge_base = {
            "authentication": [
                "Use OAuth 2.0 or JWT for modern authentication",
                "Implement proper password hashing with bcrypt or Argon2",
                "Add rate limiting to prevent brute force attacks",
                "Consider multi-factor authentication for sensitive data"
            ],
            "database": [
                "Use connection pooling for better performance",
                "Implement proper indexing strategy",
                "Use parameterized queries to prevent SQL injection",
                "Plan for database migrations and schema versioning"
            ],
            "api": [
                "Follow RESTful conventions or GraphQL best practices",
                "Implement proper error handling and status codes",
                "Use API versioning strategy",
                "Add request/response validation"
            ],
            "security": [
                "Follow OWASP Top 10 security guidelines",
                "Implement input validation and sanitization",
                "Use HTTPS everywhere and secure headers",
                "Apply principle of least privilege"
            ],
            "performance": [
                "Profile before optimizing - measure bottlenecks",
                "Implement caching at appropriate layers",
                "Use database query optimization",
                "Consider asynchronous processing for heavy operations"
            ]
        }
        
        query_lower = query.lower()
        results = []
        
        for category, rules in knowledge_base.items():
            if category in query_lower or any(word in query_lower for word in category.split()):
                for rule in rules[:max_results]:
                    results.append({
                        "category": category,
                        "rule": rule,
                        "relevance": 0.9  # Simple relevance score
                    })
        
        return {
            "results": results[:max_results],
            "query": query,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in search_rules: {e}")
        return {
            "results": [],
            "query": query,
            "total_found": 0
        }


@mcp.tool()
def list_rule_categories() -> Dict[str, Any]:
    """
    📚 List all available rule categories
    
    Returns all rule categories available in ArchGuard's knowledge base,
    helping you understand what types of guidance are available.
    """
    categories = [
        "authentication",
        "database", 
        "api",
        "security",
        "performance",
        "architecture",
        "design_patterns"
    ]
    
    return {
        "categories": categories,
        "count": len(categories)
    }


@mcp.tool()
def get_archguard_help() -> Dict[str, Any]:
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
    help_content = {
        "overview": "ArchGuard provides AI-powered architectural guidance for software development",
        
        "primary_tool": {
            "name": "get_guidance",
            "description": "Main tool for architectural analysis and recommendations",
            "when_to_use": [
                "Before implementing new features",
                "When designing system architecture", 
                "For code review and refactoring",
                "When choosing design patterns",
                "For security and performance guidance"
            ]
        },
        
        "best_practices": [
            "Be specific about what you're trying to accomplish",
            "Provide relevant code context when asking for guidance",
            "Include information about your project type and constraints",
            "Ask for guidance early in the development process",
            "Use ArchGuard for both new development and refactoring"
        ],
        
        "example_requests": [
            "Get guidance for implementing user authentication with JWT",
            "Review this API endpoint for security and performance",
            "Suggest database schema design for e-commerce orders",
            "Help me refactor this large class into smaller components",
            "What's the best caching strategy for this use case?"
        ],
        
        "tools_overview": {
            "get_guidance": "AI-powered architectural analysis and recommendations",
            "scan_secrets": "Security scanning for hardcoded credentials",
            "search_rules": "Search architectural knowledge base",
            "list_rule_categories": "View available guidance categories"
        }
    }
    
    return help_content


# Resources for Claude Code integration
@mcp.resource("archguard://rules")
def get_rules_resource() -> str:
    """Architectural rules and guidelines resource"""
    return """
# ArchGuard Architectural Rules and Guidelines

## Security Best Practices
- Use established authentication libraries (OAuth, JWT)
- Implement proper password hashing (bcrypt, Argon2)
- Add rate limiting to prevent abuse
- Never commit secrets to version control
- Use HTTPS everywhere

## Database Design
- Use connection pooling for performance
- Implement proper indexing strategy
- Use parameterized queries (prevent SQL injection)
- Plan for schema migrations
- Consider read replicas for scale

## API Design
- Follow RESTful conventions
- Implement proper error handling
- Use API versioning
- Add request/response validation
- Consider rate limiting

## Performance
- Profile before optimizing
- Implement appropriate caching
- Use database query optimization
- Consider async processing
- Implement pagination for large datasets

## Architecture
- Follow SOLID principles
- Separate concerns into focused modules
- Use dependency injection
- Consider microservices vs monolith trade-offs
- Document architectural decisions
"""


@mcp.resource("archguard://patterns")
def get_patterns_resource() -> str:
    """Design pattern recommendations resource"""
    return """
# ArchGuard Design Pattern Recommendations

## Authentication Patterns
- JWT Token Pattern: Stateless authentication
- OAuth 2.0: Delegated authorization
- Session Management: Traditional server-side sessions

## Data Access Patterns
- Repository Pattern: Abstract data access
- Unit of Work: Manage transactions
- Active Record: Object-relational mapping

## API Patterns
- REST API: Resource-based web services
- GraphQL: Query-based API
- DTO Pattern: Data transfer objects

## Caching Patterns
- Cache-Aside: Application manages cache
- Write-Through: Cache updated on write
- Cache Abstraction: Hide caching complexity

## Architectural Patterns
- Microservices: Distributed system architecture
- CQRS: Command Query Responsibility Segregation
- Event Sourcing: Event-based state management
"""


@mcp.resource("archguard://checklist")
def get_checklist_resource() -> str:
    """Code review checklist resource"""
    return """
# ArchGuard Code Review Checklist

## Security Review
- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented
- [ ] SQL injection prevention (parameterized queries)
- [ ] Authentication and authorization in place
- [ ] Error handling doesn't leak sensitive info

## Architecture Review
- [ ] Code follows SOLID principles
- [ ] Appropriate separation of concerns
- [ ] Dependencies are properly injected
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate and secure

## Performance Review
- [ ] Database queries are optimized
- [ ] Appropriate caching strategy
- [ ] No obvious performance bottlenecks
- [ ] Pagination for large datasets
- [ ] Async processing where appropriate

## Maintainability Review
- [ ] Code is readable and well-documented
- [ ] Functions are focused and not too large
- [ ] Test coverage is adequate
- [ ] Configuration is externalized
- [ ] Dependencies are up to date
"""


def run_server():
    """Run the simplified ArchGuard MCP server"""
    logger.info("Starting ArchGuard Simple MCP Server")
    mcp.run()


if __name__ == "__main__":
    run_server()