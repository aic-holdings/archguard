# ArchGuard + Claude Code Integration Guide

This guide shows you how to integrate ArchGuard with Claude Code for intelligent architectural guidance, following patterns similar to Serena's approach.

## 🎯 What ArchGuard Provides

Unlike Serena's semantic code retrieval, **ArchGuard specializes in architectural guidance**:

- **Architectural Patterns**: Suggests appropriate design patterns and architectural decisions
- **Security Guidance**: Provides comprehensive security recommendations for any codebase
- **Code Review**: Generates structured architectural review prompts 
- **Governance Rules**: Access to 40+ professional architectural standards
- **Context-Aware**: Understands project context to provide relevant guidance

## Installation

### Method 1: Direct Execution with uvx (Recommended - Serena Style)

No permanent installation needed! Run ArchGuard directly:

```bash
# Run MCP server directly (for Claude Code)
uvx --from git+https://github.com/aic-holdings/archguard archguard server

# Or test other commands
uvx --from git+https://github.com/aic-holdings/archguard archguard --help
uvx --from git+https://github.com/aic-holdings/archguard archguard init
```

### Method 2: Permanent Installation via uvx

```bash
# Install ArchGuard globally
uvx install git+https://github.com/aic-holdings/archguard.git

# Then use normally
archguard --help
archguard server
```

### Method 3: Install via pip

```bash
# Clone and install
git clone https://github.com/aic-holdings/archguard.git
cd archguard
pip install -e .
```

## Claude Code Configuration

### 1. Configure MCP Server

Add ArchGuard to your Claude Code MCP servers configuration:

**Location**: Claude Code settings → MCP Servers

#### Option A: Direct uvx execution (Serena style - Recommended)
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

#### Option B: If you've installed ArchGuard globally
```json
{
  "mcpServers": {
    "archguard": {
      "command": "archguard",
      "args": ["server"],
      "env": {
        "ARCHGUARD_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. Alternative Configuration (Development)

For development or custom installations:

```json
{
  "mcpServers": {
    "archguard-dev": {
      "command": "python",
      "args": ["-m", "archguard.cli", "server"],
      "cwd": "/path/to/archguard",
      "env": {
        "PYTHONPATH": "/path/to/archguard/src",
        "ARCHGUARD_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 3. Restart Claude Code

After configuration, restart Claude Code for the changes to take effect.

## Features Available in Claude Code

### 1. Architectural Guidance

ArchGuard provides intelligent suggestions for:

- **Code Architecture**: Best practices for structuring applications
- **Design Patterns**: Recommendations for appropriate design patterns
- **Refactoring**: Suggestions for improving existing code
- **Performance**: Optimization recommendations
- **Security**: Security best practices and vulnerability detection

### 2. Semantic Code Analysis

- **Complexity Analysis**: Identify overly complex functions and classes
- **Dependency Analysis**: Understand code dependencies and coupling
- **Pattern Recognition**: Detect common anti-patterns and code smells
- **Documentation Gaps**: Identify missing or outdated documentation

### 3. Interactive Resources

ArchGuard exposes several resources that Claude Code can access:

- `archguard://rules` - Architectural rules and guidelines
- `archguard://patterns` - Design pattern recommendations
- `archguard://checklist` - Code review checklist

## Usage Examples

### Basic Architectural Guidance

In Claude Code, you can now ask questions like:

```
"Can you use ArchGuard to analyze this function and suggest improvements?"

def complex_function(data, options, flags, mode):
    # Complex nested logic here
    pass
```

Claude Code will automatically use ArchGuard's `get_guidance` tool to provide:
- Complexity analysis
- Refactoring suggestions
- Best practice recommendations
- Performance optimization tips

### Project-Level Analysis

```
"Use ArchGuard to analyze the overall architecture of this project and suggest improvements."
```

ArchGuard will examine:
- Project structure
- Module dependencies
- Design pattern usage
- Architectural consistency

### Security Review

```
"Have ArchGuard review this code for security issues."

def authenticate_user(username, password):
    # Authentication logic
    pass
```

ArchGuard provides:
- Security vulnerability detection
- Best practice recommendations
- Compliance guidance

## Configuration Options

### Environment Variables

Configure ArchGuard behavior through environment variables:

```bash
# Logging level
ARCHGUARD_LOG_LEVEL=DEBUG

# Custom configuration file
ARCHGUARD_CONFIG_PATH=/path/to/config.toml

# Test mode (for development)
ARCHGUARD_TEST_MODE=true
```

### Project-Level Configuration

Create `.archguard.toml` in your project root:

```toml
[project]
name = "my-project"
type = "web-application"

[analysis]
max_complexity = 10
max_file_lines = 500

[patterns]
preferred_architecture = "microservices"
database_pattern = "repository"

[security]
scan_secrets = true
enforce_https = true
```

## Troubleshooting

### ArchGuard Not Available in Claude Code

1. **Check Installation**: Verify ArchGuard is installed and accessible
   ```bash
   archguard --version
   archguard server --help
   ```

2. **Verify Configuration**: Ensure MCP server configuration is correct
   ```bash
   # Test server manually
   archguard server
   ```

3. **Check Logs**: Enable debug logging to see detailed information
   ```json
   {
     "env": {
       "ARCHGUARD_LOG_LEVEL": "DEBUG"
     }
   }
   ```

### Server Startup Issues

1. **Check Dependencies**: Ensure all required packages are installed
   ```bash
   pip install fastmcp>=2.11.0 toml>=0.10.0
   ```

2. **Test Server Manually**:
   ```bash
   archguard server
   # Should start without errors
   ```

3. **Verify Python Path**: For development installations
   ```bash
   export PYTHONPATH=/path/to/archguard/src
   python -m archguard.cli server
   ```

### Performance Issues

1. **Adjust Timeout Settings**: For large codebases
   ```json
   {
     "env": {
       "ARCHGUARD_TIMEOUT": "30"
     }
   }
   ```

2. **Enable Caching**: For repeated analysis
   ```toml
   [performance]
   enable_cache = true
   cache_duration = 3600
   ```

## Advanced Usage

### Custom Analysis Rules

Create custom architectural rules:

```toml
# .archguard.toml
[rules.custom]
"no-god-objects" = "Classes should not exceed 20 methods"
"single-responsibility" = "Each module should have one primary responsibility"
"dependency-inversion" = "High-level modules should not depend on low-level modules"
```

### Integration with CI/CD

Use ArchGuard in continuous integration:

```yaml
# .github/workflows/archguard.yml
name: ArchGuard Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install ArchGuard
      run: uvx install git+https://github.com/dshanklinbv/archguard.git
    - name: Run Analysis
      run: archguard check --output-format json > analysis.json
```

## Comparison with Serena

ArchGuard provides similar semantic code analysis capabilities to Serena but focuses specifically on:

- **Architectural Guidance**: Deep understanding of software architecture patterns
- **Code Quality**: Comprehensive code quality analysis and suggestions
- **Security**: Built-in security best practices and vulnerability detection
- **Performance**: Performance optimization recommendations

While Serena is a broader coding agent toolkit, ArchGuard specializes in architectural analysis and guidance, making it an excellent complement to Claude Code's development capabilities.

## Getting Help

- **Documentation**: [ArchGuard Docs](https://github.com/dshanklinbv/archguard/docs)
- **Issues**: [GitHub Issues](https://github.com/dshanklinbv/archguard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dshanklinbv/archguard/discussions)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to ArchGuard's Claude Code integration capabilities.