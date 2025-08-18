-- Create projects table for GitHub repository tracking
-- This enables project-scoped rules with hierarchy (project > global)

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_url TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT github_url_format CHECK (github_url ~ '^https://github\.com/[^/]+/[^/]+/?$')
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_projects_github_url ON projects(github_url);
CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by);

-- Updated at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();