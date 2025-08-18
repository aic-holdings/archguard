-- Create user project access control
-- Manages which users can access which projects

CREATE TYPE user_role AS ENUM ('viewer', 'member', 'admin', 'owner');

CREATE TABLE IF NOT EXISTS user_project_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role user_role NOT NULL DEFAULT 'member',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Ensure unique user-project combinations
    UNIQUE(user_id, project_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_user_project_access_user_id ON user_project_access(user_id);
CREATE INDEX IF NOT EXISTS idx_user_project_access_project_id ON user_project_access(project_id);
CREATE INDEX IF NOT EXISTS idx_user_project_access_role ON user_project_access(role);