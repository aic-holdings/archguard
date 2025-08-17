# ArchGuard Troubleshooting Guide

This guide helps diagnose and resolve common issues when setting up, testing, or using ArchGuard with MCP clients.

## 🔍 Quick Diagnosis

### Is ArchGuard Working at All?
```bash
# Test basic functionality
uvx --from git+https://github.com/aic-holdings/archguard archguard --help

# Expected: Help text displays without errors
# If this fails, see "Installation Issues" section
```

### Is the MCP Server Responding?
```bash
# Test MCP server startup
timeout 10 uvx --from git+https://github.com/aic-holdings/archguard archguard server --help

# Expected: Help text for server command
# If this hangs or fails, see "MCP Server Issues" section
```

### Is Your MCP Client Configured Correctly?
Check your client's MCP configuration file for proper JSON formatting and correct paths.

## 🚨 Common Issues & Solutions

## Installation Issues

### Error: "uvx: command not found"
**Symptoms**: Cannot run uvx commands
**Cause**: uvx not installed or not in PATH
**Solutions**:
```bash
# Install uv (includes uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using homebrew (macOS)
brew install uv

# Verify installation
uvx --version
```

### Error: "Package not found on GitHub"
**Symptoms**: uvx fails to find ArchGuard repository
**Cause**: Network issues or incorrect repository URL
**Solutions**:
```bash
# Verify GitHub access
ping github.com

# Test repository access
git ls-remote https://github.com/aic-holdings/archguard.git

# Try alternative installation
uvx install git+https://github.com/aic-holdings/archguard.git
archguard --help
```

### Error: "Python version not supported"
**Symptoms**: Import errors or version compatibility messages
**Cause**: Python version < 3.8
**Solutions**:
```bash
# Check Python version
python --version

# Install Python 3.8+ using pyenv
pyenv install 3.11.0
pyenv global 3.11.0

# Or use system package manager
# Ubuntu/Debian: sudo apt install python3.11
# macOS: brew install python@3.11
```

## MCP Server Issues

### Error: "Server startup timeout"
**Symptoms**: MCP server hangs on startup
**Cause**: Import errors, missing dependencies, or network issues
**Diagnosis**:
```bash
# Test with detailed output
ARCHGUARD_LOG_LEVEL=DEBUG uvx --from git+https://github.com/aic-holdings/archguard archguard server --help

# Check for import errors
python -c "
import sys
sys.path.insert(0, '/tmp')  # uvx cache location varies
try:
    import archguard.server
    print('✅ Imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
"
```

**Solutions**:
```bash
# Clear uvx cache
uvx cache clear

# Reinstall dependencies
uvx install --force git+https://github.com/aic-holdings/archguard.git

# Try local installation
git clone https://github.com/aic-holdings/archguard.git
cd archguard
pip install -e .
archguard server --help
```

### Error: "Tools not discoverable"
**Symptoms**: MCP server starts but tools don't appear
**Cause**: FastMCP registration issues or import errors
**Diagnosis**:
```bash
# Test tool discovery directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uvx --from git+https://github.com/aic-holdings/archguard archguard server

# Should return JSON with tools list
```

**Solutions**:
```bash
# Verify FastMCP installation
pip show fastmcp

# Test minimal MCP server
python -c "
from fastmcp import FastMCP
mcp = FastMCP('test')
@mcp.tool
def test_tool() -> str: return 'works'
print('✅ FastMCP working')
"
```

### Error: "Resource access denied"
**Symptoms**: Cannot access archguard://rules resource
**Cause**: Resource registration or permission issues
**Solutions**:
```bash
# Test resource access
echo '{"jsonrpc": "2.0", "id": 1, "method": "resources/read", "params": {"uri": "archguard://rules"}}' | uvx --from git+https://github.com/aic-holdings/archguard archguard server

# Verify resource registration
grep -n "@mcp.resource" src/archguard/server.py
```

## MCP Client Integration Issues

### Claude Code: "MCP Server Failed to Start"
**Symptoms**: Error in VS Code Claude extension
**Diagnosis**:
1. Check VS Code output panel for Claude extension
2. Look for specific error messages
3. Verify MCP configuration JSON format

**Solutions**:
```bash
# Validate JSON configuration
python -m json.tool ~/.config/claude-code/mcp.json

# Test server manually with exact same command
uvx --from git+https://github.com/aic-holdings/archguard archguard server

# Try absolute paths
which uvx  # Use full path in configuration
```

**Alternative Configuration**:
```json
{
  "mcpServers": {
    "archguard": {
      "command": "/full/path/to/uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server"],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### Claude Desktop: "No Response from Server"
**Symptoms**: Server appears connected but doesn't respond
**Solutions**:
```bash
# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/claude-desktop.log

# Restart Claude Desktop completely
pkill -f "Claude Desktop"
open "/Applications/Claude Desktop.app"

# Verify server process
ps aux | grep archguard
```

### Error: "Permission Denied"
**Symptoms**: Cannot execute uvx or ArchGuard commands
**Cause**: File permissions or security restrictions
**Solutions**:
```bash
# Check file permissions
ls -la $(which uvx)

