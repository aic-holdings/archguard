-- Create embedding job queue system
-- Manages embedding generation as background jobs with proper tracking

-- Job status and priority enums
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'retrying');
CREATE TYPE job_priority AS ENUM ('low', 'normal', 'high', 'urgent');

-- Main embedding jobs table
CREATE TABLE IF NOT EXISTS embedding_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    
    -- Job configuration
    status job_status NOT NULL DEFAULT 'pending',
    priority job_priority NOT NULL DEFAULT 'normal',
    embedding_model TEXT NOT NULL DEFAULT 'nomic-embed-text',
    
    -- Input data for embedding
    input_text TEXT NOT NULL,
    text_hash TEXT NOT NULL, -- For deduplication
    
    -- Processing tracking
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    
    -- Timing
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Results
    embedding_vector VECTOR(768), -- Store result here (nomic-embed-text dimensions)
    embedding_dimensions INTEGER,
    error_message TEXT,
    processing_time_ms INTEGER,
    
    -- Worker tracking
    worker_id TEXT,
    worker_version TEXT,
    
    -- Metadata
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT valid_attempts CHECK (attempts >= 0 AND attempts <= max_attempts),
    CONSTRAINT completed_jobs_have_embedding CHECK (
        (status = 'completed' AND embedding_vector IS NOT NULL) OR 
        (status != 'completed')
    ),
    CONSTRAINT text_hash_not_empty CHECK (length(trim(text_hash)) > 0),
    CONSTRAINT input_text_not_empty CHECK (length(trim(input_text)) > 0)
);

-- Performance indexes for job processing
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_status ON embedding_jobs(status);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_priority ON embedding_jobs(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_rule_id ON embedding_jobs(rule_id);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_text_hash ON embedding_jobs(text_hash);
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_created_at ON embedding_jobs(created_at);

-- Partial indexes for active jobs (better performance)
CREATE INDEX IF NOT EXISTS idx_embedding_jobs_pending ON embedding_jobs(priority, created_at) 
WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_embedding_jobs_processing ON embedding_jobs(started_at) 
WHERE status = 'processing';

CREATE INDEX IF NOT EXISTS idx_embedding_jobs_failed ON embedding_jobs(attempts, created_at)
WHERE status = 'failed';

-- Function to automatically create embedding jobs when rules are inserted
CREATE OR REPLACE FUNCTION create_embedding_job_for_rule()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create job if rule doesn't already have an embedding
    IF NEW.embedding IS NULL THEN
        INSERT INTO embedding_jobs (
            rule_id, 
            input_text, 
            text_hash, 
            priority,
            project_id,
            created_by
        ) VALUES (
            NEW.id,
            NEW.title || ' ' || NEW.guidance || ' ' || COALESCE(NEW.rationale, ''),
            md5(NEW.title || ' ' || NEW.guidance || ' ' || COALESCE(NEW.rationale, '')),
            CASE NEW.priority 
                WHEN 'critical' THEN 'urgent'::job_priority
                WHEN 'high' THEN 'high'::job_priority 
                ELSE 'normal'::job_priority
            END,
            NEW.project_id,
            NEW.created_by
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-create embedding jobs
CREATE TRIGGER create_embedding_job_trigger
    AFTER INSERT ON rules
    FOR EACH ROW
    EXECUTE FUNCTION create_embedding_job_for_rule();

-- Function to transfer completed embeddings to rules
CREATE OR REPLACE FUNCTION transfer_completed_embedding()
RETURNS TRIGGER AS $$
BEGIN
    -- When job completes successfully, update the rule
    IF NEW.status = 'completed' AND OLD.status != 'completed' AND NEW.embedding_vector IS NOT NULL THEN
        UPDATE rules 
        SET 
            embedding = NEW.embedding_vector,
            updated_at = NOW()
        WHERE id = NEW.rule_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-transfer embeddings
CREATE TRIGGER transfer_embedding_trigger
    AFTER UPDATE ON embedding_jobs
    FOR EACH ROW
    EXECUTE FUNCTION transfer_completed_embedding();

-- View for job queue monitoring
CREATE OR REPLACE VIEW embedding_job_queue_status AS
SELECT 
    status,
    priority,
    COUNT(*) as job_count,
    AVG(processing_time_ms) as avg_processing_time_ms,
    MIN(created_at) as oldest_job,
    MAX(created_at) as newest_job,
    COUNT(CASE WHEN attempts >= max_attempts THEN 1 END) as permanently_failed
FROM embedding_jobs
GROUP BY status, priority
ORDER BY 
    CASE priority 
        WHEN 'urgent' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'normal' THEN 3 
        WHEN 'low' THEN 4 
    END,
    CASE status 
        WHEN 'pending' THEN 1 
        WHEN 'processing' THEN 2 
        WHEN 'retrying' THEN 3 
        WHEN 'completed' THEN 4 
        WHEN 'failed' THEN 5 
    END;