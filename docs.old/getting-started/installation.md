# Installation

This guide covers all installation methods for Symmetra, from quick trials to production deployments.

## Prerequisites

Before installing Symmetra, ensure you have:

!!! info "System Requirements"
    - **Python**: 3.8 or higher
    - **OpenAI API Key**: For vector embeddings
    - **MCP Client**: Claude Code (recommended) or compatible AI assistant

## Installation Methods

=== "uvx (Recommended)"

    The fastest way to try Symmetra without system-wide installation:

    ```bash
    # Run directly (no installation required)
    uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help

    # Start MCP server
    uvx --from git+https://github.com/aic-holdings/symmetra symmetra server
    ```

    **Advantages:**
    - ✅ No installation required
    - ✅ Always uses latest version
    - ✅ Isolated environment
    - ✅ Perfect for testing

=== "pip install"

    Standard Python package installation:

    ```bash
    # Install from PyPI (when available)
    pip install symmetra

    # Or install from source
    pip install git+https://github.com/aic-holdings/symmetra.git

    # Verify installation
    symmetra --version
    ```

    **Advantages:**
    - ✅ System-wide availability
    - ✅ Standard Python workflow
    - ✅ Easy updates with pip

=== "Local Development"

    For development, customization, or offline use:

    ```bash
    # Clone repository
    git clone https://github.com/aic-holdings/symmetra.git
    cd symmetra

    # Install with uv (recommended)
    uv sync --dev
    uv run symmetra --help

    # Or install with pip
    pip install -e ".[dev]"
    symmetra --help
    ```

    **Advantages:**
    - ✅ Full source access
    - ✅ Development tools included
    - ✅ Easy customization
    - ✅ Latest features

=== "Docker"

    Containerized deployment (experimental):

    ```bash
    # Pull and run
    docker run --rm -i --network host \
      -v "$(pwd)":/workspace \
      -e OPENAI_API_KEY="your-key-here" \
      ghcr.io/aic-holdings/symmetra:latest \
      symmetra server

    # Build from source
    git clone https://github.com/aic-holdings/symmetra.git
    cd symmetra
    docker build -t symmetra .
    docker run --rm -p 8080:8080 symmetra symmetra server --transport http
    ```

    **Advantages:**
    - ✅ Isolated environment
    - ✅ Production ready
    - ✅ Easy scaling
    - ✅ Consistent deployment

## Verification

After installation, verify Symmetra is working correctly:

```bash
# Check version
symmetra --version

# Verify MCP server starts
symmetra server --help

# Test basic functionality
symmetra check --help
```

Expected output:
```
Symmetra v1.0.0
MCP server for conversational guidance capture
```

## Configuration Setup

### 1. API Keys

Create an environment file or set environment variables:

```bash title=".env"
# OpenAI API key for embeddings
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Custom Supabase instance
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 2. Project Configuration

Create a `.symmetra.toml` file in your project root:

```toml title=".symmetra.toml"
[project]
name = "my-project"
description = "Project description"

[api]
# OpenAI configuration
openai_api_key = "sk-your-key-here"

# Optional: Model settings
embedding_model = "text-embedding-3-small"
embedding_dimensions = 384

[rules]
# Code quality settings
max_file_lines = 500
max_function_lines = 50
complexity_threshold = "medium"

[ignore]
# Paths to ignore during analysis
paths = [
    "node_modules/",
    ".git/",
    "dist/",
    "build/"
]
```

### 3. Global Configuration

For system-wide settings, create:

```bash
# Linux/macOS
~/.config/symmetra/config.toml

# Windows
%APPDATA%\symmetra\config.toml
```

```toml title="config.toml"
[general]
default_complexity_threshold = "medium"
auto_format_suggestions = true
log_level = "INFO"

[api]
openai_api_key = "your-global-key"
request_timeout = 30
max_retries = 3

