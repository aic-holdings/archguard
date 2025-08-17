# Integration Testing with MCP Clients

This guide covers testing ArchGuard with actual MCP clients like Claude Code, Claude Desktop, and other coding assistants to ensure real-world functionality.

## 🎯 Testing Overview

Integration testing validates that ArchGuard works correctly when integrated with:
- Claude Code (VS Code extension)
- Claude Desktop (standalone application)
- Other MCP-compatible coding assistants
- Terminal-based MCP clients

## 🔧 Prerequisites

Before starting integration tests:
- ArchGuard passes all [manual validation tests](manual-validation.md)
- Target MCP client is installed and working
- Network connectivity for GitHub access
- Basic familiarity with your chosen MCP client

## 🧪 Claude Code Integration Testing

### Setup Claude Code with ArchGuard

#### Step 1: Install Claude Code
```bash
# Install Claude Code VS Code extension
code --install-extension anthropic.claude-code
```

#### Step 2: Configure MCP Server
Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "archguard": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server"],
      "env": {
        "ARCHGUARD_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Step 3: Restart VS Code
Close and reopen VS Code to load the new MCP server configuration.

### Claude Code Test Scenarios

#### Test 3.1: Server Discovery
1. Open VS Code with Claude Code extension
2. Open the Claude Code panel
3. Look for ArchGuard in available tools/servers
4. Check that no error messages appear in the output

**✅ Pass Criteria:**
- ArchGuard appears in Claude's available tools
- No connection errors in Claude Code output
- Server status shows as connected

#### Test 3.2: Basic Tool Usage
In Claude Code chat, test these interactions:

```
"Use ArchGuard to get guidance for implementing user authentication"
```

**✅ Pass Criteria:**
- Claude successfully calls ArchGuard's get_guidance tool
- Returns comprehensive security recommendations
- No error messages or failures

#### Test 3.3: Code Review Integration
Share code with Claude and ask:

```
"Use ArchGuard to review this authentication function for security issues:

function authenticateUser(username, password) {
    if (username === 'admin' && password === 'password123') {
        return { success: true, token: 'abc123' };
    }
    return { success: false };
}
"
```

**✅ Pass Criteria:**
- Claude uses ArchGuard's review_code prompt
- Identifies security issues (hardcoded credentials, weak token)
- Provides specific architectural recommendations

#### Test 3.4: Help System Integration
Ask Claude:

```
"Show me how to use ArchGuard effectively"
```

**✅ Pass Criteria:**
- Claude calls get_archguard_help tool
- Displays comprehensive usage guide
- Shows examples and best practices

#### Test 3.5: Rules and Resources Access
Ask Claude:

```
"What are ArchGuard's architectural governance rules?"
```

**✅ Pass Criteria:**
- Claude accesses archguard://rules resource
- Displays the 40 governance rules
- Content is well-formatted and complete

### Claude Code Performance Testing

#### Test 3.6: Response Time Validation
Time these interactions:
- Simple guidance request: Should complete in < 5 seconds
- Complex code review: Should complete in < 10 seconds
- Help system access: Should complete in < 3 seconds

#### Test 3.7: Concurrent Usage
Test multiple rapid requests:
1. Ask for authentication guidance
2. Immediately ask for API design guidance
3. Request code review while previous requests are processing

**✅ Pass Criteria:**
- All requests complete successfully
- No conflicts or errors
- Reasonable response times maintained

## 🖥️ Claude Desktop Integration Testing

### Setup Claude Desktop with ArchGuard

#### Step 1: Configure Claude Desktop
Edit your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "archguard": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server"]
    }
  }
}
```

#### Step 2: Restart Claude Desktop
Fully quit and restart Claude Desktop application.

### Claude Desktop Test Scenarios

#### Test 4.1: Tool Availability
1. Start new conversation in Claude Desktop
2. Look for tool indicators (hammer icons)
3. Verify ArchGuard tools are available

**✅ Pass Criteria:**
- Tools show up in Claude Desktop interface
- No error messages in conversation
- All 3 ArchGuard tools are discoverable

#### Test 4.2: Architectural Guidance
Test comprehensive architectural requests:

```
"I need to design a microservices architecture for an e-commerce platform that can handle 100K daily users. Use ArchGuard to provide comprehensive guidance."
```

**✅ Pass Criteria:**
- Claude uses ArchGuard's get_guidance tool
- Provides microservices-specific recommendations
- Includes scalability and performance guidance

#### Test 4.3: Complex Code Analysis
Share a large code snippet and request analysis:

```
"Use ArchGuard to analyze this 150-line React component and suggest architectural improvements."
```

**✅ Pass Criteria:**
- Handles large code input correctly
- Provides component decomposition suggestions
- Includes React-specific architectural guidance

## 🔧 Other MCP Client Testing

### Terminal-Based Clients

#### Test with Codex CLI
```bash
# Configure Codex with ArchGuard
echo '[mcp_servers.archguard]
command = "uvx"
args = ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server"]' >> ~/.codex/config.toml

