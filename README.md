# ArchGuard
> **Production-ready architectural patterns at the speed of thought**

[![CI Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/aic-holdings/archguard/actions)
[![PyPI Version](https://img.shields.io/pypi/v/archguard.svg)](https://pypi.org/project/archguard/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/archguard.svg)](https://pypi.org/project/archguard/)

**ArchGuard is your AI coding assistant's expert architectural consultant, providing instant access to battle-tested patterns, complete implementations, and security-first best practices.**

Instead of researching Stack Overflow and piecing together tutorials, your AI assistant gets **complete, production-ready solutions** with built-in security, error handling, and deployment guidance - accelerating development while reducing architectural risk.

---

<!-- TODO: Add demo GIF or screenshot -->
<p align="center">
  <img src="docs/assets/archguard-demo.png" alt="ArchGuard providing real-time architectural guidance" width="600">
  <br>
  <em>ArchGuard integrated with Claude Code, providing real-time architectural guidance</em>
</p>

---

## ✨ Key Features

- **🚀 Complete Implementations**: Get entire auth systems, CRUD patterns, and integrations - not just code snippets
- **🔒 Security-First**: Every pattern includes RLS policies, input validation, and vulnerability prevention
- **⚡ Instant Delivery**: Vector-powered search returns comprehensive solutions in milliseconds
- **🎯 Context-Aware**: Patterns adapt to your stack (Next.js, Supabase, Tailwind, ShadCN, etc.)
- **🤖 AI-Native Integration**: Seamless integration with Claude Code and other MCP-compatible assistants
- **📋 Project Checklists**: Step-by-step guidance for building complete applications from scratch

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

- *"Get guidance for implementing Supabase authentication"* → Complete Next.js SSR auth system
- *"Show me a ShadCN form with validation"* → Full react-hook-form + zod + error handling
- *"I need file upload with Supabase Storage"* → Drag-drop, resize, security policies included
- *"Help me build a documentation site"* → Step-by-step Nextra setup checklist
- *"Create a Stripe subscription flow"* → Payment processing with webhooks and edge cases

## 📋 What You Get

### Production-Ready Patterns
ArchGuard provides complete implementations for:

- **🔐 Authentication Systems**: Supabase Auth with SSR, email confirmation, RLS policies
- **📝 Form Handling**: ShadCN + react-hook-form + Zod validation with error states
- **📁 File Management**: Upload, resize, CDN delivery with security best practices
- **💳 Payment Processing**: Stripe integration with webhooks and subscription management
- **📊 Data Tables**: Server-side pagination, filtering, sorting with Supabase
- **✉️ Email Systems**: Transactional emails with templates and delivery tracking
- **🔄 Real-time Features**: Live chat, notifications with Supabase Realtime
- **📱 Image Optimization**: Next.js Image with WebP conversion and responsive sizing

### Example: Complete Auth Implementation
When you ask for "Supabase authentication guidance", you get:
- ✅ 2,700+ lines of production-ready code
- ✅ Server and client component setup
- ✅ Middleware for session management
- ✅ Email confirmation flow
- ✅ Protected route patterns
- ✅ RLS security policies
- ✅ Error handling and edge cases
- ✅ Testing examples and deployment checklist

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

## 🔗 Detailed Integration Guide

### Project Setup & Configuration

If you are mostly working with the same project, you can configure to always activate it at startup
by passing `--project <path_or_name>` to the ArchGuard server command in your client's MCP config.
This is especially useful for clients which configure MCP servers on a per-project basis, like Claude Code.

Otherwise, the recommended way is to just ask the LLM to activate a project by providing it an absolute path to, or,
in case the project was configured before, by its name. The default project name is the directory name.

* "Configure ArchGuard for the project /path/to/my_project"
* "Activate ArchGuard for my_project"

All projects that have been configured will be automatically added to your global ArchGuard config, and for each
project, the file `.archguard.toml` will be generated. You can adjust the latter, e.g., by changing the name
(which you refer to during activation) or other architectural rules. Make sure to not have two different projects with
the same name.

ℹ️ For larger projects, we recommend that you analyze your project to accelerate ArchGuard's guidance; otherwise the first
analysis may be slower. To do so, run this from the project directory (or pass the path to the project as an argument):

```shell
uvx --from git+https://github.com/aic-holdings/archguard archguard check
```

### Running the ArchGuard MCP Server

There are several ways to run the ArchGuard MCP server, depending on your setup:

**Option 1: Direct execution with uvx (Recommended)**
```shell
uvx --from git+https://github.com/aic-holdings/archguard archguard server
```

**Option 2: Local development with uv**
```shell
# From ArchGuard source directory
uv run archguard server
```

**Option 3: After installation**
```shell
# If you've installed ArchGuard globally
archguard server
```

**Option 4: Docker**
```shell
docker run --rm -i --network host \
  -v "$(pwd)":/workspace \
  ghcr.io/aic-holdings/archguard:latest \
  archguard server --transport stdio
```

### Claude Code

ArchGuard is a great way to make Claude Code both cheaper and more powerful with architectural guidance!

From your project directory, add ArchGuard with a command like this:

```shell
claude mcp add archguard -- <archguard-mcp-server> --context ide-assistant --project $(pwd)
```

where `<archguard-mcp-server>` is your way of [running the ArchGuard MCP server](#running-the-archguard-mcp-server).
For example, when using `uvx`, you would run:

```shell
claude mcp add archguard -- uvx --from git+https://github.com/aic-holdings/archguard archguard server --context ide-assistant --project $(pwd)
```

ℹ️ ArchGuard comes with architectural guidance instructions, and Claude needs to read them to properly use ArchGuard's tools.
  As of version `v1.0.52`, Claude Code reads the instructions of the MCP server, so this **is handled automatically**.
  If you are using an older version, or if Claude fails to read the instructions, you can ask it explicitly
  to "read ArchGuard's initial instructions" or access ArchGuard's guidance resources directly.
  Note that you may have to make Claude read the instructions when you start a new conversation and after any compacting operation to ensure Claude remains properly configured to use ArchGuard's tools.

### Other Terminal-Based Clients

There are many terminal-based coding assistants that support MCP servers, such as [Codex](https://github.com/openai/codex?tab=readme-ov-file#model-context-protocol-mcp),
[Gemini-CLI](https://github.com/google-gemini/gemini-cli), [Qwen3-Coder](https://github.com/QwenLM/Qwen3-Coder),
[rovodev](https://community.atlassian.com/forums/Rovo-for-Software-Teams-Beta/Introducing-Rovo-Dev-CLI-AI-Powered-Development-in-your-terminal/ba-p/3043623),
the [OpenHands CLI](https://docs.all-hands.dev/usage/how-to/cli-mode) and [opencode](https://github.com/sst/opencode).

They generally benefit from the architectural guidance tools provided by ArchGuard. You might want to customize some aspects of ArchGuard
by writing your own rules or configuration to adjust it to your workflow, to other MCP servers you are using, and to
the client's internal capabilities.

### Claude Desktop

For [Claude Desktop](https://claude.ai/download) (available for Windows and macOS), go to File / Settings / Developer / MCP Servers / Edit Config,
which will let you open the JSON file `claude_desktop_config.json`.
Add the `archguard` MCP server configuration, using a [run command](#running-the-archguard-mcp-server) depending on your setup.

* local installation:

   ```json
   {
       "mcpServers": {
           "archguard": {
               "command": "/abs/path/to/uv",
               "args": ["run", "--directory", "/abs/path/to/archguard", "archguard", "server"]
           }
       }
   }
   ```

* uvx:

   ```json
   {
       "mcpServers": {
           "archguard": {
               "command": "/abs/path/to/uvx",
               "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server"]
           }
       }
   }
   ```

* docker:

  ```json
   {
       "mcpServers": {
           "archguard": {
               "command": "docker",
               "args": ["run", "--rm", "-i", "--network", "host", "-v", "/path/to/your/projects:/workspaces/projects", "ghcr.io/aic-holdings/archguard:latest", "archguard", "server", "--transport", "stdio"]
           }
       }
   }
   ```

If you are using paths containing backslashes for paths on Windows
(note that you can also just use forward slashes), be sure to escape them correctly (`\\`).

That's it! Save the config and then restart Claude Desktop. You are ready for configuring your first project.

ℹ️ You can further customize the run command using additional arguments (see [command-line arguments](#command-line-arguments)).

Note: on Windows and macOS there are official Claude Desktop applications by Anthropic, for Linux there is an [open-source
community version](https://github.com/aaddrick/claude-desktop-debian).

⚠️ Be sure to fully quit the Claude Desktop application, as closing Claude will just minimize it to the system tray – at least on Windows.

⚠️ Some clients may leave behind zombie processes. You will have to find and terminate them manually then.
    With ArchGuard, you can activate the HTTP mode to prevent unnoted processes and also use the HTTP interface
    for monitoring ArchGuard status.

After restarting, you should see ArchGuard's tools in your chat interface (notice the small hammer icon).

For more information on MCP servers with Claude Desktop, see [the official quick start guide](https://modelcontextprotocol.io/quickstart/user).

### MCP Coding Clients (Cline, Roo-Code, Cursor, Windsurf, etc.)

Being an MCP Server, ArchGuard can be included in any MCP Client. The same configuration as above,
perhaps with small client-specific modifications, should work. Most of the popular
existing coding assistants (IDE extensions or VSCode-like IDEs) support connections
to MCP Servers. It is **recommended to use the `ide-assistant` context** for these integrations by adding `"--context", "ide-assistant"` to the `args` in your MCP client's configuration. Including ArchGuard generally boosts their performance
by providing them tools for architectural guidance and code quality analysis.

In this case, the billing for the usage continues to be controlled by the client of your choice
(unlike with the Claude Desktop client). But you may still want to use ArchGuard through such an approach,
e.g., for one of the following reasons:

1. You are already using a coding assistant (say Cline or Cursor) and just want to make it more architecturally aware.
2. You are on Linux and don't want to use the [community-created Claude Desktop](https://github.com/aaddrick/claude-desktop-debian).
3. You want tighter integration of ArchGuard into your IDE and don't mind paying for that.

### Command-Line Arguments

The ArchGuard MCP server supports several command-line arguments for customization:

```shell
archguard server [OPTIONS]

Options:
  --project PATH          Project path to activate automatically
  --context CONTEXT       Context mode (ide-assistant, terminal, etc.)
  --transport TRANSPORT   Transport mode (stdio, http)
  --port PORT            HTTP port (when using http transport)
  --log-level LEVEL      Logging level (DEBUG, INFO, WARNING, ERROR)
  --config PATH          Custom configuration file path
  --help                 Show this message and exit
```

**Examples:**
```shell
# Start with specific project
archguard server --project /path/to/my/project

# Start in IDE assistant mode
archguard server --context ide-assistant

# Start HTTP server on custom port
archguard server --transport http --port 8080

# Debug mode with verbose logging
archguard server --log-level DEBUG
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