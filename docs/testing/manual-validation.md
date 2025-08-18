# Manual Validation Testing

This guide provides step-by-step manual testing procedures to validate Symmetra's functionality without requiring MCP Inspector or other tools.

## 🎯 Testing Objectives

- Verify basic server functionality
- Test all command-line interfaces
- Validate uvx execution patterns
- Confirm MCP protocol compliance
- Test error handling and edge cases

## 🔧 Prerequisites

- Python 3.8+ installed
- `uvx` or `uv` package manager available
- Basic command-line familiarity
- Internet connection for GitHub access

## 📋 Test Categories

## 1. Basic Command Line Testing

### Test 1.1: Help Command Validation
```bash
# Test main help
uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help

# Expected output:
# - Usage information displayed
# - Available commands listed (init, check, config, server, http)
# - No error messages
# - Professional formatting
```

**✅ Pass Criteria:**
- Help text displays correctly
- All 5 commands are listed
- No Python errors or exceptions
- Output is well-formatted

### Test 1.2: Subcommand Help Validation
```bash
# Test server help
uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --help

# Test http help  
uvx --from git+https://github.com/aic-holdings/symmetra symmetra http --help

# Test init help
uvx --from git+https://github.com/aic-holdings/symmetra symmetra init --help
```

**✅ Pass Criteria:**
- Each subcommand shows appropriate help
- Options and arguments are documented
- No import or execution errors

### Test 1.3: Version and Info Commands
```bash
# Test basic execution (should not hang)
timeout 5 uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --help || echo "Help completed"
```

**✅ Pass Criteria:**
- Commands execute and return promptly
- No infinite loops or hanging processes

## 2. MCP Server Testing

### Test 2.1: Server Startup
```bash
# Start server and test basic startup
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | uvx --from git+https://github.com/aic-holdings/symmetra symmetra server
```

**✅ Pass Criteria:**
- Server starts without errors
- Responds to initialization message
- No import failures or exceptions

### Test 2.2: Tool Discovery
```bash
# Test tools/list method
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | uvx --from git+https://github.com/aic-holdings/symmetra symmetra server
```

**✅ Pass Criteria:**
- Returns list of available tools
- Should include: get_guidance, get_symmetra_help, review_code
- Valid JSON response format

### Test 2.3: Resource Discovery  
```bash
# Test resources/list method
echo '{"jsonrpc": "2.0", "id": 3, "method": "resources/list"}' | uvx --from git+https://github.com/aic-holdings/symmetra symmetra server
```

**✅ Pass Criteria:**
- Returns list of available resources
- Should include: symmetra://rules
- Valid JSON response format

## 3. uvx Execution Pattern Testing

### Test 3.1: Direct Execution Pattern
```bash
# Test Serena-style direct execution
uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help
```

**✅ Pass Criteria:**
- Executes without permanent installation
- Downloads and runs successfully
- Same behavior as permanent installation

### Test 3.2: Repeated Execution
```bash
# Test multiple executions (caching behavior)
uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help
uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --help
```

**✅ Pass Criteria:**
- Subsequent executions are faster (caching works)
- Consistent behavior across executions
- No conflicts or cache corruption

### Test 3.3: Network Dependency Testing
```bash
# Test GitHub access and download
time uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help
```

**✅ Pass Criteria:**
- Downloads complete successfully
- Reasonable download time (< 60 seconds on good connection)
- Handles network issues gracefully

## 4. Error Handling Testing

### Test 4.1: Invalid Commands
```bash
# Test invalid command
uvx --from git+https://github.com/aic-holdings/symmetra symmetra invalid-command

# Test invalid options
uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --invalid-option
```

**✅ Pass Criteria:**
- Shows helpful error messages
- Suggests valid alternatives
- Exits with non-zero status code

### Test 4.2: Network Issues Simulation
```bash
# Test with invalid repository (should fail gracefully)
uvx --from git+https://github.com/invalid/nonexistent symmetra --help
```

**✅ Pass Criteria:**
- Fails with clear error message
- No confusing stack traces
- Appropriate exit codes

### Test 4.3: MCP Protocol Error Handling
```bash
# Test invalid JSON message
echo 'invalid json' | uvx --from git+https://github.com/aic-holdings/symmetra symmetra server
```

**✅ Pass Criteria:**
- Handles invalid input gracefully
- Doesn't crash the server
- Returns appropriate error response

## 5. Functional Testing

### Test 5.1: Architecture Guidance Testing
Create a test script to validate guidance functionality:

