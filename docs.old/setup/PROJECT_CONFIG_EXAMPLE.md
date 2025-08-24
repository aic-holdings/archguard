# Project-Based Configuration Guide

Symmetra now supports project-specific configuration through the `.symmetra.toml` file in your project root.

## Setup Steps

### 1. Configure Your Project

Edit the `.symmetra.toml` file in your project root:

```toml
# Symmetra Project Configuration
# This file defines architectural rules and settings for your project

[project]
name = "your-project-name"
# architecture_style = "clean_architecture"  # Options: clean_architecture, layered, microservices

[api]
# OpenAI API key for embeddings and analysis
openai_api_key = "sk-your-actual-openai-key-here"

# Optional: Custom Supabase database (leave commented to use shared database)
# supabase_url = "YOUR_CUSTOM_SUPABASE_URL"
# supabase_key = "YOUR_CUSTOM_SUPABASE_ANON_KEY"

[rules]
max_file_lines = 300
max_function_lines = 50
complexity_threshold = "medium"  # Options: low, medium, high
enforce_type_hints = true

[ignore]
paths = [
    "migrations/",
    "node_modules/",
    ".git/",
    "__pycache__/",
    "*.pyc"
]
```

### 2. Add Your OpenAI API Key

1. Get your API key from https://platform.openai.com/api-keys
2. Replace `"sk-your-actual-openai-key-here"` with your actual key
3. Save the file

### 3. Configuration Priority

Symmetra uses this priority order for configuration:
1. **Environment variables** (highest priority)
2. **Project config** (`.symmetra.toml` in your project)
3. **Global config** (`~/.config/symmetra/config.toml`)
4. **Default values** (lowest priority)

## Usage Examples

### Basic Usage (Shared Database)
Just add your OpenAI API key - you'll automatically use Symmetra's shared database with 1,000+ rules:

```toml
[api]
openai_api_key = "sk-your-key-here"
```

### Advanced Usage (Custom Database)
For teams who want their own rules database:

```toml
[api]
openai_api_key = "sk-your-key-here"
supabase_url = "https://your-project.supabase.co"
supabase_key = "your-supabase-anon-key"
```

### Environment Variable Override
You can still use environment variables to override project settings:

```bash
export OPENAI_API_KEY="sk-different-key"
export SYMMETRA_SUPABASE_URL="https://different-db.supabase.co"
```

## Benefits

✅ **Project-specific**: Each project can have its own configuration  
✅ **Version controlled**: Configuration travels with your code  
✅ **Flexible**: Mix project config with environment variables as needed  
✅ **Secure**: Keep sensitive keys in environment variables for production  

## Security Best Practices

- **Development**: Store API keys in `.symmetra.toml` for convenience
- **Production**: Use environment variables for API keys
- **Team sharing**: Add `.symmetra.toml` to `.gitignore` if it contains sensitive keys

```bash
# Add to .gitignore if your .symmetra.toml contains sensitive keys
echo ".symmetra.toml" >> .gitignore
```