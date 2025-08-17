"""
ArchGuard HTTP Server - Production deployment version
"""

# Use absolute imports to avoid issues with direct module execution
try:
    from archguard.server import mcp
    from archguard.config import ArchGuardConfig
except ImportError:
    # Fallback for development/direct execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from archguard.server import mcp
    from archguard.config import ArchGuardConfig

# Create FastAPI app for uvicorn compatibility  
try:
    app = mcp.create_app()
except AttributeError:
    import warnings
    warnings.warn("MCP server does not support create_app method. HTTP mode may not work correctly.")
    app = None

def main(host: str = None, port: int = None):
    """Main entry point for the HTTP server"""
    # Use centralized config if not provided
    if host is None:
        host = ArchGuardConfig.get_http_host()
    if port is None:
        port = ArchGuardConfig.get_http_port()
    
    path = ArchGuardConfig.get_http_path()
    
    print("🛡️ Starting ArchGuard MCP Server (HTTP mode)...")
    print(f"🌐 Server will be available at: http://localhost:{port}{path}")
    print("📋 Use this for production deployments and Docker containers")
    
    # Run with HTTP transport for production
    mcp.run(transport="http", host=host, port=port, path=path)

if __name__ == "__main__":
    main()