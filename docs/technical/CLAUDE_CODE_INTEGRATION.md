# Symmetra + Claude Code Integration Guide

This guide shows you how to integrate Symmetra with Claude Code for intelligent architectural guidance, following patterns similar to Serena's approach.

## 🎯 What Symmetra Provides

**Symmetra specializes in AI-powered architectural guidance**:

- **AI-First Analysis**: Uses intelligent reasoning rather than rigid rules for contextual guidance
- **Architectural Patterns**: Suggests appropriate design patterns and architectural decisions
- **Security Guidance**: Provides comprehensive security recommendations for any codebase
- **Code Review**: Generates structured architectural review prompts 
- **Context-Aware**: Understands project context to provide relevant guidance

## 🔄 Server Modes

Symmetra offers two modes to match different needs:

### Simple Mode (Recommended - Default)
- **AI-powered guidance** for architectural decisions
- **Essential security scanning** for hardcoded secrets
- **Focused and fast** - optimized for real-time use with Claude Code
- **Intelligent recommendations** based on context and best practices

### Complex Mode (Advanced Use)
- **Full detector suite** with comprehensive rule engines
- **Detailed static analysis** with complex pattern matching
- **Extensive coverage** of code quality metrics
- **More thorough but slower** analysis

## Installation

### Method 1: Direct Execution with uvx (Recommended - Serena Style)

No permanent installation needed! Run Symmetra directly:

```bash
# Run MCP server directly (for Claude Code)
uvx --from git+https://github.com/aic-holdings/symmetra symmetra server

# Or test other commands
uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help
uvx --from git+https://github.com/aic-holdings/symmetra symmetra init
```

### Method 2: Permanent Installation via uvx

```bash
# Install Symmetra globally
uvx install git+https://github.com/aic-holdings/symmetra.git

# Then use normally
symmetra --help
symmetra server
```

### Method 3: Install via pip

```bash
# Clone and install
git clone https://github.com/aic-holdings/symmetra.git
cd symmetra
pip install -e .
```

## Claude Code Configuration

### 1. Configure MCP Server

Add Symmetra to your Claude Code MCP servers configuration:

**Location**: Claude Code settings → MCP Servers

#### Option A: Direct uvx execution (Simple AI-first mode - Recommended)
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra", "server", "--mode", "simple"],
      "env": {
        "ARCHGUARD_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Option A-Alt: Complex mode (Full detectors - for advanced use)
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra", "server", "--mode", "complex"],
      "env": {
        "ARCHGUARD_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Option B: If you've installed Symmetra globally
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "symmetra",
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
    "symmetra-dev": {
      "command": "python",
      "args": ["-m", "symmetra.cli", "server"],
      "cwd": "/path/to/symmetra",
      "env": {
        "PYTHONPATH": "/path/to/symmetra/src",
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

Symmetra provides intelligent suggestions for:

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

Symmetra exposes several resources that Claude Code can access:

- `symmetra://rules` - Architectural rules and guidelines
- `symmetra://patterns` - Design pattern recommendations
- `symmetra://checklist` - Code review checklist

## Usage Examples

### Basic Architectural Guidance

In Claude Code, you can now ask questions like:

```
"Can you use Symmetra to analyze this function and suggest improvements?"

def complex_function(data, options, flags, mode):
    # Complex nested logic here
    pass
```

Claude Code will automatically use Symmetra's `get_guidance` tool to provide:
- Complexity analysis
- Refactoring suggestions
- Best practice recommendations
- Performance optimization tips

### Project-Level Analysis

```
"Use Symmetra to analyze the overall architecture of this project and suggest improvements."
```

Symmetra will examine:
- Project structure
- Module dependencies
- Design pattern usage
- Architectural consistency

### Security Review

```
"Have Symmetra review this code for security issues."

def authenticate_user(username, password):
    # Authentication logic
    pass
```

Symmetra provides:
- Security vulnerability detection
- Best practice recommendations
- Compliance guidance

## Configuration Options

### Environment Variables

Configure Symmetra behavior through environment variables:

```bash
# Logging level
ARCHGUARD_LOG_LEVEL=DEBUG

# Custom configuration file
ARCHGUARD_CONFIG_PATH=/path/to/config.toml

# Test mode (for development)
ARCHGUARD_TEST_MODE=true
```

### Project-Level Configuration

Create `.symmetra.toml` in your project root:

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

### Symmetra Not Available in Claude Code

1. **Check Installation**: Verify Symmetra is installed and accessible
   ```bash
   symmetra --version
   symmetra server --help
   ```

2. **Verify Configuration**: Ensure MCP server configuration is correct
   ```bash
   # Test server manually
   symmetra server
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
   symmetra server
   # Should start without errors
   ```

3. **Verify Python Path**: For development installations
   ```bash
   export PYTHONPATH=/path/to/symmetra/src
   python -m symmetra.cli server
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
# .symmetra.toml
[rules.custom]
"no-god-objects" = "Classes should not exceed 20 methods"
"single-responsibility" = "Each module should have one primary responsibility"
"dependency-inversion" = "High-level modules should not depend on low-level modules"
```

### Integration with CI/CD

Use Symmetra in continuous integration:

```yaml
# .github/workflows/symmetra.yml
name: Symmetra Analysis
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
    - name: Install Symmetra
      run: uvx --from git+https://github.com/aic-holdings/symmetra symmetra
    - name: Run Analysis
      run: symmetra check --output-format json > analysis.json
```

## Comparison with Serena

Symmetra provides similar semantic code analysis capabilities to Serena but focuses specifically on:

- **Architectural Guidance**: Deep understanding of software architecture patterns
- **Code Quality**: Comprehensive code quality analysis and suggestions
- **Security**: Built-in security best practices and vulnerability detection
- **Performance**: Performance optimization recommendations

While Serena is a broader coding agent toolkit, Symmetra specializes in architectural analysis and guidance, making it an excellent complement to Claude Code's development capabilities.

## Getting Help

- **Documentation**: [Symmetra Docs](https://github.com/aic-holdings/symmetra/docs)
- **Issues**: [GitHub Issues](https://github.com/aic-holdings/symmetra/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aic-holdings/symmetra/discussions)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to Symmetra's Claude Code integration capabilities.