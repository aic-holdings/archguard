"""
Guidance Tools - Traditional architectural guidance and advice

This module contains the original ArchGuard tools focused on providing
general architectural guidance, best practices, and design recommendations.
"""

from typing import Dict, Any
from ..rules_engine import create_rule_engine

# Initialize rule engine (use vector search for comprehensive guides)
rule_engine = create_rule_engine("vector")

def get_guidance(action: str, code: str = "", context: str = "", 
                server_context: str = None, server_project: str = None) -> dict:
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
        server_context: Server context (ide-assistant, agent, desktop-app)
        server_project: Project directory path
        
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
    # Build project context for rule engine
    project_context = {
        "server_context": server_context,
        "project": server_project
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
    if server_context == 'ide-assistant':
        guidance.append("💡 IDE Integration: Consider adding IntelliSense-friendly type hints")
        guidance.append("🔧 IDE Integration: Structure code for better refactoring support")
    elif server_context == 'agent':
        guidance.append("🤖 Agent Mode: Focus on automated code generation patterns")
        guidance.append("🔄 Agent Mode: Design for programmatic modification")
    
    # Add project-specific guidance if project directory is available
    if server_project:
        guidance.append(f"📁 Project Context: Working in {server_project}")
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