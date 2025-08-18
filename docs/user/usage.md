# Symmetra Usage Guide

Complete guide to using Symmetra for architectural guidance in your development workflow.

## Quick Start

### Basic Usage with AI Assistant

Once Symmetra is installed and configured, you can start getting architectural guidance immediately:

```
👤 You: "I need to implement user authentication in my Python API"

🤖 AI: Let me get architectural guidance for that.

[AI calls Symmetra get_guidance tool]

🏗️ Symmetra provides:
- Use bcrypt for password hashing, never store plaintext
- Implement JWT tokens with short expiration times
- Add rate limiting for login endpoints
- Use environment variables for secret keys
```

### Searching for Specific Rules

```
👤 You: "What are the best practices for Python project structure?"

🤖 AI: Let me search Symmetra's rules for Python project guidance.

[AI calls search_rules tool]

🔍 Symmetra returns:
- python-project-structure: Use src/ layout with pyproject.toml
- python-dependency-management: Pin versions with ranges
- python-code-quality: Use black, ruff, mypy, pytest
```

## Core MCP Tools

### get_guidance()

**Purpose**: Get contextual architectural guidance for what you're building.

**When to use**:
- Planning a new feature
- Refactoring existing code
- Making architectural decisions
- Code reviews

**Examples**:

```python
# Through AI assistant:
"Get guidance for implementing a caching layer in my API"
"Help me design a microservices architecture"
"What's the best way to handle database migrations?"

# Direct MCP call:
get_guidance(
    action="implement Redis caching for user sessions",
    code="def get_user(user_id): return db.query(...)",
    context="REST API with high traffic requirements"
)
```

**Response format**:
```json
{
  "guidance": [
    "🔧 Use Redis with connection pooling for session storage",
    "⏱️ Set appropriate TTL based on session requirements",
    "🔄 Implement cache invalidation strategy"
  ],
  "status": "advisory",
  "complexity_score": "medium",
  "patterns": ["caching", "session-management"],
  "rules_applied": 3
}
```

### search_rules()

**Purpose**: Find specific rules by topic or keyword.

**When to use**:
- Exploring available guidance
- Learning about specific topics
- Finding rules for code reviews

**Examples**:

```python
# Search by technology
search_rules("python testing")
search_rules("database performance")
search_rules("security authentication")

# Search by pattern
search_rules("microservices")
search_rules("caching")
search_rules("error handling")
```

### list_rule_categories()

**Purpose**: Discover available rule categories.

**Response**:
```json
{
  "categories": [
    {"name": "architecture", "rule_count": 15},
    {"name": "security", "rule_count": 8},
    {"name": "performance", "rule_count": 12},
    {"name": "testing", "rule_count": 6}
  ]
}
```

## Context-Aware Guidance

Symmetra adapts its responses based on your context:

### IDE Assistant Mode
**Optimized for**: Quick, actionable advice during coding

```bash
export ARCHGUARD_DEFAULT_CONTEXT=ide-assistant
```

**Characteristics**:
- Concise guidance (1-3 points)
- Code-focused recommendations
- Fast response times
- Minimal explanations

**Example**:
```
Input: "Add error handling to this function"
Output: "🚨 Add try/catch with specific exception types, log errors with context"
```

### Agent Mode
**Optimized for**: Automated processing and detailed analysis

```bash
export ARCHGUARD_DEFAULT_CONTEXT=agent
```

**Characteristics**:
- Structured data format
- Detailed rationale
- Machine-readable patterns
- Comprehensive coverage

**Example**:
```json
{
  "guidance": ["Detailed architectural recommendations"],
  "rationale": "Why these recommendations matter",
  "patterns": ["error-handling", "logging", "monitoring"],
  "complexity_score": "high",
  "implementation_steps": ["Step 1", "Step 2", "Step 3"]
}
```

### Desktop App Mode
**Optimized for**: Learning and discussion

```bash
export ARCHGUARD_DEFAULT_CONTEXT=desktop-app
```

