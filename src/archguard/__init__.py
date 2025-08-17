"""ArchGuard MCP Server - Architectural decision tracking and governance."""

__version__ = "0.1.0"
__author__ = "Claude"
__email__ = "noreply@anthropic.com"

from .server import main as server_main
from .http_server import main as http_server_main

__all__ = ["server_main", "http_server_main"]