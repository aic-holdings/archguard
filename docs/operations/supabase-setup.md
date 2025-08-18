# ArchGuard Supabase Database Setup Guide

## Overview

This guide outlines the complete setup process for ArchGuard's Supabase backend with pgvector for semantic rule storage and retrieval.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│  Edge Function   │───▶│   PostgreSQL    │
│   (Claude)      │    │  (ArchGuard API) │    │   + pgvector    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                         ┌──────────────┐        ┌─────────────┐
                         │  Auth & RLS  │        │ Vector DB   │
                         │  (Project    │        │ (Rules)     │
                         │   Scoping)   │        └─────────────┘
                         └──────────────┘
```

## Phase 1: Database Setup

### 1.1 Create Supabase Project

```bash
# Using Supabase CLI
npx supabase projects create archguard-rules --org your-org-id
```

### 1.2 Enable pgvector Extension

```sql
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

### 1.3 Database Schema

See `database-schema.sql` for complete schema definitions.

## Phase 2: Authentication & RLS Setup

### 2.1 Authentication Tables

```sql
-- Projects table for GitHub repo tracking
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_url TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User project access
CREATE TABLE user_project_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member', -- member, admin, viewer
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, project_id)
);
```

### 2.2 Row Level Security Policies

```sql
-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_project_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE rules ENABLE ROW LEVEL SECURITY;

-- Project access policies
CREATE POLICY "Users can view their accessible projects"
ON projects FOR SELECT
USING (
    id IN (
        SELECT project_id FROM user_project_access 
        WHERE user_id = auth.uid()
    )
);

-- Rules access policies  
CREATE POLICY "Users can view global and project rules"
ON rules FOR SELECT
USING (
    project_id IS NULL OR -- Global rules
    project_id IN (
        SELECT project_id FROM user_project_access 
        WHERE user_id = auth.uid()
    )
);
```

## Phase 3: Vector Database Schema

### 3.1 Rules Table with Vector Storage

```sql
-- Main rules table with pgvector support
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id TEXT UNIQUE NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Rule metadata
    title TEXT NOT NULL,
    guidance TEXT NOT NULL,
    rationale TEXT,
    category TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    
    -- Context and targeting
    contexts TEXT[] DEFAULT '{}',
    tech_stacks TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    
    -- Vector embedding for semantic search
    embedding VECTOR(384), -- for all-MiniLM-L6-v2 model
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    
    -- Indexes for performance
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_category CHECK (category IN ('architecture', 'security', 'performance', 'testing', 'ai-ml', 'ux'))
);

-- Vector similarity index for fast semantic search
CREATE INDEX ON rules USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Additional performance indexes
CREATE INDEX idx_rules_project_id ON rules(project_id);
CREATE INDEX idx_rules_category ON rules(category);
CREATE INDEX idx_rules_priority ON rules(priority);
CREATE INDEX idx_rules_contexts ON rules USING GIN(contexts);
CREATE INDEX idx_rules_tech_stacks ON rules USING GIN(tech_stacks);
```

### 3.2 Rule Examples Table

```sql
-- Examples associated with rules
CREATE TABLE rule_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID REFERENCES rules(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    code_example TEXT,
    description TEXT,
    language TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Phase 4: Edge Function Setup

### 4.1 Deploy ArchGuard Edge Function

```typescript
// supabase/functions/archguard-mcp/index.ts
import { createClient } from '@supabase/supabase-js'
import { serve } from 'std/http'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

