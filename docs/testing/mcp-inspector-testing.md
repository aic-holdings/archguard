# MCP Inspector Testing for ArchGuard

The MCP Inspector is an interactive tool that lets you test and explore ArchGuard's capabilities in real-time. This is the best way to validate that ArchGuard works correctly before integrating it with your coding assistants.

## 🔧 Setup MCP Inspector

### Install MCP Inspector
```bash
# Install globally with npm
npm install -g @modelcontextprotocol/inspector

# Verify installation
mcp-inspector --version
```

### Alternative Installation Methods
```bash
# Using npx (no global install)
npx @modelcontextprotocol/inspector

# Using pnpm
pnpm add -g @modelcontextprotocol/inspector

# Using yarn
yarn global add @modelcontextprotocol/inspector
```

## 🚀 Launch ArchGuard with MCP Inspector

### Method 1: Direct uvx Execution (Recommended)
```bash
# Launch ArchGuard with MCP Inspector
mcp-inspector uvx --from git+https://github.com/aic-holdings/archguard archguard server
```

### Method 2: Local Development Testing
```bash
# If you have ArchGuard cloned locally
cd archguard
mcp-inspector uv run archguard server

# Or with absolute path
mcp-inspector python /absolute/path/to/archguard/src/archguard/server.py
```

### Method 3: After Global Installation
```bash
# If you've installed ArchGuard globally
uvx install git+https://github.com/aic-holdings/archguard.git
mcp-inspector archguard server
```

## 🧪 Interactive Testing Guide

Once MCP Inspector launches, you'll see a web interface. Here's how to test ArchGuard:

### 1. Verify Server Connection
- ✅ **Server Status**: Should show "Connected" 
- ✅ **Protocol**: Should show "Model Context Protocol"
- ✅ **Server Info**: Should display "ArchGuard" as server name

### 2. Explore Available Tools
You should see **3 tools** in the left sidebar:

#### 🛠️ **get_guidance**
**Purpose**: Primary architectural guidance tool

**Test it**:
```json
{
  "action": "create user authentication system",
  "code": "",
  "context": "startup MVP application"
}
```

**Expected Result**:
- List of security recommendations
- Authentication patterns suggested
- Complexity score: "high"
- Multiple guidance points about JWT, bcrypt, etc.

#### 📚 **get_archguard_help**  
**Purpose**: Usage guide for coding agents

**Test it**:
```json
{}
```

**Expected Result**:
- Comprehensive usage guide
- Examples of effective interactions
- Pro tips and best practices
- Quick reference section

#### 🔍 **review_code**
**Purpose**: Generate structured code review prompt

**Test it**:
```json
{
  "code": "def authenticate_user(username, password):\n    if username == 'admin' and password == 'password123':\n        return True\n    return False"
}
```

**Expected Result**:
- Structured architectural review prompt
- Security analysis checklist
- Performance considerations
- Refactoring opportunities

### 3. Test Resources
Click on **Resources** tab:

#### 📋 **archguard://rules**
**Expected Content**:
- 40 architectural governance rules
- Organized by categories (Security, Performance, etc.)
- Professional standards reference

### 4. Test Prompts
Click on **Prompts** tab:

#### 🎨 **review_code**
**Test with**:
```json
{
  "code": "class UserManager:\n    def __init__(self):\n        self.users = []\n        self.database = 'sqlite:///users.db'\n    \n    def add_user(self, data):\n        self.users.append(data)\n        # TODO: Save to database"
}
```

**Expected Result**:
- Comprehensive architectural review template
- Structured analysis checklist
- Specific recommendations for improvement

## ✅ Validation Checklist

Use this checklist to ensure ArchGuard is working correctly:

### 🔌 **Connection & Setup**
- [ ] MCP Inspector connects successfully
- [ ] No error messages in console
- [ ] Server status shows "Connected"
- [ ] ArchGuard identified as server name

### 🛠️ **Tools Functionality**
- [ ] **get_guidance** returns comprehensive recommendations
- [ ] **get_archguard_help** provides detailed usage guide  
- [ ] **review_code** generates structured prompts
- [ ] All tools have rich, detailed descriptions
- [ ] Tools respond within reasonable time (< 5 seconds)

