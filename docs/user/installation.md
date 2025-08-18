# Symmetra Installation Guide

Complete installation guide for Symmetra MCP server with local embeddings.

## Prerequisites

### System Requirements
- **Python 3.8+** (3.11+ recommended)
- **Node.js 18+** (for Claude Code/Cursor integration)
- **4GB+ RAM** (8GB+ recommended for vector operations)
- **macOS, Linux, or Windows** (WSL2 for Windows)

### Required Software

#### 1. Ollama (for local embeddings)
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows (use WSL2 or download from https://ollama.com/download)
# After installation, start Ollama service
ollama serve
```

#### 2. Git
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Check installation
git --version
```

## Installation Methods

### Method 1: Direct Installation (Recommended)

#### Step 1: Clone Repository
```bash
git clone https://github.com/aic-holdings/symmetra.git
cd symmetra
```

#### Step 2: Install Dependencies
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install Symmetra
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

#### Step 3: Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
vim .env
```

### Method 2: uvx Installation (Quick Start)

#### For Claude Code Users
```bash
# Install directly from GitHub
uvx --from git+https://github.com/aic-holdings/symmetra symmetra --help

# Or add to Claude Code MCP config
```

Add to `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra"],
      "env": {
        "ARCHGUARD_ENGINE_TYPE": "keyword"
      }
    }
  }
}
```

## Database Setup

### Option 1: Use Existing Supabase Project

#### Step 1: Get Your Project Details
```bash
# If you have Supabase CLI
npx supabase projects list

# Note your project ID and URL
```

#### Step 2: Run Database Setup
```bash
# Setup database schema and bootstrap rules
python scripts/setup_database.py --project-id your-project-id

# This will:
# - Create all required tables
# - Enable pgvector extension
# - Insert bootstrap rules
# - Setup job queue system
```

### Option 2: Create New Supabase Project

#### Using Symmetra's MCP Integration
If you have Claude Code with Supabase MCP configured, Symmetra can create the project for you:

```bash
# Will prompt for organization and handle project creation
python scripts/setup_database.py --create-project
```

#### Manual Creation
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note the project ID and URL
4. Run setup script with your project ID

## Embedding System Setup

### Step 1: Install Ollama Model
```bash
# Setup Ollama with nomic-embed-text
python scripts/setup_ollama_embeddings.py

# This will:
# - Check Ollama installation
# - Pull nomic-embed-text model
# - Test embedding generation
# - Update configuration
```

### Step 2: Configure Environment
Edit `.env` file:
```bash
# Database Configuration
ARCHGUARD_SUPABASE_URL=https://your-project.supabase.co
ARCHGUARD_SUPABASE_KEY=your-anon-key
ARCHGUARD_SUPABASE_PROJECT_ID=your-project-id

# Embedding Configuration
ARCHGUARD_ENGINE_TYPE=vector
ARCHGUARD_EMBEDDING_PROVIDER=ollama
ARCHGUARD_EMBEDDING_MODEL=nomic-embed-text

# Optional: Project Context
ARCHGUARD_PROJECT_ID=https://github.com/username/repo
ARCHGUARD_DEFAULT_CONTEXT=ide-assistant
```

### Step 3: Generate Initial Embeddings
```bash
# Insert Python best practices rules and generate embeddings
python scripts/generate_embeddings_ollama.py \
  --project-id your-project-id \
  --insert-python-rules

# Start embedding worker for background processing
python scripts/embedding_worker.py --project-id your-project-id
```

## MCP Client Integration

### Claude Code Configuration

Add to `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "python",
      "args": ["-m", "symmetra.server"],
      "cwd": "/path/to/symmetra",
      "env": {
        "ARCHGUARD_ENGINE_TYPE": "vector",
        "ARCHGUARD_SUPABASE_URL": "https://your-project.supabase.co",
        "ARCHGUARD_SUPABASE_KEY": "your-anon-key",
        "ARCHGUARD_PROJECT_ID": "https://github.com/username/repo"
      }
    }
  }
}
```

### Cursor Configuration

Add to your Cursor MCP settings:
```json
{
  "mcp": {
    "servers": {
      "symmetra": {
        "command": "python",
        "args": ["-m", "symmetra.server"],
        "cwd": "/path/to/symmetra",
        "env": {
          "ARCHGUARD_ENGINE_TYPE": "vector"
        }
      }
    }
  }
}
```

### Alternative: uvx Configuration

For distribution without local installation:
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra"],
      "env": {
        "ARCHGUARD_ENGINE_TYPE": "keyword"
      }
    }
  }
}
```

## Verification

### Test Installation
```bash
# Test basic functionality
python -c "from symmetra.server import get_guidance; print('✅ Symmetra installed')"

# Test MCP tools
python -c "from symmetra.server import search_rules; print(search_rules('python'))"

# Test embedding system
python scripts/embedding_worker.py --project-id your-project-id --monitor-only
```

### Test with AI Assistant

Ask your AI assistant:
```
Can you get guidance for "implementing user authentication in Python"?
```

Expected response should include Symmetra architectural guidance.

## Common Installation Issues

### Ollama Service Not Running
```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/version

# If not running, start service
ollama serve

# Pull required model
ollama pull nomic-embed-text
```

### Permission Errors
```bash
# Fix Python package permissions
sudo chown -R $USER:$USER .venv/

# Fix script permissions
chmod +x scripts/*.py
```

### Database Connection Issues
```bash
# Test Supabase connection
python -c "
import os
from supabase import create_client
client = create_client(
    os.getenv('ARCHGUARD_SUPABASE_URL'),
    os.getenv('ARCHGUARD_SUPABASE_KEY')
)
print('✅ Database connection successful')
"
```

### MCP Integration Issues
```bash
# Test MCP server directly
python -m symmetra.server

# Check Claude Code logs
tail -f ~/.claude/logs/mcp.log

# Verify environment variables
env | grep ARCHGUARD
```

## Performance Optimization

### For Development
```bash
# Use keyword engine for faster startup
export ARCHGUARD_ENGINE_TYPE=keyword

# Reduce log verbosity
export ARCHGUARD_LOG_LEVEL=WARNING
```

### For Production
```bash
# Use vector engine with caching
export ARCHGUARD_ENGINE_TYPE=vector
export ARCHGUARD_CACHE_TTL=3600

# Run multiple embedding workers
python scripts/embedding_worker.py --project-id your-project-id --worker-id worker-01 &
python scripts/embedding_worker.py --project-id your-project-id --worker-id worker-02 &
```

## Next Steps

After installation:
1. **Read the [Usage Guide](usage.md)** - Learn how to use Symmetra effectively
2. **Check [Examples](examples/)** - See real-world usage patterns
3. **Add Custom Rules** - Extend Symmetra for your specific needs
4. **Join the Community** - Contribute rules and improvements

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/aic-holdings/symmetra/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aic-holdings/symmetra/discussions)
- **Documentation**: [docs/](https://github.com/aic-holdings/symmetra/tree/main/docs)

## Uninstallation

```bash
# Remove virtual environment
rm -rf .venv

# Remove configuration
rm .env

# Remove Ollama model (optional)
ollama rm nomic-embed-text

# Remove repository
cd .. && rm -rf symmetra
```