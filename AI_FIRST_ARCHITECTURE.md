# ArchGuard AI-First Architecture

## Summary

We've successfully pivoted ArchGuard from a complex deterministic rule system to a simpler, AI-powered architectural guidance system. This aligns much better with our core goal: **getting Claude Code excellent architectural guidance**.

## What We Built

### 🎯 Simple AI-First Server (`simple_server.py`)
- **AI-powered guidance engine** that provides contextual architectural advice
- **Essential security scanning** for hardcoded secrets (focused, not comprehensive)
- **5 core MCP tools** optimized for Claude Code integration
- **Fast and focused** - optimized for real-time conversations

### 🧠 AI Guidance Engine (`ai_guidance.py`)
- **Context-aware recommendations** based on action, code, and project context
- **Pattern recognition** for common architectural scenarios (auth, APIs, databases, etc.)
- **Complexity assessment** to help prioritize work
- **Architectural pattern suggestions** for different use cases

### 🔍 Simple Secret Detection
- **Focused security scanning** for obvious issues like hardcoded API keys
- **Fast pattern matching** without complex AST parsing
- **Essential protection** without over-engineering

## Architecture Philosophy

### Before (Complex/Deterministic)
```
600+ lines of DetectionEngine
Complex AST parsing
Hardcoded thresholds and weights
Extensive rule systems
Multiple detector classes
```

### After (AI-First/Simple)
```
~300 lines total
AI-powered guidance
Simple pattern detection for secrets
Context-aware recommendations
Focused on Claude Code integration
```

## Benefits of AI-First Approach

1. **More Intelligent**: AI can provide nuanced, contextual guidance
2. **Faster Development**: Less complex code to maintain
3. **Better User Experience**: More natural, conversational guidance
4. **Future-Proof**: Can evolve with AI capabilities
5. **Focused**: Optimized for our core use case (Claude Code guidance)

## Server Modes

### Simple Mode (Default - Recommended)
```bash
archguard server --mode simple
```
- AI-powered architectural guidance
- Essential security scanning
- Fast and optimized for Claude Code
- 5 focused MCP tools

### Complex Mode (Legacy/Advanced)
```bash
archguard server --mode complex  
```
- Full detector suite
- Comprehensive static analysis
- More thorough but slower
- For users who need detailed analysis

## Claude Code Integration

### Recommended Configuration
```json
{
  "mcpServers": {
    "archguard": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/archguard", "archguard", "server", "--mode", "simple"],
      "env": {
        "ARCHGUARD_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## MCP Tools Available

1. **`get_guidance(action, code, context)`** - Main AI architectural analysis
2. **`scan_secrets(code)`** - Essential security scanning
3. **`search_rules(query)`** - Search architectural knowledge base
4. **`list_rule_categories()`** - View available guidance categories
5. **`get_archguard_help()`** - Usage instructions

## Test Results

✅ AI guidance system working  
✅ Secret detection working  
✅ MCP server tools registered  
✅ CLI integration ready  
✅ uvx installation compatible  

## Next Steps

1. **Test with Claude Code** - Configure MCP integration and test real conversations
2. **Gather Feedback** - See how the AI guidance works in practice
3. **Iterate** - Improve guidance based on actual usage
4. **Enhance AI Logic** - Add more sophisticated reasoning as needed

## Key Insight

**We validated your architectural instinct**: The complex deterministic approach was over-engineered for our goal. The AI-first approach is:
- Simpler to maintain
- More aligned with our end goal
- Better suited for Claude Code integration
- More flexible and extensible

This proves that sometimes the best architecture is the simplest one that achieves the goal effectively.

## Files Created/Modified

### New Files (AI-First)
- `src/archguard/ai_guidance.py` - AI guidance engine
- `src/archguard/simple_server.py` - Simple MCP server
- `test_simple_server.py` - Test suite

### Modified Files
- `src/archguard/cli.py` - Added --mode option
- `docs/technical/CLAUDE_CODE_INTEGRATION.md` - Updated for both modes

### Kept (Essential)
- Original complex server (as --mode complex option)
- Basic infrastructure and configuration
- Core MCP integration patterns

The pivot to AI-first architecture was the right call. It's simpler, more focused, and better aligned with our goal of providing excellent architectural guidance to Claude Code.