# Test in Codex session
codex
# In Codex: "Use ArchGuard to get guidance for implementing JWT authentication"
```

#### Test with Gemini CLI
Configure and test ArchGuard with Gemini CLI if available.

### IDE Extensions

#### Test with Cursor
If using Cursor IDE:
1. Configure ArchGuard as MCP server
2. Test architectural guidance integration
3. Verify code review functionality

#### Test with Windsurf
If using Windsurf:
1. Add ArchGuard to MCP configuration
2. Test semantic analysis capabilities
3. Validate architectural recommendations

## 📊 Integration Test Matrix

| Client | Server Discovery | Tool Usage | Code Review | Performance | Notes |
|--------|------------------|------------|-------------|-------------|-------|
| Claude Code | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | VS Code extension |
| Claude Desktop | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | Standalone app |
| Codex CLI | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | Terminal-based |
| Cursor | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | IDE integration |
| Windsurf | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | Web-based IDE |

## 🐛 Common Integration Issues

### Issue: "MCP Server Not Found"
**Symptoms**: ArchGuard doesn't appear in tool list
**Solutions**:
```bash
# Verify uvx works independently
uvx --from git+https://github.com/aic-holdings/archguard archguard --help

# Check MCP client configuration format
# Ensure proper JSON formatting and paths
```

### Issue: "Tool Execution Failures"
**Symptoms**: Tools discovered but fail when called
**Solutions**:
```bash
# Test ArchGuard server manually
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uvx --from git+https://github.com/aic-holdings/archguard archguard server

# Check for import errors or dependency issues
```

### Issue: "Slow Response Times"
**Symptoms**: Tools work but respond very slowly
**Solutions**:
- Check internet connection speed
- Try installing ArchGuard locally for testing
- Monitor system resource usage

### Issue: "Incomplete Responses"
**Symptoms**: Tools return partial or empty responses
**Solutions**:
- Check for timeout settings in MCP client
- Verify ArchGuard server logs
- Test with simpler requests first

## 🔍 Advanced Integration Testing

### Test 5.1: Multi-Project Configuration
Test ArchGuard with project-specific configurations:

```json
{
  "mcpServers": {
    "archguard-project1": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server", "--project", "/path/to/project1"]
    },
    "archguard-project2": {
      "command": "uvx", 
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server", "--project", "/path/to/project2"]
    }
  }
}
```

### Test 5.2: Environment-Specific Testing
Test different environment configurations:

```json
{
  "mcpServers": {
    "archguard-dev": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server"],
      "env": {
        "ARCHGUARD_LOG_LEVEL": "DEBUG",
        "ARCHGUARD_CONTEXT": "development"
      }
    }
  }
}
```

### Test 5.3: Load Testing
Simulate heavy usage:
1. Open multiple conversations with ArchGuard
2. Make concurrent requests for guidance
3. Test with large code snippets
4. Monitor resource usage and response times

## 📝 Integration Test Report Template

```markdown
# ArchGuard Integration Test Report

**Date**: [Date]
**Tester**: [Name]
**Environment**: [OS, Client versions]

## Test Summary
- **Claude Code**: ✅ Pass / ❌ Fail / ⚠️ Issues
- **Claude Desktop**: ✅ Pass / ❌ Fail / ⚠️ Issues
- **Other Clients**: [List results]

## Detailed Results

### Claude Code Integration
- Server Discovery: ✅/❌
- Tool Usage: ✅/❌
- Code Review: ✅/❌
- Performance: ✅/❌
- Notes: [Specific observations]

### Claude Desktop Integration
- Server Discovery: ✅/❌
- Tool Usage: ✅/❌
- Code Review: ✅/❌
- Performance: ✅/❌
- Notes: [Specific observations]

## Performance Metrics
- Average Response Time: [X seconds]
- Memory Usage: [X MB]
- Concurrent Request Handling: ✅/❌

## Issues Identified
1. [Issue description]
   - Impact: High/Medium/Low
   - Workaround: [If available]

## Recommendations
- [Suggestions for improvement]
- [Configuration optimizations]

## Overall Assessment
- Ready for production use: ✅/❌
- Recommended for team deployment: ✅/❌
- Major issues requiring resolution: [List if any]
```

## 🚀 Production Readiness Checklist

Before deploying ArchGuard in production:

- [ ] All integration tests pass with primary MCP client
- [ ] Performance meets requirements (< 5 second responses)
- [ ] No critical issues identified
- [ ] Team training completed on ArchGuard usage
- [ ] Monitoring and alerting configured
- [ ] Rollback plan prepared

## 🔄 Continuous Integration Testing

Set up automated integration testing:

```bash
# Create integration test script
cat > test_integration.sh << 'EOF'
#!/bin/bash
set -e

echo "🧪 Running ArchGuard Integration Tests"

# Test 1: Server startup
echo "Testing server startup..."
timeout 10 uvx --from git+https://github.com/aic-holdings/archguard archguard server --help

# Test 2: MCP protocol
echo "Testing MCP protocol..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | timeout 10 uvx --from git+https://github.com/aic-holdings/archguard archguard server

# Test 3: Configuration validation
echo "Testing configuration..."
python -c "import json; json.load(open('claude_config_test.json'))"

echo "✅ All integration tests passed"
EOF

chmod +x test_integration.sh
./test_integration.sh
```

## 📚 Next Steps

After successful integration testing:

1. **[Troubleshooting Guide](troubleshooting.md)** - Address any remaining issues
2. **Production Deployment** - Roll out to team
3. **User Training** - Educate team on ArchGuard usage
4. **Monitoring Setup** - Track usage and performance

---

**Important**: Integration testing should be repeated whenever ArchGuard is updated or when MCP client configurations change.