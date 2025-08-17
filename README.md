# ArchGuard

**Real-time AI Governance via MCP**

ArchGuard is a working MCP (Model Context Protocol) server that provides real-time coding guidance to AI agents. Built with FastMCP 2.0, it offers advisory governance without blocking development workflow.

## 🚀 Quick Start

```bash
# Install FastMCP
pip install fastmcp

# Run ArchGuard server
python archguard_server.py

# For Claude Code integration
fastmcp install archguard_server.py --name "ArchGuard"
```

Once installed, ask Claude Code:
- *"Get guidance for creating a user authentication system"*
- *"Should I create this 500-line component?"*
- *"What are the governance rules for API design?"*

## 🛡️ What ArchGuard Does

ArchGuard provides **advisory guidance** for AI agents during development:

- **File Size**: Recommends keeping files under 300 lines
- **Security**: Authentication patterns, password handling best practices
- **Code Structure**: Breaking up large code blocks into smaller functions  
- **API Design**: API-first principles and documentation reminders
- **Database**: Soft deletes and proper indexing recommendations

**Example Response:**
```json
{
  "guidance": [
    "🔒 Use secure authentication patterns",
    "🔐 Never store passwords in plain text"
  ],
  "status": "advisory",
  "action": "create user authentication system"
}
```

## 🧪 Testing

```bash
# Run comprehensive test suite
python test_client.py

# Test HTTP production mode  
python archguard_http_server.py &
python test_http_client.py
```

## 🏗️ Architecture

### MCP Tools
- **`get_guidance(action, code)`** - Get coding guidance for proposed actions

### MCP Resources  
- **`archguard://rules`** - Current governance rules reference

### MCP Prompts
- **`review_code(code)`** - Generate structured code review prompts

### Transport Modes
- **Stdio** (default): For local development and Claude Code integration
- **HTTP**: For production deployment and horizontal scaling

## 📋 Features

### ✅ Working in v0
- Real-time guidance via MCP protocol
- FastMCP 2.0 framework integration
- Multi-transport support (stdio + HTTP)
- Comprehensive test suite
- Claude Code ready

### 🔄 Planned for v0.1
- Ollama integration for advanced code analysis
- Expanded governance rule engine
- Compliance tracking and history

## 🔧 Development

### File Structure
```
archguard/
├── README.md                    # This file
├── archguard_server.py         # Main MCP server
├── archguard_http_server.py    # Production HTTP version
├── tests/                      # Test suite
└── docs/                       # Documentation
```

### Adding New Guidance Rules
```python
# In archguard_server.py get_guidance() function
if "new_pattern" in action.lower():
    guidance.append("💡 Your new guidance message")
```

### Testing Changes
```bash
# Quick validation
python tests/test_client.py

# Full validation including HTTP
python tests/run_all_tests.py
```

## 📚 Documentation

- **[Implementation Guide](docs/IMPLEMENTATION.md)** - Technical architecture and decisions
- **[Testing Results](docs/TESTING_RESULTS.md)** - Comprehensive test outcomes
- **[Original Spec](docs/ORIGINAL_SPEC.md)** - Historical MCP server specification

## 🎯 Design Philosophy

**Advisory, Not Blocking**: ArchGuard provides suggestions without breaking development flow. AI agents receive guidance but can proceed with human oversight.

**MCP Native**: Built specifically for the Model Context Protocol, ensuring compatibility with any MCP-enabled AI system.

**Production Ready**: Supports both local development (stdio) and production deployment (HTTP) from day one.

## 🤝 Contributing

ArchGuard follows a simple contribution model:

1. Test your changes: `python tests/run_all_tests.py`
2. Ensure guidance is helpful, not restrictive
3. Maintain advisory (not blocking) behavior
4. Add tests for new guidance rules

## 📄 License

Open Source - License TBD

---

**ArchGuard v0** - Constitutional governance for AI development without the friction.