# Fix permissions if needed
chmod +x $(which uvx)

# On macOS, check security settings
# System Preferences > Security & Privacy > Privacy > Developer Tools
```

## Performance Issues

### Slow Startup Times
**Symptoms**: ArchGuard takes > 30 seconds to start
**Causes**: Network latency, large downloads, system resources
**Solutions**:
```bash
# Pre-install to avoid repeated downloads
uvx install git+https://github.com/aic-holdings/archguard.git

# Use local development setup
git clone https://github.com/aic-holdings/archguard.git
cd archguard
pip install -e .

# Monitor download progress
uvx --verbose --from git+https://github.com/aic-holdings/archguard archguard --help
```

### High Memory Usage
**Symptoms**: System becomes slow when using ArchGuard
**Solutions**:
```bash
# Monitor memory usage
ps aux | grep archguard

# Restart server if memory usage is excessive
pkill -f archguard

# Consider local installation instead of uvx
```

### Timeout Errors
**Symptoms**: Requests timeout before completing
**Solutions**:
```bash
# Increase timeout in MCP client configuration
{
  "mcpServers": {
    "archguard": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server"],
      "timeout": 30000
    }
  }
}

# Test with simpler requests first
```

## Connectivity Issues

### Network/Firewall Problems
**Symptoms**: Cannot download ArchGuard from GitHub
**Solutions**:
```bash
# Test GitHub connectivity
curl -I https://github.com/aic-holdings/archguard

# Check proxy settings
env | grep -i proxy

# Try with proxy configuration
export https_proxy=http://proxy.company.com:8080
uvx --from git+https://github.com/aic-holdings/archguard archguard --help
```

### Corporate Network Issues
**Symptoms**: Downloads fail behind corporate firewall
**Solutions**:
```bash
# Download manually and install locally
wget https://github.com/aic-holdings/archguard/archive/main.zip
unzip main.zip
cd archguard-main
pip install -e .

# Configure git to use HTTPS instead of SSH
git config --global url."https://github.com/".insteadOf git@github.com:
```

## Development Issues

### Import Errors During Development
**Symptoms**: Cannot import ArchGuard modules
**Solutions**:
```bash
# Verify Python path
export PYTHONPATH=/path/to/archguard/src:$PYTHONPATH

# Install in development mode
pip install -e .

# Check for circular imports
python -c "import archguard.server; print('✅ Import successful')"
```

### Test Failures
**Symptoms**: pytest tests fail
**Solutions**:
```bash
# Run tests with verbose output
python -m pytest test/ -v -s

# Install test dependencies
pip install -e ".[dev]"

# Run specific failing test
python -m pytest test/test_specific.py::test_name -v
```

## Advanced Debugging

### Enable Debug Logging
```bash
# Enable detailed logging
export ARCHGUARD_LOG_LEVEL=DEBUG

# Run with debug output
uvx --from git+https://github.com/aic-holdings/archguard archguard server 2>&1 | tee debug.log
```

### MCP Protocol Debugging
```bash
# Test MCP communication manually
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "debug", "version": "1.0"}}}' | uvx --from git+https://github.com/aic-holdings/archguard archguard server | jq .
```

### Trace Network Requests
```bash
# Monitor network traffic (macOS)
sudo tcpdump -i any host github.com

# Monitor with netstat
netstat -an | grep :443
```

## 📋 Diagnostic Checklist

When reporting issues, include this information:

### System Information
- [ ] Operating System: [OS version]
- [ ] Python Version: `python --version`
- [ ] uvx Version: `uvx --version`
- [ ] Network: [Corporate/Home/VPN]

### Error Details
- [ ] Exact error message
- [ ] Command that triggered the error
- [ ] Debug logs (with ARCHGUARD_LOG_LEVEL=DEBUG)
- [ ] Steps to reproduce

### Configuration
- [ ] MCP client configuration file
- [ ] Environment variables set
- [ ] Any custom settings

### Testing Results
- [ ] Basic uvx command works: ✅/❌
- [ ] MCP server starts: ✅/❌
- [ ] Tools discoverable: ✅/❌
- [ ] Client integration: ✅/❌

## 🆘 Getting Additional Help

### Community Resources
1. **GitHub Issues**: [ArchGuard Issues](https://github.com/aic-holdings/archguard/issues)
2. **Documentation**: [Full Documentation](../README.md)
3. **MCP Protocol**: [Official MCP Docs](https://modelcontextprotocol.io/)

### Creating a Bug Report
Include:
1. Complete diagnostic checklist (above)
2. Minimal reproduction steps
3. Expected vs actual behavior
4. Relevant log files or error messages

### Emergency Workarounds
```bash
# Complete reset - start fresh
uvx cache clear
rm -rf ~/.config/claude-code/mcp.json
# Reconfigure from scratch

# Fallback to local installation
git clone https://github.com/aic-holdings/archguard.git
cd archguard
pip install -e .
# Use "archguard server" instead of uvx command
```

---

**Remember**: Most issues are configuration-related. Double-check JSON formatting, file paths, and network connectivity before diving into complex debugging.