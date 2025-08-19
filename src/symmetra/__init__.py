"""Symmetra MCP Server - Architectural decision tracking and governance."""

__version__ = "0.1.0"
__author__ = "Claude"
__email__ = "noreply@anthropic.com"

# Import functions only when needed to avoid circular imports
def _get_server_main():
    from .server import main
    return main

def _get_http_server_main():
    from .http_server import main
    return main

# Make functions available as module attributes
server_main = _get_server_main
http_server_main = _get_http_server_main

__all__ = ["server_main", "http_server_main"]