**Characteristics**:
- Educational explanations
- Examples and alternatives
- Conversational tone
- Background context

## Working with Embeddings

### Understanding Vector vs Keyword Search

#### Keyword Engine (Default)
- **Fast**: <50ms response time
- **Exact matches**: Finds rules with matching keywords
- **Good for**: Specific technical terms

```python
# Keyword search example
search_rules("pytest unit testing")
# Finds rules containing "pytest", "unit", or "testing"
```

#### Vector Engine (Semantic)
- **Intelligent**: <200ms response time
- **Semantic understanding**: Finds conceptually related rules
- **Good for**: Natural language queries

```python
# Vector search example
search_rules("how to test my code effectively")
# Finds testing-related rules even without exact keyword matches
```

### Creating New Embeddings

#### Method 1: Automatic (Recommended)
When you add new rules, embeddings are generated automatically:

```python
# Insert rule - embedding job created automatically
INSERT INTO rules (rule_id, title, guidance, ...) VALUES (...);

# Start worker to process jobs
python scripts/embedding_worker.py --project-id your-project-id
```

#### Method 2: Manual
For batch processing or custom workflows:

```python
# Generate embeddings for specific rules
python scripts/generate_embeddings_ollama.py \
  --project-id your-project-id \
  --model nomic-embed-text
```

### Monitoring Embedding Jobs

```bash
# Monitor job queue status
python scripts/embedding_worker.py \
  --project-id your-project-id \
  --monitor-only

# Output:
# 📊 Job Queue Status:
#    completed normal:   8 jobs (avg: 245ms)
#    pending   high:     2 jobs (avg: N/A)
#    processing normal:  1 jobs (avg: N/A)
```

## Creating Custom Rules

### Rule Structure

Every rule has these components:

```python
{
    "rule_id": "unique-identifier",
    "title": "Human-readable title",
    "guidance": "🔧 Actionable guidance with emoji",
    "rationale": "Why this guidance matters",
    "category": "architecture|security|performance|testing|ai-ml|ux|devops|data",
    "priority": "low|medium|high|critical",
    "contexts": ["ide-assistant", "agent", "desktop-app"],
    "tech_stacks": ["python", "javascript", "database"],
    "keywords": ["relevant", "search", "terms"]
}
```

### Adding Rules via Database

#### Option 1: Direct SQL
```sql
INSERT INTO rules (rule_id, title, guidance, rationale, category, priority, contexts, tech_stacks, keywords)
VALUES (
    'my-custom-rule',
    'Custom Architecture Pattern',
    '🏗️ Use this pattern for maximum awesomeness',
    'This pattern improves maintainability and reduces complexity',
    'architecture',
    'high',
    ARRAY['ide-assistant', 'agent'],
    ARRAY['python', 'web'],
    ARRAY['pattern', 'architecture', 'maintainability']
);
```

#### Option 2: Python Script
```python
from symmetra.rules_engine import create_rule_engine

engine = create_rule_engine("keyword")
engine.add_rule({
    "rule_id": "my-custom-rule",
    "title": "Custom Architecture Pattern",
    # ... rest of rule definition
})
```

### Best Practices for Rule Creation

#### 1. Clear, Actionable Guidance
```
❌ Bad: "Think about performance"
✅ Good: "🚀 Use connection pooling with max 10 connections for database access"
```

#### 2. Specific Context Targeting
```python
# Target specific contexts
"contexts": ["ide-assistant"]  # Quick coding advice
"contexts": ["agent"]          # Automated analysis
"contexts": ["desktop-app"]    # Learning/discussion
```

#### 3. Relevant Keywords
```python
# Include variations and synonyms
"keywords": ["database", "db", "persistence", "storage", "sql", "nosql"]
```

#### 4. Appropriate Priority
```python
"priority": "critical"  # Security vulnerabilities, data loss
"priority": "high"      # Architecture decisions, performance
"priority": "medium"    # Best practices, maintainability
"priority": "low"       # Style preferences, nice-to-haves
```

## Advanced Usage

### Project-Specific Configuration