### 📋 **Resources & Content**
- [ ] **archguard://rules** loads successfully
- [ ] Rules content is comprehensive (40+ rules)
- [ ] Content is well-formatted and readable
- [ ] Categories are properly organized

### 🎨 **Prompts & Templates**
- [ ] **review_code** prompt generates correctly
- [ ] Template includes all review categories
- [ ] Checklist is comprehensive and actionable
- [ ] Formatting is professional and clear

### 🔍 **Content Quality**
- [ ] Tool descriptions are detailed and helpful
- [ ] Guidance is specific and actionable
- [ ] Security recommendations are comprehensive
- [ ] Architectural patterns are suggested appropriately

## 🧪 Advanced Testing Scenarios

### Test Complex Architecture Guidance
```json
{
  "action": "design microservices architecture for e-commerce platform",
  "context": "handling 100K+ daily users, needs to scale to 1M users",
  "code": ""
}
```

**Expected**: Microservices patterns, scalability guidance, service design recommendations

### Test Security Analysis
```json
{
  "action": "implement JWT authentication with refresh tokens",
  "context": "enterprise application with strict security requirements",
  "code": "const jwt = require('jsonwebtoken');\nconst secret = 'my-secret-key';"
}
```

**Expected**: Security warnings about hardcoded secrets, JWT best practices, token management guidance

### Test Code Analysis
```json
{
  "action": "refactor large component",
  "code": "// Large component with 200+ lines\nclass UserDashboard extends React.Component {\n  // ... 200 lines of mixed logic\n}",
  "context": "React application"
}
```

**Expected**: Decomposition suggestions, component patterns, maintainability improvements

## 📊 Performance Testing

### Response Time Expectations
- **get_guidance**: < 3 seconds for typical requests
- **get_archguard_help**: < 1 second (static content)
- **review_code**: < 2 seconds for prompts

### Memory Usage
- Inspector should remain responsive
- No memory leaks during extended testing
- Server restarts cleanly between tests

## 🐛 Troubleshooting Inspector Issues

### Common Problems & Solutions

#### **"Connection Failed" Error**
```bash
# Check if ArchGuard starts independently
uvx --from git+https://github.com/aic-holdings/archguard archguard server --help

# Verify network connectivity
ping github.com

# Try alternative installation
uvx install git+https://github.com/aic-holdings/archguard.git
mcp-inspector archguard server
```

#### **"No Tools Found" Error**
- Check console for import errors
- Verify Python dependencies are installed
- Try restarting the inspector

#### **Slow Responses**
- Check internet connection speed
- Verify system resources (CPU, memory)
- Try local development setup instead of uvx

#### **Tool Execution Errors**
- Review the tool parameters format
- Check for required vs optional parameters
- Verify JSON syntax in test inputs

## 📝 Documenting Test Results

Create a test report:

```markdown
## ArchGuard MCP Inspector Test Report

**Date**: [Current Date]
**Version**: [ArchGuard Version]
**Environment**: [OS, Python version, Node version]

### Connection Status
- [x] Server connects successfully
- [x] No console errors
- [x] Proper server identification

### Tool Testing Results
- [x] get_guidance: ✅ Working, comprehensive responses
- [x] get_archguard_help: ✅ Working, detailed guide
- [x] review_code: ✅ Working, structured prompts

### Resource Testing
- [x] archguard://rules: ✅ Accessible, 40+ rules loaded

### Performance
- Average response time: [X seconds]
- Memory usage: [Normal/High]
- Stability: [Stable/Issues noted]

### Issues Found
- [List any issues or observations]

### Recommendations
- [Any suggestions for improvement]
```

## 🎯 Next Steps

After successful MCP Inspector testing:

1. **[Manual Validation](manual-validation.md)** - Test specific use cases
2. **[Integration Testing](integration-testing.md)** - Test with Claude Code
3. **Production Deployment** - Configure your coding assistant

---

**Tip**: Keep the MCP Inspector open while developing - it's perfect for testing changes in real-time!