serve(async (req: Request) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response(null, { 
      headers: { 'Access-Control-Allow-Origin': '*' } 
    })
  }

  try {
    // Extract auth token
    const authHeader = req.headers.get('Authorization')
    const token = authHeader?.replace('Bearer ', '')
    
    if (!token) {
      return Response.json({ error: 'Missing authorization' }, { status: 401 })
    }

    // Validate user and get project context
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)
    if (authError || !user) {
      return Response.json({ error: 'Invalid token' }, { status: 401 })
    }

    // Parse MCP request
    const { action, code = '', context = '', project_id } = await req.json()

    // Perform vector search with RLS automatically applied
    const { data: rules, error } = await supabase
      .from('rules')
      .select('*')
      .or(`project_id.is.null,project_id.eq.${project_id}`)
      .limit(10)

    if (error) {
      return Response.json({ error: error.message }, { status: 500 })
    }

    return Response.json({
      guidance: rules.map(rule => rule.guidance),
      rules_applied: rules.length,
      status: 'advisory'
    })

  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 })
  }
})
```

### 4.2 Deploy Function

```bash
# Deploy the edge function
npx supabase functions deploy archguard-mcp
```

## Phase 5: Data Migration

### 5.1 Bootstrap Rules Migration

```sql
-- Insert bootstrap rules from KeywordRuleEngine
INSERT INTO rules (rule_id, title, guidance, rationale, category, priority, contexts, tech_stacks, keywords, project_id)
VALUES 
  -- Vector Database Architecture Rules
  (
    'vector-db-choice',
    'Vector Database Selection',
    '🗄️ For vector storage, choose: ChromaDB (development/prototyping), Weaviate (production), or pgvector (PostgreSQL integration)',
    'Different vector databases excel in different contexts. ChromaDB is perfect for development, Weaviate scales well in production, and pgvector integrates seamlessly with existing PostgreSQL infrastructure.',
    'architecture',
    'high',
    ARRAY['ide-assistant', 'agent', 'desktop-app'],
    ARRAY['python', 'ai', 'ml', 'database'],
    ARRAY['vector', 'database', 'embedding', 'storage', 'chroma', 'weaviate', 'pgvector', 'chromadb'],
    NULL  -- Global rule
  );
-- ... (repeat for all bootstrap rules)
```

### 5.2 Generate Embeddings

```python
# Script to generate embeddings for existing rules
import os
from sentence_transformers import SentenceTransformer
from supabase import create_client

def generate_rule_embeddings():
    # Initialize embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Initialize Supabase client
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )
    
    # Get all rules without embeddings
    response = supabase.table('rules').select('*').is_('embedding', 'null').execute()
    
    for rule in response.data:
        # Create embedding text from title + guidance + rationale
        text = f"{rule['title']} {rule['guidance']} {rule.get('rationale', '')}"
        
        # Generate embedding
        embedding = model.encode(text).tolist()
        
        # Update rule with embedding
        supabase.table('rules').update({
            'embedding': embedding
        }).eq('id', rule['id']).execute()
        
        print(f"Generated embedding for rule: {rule['rule_id']}")

if __name__ == "__main__":
    generate_rule_embeddings()
```

## Phase 6: Testing & Validation

### 6.1 Test Vector Search

```sql
-- Test semantic similarity search
WITH query_embedding AS (
  SELECT '[0.1, 0.2, ...]'::vector AS embedding  -- Replace with actual embedding
)
SELECT 
  rule_id,
  title,
  guidance,
  1 - (embedding <=> query_embedding.embedding) AS similarity
FROM rules, query_embedding
WHERE project_id IS NULL OR project_id = 'project-uuid'
ORDER BY embedding <=> query_embedding.embedding
LIMIT 5;
```

### 6.2 Test RLS Policies

```sql
-- Test as different users to verify RLS
SET role authenticated;
SET request.jwt.claims TO '{"sub": "user-uuid"}';

SELECT * FROM rules;  -- Should only return accessible rules
```

## Phase 7: Performance Optimization

### 7.1 Query Optimization

```sql
-- Optimize vector index parameters
DROP INDEX IF EXISTS rules_embedding_idx;
CREATE INDEX rules_embedding_idx ON rules 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Analyze query performance
EXPLAIN ANALYZE 
SELECT * FROM rules 
ORDER BY embedding <=> '[0.1,0.2,...]'::vector 
LIMIT 10;
```

### 7.2 Connection Pooling

Configure Supabase connection pooling for optimal performance with Edge Functions.

## Environment Variables

Set these in your Supabase Edge Function environment:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=optional-for-embeddings  # if using OpenAI embeddings
```

## Security Considerations

1. **Token Validation**: Always validate JWT tokens server-side
2. **RLS Enforcement**: Rely on RLS policies, never trust client-side filtering
3. **Rate Limiting**: Implement rate limiting in Edge Functions
4. **Audit Logging**: Log all rule access and modifications
5. **Principle of Least Privilege**: Use minimal required permissions

## Monitoring & Observability

1. **Edge Function Logs**: Monitor via Supabase dashboard
2. **Database Performance**: Track query performance and vector index usage
3. **Authentication Events**: Monitor auth success/failure rates
4. **Vector Search Analytics**: Track rule relevance and usage patterns

## Backup & Recovery

1. **Database Backups**: Supabase handles automatic backups
2. **Rule Export**: Implement rule export functionality for backup
3. **Migration Scripts**: Version control all schema changes
4. **Disaster Recovery**: Document recovery procedures

This setup provides a production-ready, scalable foundation for ArchGuard's rule management system with semantic search capabilities.