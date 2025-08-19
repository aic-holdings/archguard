# Symmetra Configuration Guide

Symmetra supports layered configuration with multiple override levels for maximum flexibility.

## Configuration Hierarchy

1. **Global Defaults** (built-in)
2. **Environment Variables** (`.env` file or system)
3. **Project Configuration** (`.symmetra.toml`)
4. **Runtime Parameters** (CLI arguments)

Higher levels override lower levels.

## Environment Variables

### Core Configuration

```bash
# Rule Engine Type
SYMMETRA_ENGINE_TYPE=keyword  # Options: keyword, vector
SYMMETRA_DEFAULT_CONTEXT=ide-assistant  # Options: ide-assistant, agent, desktop-app

# Project Context
SYMMETRA_PROJECT_ID=https://github.com/username/repo
SYMMETRA_PROJECT_NAME=MyProject
```

### Supabase Integration

```bash
# Database Configuration
SYMMETRA_SUPABASE_URL=https://your-project.supabase.co
SYMMETRA_SUPABASE_KEY=your-anon-key
SYMMETRA_SUPABASE_PROJECT_ID=your-project-id

# Vector Search Configuration
SYMMETRA_EMBEDDING_MODEL=all-MiniLM-L6-v2  # Options: all-MiniLM-L6-v2, all-mpnet-base-v2
```

### Debug and Logging

```bash
# Development Configuration
SYMMETRA_DEBUG=false
SYMMETRA_LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
SYMMETRA_VERBOSE=false
```

### Advanced Options

```bash
# Performance Tuning
SYMMETRA_MAX_RULES=10
SYMMETRA_CACHE_TTL=3600
SYMMETRA_TIMEOUT=30

# Custom Endpoints
SYMMETRA_VECTOR_ENDPOINT=http://localhost:8000/embed
SYMMETRA_RULES_ENDPOINT=http://localhost:8001/rules
```

## Project Configuration (.symmetra.toml)

Create a `.symmetra.toml` file in your project root for project-specific settings:

```toml
[project]
name = "MyAwesomeProject"
description = "Next-generation web application"
tech_stack = ["python", "react", "postgresql"]
context = "ide-assistant"

[rules]
# Override default rule priorities
priorities = { security = "critical", performance = "high" }

# Custom rule categories for this project
categories = ["custom-auth", "api-design", "database"]

# Disable specific rules
disabled = ["sqlite-usage", "sync-database-calls"]

[guidance]
# Customize guidance verbosity
detail_level = "concise"  # Options: minimal, concise, detailed, verbose

# Context-specific overrides
[guidance.ide-assistant]
max_suggestions = 3
include_examples = false

[guidance.agent]
max_suggestions = 10
include_examples = true
include_rationale = true

[vector_search]
# Vector search configuration
enabled = true
similarity_threshold = 0.7
max_results = 5
embedding_model = "all-MiniLM-L6-v2"

[integrations]
# Third-party integrations
eslint_integration = true
prettier_integration = true
sonar_integration = false

[custom_rules]
# Path to custom rules directory
rules_path = "./symmetra-rules"
auto_reload = true
```

## MCP Client Configuration

### Claude Code Configuration

Add to your MCP configuration file (`.claude/mcp.json`):

```json
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra"],
      "env": {
        "SYMMETRA_ENGINE_TYPE": "vector",
        "SYMMETRA_PROJECT_ID": "https://github.com/username/repo",
        "SYMMETRA_SUPABASE_URL": "https://your-project.supabase.co",
        "SYMMETRA_SUPABASE_KEY": "your-anon-key"
      }
    }
  }
}
```

### Cursor Configuration

Add to your MCP configuration:

```json
{
  "mcp": {
    "servers": {
      "symmetra": {
        "command": "python",
        "args": ["-m", "symmetra.server"],
        "cwd": "/path/to/symmetra",
        "env": {
          "SYMMETRA_ENGINE_TYPE": "vector",
          "SYMMETRA_PROJECT_ID": "https://github.com/username/repo"
        }
      }
    }
  }
}
```

## Configuration Loading Order

Symmetra loads configuration in this order:

1. **Built-in defaults**
2. **System environment variables**
3. **`.env` file** (if present)
4. **`.symmetra.toml`** (if present)
5. **Runtime parameters** (--context, --project flags)

## Environment File Template

Create a `.env` file from the template:

```bash
# Copy the example and customize
cp .env.example .env

# Edit with your values
vim .env
```

Example `.env` content:

```bash
# Symmetra Configuration
SYMMETRA_ENGINE_TYPE=vector
SYMMETRA_DEFAULT_CONTEXT=ide-assistant

# Supabase Integration
SYMMETRA_SUPABASE_URL=https://kkvkwxfirmeywhvndjaa.supabase.co
SYMMETRA_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SYMMETRA_SUPABASE_PROJECT_ID=kkvkwxfirmeywhvndjaa

# Project Context
SYMMETRA_PROJECT_ID=https://github.com/aic-holdings/symmetra
SYMMETRA_PROJECT_NAME=Symmetra

# Vector Search
SYMMETRA_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Development
SYMMETRA_DEBUG=false
SYMMETRA_LOG_LEVEL=INFO
```

## Dynamic Configuration

Symmetra supports runtime configuration updates:

```python
from symmetra.config import update_config

# Update configuration at runtime
update_config({
    "max_rules": 15,
    "context": "agent",
    "detail_level": "verbose"
})
```

## Validation

Symmetra validates configuration on startup:

- **Required fields**: Ensures critical configuration is present
- **Type checking**: Validates data types and formats
- **Range validation**: Checks numeric ranges and enum values
- **Dependency validation**: Ensures related settings are compatible

## Troubleshooting

### Common Configuration Issues

1. **Missing Supabase credentials**
   ```bash
   Error: SYMMETRA_SUPABASE_URL not set
   Solution: Set environment variable or add to .env file
   ```

2. **Invalid engine type**
   ```bash
   Error: Unknown engine type: 'vectors'
   Solution: Use 'keyword' or 'vector'
   ```

3. **Project file not found**
   ```bash
   Warning: .symmetra.toml not found, using defaults
   Solution: Create .symmetra.toml or verify file path
   ```

### Debug Configuration

Enable debug mode to see configuration loading:

```bash
SYMMETRA_DEBUG=true python -m symmetra.server
```

This will show:
- Configuration sources loaded
- Final merged configuration
- Environment variable resolution
- File path resolution

## Best Practices

1. **Use .env for local development**
2. **Use .symmetra.toml for project-specific settings**
3. **Use environment variables for production deployment**
4. **Keep sensitive data in environment variables, not files**
5. **Version control .symmetra.toml, ignore .env**
6. **Document project-specific configuration in README**

## Security Considerations

- **Never commit `.env` files** to version control
- **Use environment variables** for sensitive data in production
- **Rotate Supabase keys** regularly
- **Use read-only database keys** when possible
- **Validate all external configuration** inputs