```bash
# Create test file
cat > test_guidance.py << 'EOF'
import json
import subprocess
import sys

def test_guidance():
    # Start server process
    proc = subprocess.Popen([
        'uvx', '--from', 'git+https://github.com/aic-holdings/symmetra',
        'symmetra', 'server'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Send initialization
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    proc.stdin.write(json.dumps(init_msg) + '\n')
    proc.stdin.flush()
    
    # Test get_guidance tool
    guidance_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_guidance",
            "arguments": {
                "action": "create user authentication system",
                "context": "startup application"
            }
        }
    }
    
    proc.stdin.write(json.dumps(guidance_msg) + '\n')
    proc.stdin.flush()
    
    # Wait briefly then terminate
    import time
    time.sleep(2)
    proc.terminate()
    
    print("✅ Guidance functionality test completed")
    return True

if __name__ == "__main__":
    test_guidance()
EOF

# Run the test
python test_guidance.py
```

**✅ Pass Criteria:**
- Script runs without errors
- Server responds to tool calls
- Guidance content is returned

## 6. Integration Pattern Testing

### Test 6.1: Claude Code Configuration Format
```bash
# Test configuration that would be used in Claude Code
cat > claude_config_test.json << 'EOF'
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra", "server"],
      "env": {
        "ARCHGUARD_LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF

# Validate JSON format
python -m json.tool claude_config_test.json
```

**✅ Pass Criteria:**
- JSON is valid and well-formed
- Configuration follows Claude Code MCP format
- All required fields are present

### Test 6.2: Environment Variable Testing
```bash
# Test with different log levels
ARCHGUARD_LOG_LEVEL=DEBUG uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --help

# Test with custom config path
ARCHGUARD_CONFIG_PATH=/tmp/test-config.toml uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --help
```

**✅ Pass Criteria:**
- Environment variables are respected
- No errors with different configurations
- Appropriate behavior changes with settings

## 7. Performance Testing

### Test 7.1: Startup Time Measurement
```bash
# Measure cold start time
time uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help

# Measure warm start time (cached)
time uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help
```

**✅ Pass Criteria:**
- Cold start completes within reasonable time (< 30 seconds)
- Warm start is significantly faster (< 5 seconds)
- Performance is acceptable for daily use

### Test 7.2: Memory Usage Monitoring
```bash
# Monitor memory usage during execution
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | (uvx --from git+https://github.com/aic-holdings/symmetra symmetra server &) && sleep 5 && pkill -f symmetra
```

**✅ Pass Criteria:**
- Reasonable memory usage (< 100MB typical)
- No obvious memory leaks
- Clean process termination

## 8. Documentation Validation

### Test 8.1: Help Content Quality
Manually review the help output for:
- Clear, professional language
- Comprehensive examples
- Proper formatting
- No typos or errors

### Test 8.2: Error Message Quality
Test various error conditions and verify:
- Error messages are helpful and specific
- Suggestions for fixes are provided
- No confusing technical jargon
- Appropriate detail level

## 📊 Test Results Documentation

Create a test report using this template:

```markdown
# Symmetra Manual Validation Report

**Date**: [Date]
**Tester**: [Name]
**Environment**: [OS, Python version]
**Symmetra Version**: [Git commit hash]

## Test Results Summary
- Total Tests: 24
- Passed: [Number]
- Failed: [Number]
- Warnings: [Number]

## Detailed Results

### 1. Basic Command Line Testing
- [ ] 1.1 Help Command Validation
- [ ] 1.2 Subcommand Help Validation  
- [ ] 1.3 Version and Info Commands

### 2. MCP Server Testing
- [ ] 2.1 Server Startup
- [ ] 2.2 Tool Discovery
- [ ] 2.3 Resource Discovery

### 3. uvx Execution Pattern Testing
- [ ] 3.1 Direct Execution Pattern
- [ ] 3.2 Repeated Execution
- [ ] 3.3 Network Dependency Testing

### 4. Error Handling Testing
- [ ] 4.1 Invalid Commands
- [ ] 4.2 Network Issues Simulation
- [ ] 4.3 MCP Protocol Error Handling

### 5. Functional Testing
- [ ] 5.1 Architecture Guidance Testing

### 6. Integration Pattern Testing
- [ ] 6.1 Claude Code Configuration Format
- [ ] 6.2 Environment Variable Testing

### 7. Performance Testing
- [ ] 7.1 Startup Time Measurement
- [ ] 7.2 Memory Usage Monitoring

### 8. Documentation Validation
- [ ] 8.1 Help Content Quality
- [ ] 8.2 Error Message Quality

## Issues Found
[List any issues discovered during testing]

## Recommendations
[Suggestions for improvements]

## Overall Assessment
[Ready for production / Needs work / Critical issues found]
```

## 🚀 Next Steps

After completing manual validation:

1. **[Integration Testing](integration-testing.md)** - Test with actual MCP clients
2. **[Troubleshooting](troubleshooting.md)** - Address any issues found
3. **Production Deployment** - Configure with your coding assistant

---

**Tip**: Run manual validation tests regularly, especially after making changes to Symmetra's core functionality.