# Contributing to Symmetra

We love your input! We want to make contributing to Symmetra as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

### Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Setting up your development environment

```bash
# Clone the repository
git clone https://github.com/aic-holdings/symmetra
cd symmetra

# Install development dependencies
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Running tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=symmetra

# Run specific test file
pytest test/test_server.py

# Run tests in parallel
pytest -n auto
```

### Code quality checks

We use several tools to maintain code quality:

```bash
# Format code with black
black src/ test/

# Sort imports with isort
isort src/ test/

# Lint with flake8
flake8 src/ test/

# Type checking with mypy
mypy src/

# Run all checks at once
uv run pre-commit run --all-files
```

### Running the development server

```bash
# Start the MCP server
uv run symmetra server

# Start the HTTP server
uv run symmetra http --port 8080

# Run with debug logging
ARCHGUARD_LOG_LEVEL=DEBUG uv run symmetra server
```

## Testing

### Test Structure

- `test/` - All test files
- `test/conftest.py` - Shared pytest fixtures
- `test/test_*.py` - Test modules matching the source structure

### Writing Tests

We use pytest for testing. Here's a simple test example:

```python
import pytest
from symmetra.server import get_guidance

def test_get_guidance_basic():
    """Test basic guidance functionality."""
    result = get_guidance("create user authentication", "")
    
    assert "guidance" in result
    assert isinstance(result["guidance"], list)
    assert len(result["guidance"]) > 0
    assert result["status"] == "advisory"
```

### Async Tests

For async functions, use pytest-asyncio:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality."""
    result = await some_async_function()
    assert result is not None
```

## Adding New Features

### Architectural Guidance Rules

To add new guidance rules, modify `src/symmetra/server.py`:

```python
@mcp.tool
def get_guidance(action: str, code: str = "") -> dict:
    """Get coding guidance for a proposed action"""
    guidance = []
    
    # Add your new rule here
    if "your_pattern" in action.lower():
        guidance.append("Your guidance message")
    
    return {
        "guidance": guidance,
        "status": "advisory",
        "action": action,
        "code_length": len(code)
    }
```

### CLI Commands

To add new CLI commands, modify `src/symmetra/cli.py`:

```python
def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command")
    
    # Add your new command
    new_parser = subparsers.add_parser("newcommand", help="Your command help")
    new_parser.add_argument("--option", help="Command option")
```

### Configuration Options

To add new configuration options, modify `src/symmetra/config.py`:

```python
class SymmetraConfig:
    @classmethod
    def get_new_option(cls) -> str:
        """Get new configuration option"""
        return os.getenv("ARCHGUARD_NEW_OPTION", "default_value")
```

## Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples where helpful
- Update both inline docstrings and markdown documentation
- Test all code examples

### Documentation Structure

- `README.md` - Main project documentation
- `docs/` - Detailed documentation
- `CONTRIBUTING.md` - This file
- `CODE_OF_CONDUCT.md` - Community guidelines

## Issue Reporting

### Bug Reports

Good bug reports are extremely helpful! When filing a bug report, please include:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### Feature Requests

We love feature requests! When proposing a feature:

- Explain the problem the feature would solve
- Describe the solution you'd like
- Describe alternatives you've considered
- Provide any additional context

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/). Version numbers are:

- MAJOR version when you make incompatible API changes
- MINOR version when you add functionality in a backwards compatible manner
- PATCH version when you make backwards compatible bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create release PR
5. Tag release after merge
6. Publish to PyPI (automated)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to ask questions:

- Open an issue for bugs or feature requests
- Start a discussion for general questions
- Email us at support@symmetra.dev

## Recognition

Contributors who make significant improvements will be:

- Added to the contributors list in README.md
- Mentioned in release notes
- Invited to join the maintainer team (for regular contributors)

Thank you for contributing to Symmetra! 🎉