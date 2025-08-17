"""
ArchGuard v0 - AI Governance MCP Server
Provides real-time coding guidance for AI agents.
"""

from fastmcp import FastMCP

# Create the ArchGuard MCP server
mcp = FastMCP("ArchGuard")

@mcp.tool
def get_guidance(action: str, code: str = "") -> dict:
    """Get coding guidance for a proposed action"""
    guidance = []
    
    # File size guidance
    if "file" in action.lower() and "create" in action.lower():
        guidance.append("💡 Keep files under 300 lines for maintainability")
    
    # Security guidance
    if any(keyword in action.lower() for keyword in ["auth", "password", "login", "security"]):
        guidance.append("🔒 Use secure authentication patterns")
        guidance.append("🔐 Never store passwords in plain text")
    
    # Code length guidance
    if len(code) > 1000:
        guidance.append("📏 Consider breaking large code blocks into smaller functions")
    
    # API guidance
    if "api" in action.lower():
        guidance.append("🌐 Follow API-first design principles")
        guidance.append("📝 Document your API endpoints")
    
    # Database guidance
    if any(keyword in action.lower() for keyword in ["database", "db", "sql"]):
        guidance.append("🗄️ Use soft deletes instead of hard deletes")
        guidance.append("🔍 Add proper indexing for query performance")
    
    # Default guidance
    if not guidance:
        guidance.append("✅ No specific guidance - proceed with best practices")
    
    return {
        "guidance": guidance,
        "status": "advisory",
        "action": action,
        "code_length": len(code) if code else 0
    }

@mcp.resource("archguard://rules")
def get_rules() -> str:
    """Get the current governance rules"""
    return """
ArchGuard Governance Rules v0:

1. File Size: Keep files under 300 lines
2. Security: Use secure auth patterns, no plain text passwords
3. Code Structure: Break large code blocks into smaller functions
4. API Design: Follow API-first principles with documentation
5. Database: Use soft deletes, proper indexing
6. General: Follow established best practices
"""

@mcp.prompt
def review_code(code: str) -> str:
    """Generate a prompt for code review"""
    return f"""Please review this code for potential improvements:

{code}

Consider:
- Code structure and readability
- Security implications
- Performance considerations
- Best practices adherence
"""

def main():
    """Main entry point for the MCP server"""
    print("🛡️ Starting ArchGuard MCP Server...")
    mcp.run()  # Default: stdio transport

if __name__ == "__main__":
    main()