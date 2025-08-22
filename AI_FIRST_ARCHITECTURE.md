# Symmetra: Conversational Guidance Capture Architecture

## Summary

Symmetra has evolved into a **conversational guidance capture system** that enables developers to capture architectural patterns directly from their codebase through natural conversation with Claude Code. The core achievement is the ability to say *"This error handling pattern is clean - let's add it as guidance!"* and have it instantly searchable for future use.

## What We Built

### 🎯 Conversational Guidance Capture (`guidance_manager.py`)
- **Pattern capture through conversation** - capture architectural insights as you discover them
- **Intelligent refinement** - conversational prompts help improve guidance quality  
- **Vector-powered search** - instant retrieval of relevant patterns using OpenAI embeddings
- **Claude Code integration** - seamlessly capture patterns during development workflow

### 🧠 MCP Guidance Tools (`mcp_guidance_tool.py`)
- **Capture guidance** - turn discovered patterns into searchable knowledge
- **Refine guidance** - improve existing guidance through conversation
- **Context-aware categorization** - automatic organization by category and tech stack
- **Project-specific storage** - guidance tied to specific projects and contexts

### 🔍 Comprehensive Detection Suite (`detection_tools.py`)
- **Hybrid detection system** combining pattern matching, AST analysis, and contextual understanding
- **Security scanning** for hardcoded secrets, injection risks, and protocol issues
- **Code quality analysis** for maintainability, complexity, and architectural concerns
- **Multiple report formats** optimized for different use cases

## Architecture Philosophy

### The Problem We Solved
Traditional architectural guidance systems require developers to:
- Leave their coding context to search documentation
- Remember to document patterns after the fact
- Manually organize and categorize knowledge
- Hope teammates find relevant patterns when needed

### The Conversational Solution
```
Developer: "This error handling pattern is clean - let's add it as guidance!"
Symmetra: "I can see the pattern uses try/catch with structured logging. 
          What would you like to call this guidance?"
Developer: "Error handling with structured logging for API endpoints"
Symmetra: "Added! It's now searchable and will appear when teammates 
          ask about error handling patterns."
```

## Benefits of Conversational Capture

1. **Zero Context Switching**: Capture patterns without leaving your workflow
2. **Natural Language Interface**: Describe patterns in your own words
3. **Intelligent Organization**: Automatic categorization and tagging
4. **Instant Availability**: Patterns become searchable immediately
5. **Living Knowledge Base**: Grows organically as you discover patterns

## Core Components

### Guidance Management System
The heart of Symmetra's conversational capture:
- **Vector embeddings** for semantic search using OpenAI text-embedding-3-small
- **Supabase database** with pgvector extension for scalable storage
- **Smart categorization** with automatic tech stack and context detection
- **Project isolation** with per-project guidance collections

### MCP Integration
Seamless integration with Claude Code and other MCP clients:
- **Conversational tools** for natural pattern capture
- **Search tools** for instant pattern retrieval  
- **Detection tools** for comprehensive code analysis
- **Context-aware responses** based on current project and files

## Claude Code Integration

### Configuration
```json
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra", "server"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  }
}
```

### Project Configuration
Create `.symmetra.toml` in your project root:
```toml
[project]
name = "my-project"

[api]
openai_api_key = "sk-your-api-key-here"
```

## MCP Tools Available

### Guidance Tools
1. **`capture_guidance()`** - Conversational pattern capture from current context
2. **`refine_guidance()`** - Improve existing guidance through conversation
3. **`search_guidance()`** - Find relevant patterns using semantic search

### Detection Tools  
4. **`detect_issues()`** - Comprehensive code analysis with security and quality checks
5. **`analyze_code_context()`** - Extract and understand code structure and relationships
6. **`batch_analyze_issues()`** - Deep analysis with optional LLM enhancement

### Information Tools
7. **`get_guidance_info()`** - Learn about the guidance system
8. **`get_detection_info()`** - Understand detection capabilities

## Validation Results

✅ **Conversational capture working** - Successfully capture patterns through natural conversation  
✅ **Vector search operational** - Semantic search with OpenAI embeddings returning relevant results  
✅ **Database integration complete** - Supabase storage with pgvector extension functioning  
✅ **MCP tools registered** - All guidance and detection tools available in Claude Code  
✅ **CLI functionality validated** - Command-line interface for guidance management working  
✅ **Project isolation working** - Per-project guidance collections properly isolated  
✅ **Comprehensive testing passed** - All Symmetra functionality validated through test suite  

## Real-World Usage

### Typical Workflow
1. **Discover Pattern**: Working on code, notice clean implementation  
2. **Capture Instantly**: Say "This pattern is great - let's save it as guidance!"  
3. **Conversational Refinement**: Symmetra helps improve the guidance through questions  
4. **Instant Availability**: Pattern immediately searchable for future use  
5. **Team Benefits**: Teammates get guidance when working on similar problems  

### Example Patterns Captured
- ✅ **ORM Best Practices** - Complete Drizzle ORM guide for AI agents
- ✅ **Error Handling Patterns** - Structured logging and error boundaries  
- ✅ **Authentication Flows** - Supabase auth implementation patterns
- ✅ **API Design** - RESTful endpoint design with validation

## Architectural Achievement

**The Self-Improving Development Loop**: Symmetra creates a feedback loop where discovering good patterns immediately benefits the entire team:

```
Code → Discover Pattern → Capture Conversationally → Instant Search → Better Code
  ↑                                                                        ↓
  ←←←←←←←←←←←← Team Learning & Knowledge Sharing ←←←←←←←←←←←←←←←←←←←
```

This represents a fundamental shift from "document after the fact" to "capture in the moment" knowledge management.

## Files Implementing the Vision

### Core System
- **`src/symmetra/guidance_manager.py`** - Heart of conversational capture system
- **`src/symmetra/mcp_guidance_tool.py`** - MCP integration for Claude Code  
- **`src/symmetra/cloud_vector_search.py`** - Semantic search with embeddings
- **`src/symmetra/config.py`** - Flexible project configuration system

### Detection Suite  
- **`src/symmetra/tools/detection_tools.py`** - Comprehensive code analysis
- **`src/symmetra/tools/guidance_tools.py`** - Guidance search and management
- **`src/symmetra/server.py`** - Full MCP server with all capabilities

### Knowledge Base
- **`docs/guidance/drizzle-orm-for-ai-agents.md`** - Complete ORM guidance example
- **`.symmetra.toml`** - Project configuration for guidance context

The conversational guidance capture system represents a breakthrough in how development teams can build and maintain their architectural knowledge - making it as natural as having a conversation.