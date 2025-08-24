# Symmetra Quick Start Guide

Get Symmetra running in 5 minutes and start receiving architectural guidance immediately.

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Symmetra (1 minute)
```bash
# Clone and install
git clone https://github.com/aic-holdings/symmetra.git
cd symmetra
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

### Step 2: Configure MCP (2 minutes)
Add to your `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "python",
      "args": ["-m", "symmetra.server"],
      "cwd": "/path/to/symmetra",
      "env": {
        "SYMMETRA_ENGINE_TYPE": "keyword"
      }
    }
  }
}
```

### Step 3: Test Integration (1 minute)
Restart Claude Code and ask:
```
Can you get architectural guidance for "implementing user authentication in Python"?
```

### Step 4: (Optional) Setup Vector Search (1 minute)
For semantic search capabilities:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull nomic-embed-text
```

## 🎯 First Use Cases

### 1. Code Review Assistant
```
👤 "Review this authentication function for security issues"

🤖 [AI calls Symmetra get_guidance tool]

🏗️ Symmetra provides:
- 🔐 Never store passwords in plaintext - use bcrypt hashing
- 🔑 Implement JWT tokens with short expiration times  
- 🚦 Add rate limiting to prevent brute force attacks
- 🛡️ Use environment variables for secret keys
```

### 2. Architecture Planning
```
👤 "Help me design a microservices architecture for an e-commerce platform"

🤖 [AI calls search_rules tool for "microservices architecture"]

🔍 Symmetra returns:
- microservice-boundaries: Define services around business capabilities
- api-gateway-pattern: Use gateway for routing and authentication
- data-consistency: Plan for eventual consistency across services
```

### 3. Technology Decisions
```
👤 "What's the best way to handle caching in my Python API?"

🤖 [AI calls get_guidance tool]

🏗️ Symmetra provides:
- ⚡ Use Redis for distributed session storage
- 🕒 Set appropriate TTL based on data freshness requirements
- 🔄 Implement cache invalidation strategy for data updates
```

## 📚 Common Workflows

### Development Workflow
1. **Planning**: Get guidance before implementing features
2. **Coding**: Search rules for specific technical questions  
3. **Review**: Get architectural feedback on code changes
4. **Deployment**: Check best practices for production

### Team Integration
1. **Onboarding**: New team members learn patterns quickly
2. **Standards**: Consistent architectural guidance across team
3. **Reviews**: Automated suggestions during code review
4. **Documentation**: Living architectural knowledge base

## 🔧 Configuration Options

### Context-Aware Guidance
```bash
# For real-time coding assistance
export SYMMETRA_DEFAULT_CONTEXT=ide-assistant

# For automated processing  
export SYMMETRA_DEFAULT_CONTEXT=agent

# For learning and discussion
export SYMMETRA_DEFAULT_CONTEXT=desktop-app
```

### Performance Tuning
```bash
# Fast keyword search (default)
export SYMMETRA_ENGINE_TYPE=keyword

# Intelligent semantic search
export SYMMETRA_ENGINE_TYPE=vector

# Limit results for speed
export SYMMETRA_MAX_RULES=5
```

## 🎨 Advanced Features

### Custom Rules
Create project-specific guidance:
```python
# Add to your project's rules
{
    "rule_id": "our-auth-pattern",
    "title": "Use Company SSO Integration", 
    "guidance": "🔐 Always integrate with our corporate SSO provider for authentication",
    "category": "security",
    "tech_stacks": ["python", "web"],
    "keywords": ["auth", "login", "sso"]
}
```

### Vector Search
For natural language queries:
```bash
# Setup vector capabilities
python scripts/setup_database.py --project-id your-project-id
python scripts/generate_embeddings_ollama.py --project-id your-project-id
```

### Project Context
Configure for your specific project:
```bash
export SYMMETRA_PROJECT_ID=https://github.com/yourteam/yourproject
export SYMMETRA_TECH_STACK=python,fastapi,postgresql
```

## 🐛 Quick Troubleshooting

### Symmetra tools not appearing?
```bash
# Restart Claude Code completely
# Check MCP configuration in ~/.claude/mcp.json
# Verify absolute paths in configuration
```

### "Module not found" errors?
```bash
# Check virtual environment
source .venv/bin/activate
pip list | grep symmetra

# Reinstall if needed
pip install -e .
```

### Slow responses?
```bash
# Use keyword engine for speed
export SYMMETRA_ENGINE_TYPE=keyword

# Reduce result count
export SYMMETRA_MAX_RULES=3
```

### Want more details?
- 📖 [Full Installation Guide](installation.md)
- 🎓 [Complete Usage Guide](usage.md)  
- 🔧 [Troubleshooting Guide](troubleshooting.md)

## 💡 Tips for Success

### 1. Be Specific in Requests
```bash
❌ "Help with security"
✅ "Get guidance for implementing JWT authentication with refresh tokens"
```

### 2. Provide Context
```bash
❌ "Optimize this function"
✅ "Optimize this database query function for a high-traffic API"
```

### 3. Use Search for Discovery
```bash
# Explore available guidance
"Search Symmetra rules for Python testing best practices"
"What categories of rules are available in Symmetra?"
```

### 4. Leverage Different Contexts
```bash
# Quick coding help
context="ide-assistant" → Concise, actionable advice

# Automated analysis  
context="agent" → Structured data for processing

# Learning session
context="desktop-app" → Detailed explanations
```

## 🎉 You're Ready!

Symmetra is now providing architectural guidance to your AI assistant. Start by asking for guidance on your current coding challenges and discover how Symmetra can improve your development workflow.

**Next Steps:**
1. Try the example queries above
2. Explore different rule categories
3. Add custom rules for your project
4. Share Symmetra with your team

**Happy coding with better architecture! 🚀**