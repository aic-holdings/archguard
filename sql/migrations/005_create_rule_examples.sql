-- Create rule examples table
-- Stores code examples and implementation patterns for rules

CREATE TABLE IF NOT EXISTS rule_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    
    -- Example content
    title TEXT NOT NULL,
    description TEXT,
    code_example TEXT,
    language TEXT,
    
    -- Example type and context
    example_type TEXT DEFAULT 'good' CHECK (example_type IN ('good', 'bad', 'before', 'after')),
    tech_stack TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Validation
    CONSTRAINT title_not_empty CHECK (length(trim(title)) > 0)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_rule_examples_rule_id ON rule_examples(rule_id);
CREATE INDEX IF NOT EXISTS idx_rule_examples_language ON rule_examples(language);
CREATE INDEX IF NOT EXISTS idx_rule_examples_tech_stack ON rule_examples(tech_stack);
CREATE INDEX IF NOT EXISTS idx_rule_examples_type ON rule_examples(example_type);