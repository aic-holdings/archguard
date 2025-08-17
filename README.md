# ArchGuard
> **Your AI-powered architectural co-pilot for maintaining clean, scalable codebases**

[![CI Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/aic-holdings/archguard/actions)
[![PyPI Version](https://img.shields.io/pypi/v/archguard.svg)](https://pypi.org/project/archguard/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/archguard.svg)](https://pypi.org/project/archguard/)

**ArchGuard is an extensible AI-powered toolkit that helps development teams define, verify, and maintain their software architecture through real-time guidance and automated analysis.**

Unlike traditional linters that focus on syntax, ArchGuard provides **semantic architectural guidance** that understands your codebase's structure, patterns, and design decisions, helping prevent architectural drift before it starts.

---

<!-- TODO: Add demo GIF or screenshot -->
<p align="center">
  <img src="docs/assets/archguard-demo.png" alt="ArchGuard providing real-time architectural guidance" width="600">
  <br>
  <em>ArchGuard integrated with Claude Code, providing real-time architectural guidance</em>
</p>

---

## ✨ Key Features

- **🏗️ Real-time Architectural Guidance**: Get instant feedback on architectural decisions as you code
- **🤖 AI-Native Integration**: Works seamlessly with AI coding assistants through Model Context Protocol (MCP)
- **📐 Configurable Rule Engine**: Define project-specific architectural patterns and constraints
- **🔄 Multi-Transport Support**: Stdio for local development, HTTP for production deployment
- **🎯 Advisory, Not Blocking**: Provides guidance without breaking your development flow
- **🌐 Framework Agnostic**: Works with any MCP-compatible AI system (Claude Code, Claude Desktop, etc.)

## 🚀 Quick Start

### Installation

**Option 1: Direct execution with uvx (Recommended)**
```bash
# Run without installation - perfect for trying ArchGuard
uvx --from git+https://github.com/aic-holdings/archguard archguard --help
```

**Option 2: Local development**
```bash
# Clone and install with uv
git clone https://github.com/aic-holdings/archguard
cd archguard
uv run archguard --help

# Or with pip
pip install -e .
archguard --help
```

**Option 3: Docker (Experimental)**
```bash
docker run --rm -i --network host \
  -v "$(pwd)":/workspace \
  ghcr.io/aic-holdings/archguard:latest \
  archguard check
```

### Integration with AI Coding Assistants

**Claude Code Integration**

Add to your Claude Code MCP settings (`~/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "archguard": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/aic-holdings/archguard",
        "archguard-server"
      ]
    }
  }
}
```

**Claude Desktop Integration**

Add to your Claude Desktop settings:

```json
{
  "mcpServers": {
    "archguard": {
      "command": "archguard-server"
    }
  }
}
```

### Basic Usage

Once integrated, ask your AI assistant:

- *"Should I create this 500-line component?"*
- *"Get guidance for implementing user authentication"*
- *"What are the architectural patterns I should follow for this API?"*
- *"Review this code for architectural anti-patterns"*

## 📋 Core Capabilities

### Architectural Guidance
ArchGuard provides intelligent recommendations for:

- **Component Size**: Suggests optimal file and component sizes
- **Separation of Concerns**: Identifies when logic should be split or refactored
- **Design Patterns**: Recommends appropriate architectural patterns
- **Security Practices**: Guides secure coding practices and authentication patterns
- **Database Design**: Suggests proper indexing, relationships, and data modeling
- **API Design**: Promotes consistent, well-documented API patterns

### Example Response
```json
{
  "guidance": [
    "🏗️ Consider breaking this 450-line component into smaller, focused modules",
    "🔒 Use secure authentication patterns with proper session management",
    "🔐 Never store passwords in plain text - use bcrypt or similar hashing",
    "📊 Add database indexes for frequently queried fields"
  ],
  "status": "advisory",
  "action": "create user authentication system",
  "complexity_score": "medium"
}
```

## 🔧 Commands & Usage

### Available Commands

```bash
# Start MCP server for AI integration
archguard server

# Start HTTP server for production deployment  
archguard http --host 0.0.0.0 --port 8080

# Initialize ArchGuard in a new project
archguard init

# Run architectural analysis on current project
archguard check

# Validate specific files or directories
archguard validate src/components/

# Show configuration
archguard config show
```

### Development Workflow

```bash
# Run tests before committing
pytest test/

# Check architectural compliance
archguard check

# Start development server
uv run archguard server

# Deploy to production
archguard http --port 8080
```

## ⚙️ Configuration

ArchGuard supports flexible, layered configuration:

### Global Configuration
`~/.config/archguard/config.toml`
```toml
[general]
default_complexity_threshold = "medium"
auto_format_suggestions = true

[rules]
max_file_lines = 300
max_function_lines = 50
enforce_type_hints = true
```

### Project Configuration
`.archguard.toml` (in project root)
```toml
[project]
name = "my-awesome-app"
architecture_style = "clean_architecture"

[rules]
max_file_lines = 500  # Override global setting
custom_patterns = [
    "no_god_objects",
    "single_responsibility"
]

[ignore]
paths = ["migrations/", "legacy/"]
```

## 🏗️ Architecture & Integration

### MCP Protocol Integration
ArchGuard implements the Model Context Protocol (MCP) specification:

- **Tools**: `get_guidance(action, code)` - Real-time architectural advice
- **Resources**: `archguard://rules` - Access to governance rules and patterns  
- **Prompts**: `review_code(code)` - Structured code review templates

### Transport Modes
- **Stdio** (default): Optimal for local development and AI assistant integration
- **HTTP**: Production-ready with horizontal scaling support

### Supported AI Platforms
- ✅ Claude Code
- ✅ Claude Desktop  
- ✅ Any MCP-compatible client
- 🔄 Planned: Direct OpenAI integration
- 🔄 Planned: Local LLM support (Ollama)

## 📚 Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Get up and running in 5 minutes
- **[Configuration Reference](docs/configuration.md)** - Complete configuration options
- **[Rule Development](docs/rules.md)** - Writing custom architectural rules
- **[API Reference](docs/api.md)** - MCP protocol implementation details
- **[Integration Guide](docs/integrations.md)** - Platform-specific setup instructions
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to ArchGuard

## 🎯 Design Philosophy

**🤝 Advisory, Not Blocking**: ArchGuard provides intelligent suggestions without breaking your development flow. AI agents receive guidance but developers maintain full control.

**🧠 AI-Native**: Built specifically for AI-powered development workflows, ensuring seamless integration with modern coding assistants.

**🔧 Extensible by Design**: Plugin architecture allows teams to customize rules and integrations for their specific needs.

**⚡ Performance First**: Designed for real-time feedback with minimal overhead in your development environment.

## 🚀 Roadmap

### v0.2 - Enhanced Intelligence
- [ ] Language Server Protocol (LSP) integration for semantic code understanding
- [ ] Advanced dependency analysis and visualization
- [ ] Custom rule development with Python plugins
- [ ] Integration with popular CI/CD platforms

### v0.3 - Team Collaboration  
- [ ] Team governance dashboards
- [ ] Architectural decision record (ADR) integration
- [ ] Slack/Discord notifications for violations
- [ ] Multi-repository governance

### v1.0 - Enterprise Ready
- [ ] Advanced security analysis
- [ ] Performance impact prediction
- [ ] Compliance reporting (SOC2, HIPAA, etc.)
- [ ] Enterprise SSO integration

## 🤝 Contributing

We welcome contributions! ArchGuard is built by developers, for developers.

- **🐛 Found a bug?** [Open an issue](https://github.com/aic-holdings/archguard/issues/new/choose)
- **💡 Have a feature idea?** [Start a discussion](https://github.com/aic-holdings/archguard/discussions)
- **📝 Want to contribute?** Check our [Contributing Guide](CONTRIBUTING.md)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/aic-holdings/archguard
cd archguard

# Install development dependencies
uv sync --dev

# Run tests
pytest

# Run the development server
uv run archguard server
```

## 🌟 Community & Support

- **📖 Documentation**: [archguard.dev](https://archguard.dev)
- **💬 Discussions**: [GitHub Discussions](https://github.com/aic-holdings/archguard/discussions)
- **🐛 Issues**: [GitHub Issues](https://github.com/aic-holdings/archguard/issues)
- **📧 Email**: support@archguard.dev

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built on the excellent [FastMCP](https://github.com/jlowin/fastmcp) framework
- Inspired by the architectural guidance principles of Clean Architecture and Domain-Driven Design
- Special thanks to the [Anthropic MCP](https://modelcontextprotocol.io/) team for the protocol specification

---

**ArchGuard v0** - Bringing architectural intelligence to AI-powered development.

*Built with ❤️ by developers who care about code quality and team productivity.*