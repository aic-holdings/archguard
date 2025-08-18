-- Create rules table with pgvector support
-- Core table for storing architectural guidance rules

CREATE TYPE rule_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE rule_category AS ENUM ('architecture', 'security', 'performance', 'testing', 'ai-ml', 'ux', 'devops', 'data');

CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id TEXT UNIQUE NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Rule content
    title TEXT NOT NULL,
    guidance TEXT NOT NULL,
    rationale TEXT,
    
    -- Classification
    category rule_category NOT NULL,
    priority rule_priority NOT NULL DEFAULT 'medium',
    
    -- Context targeting
    contexts TEXT[] DEFAULT '{}',
    tech_stacks TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    
    -- Vector embedding for semantic search (384 dimensions for all-MiniLM-L6-v2)
    embedding VECTOR(384),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Validation
    CONSTRAINT rule_id_format CHECK (rule_id ~ '^[a-z0-9-]+$'),
    CONSTRAINT contexts_not_empty CHECK (array_length(contexts, 1) > 0),
    CONSTRAINT title_not_empty CHECK (length(trim(title)) > 0),
    CONSTRAINT guidance_not_empty CHECK (length(trim(guidance)) > 0)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_rules_project_id ON rules(project_id);
CREATE INDEX IF NOT EXISTS idx_rules_category ON rules(category);
CREATE INDEX IF NOT EXISTS idx_rules_priority ON rules(priority);
CREATE INDEX IF NOT EXISTS idx_rules_rule_id ON rules(rule_id);

-- GIN indexes for array columns
CREATE INDEX IF NOT EXISTS idx_rules_contexts ON rules USING GIN(contexts);
CREATE INDEX IF NOT EXISTS idx_rules_tech_stacks ON rules USING GIN(tech_stacks);
CREATE INDEX IF NOT EXISTS idx_rules_keywords ON rules USING GIN(keywords);

-- Vector similarity index for semantic search
-- Using ivfflat with cosine distance for good performance
CREATE INDEX IF NOT EXISTS idx_rules_embedding 
ON rules USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Updated at trigger
CREATE TRIGGER update_rules_updated_at 
    BEFORE UPDATE ON rules 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();