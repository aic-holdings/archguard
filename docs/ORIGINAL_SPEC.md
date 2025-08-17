# ArchGuard MCP Server Specification

## Overview

The ArchGuard MCP server provides constitutional governance tools for AI agents through the Model Context Protocol. This document defines the server's capabilities, tools, and data models.

## MCP Tools Provided

### Core Governance Tools

#### `get_constitutional_rules`
Retrieve governance rules based on filters.

**Parameters:**
- `category` (optional): Rule category filter
- `priority` (optional): Rule priority filter  
- `active_only` (boolean, default: true): Only return active rules

**Returns:** Array of constitutional rules with metadata

#### `check_rule_compliance`
Record compliance check for a specific rule.

**Parameters:**
- `rule_slug` (required): Unique identifier for the rule
- `context` (optional): Description of current action/task
- `status` (required): Compliance status (acknowledged, compliant, violated, not_applicable)
- `notes` (optional): AI agent's assessment or reasoning

**Returns:** Compliance check record

#### `validate_action`
Validate a proposed action against all applicable constitutional rules.

**Parameters:**
- `action_description` (required): Description of proposed action
- `proposed_code` (optional): Code that will be written/modified
- `context` (optional): Additional context about the task

**Returns:** Validation results with violations, warnings, and recommendations

#### `record_violation`
Record when a constitutional rule is violated.

**Parameters:**
- `rule_slug` (required): Rule that was violated
- `description` (required): What was violated and how
- `violation_type` (required): intentional, unintentional, system_override
- `justification` (optional): Why violation was necessary
- `severity` (required): low, medium, high, critical

**Returns:** Violation record

### Session Management Tools

#### `start_constitution_session`
Begin a new governance session for tracking compliance.

**Parameters:**
- `task_description` (optional): What the AI is working on
- `goals` (optional): Session-specific goals
- `constraints` (optional): Session-specific constraints

**Returns:** Session metadata

#### `end_constitution_session`
End the current governance session.

**Parameters:**
- `status` (optional): Session completion status

**Returns:** Final session summary with compliance metrics

#### `get_session_compliance_score`
Get compliance score for current session.

**Returns:** Compliance score (0-100) and metrics

### Rule Management Tools

#### `get_applicable_rules`
Get rules that apply to a specific context or task type.

**Parameters:**
- `context` (required): Description of current context
- `task_type` (optional): Type of development task

**Returns:** Array of relevant constitutional rules

#### `search_rules`
Search constitutional rules by content.

**Parameters:**
- `query` (required): Search query
- `category` (optional): Limit search to specific category

**Returns:** Array of matching rules with relevance scores

### Reporting Tools

#### `get_compliance_history`
Retrieve compliance history for analysis.

**Parameters:**
- `agent_id` (optional): Filter by specific AI agent
- `date_range` (optional): Date range for history
- `rule_category` (optional): Filter by rule category

**Returns:** Compliance history data

#### `get_violation_summary`
Get summary of rule violations.

**Parameters:**
- `severity` (optional): Filter by violation severity
- `resolved_only` (boolean): Only show resolved violations

**Returns:** Violation summary with trends

## Data Models

### ConstitutionalRule
```json
{
  "id": "integer",
  "slug": "string (unique)",
  "title": "string",
  "category": "enum",
  "priority": "enum", 
  "description": "text",
  "rationale": "text",
  "examples": "text",
  "enforcement_logic": "text",
  "is_active": "boolean",
  "version": "integer",
  "created_by": "string",
  "tags": "array",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### ComplianceCheck
```json
{
  "id": "integer",
  "rule_id": "integer",
  "checked_by": "string",
  "session_id": "string",
  "status": "enum",
  "notes": "text",
  "context": "text",
  "metadata": "object",
  "created_at": "datetime"
}
```

### RuleViolation
```json
{
  "id": "integer",
  "rule_id": "integer", 
  "violated_by": "string",
  "session_id": "string",
  "violation_type": "string",
  "description": "text",
  "justification": "text",
  "severity": "string",
  "resolved": "boolean",
  "resolution_notes": "text",
  "resolved_at": "datetime",
  "created_at": "datetime"
}
```

### ConstitutionSession
```json
{
  "id": "integer",
  "session_id": "string (unique)",
  "agent_id": "string",
  "user_id": "string",
  "task_description": "text",
  "goals": "array",
  "constraints": "array", 
  "rules_checked": "integer",
  "compliance_score": "integer",
  "violations_count": "integer",
  "is_active": "boolean",
  "status": "string",
  "created_at": "datetime",
  "ended_at": "datetime"
}
```

## Configuration

### Database Connection
- **SQLite** (default): `sqlite:///archguard_constitution.db`
- **PostgreSQL**: Configurable via `ARCHGUARD_DATABASE_URL`

### Environment Variables
- `ARCHGUARD_DATABASE_URL`: Database connection string
- `ARCHGUARD_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ARCHGUARD_SESSION_TIMEOUT`: Session timeout in minutes (default: 60)

## Usage Patterns

### Basic Compliance Check
1. AI agent calls `start_constitution_session`
2. Before each significant action, calls `validate_action`
3. Records compliance with `check_rule_compliance`  
4. At end of work, calls `end_constitution_session`

### Rule Violation Handling
1. If `validate_action` shows violations, agent can:
   - Modify approach to comply
   - Record intentional violation with `record_violation`
   - Ask human for guidance

### Continuous Governance
1. Long-running sessions maintain constitutional context
2. Compliance scores track governance adherence over time
3. Violation patterns identify areas needing rule refinement

## Error Handling

### Common Error Responses
- `RULE_NOT_FOUND`: Referenced rule slug doesn't exist
- `SESSION_NOT_ACTIVE`: No active constitution session  
- `INVALID_PARAMETERS`: Required parameters missing or invalid
- `DATABASE_ERROR`: Governance database connection issues

### Fallback Behavior
- If governance server unavailable, AI agents continue with warnings
- Critical rule violations block actions even if server has issues
- Compliance data cached locally until server reconnection

## Security Considerations

- Governance database isolated from application data
- No sensitive application data stored in governance system
- Audit trail for all governance decisions and overrides
- Rule modifications require appropriate permissions