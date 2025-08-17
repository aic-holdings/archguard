"""
Pytest configuration and fixtures for ArchGuard tests.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from typing import Generator, AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_architecture_file(temp_dir: Path) -> Path:
    """Create a sample architecture file for testing."""
    arch_file = temp_dir / "architecture.md"
    arch_file.write_text("""# Sample Architecture

## Components
- Component A: Handles user authentication
- Component B: Manages data persistence

## Decisions
- Decision 1: Use PostgreSQL for primary database
- Decision 2: Implement microservices architecture
""")
    return arch_file


@pytest.fixture
def sample_project_structure(temp_dir: Path) -> Path:
    """Create a sample project structure for testing."""
    # Create basic project structure
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.py").write_text("# Main application file")
    
    (temp_dir / "docs").mkdir()
    (temp_dir / "docs" / "README.md").write_text("# Project Documentation")
    
    (temp_dir / "config").mkdir()
    (temp_dir / "config" / "settings.json").write_text('{"env": "test"}')
    
    return temp_dir


@pytest.fixture
async def mcp_server():
    """Start an MCP server instance for testing."""
    from archguard.server import mcp
    
    # Return the MCP server instance directly
    yield mcp
    
    # Cleanup server if needed


@pytest.fixture
def client():
    """Create a test client for HTTP server testing."""
    from fastapi.testclient import TestClient
    from archguard.http_server import app
    
    if app is not None:
        return TestClient(app)
    else:
        # Fallback: create app manually if needed
        from archguard.server import mcp
        if hasattr(mcp, 'create_app'):
            return TestClient(mcp.create_app())
        else:
            pytest.skip("HTTP app not available")


# Environment fixtures
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Store original values
    original_env = {}
    test_vars = {
        "ARCHGUARD_TEST_MODE": "true",
        "ARCHGUARD_LOG_LEVEL": "DEBUG",
    }
    
    for key, value in test_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


# Markers for different test categories
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )