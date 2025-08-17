"""
ArchGuard HTTP Server - Production deployment version
"""

from archguard_server import mcp

if __name__ == "__main__":
    print("🛡️ Starting ArchGuard MCP Server (HTTP mode)...")
    print("🌐 Server will be available at: http://localhost:8003/mcp")
    print("📋 Use this for production deployments and Docker containers")
    
    # Run with HTTP transport for production
    mcp.run(transport="http", host="0.0.0.0", port=8003, path="/mcp")