[database]
# Optional: Use custom database
# supabase_url = "https://your-instance.supabase.co"
# supabase_key = "your-key"
```

## MCP Client Integration

### Claude Code Setup

Add Symmetra to your Claude Code MCP configuration:

```json title="~/.config/claude-code/mcp_servers.json"
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/aic-holdings/symmetra",
        "symmetra", "server"
      ],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  }
}
```

For project-specific setup:
```bash
cd your-project
claude mcp add symmetra -- uvx --from git+https://github.com/aic-holdings/symmetra symmetra server --project $(pwd)
```

### Claude Desktop Setup

Add to your Claude Desktop configuration:

```json title="claude_desktop_config.json"
{
  "mcpServers": {
    "symmetra": {
      "command": "/path/to/uvx",
      "args": [
        "--from", "git+https://github.com/aic-holdings/symmetra",
        "symmetra", "server"
      ],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  }
}
```

## Troubleshooting Installation

### Common Issues

!!! bug "Python Version Issues"
    
    **Error**: `python: command not found` or version too old
    
    **Solutions**:
    ```bash
    # Check Python version
    python --version
    python3 --version
    
    # Install Python 3.8+ if needed
    # On macOS with Homebrew
    brew install python@3.11
    
    # On Ubuntu/Debian
    sudo apt update
    sudo apt install python3.11 python3.11-venv
    
    # Use specific Python version
    python3.11 -m pip install symmetra
    ```

!!! bug "pip Installation Failures"
    
    **Error**: Permission denied or package conflicts
    
    **Solutions**:
    ```bash
    # Use virtual environment
    python -m venv symmetra-env
    source symmetra-env/bin/activate  # Linux/macOS
    # symmetra-env\Scripts\activate    # Windows
    pip install symmetra
    
    # Or install with --user flag
    pip install --user symmetra
    
    # Update pip if outdated
    python -m pip install --upgrade pip
    ```

!!! bug "OpenAI API Issues"
    
    **Error**: Authentication or quota errors
    
    **Solutions**:
    - Verify API key is correct and active
    - Check OpenAI usage limits and billing
    - Test API key independently:
    ```bash
    curl https://api.openai.com/v1/models \
      -H "Authorization: Bearer $OPENAI_API_KEY"
    ```

!!! bug "MCP Connection Issues"
    
    **Error**: Claude Code can't connect to Symmetra
    
    **Solutions**:
    - Restart Claude Code after MCP configuration
    - Check MCP server logs:
    ```bash
    symmetra server --log-level DEBUG
    ```
    - Verify command path in MCP config
    - Test server manually:
    ```bash
    symmetra server --transport stdio
    ```

### Platform-Specific Notes

=== "macOS"

    ```bash
    # Install prerequisites
    brew install python@3.11 uv
    
    # Install Symmetra
    uv tool install --from git+https://github.com/aic-holdings/symmetra symmetra
    
    # Add to PATH if needed
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

=== "Linux"

    ```bash
    # Ubuntu/Debian
    sudo apt update
    sudo apt install python3.11 python3.11-venv python3-pip
    
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Install Symmetra
    pip install --user symmetra
    ```

=== "Windows"

    ```powershell
    # Install Python from python.org or Microsoft Store
    # Install uv
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # Install Symmetra
    pip install symmetra
    
    # Or use uvx
    uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help
    ```

## Advanced Installation

### Production Deployment

For production use, consider these additional steps:

```bash
# Install with production dependencies
pip install "symmetra[production]"

# Set up systemd service (Linux)
sudo tee /etc/systemd/system/symmetra.service << EOF
[Unit]
Description=Symmetra MCP Server
After=network.target

[Service]
Type=simple
User=symmetra
WorkingDirectory=/opt/symmetra
Environment=OPENAI_API_KEY=your-key
ExecStart=/opt/symmetra/bin/symmetra server --transport http --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable symmetra
sudo systemctl start symmetra
```

### Development Environment

Set up a complete development environment:

```bash
# Clone and setup
git clone https://github.com/aic-holdings/symmetra.git
cd symmetra

# Install development dependencies
uv sync --dev --all-extras

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Start development server
uv run symmetra server --log-level DEBUG
```

## Updating Symmetra

### Regular Updates

```bash
# uvx automatically uses latest version
uvx --from git+https://github.com/aic-holdings/symmetra symmetra --version

# pip updates
pip install --upgrade symmetra

# Development updates
cd symmetra
git pull origin main
uv sync
```

### Version Management

```bash
# Check current version
symmetra --version

# Install specific version
pip install symmetra==1.0.0

# Check for updates
pip list --outdated | grep symmetra
```

---

!!! success "Installation Complete"
    You're now ready to integrate Symmetra with your AI coding workflow! 
    
    **Next steps:**
    - [Quick Start Guide](quickstart.md) - Get up and running in 5 minutes
    - [Configuration](configuration.md) - Customize for your workflow
    - [Claude Code Integration](../integrations/claude-code.md) - Detailed setup guide