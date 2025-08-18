# Symmetra Testing Guide

This directory contains comprehensive testing documentation and tools to validate Symmetra's functionality before deploying it with your coding assistants.

## 🧪 Quick Test Overview

Before integrating Symmetra with Claude Code or other MCP clients, run these tests to ensure everything works correctly:

1. **[MCP Inspector Testing](mcp-inspector-testing.md)** - Interactive testing with MCP Inspector tools
2. **[Manual Validation](manual-validation.md)** - Step-by-step manual testing procedures  
3. **[Integration Testing](integration-testing.md)** - Test Symmetra with different MCP clients
4. **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- `uvx` or `uv` package manager
- Internet connection for GitHub access

### 1. Test Basic Functionality
```bash
# Test help command
uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help

# Test MCP server startup
uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --help
```

### 2. Run MCP Inspector Tests
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test Symmetra with MCP Inspector
mcp-inspector uvx --from git+https://github.com/aic-holdings/symmetra symmetra server
```

### 3. Run Automated Test Suite
```bash
# Clone repository for full testing
git clone https://github.com/aic-holdings/symmetra.git
cd symmetra

# Run comprehensive tests
python -m pytest test/ -v
python test/test_pre_uvx_validation.py
python test/test_serena_style_execution.py
```

## 📋 Test Categories

### ✅ Automated Tests
- **Unit Tests**: Core functionality validation
- **Integration Tests**: MCP server communication
- **uvx Tests**: Serena-style execution validation
- **Claude Code Tests**: Client compatibility validation

### 🔍 Interactive Tests  
- **MCP Inspector**: Real-time tool testing and exploration
- **Manual Validation**: Step-by-step verification procedures
- **Client Integration**: Testing with actual coding assistants

### 🎯 Validation Areas
- **Tool Functionality**: All MCP tools work correctly
- **Resource Access**: Symmetra rules and guidance available
- **Prompt Generation**: Code review templates function properly
- **Error Handling**: Graceful failure and recovery
- **Performance**: Response times and resource usage

## 📊 Expected Test Results

### ✅ Successful Test Indicators
- All pytest tests pass (12/12)
- MCP Inspector shows 3 tools: `get_guidance`, `get_symmetra_help`, `review_code`
- Resources accessible: `symmetra://rules`
- Server starts without errors
- Rich tool descriptions visible in inspector
- Claude Code configuration validates successfully

### ❌ Common Issues
- Import errors → Check Python path and dependencies
- Server startup failures → Verify uvx installation and GitHub access
- MCP connection issues → Check firewall and network settings
- Tool discovery problems → Validate MCP client configuration

## 🔧 Development Testing

For contributors and advanced users:

```bash
# Clone and setup development environment
git clone https://github.com/aic-holdings/symmetra.git
cd symmetra

# Install development dependencies
pip install -e ".[dev]"

# Run full test suite
python -m pytest test/ -v --cov=src/symmetra

# Test with different Python versions
tox

# Validate packaging
python -m build
python -m twine check dist/*
```

## 📚 Additional Resources

- **[MCP Inspector Documentation](https://modelcontextprotocol.io/legacy/tools/inspector)**
- **[MCP Protocol Specification](https://modelcontextprotocol.io/specification)**
- **[Claude Code MCP Setup](https://docs.anthropic.com/en/docs/claude-code/mcp)**
- **[Symmetra GitHub Repository](https://github.com/aic-holdings/symmetra)**

## 🆘 Getting Help

If tests fail or you encounter issues:

1. Check the **[Troubleshooting Guide](troubleshooting.md)**
2. Review test output for specific error messages
3. Verify your environment meets all prerequisites
4. Open an issue on [GitHub](https://github.com/aic-holdings/symmetra/issues)

---

**Next**: Start with **[MCP Inspector Testing](mcp-inspector-testing.md)** for interactive validation of Symmetra's capabilities.