Create `.symmetra.toml` in your project root:

```toml
[project]
name = "MyApp"
tech_stack = ["python", "fastapi", "postgresql"]
context = "ide-assistant"

[rules]
priorities = { security = "critical", performance = "high" }
disabled = ["legacy-pattern-rule"]

[guidance]
detail_level = "concise"
max_suggestions = 3

[custom_rules]
rules_path = "./custom-rules/"
auto_reload = true
```

### Environment-Specific Settings

```bash
# Development
export ARCHGUARD_ENGINE_TYPE=keyword
export ARCHGUARD_LOG_LEVEL=DEBUG
export ARCHGUARD_MAX_RULES=5

# Production
export ARCHGUARD_ENGINE_TYPE=vector
export ARCHGUARD_LOG_LEVEL=INFO
export ARCHGUARD_MAX_RULES=10
export ARCHGUARD_CACHE_TTL=3600
```

### Batch Operations

```python
# Bulk add rules
python scripts/bulk_import_rules.py --file rules.json

# Bulk generate embeddings
python scripts/generate_embeddings_ollama.py \
  --project-id your-project-id \
  --batch-size 50

# Export rules for backup
python scripts/export_rules.py --format json --output backup.json
```

## Integration Patterns

### Code Review Integration

```python
# Get guidance for code review
guidance = get_guidance(
    action="review this authentication implementation",
    code="""
    def login(username, password):
        user = User.find_by_username(username)
        if user and user.password == password:
            return generate_token(user)
        return None
    """,
    context="security review"
)
```

### CI/CD Pipeline Integration

```bash
# Add to your CI pipeline
- name: Architecture Review
  run: |
    python -m symmetra.cli review \
      --files "src/**/*.py" \
      --context agent \
      --format json \
      --output arch-review.json
```

### IDE Integration

```python
# VS Code extension integration
from symmetra.server import get_guidance

def on_file_save(file_content, file_path):
    guidance = get_guidance(
        action=f"review changes in {file_path}",
        code=file_content,
        context="ide-assistant"
    )
    show_suggestions(guidance)
```

## Performance Tuning

### Response Time Optimization

```bash
# Fast keyword search
export ARCHGUARD_ENGINE_TYPE=keyword
# ~25ms response time

# Semantic vector search with caching
export ARCHGUARD_ENGINE_TYPE=vector
export ARCHGUARD_CACHE_TTL=3600
# ~50ms with cache, ~200ms without
```

### Memory Usage Optimization

```bash
# Limit rule set size
export ARCHGUARD_MAX_RULES=10

# Use smaller embedding model
export ARCHGUARD_EMBEDDING_MODEL=all-minilm  # 384D instead of 768D
```

### Concurrent Processing

```bash
# Multiple embedding workers
python scripts/embedding_worker.py --worker-id worker-01 &
python scripts/embedding_worker.py --worker-id worker-02 &
python scripts/embedding_worker.py --worker-id worker-03 &
```

## Troubleshooting

### Common Issues

#### "No rules found"
```bash
# Check if rules are loaded
python -c "from symmetra.server import list_rule_categories; print(list_rule_categories())"

# Re-insert bootstrap rules
python scripts/generate_embeddings_ollama.py --insert-python-rules
```

#### "Embedding generation slow"
```bash
# Check Ollama service
curl -s http://localhost:11434/api/version

# Monitor embedding worker
python scripts/embedding_worker.py --monitor-only

# Use faster model
export ARCHGUARD_EMBEDDING_MODEL=all-minilm
```

#### "MCP connection failed"
```bash
# Test MCP server directly
python -m symmetra.server

# Check environment variables
env | grep ARCHGUARD

# Verify database connection
python -c "from mcp__supabase__execute_sql import execute_sql; print('✅ Connected')"
```

## Next Steps

- **Explore [Examples](examples/)** for real-world usage patterns
- **Read [API Reference](api/)** for detailed tool documentation
- **Check [Contributing Guide](../CONTRIBUTING.md)** to add your own rules
- **Join the community** to share feedback and improvements