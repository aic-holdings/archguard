# Symmetra MCP Tools API Reference

Symmetra provides several MCP tools for architectural guidance and rule management. All tools return structured data optimized for AI consumption.

## Core Tools

### get_guidance()

**Purpose**: Get architectural guidance for code actions

**Parameters**:
- `action` (string, required): Description of what you're planning to do
- `code` (string, optional): Existing code to analyze  
- `context` (string, optional): Additional context about your project

**Returns**:
```json
{
  "guidance": ["🔧 Use async/await for database operations", "📊 Consider adding error handling"],
  "status": "advisory",
  "action": "create user authentication system",
  "complexity_score": "medium",
  "patterns": ["authentication", "security"],
  "rules_applied": 3
}
```

**Example Usage**:
```python
# Get guidance for implementing authentication
guidance = get_guidance(
    action="implement JWT authentication for API",
    code="def login(username, password):\n    # TODO: implement",
    context="REST API with PostgreSQL backend"
)
```

**Response Fields**:
- `guidance`: List of actionable recommendations
- `status`: Always "advisory" (never blocking)
- `action`: Echo of your original action
- `complexity_score`: Estimated complexity (low/medium/high)
- `patterns`: Suggested architectural patterns
- `rules_applied`: Number of rules that matched

### search_rules()

**Purpose**: Search for specific architectural rules

**Parameters**:
- `query` (string, required): Search terms
- `max_results` (integer, optional): Maximum results to return (default: 5)

**Returns**:
```json
{
  "rules": [
    {
      "rule_id": "database-connection-pooling",
      "title": "Database Connection Pooling",
      "guidance": "Use connection pooling for database access",
      "category": "performance",
      "priority": "high",
      "search_score": 0.95
    }
  ],
  "total_found": 12,
  "query": "database performance"
}
```

**Example Usage**:
```python
# Search for security-related rules
rules = search_rules(
    query="authentication security best practices",
    max_results=10
)
```

### list_rule_categories()

**Purpose**: Get available rule categories

**Parameters**: None

**Returns**:
```json
{
  "categories": [
    {
      "name": "architecture",
      "description": "System design and structure guidance",
      "rule_count": 15
    },
    {
      "name": "security", 
      "description": "Security best practices and vulnerability prevention",
      "rule_count": 8
    },
    {
      "name": "performance",
      "description": "Performance optimization recommendations", 
      "rule_count": 12
    }
  ]
}
```

**Example Usage**:
```python
# Get all available categories
categories = list_rule_categories()
for category in categories['categories']:
    print(f"{category['name']}: {category['rule_count']} rules")
```

## Advanced Tools

### get_symmetra_help()

**Purpose**: Get comprehensive help on using Symmetra effectively

**Parameters**: None

**Returns**:
```json
{
  "usage_guide": "Detailed instructions on using Symmetra",
  "best_practices": ["How to phrase requests", "Integration workflows"],
  "examples": ["Example interactions", "Common patterns"],
  "capabilities": ["What Symmetra can analyze", "Supported architectures"]
}
```

**Example Usage**:
```python
# Get help using Symmetra
help_info = get_symmetra_help()
print(help_info['usage_guide'])
```

## Context-Aware Behavior

Symmetra adapts its responses based on context:

### IDE Assistant Context
- **Concise, actionable guidance**
- **Fast response times** 
- **Code-focused recommendations**

```python
# Set context for IDE integration
guidance = get_guidance(
    action="refactor this component",
    code=component_code,
    context="ide-assistant"  # Triggers concise mode
)
```

### Agent Context  
- **Structured data for automation**
- **Detailed rationale**
- **Machine-readable patterns**

```python
# Set context for automated agents
guidance = get_guidance(
    action="analyze system architecture", 
    context="agent"  # Triggers detailed mode
)
```

### Desktop App Context
- **Explanatory guidance**
- **Educational context**
- **Conversational tone**

```python
# Set context for interactive discussions
guidance = get_guidance(
    action="design microservices architecture",
    context="desktop-app"  # Triggers explanatory mode
)
```

## Error Handling

All tools return structured error information:

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Action parameter is required",
    "details": {
      "parameter": "action",
      "expected": "string",
      "received": "null"
    }
  }
}
```

**Common Error Codes**:
- `INVALID_PARAMETER`: Missing or invalid parameter
- `RULE_ENGINE_ERROR`: Internal rule engine failure
- `DATABASE_ERROR`: Database connection or query error
- `RATE_LIMIT_EXCEEDED`: Too many requests

## Performance Characteristics

### Response Times
- **Keyword engine**: < 50ms typical
- **Vector engine**: < 200ms typical  
- **Database queries**: < 100ms typical

### Rate Limits
- **Default**: 100 requests per minute
- **Configurable**: Via `ARCHGUARD_RATE_LIMIT` environment variable

### Caching
- **Rule cache**: 1 hour TTL
- **Guidance cache**: 5 minutes TTL
- **Search cache**: 15 minutes TTL

## Integration Patterns

### Direct Integration
```python
from symmetra.server import get_guidance

# Direct function calls
result = get_guidance("implement caching layer")
```

### MCP Protocol Integration
```python
# Via MCP client
mcp_client.call_tool("get_guidance", {
    "action": "implement caching layer",
    "code": existing_code
})
```

### HTTP API Integration
```bash
# Via HTTP transport
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_guidance", "arguments": {"action": "implement caching layer"}}}'
```

## Rule Matching Algorithm

Symmetra uses different matching strategies based on engine type:

### Keyword Engine
1. **Tokenize** action and code into keywords
2. **Score** rules based on keyword overlap
3. **Boost** high-priority rules (1.5x multiplier)
4. **Filter** by context if specified
5. **Rank** by final relevance score

### Vector Engine  
1. **Embed** action + code using sentence transformers
2. **Search** vector database using cosine similarity
3. **Filter** by project and context
4. **Rank** by semantic similarity score
5. **Apply** priority boosting

## Extensibility

### Custom Tools
Add custom tools by extending the MCP server:

```python
@mcp.tool()
def custom_analysis(code: str) -> dict:
    """Custom architectural analysis"""
    return {"analysis": "custom logic here"}
```

### Custom Rule Engines
Implement the `RuleEngine` interface:

```python
class CustomRuleEngine(RuleEngine):
    def find_relevant_rules(self, action, code="", context=""):
        # Custom rule matching logic
        return rules
```

## Monitoring and Observability

### Built-in Metrics
- **Request latency** 
- **Rule match rates**
- **Error frequencies**
- **Cache hit ratios**

### Custom Metrics
```python
from symmetra.metrics import track_usage

@track_usage("custom_guidance")
def my_guidance_function():
    # Your custom logic
    pass
```

### Logging
```python
import logging

# Configure Symmetra logging
logging.getLogger('symmetra').setLevel(logging.DEBUG)
```