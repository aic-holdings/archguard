# ArchGuard Query Processing Data Flow

This document shows the complete data flow when a user submits an architectural guidance query to ArchGuard.

## System Overview

ArchGuard uses AI-first architecture with vector search to provide team-specific architectural guidance. Instead of hardcoded rules, it retrieves relevant rules from a vector database and synthesizes them into contextual advice.

## Complete Data Flow Diagram

```mermaid
graph TD
    %% User Input
    User[👤 Developer] -->|"create user authentication system"| ClaudeCode[🤖 Claude Code]
    
    %% MCP Layer
    ClaudeCode -->|MCP Tool Call| MCPServer[📡 ArchGuard MCP Server<br/>simple_server.py]
    MCPServer -->|get_guidance()| GuidanceEngine[🧠 AI Guidance Engine<br/>ai_guidance.py]
    
    %% Decision Point
    GuidanceEngine -->|Check availability| VectorDecision{Vector Search<br/>Available?}
    
    %% Vector Search Path (Primary)
    VectorDecision -->|✅ Yes| VectorEngine[🔍 Vector Search Engine<br/>vector_search.py]
    VectorEngine -->|1. Generate embedding| EmbeddingModel[🎯 SentenceTransformer<br/>all-MiniLM-L6-v2]
    EmbeddingModel -->|"create auth" → [0.1, 0.8, ...]| VectorEngine
    
    VectorEngine -->|2. Query with embedding| SupabaseDB[(🗄️ Supabase Database<br/>pgvector)]
    SupabaseDB -->|3. Return similar rules| RuleResults[📋 Retrieved Rules<br/>• Auth Security Pattern<br/>• JWT Best Practices<br/>• Rate Limiting Design]
    
    %% AI Synthesis
    RuleResults -->|4. Synthesize guidance| AISynthesis[🎨 AI Synthesis<br/>Combine rules into<br/>coherent advice]
    
    %% Fallback Path
    VectorDecision -->|❌ No| HardcodedFallback[🔧 Hardcoded Analysis<br/>Pattern matching on keywords]
    
    %% Response Assembly
    AISynthesis -->|Vector guidance| ResponseBuilder[📦 Response Builder]
    HardcodedFallback -->|Fallback guidance| ResponseBuilder
    
    ResponseBuilder -->|5. Add metadata| ResponseData[📊 Enhanced Response<br/>• guidance: [rules + advice]<br/>• rules_applied: [rule names]<br/>• complexity_score: medium<br/>• patterns: [JWT, OAuth]<br/>• code_analysis: metadata]
    
    %% Return Path
    ResponseData -->|JSON response| MCPServer
    MCPServer -->|MCP response| ClaudeCode
    ClaudeCode -->|Formatted advice| User
    
    %% Database Details
    SupabaseDB --> GlobalRules[🌍 Global Rules<br/>Bootstrap architectural<br/>patterns and practices]
    SupabaseDB --> TeamRules[👥 Team-Specific Rules<br/>Project-filtered<br/>custom standards]
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef mcpClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef vectorClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef aiClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef dbClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef fallbackClass fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class User,ClaudeCode userClass
    class MCPServer,ResponseBuilder mcpClass
    class VectorEngine,EmbeddingModel,VectorDecision vectorClass
    class GuidanceEngine,AISynthesis aiClass
    class SupabaseDB,GlobalRules,TeamRules dbClass
    class HardcodedFallback fallbackClass
```

## Detailed Step-by-Step Flow

### 1. Query Initiation
```
User Request: "create user authentication system"
Context: "Building a Python FastAPI application that needs secure user authentication with JWT tokens"
```

### 2. MCP Tool Processing
- **simple_server.py** receives the MCP tool call
- Validates input parameters
- Calls `guidance_engine.get_guidance(action, code, context, project_id)`

### 3. Vector Search Decision
The AI Guidance Engine checks if vector search is available:
```python
if vector_search_engine.is_available():
    # Use vector search + AI synthesis
    guidance = self._get_vector_guidance(action, code, context, project_id)
else:
    # Fallback to hardcoded pattern matching
    guidance = self._analyze_action(action, code, context)
```

### 4. Vector Search Process (Primary Path)
If vector search is available:

#### 4a. Query Embedding
```python
# Generate embedding for: "create user authentication system Building a Python FastAPI..."
query_embedding = model.encode(query)  # Returns: [0.1, 0.8, -0.3, ...]
```

#### 4b. Database Query
```sql
SELECT rule_id, title, guidance, rationale, category, priority, embedding
FROM rules 
WHERE project_id IS NULL OR project_id = $project_id
AND embedding IS NOT NULL
```

#### 4c. Similarity Calculation
```python
# For each rule in database:
similarity = cosine_similarity(query_embedding, rule_embedding)
# Sort by similarity, return top 3-5 rules
```

#### 4d. Retrieved Rules Example
```json
[
  {
    "title": "JWT Security Implementation",
    "guidance": "Use RS256 for JWT signing, implement token rotation",
    "category": "security",
    "priority": "high",
    "similarity": 0.89
  },
  {
    "title": "Authentication Rate Limiting",
    "guidance": "Implement 5 attempts per minute per IP",
    "category": "security", 
    "priority": "high",
    "similarity": 0.84
  }
]
```

### 5. AI Synthesis
The system combines retrieved rules into coherent guidance:
```python
# Build structured response with:
# - Rule context ("Applying guidance from: JWT Security, Rate Limiting...")
# - Organized sections (Security Foundation, Token Management, etc.)
# - Specific actionable advice from each rule
# - Rationale explanations
```

### 6. Response Enhancement
```python
return GuidanceResponse(
    guidance=synthesized_guidance,           # List of structured advice
    status="advisory",                       # Never blocking
    action="create user authentication system",
    complexity_score="medium",               # Based on complexity indicators
    patterns=["JWT Token Pattern", "OAuth 2.0"],  # Suggested patterns
    rules_applied=["JWT Security", "Rate Limiting"],  # Which rules used
    code_analysis={                          # Metadata
        "lines_analyzed": 0,
        "context_provided": True,
        "rules_matched": 2
    }
)
```

### 7. Fallback Path
If vector search is unavailable, the system uses hardcoded pattern matching:
```python
if 'auth' in action.lower():
    guidance = [
        "🔐 Authentication System Architecture:",
        "• Use bcrypt or Argon2 for password hashing",
        "• Implement JWT with proper secret management",
        # ... more hardcoded advice
    ]
```

## Key Architectural Decisions

### Why Vector Search?
- **Team-Specific**: Each team can have custom rules that override defaults
- **Semantic**: Finds relevant rules even with different terminology
- **Scalable**: Can handle thousands of rules efficiently
- **Contextual**: Considers project context and constraints

### Why AI Synthesis?
- **Coherent**: Combines multiple rules into structured advice
- **Contextual**: Adapts guidance to specific situations
- **Comprehensive**: Provides both what to do and why

### Why Fallback System?
- **Reliability**: Always provides guidance even if vector search fails
- **Development**: Works during development without database setup
- **Graceful Degradation**: Maintains functionality under all conditions

## Performance Characteristics

- **Vector Search**: ~100-200ms for embedding + similarity search
- **AI Synthesis**: ~50-100ms for response generation
- **Total Response Time**: ~200-300ms (well under 500ms MVP target)
- **Database Load**: Minimal - only embedding comparisons, no complex joins

## Security & Access Control

- **Global Rules**: Available to all users (bootstrap patterns)
- **Team Rules**: Filtered by project_id using Supabase RLS
- **No User Data**: Only rule metadata stored, no sensitive information
- **Stateless**: Each request is independent, no session state