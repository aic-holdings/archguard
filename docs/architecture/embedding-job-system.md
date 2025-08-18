# Embedding Job Queue System Architecture

## Overview

A robust system for managing embedding generation at scale with proper job tracking, retry logic, and status monitoring.

## System Design

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Rule Input    │───▶│  Embedding Jobs  │───▶│ Embedding Worker│
│   (Raw Data)    │    │   (Job Queue)    │    │   (Processor)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Job Status      │    │  Vector Storage │
                       │  Tracking        │    │  (pgvector)     │
                       └──────────────────┘    └─────────────────┘
```

## Database Schema

### embedding_jobs Table

```sql
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'retrying');
CREATE TYPE job_priority AS ENUM ('low', 'normal', 'high', 'urgent');

CREATE TABLE embedding_jobs (
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
    embedding_vector VECTOR(768), -- Store result here
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
    )
);

-- Indexes for job processing
CREATE INDEX idx_embedding_jobs_status ON embedding_jobs(status);
CREATE INDEX idx_embedding_jobs_priority ON embedding_jobs(priority, created_at);
CREATE INDEX idx_embedding_jobs_rule_id ON embedding_jobs(rule_id);
CREATE INDEX idx_embedding_jobs_text_hash ON embedding_jobs(text_hash);
CREATE INDEX idx_embedding_jobs_created_at ON embedding_jobs(created_at);

-- Partial indexes for active jobs
CREATE INDEX idx_embedding_jobs_pending ON embedding_jobs(priority, created_at) 
WHERE status = 'pending';

CREATE INDEX idx_embedding_jobs_processing ON embedding_jobs(started_at) 
WHERE status = 'processing';
```

## Job Lifecycle

### 1. Job Creation Phase
```sql
-- Insert rule without embedding, create job automatically
INSERT INTO rules (rule_id, title, guidance, ...) VALUES (...);

-- Trigger creates embedding job
INSERT INTO embedding_jobs (rule_id, input_text, text_hash, priority)
SELECT 
    NEW.id,
    NEW.title || ' ' || NEW.guidance || ' ' || COALESCE(NEW.rationale, ''),
    md5(NEW.title || ' ' || NEW.guidance || ' ' || COALESCE(NEW.rationale, '')),
    CASE NEW.priority 
        WHEN 'critical' THEN 'urgent'::job_priority
        WHEN 'high' THEN 'high'::job_priority 
        ELSE 'normal'::job_priority
    END;
```

### 2. Job Processing Phase
```sql
-- Worker picks up next job
WITH next_job AS (
    SELECT id FROM embedding_jobs 
    WHERE status = 'pending'
    ORDER BY priority DESC, created_at ASC
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE embedding_jobs 
SET 
    status = 'processing',
    started_at = NOW(),
    worker_id = $1,
    attempts = attempts + 1
WHERE id = (SELECT id FROM next_job)
RETURNING *;
```

### 3. Job Completion Phase
```sql
-- Success: Update job and rule
UPDATE embedding_jobs 
SET 
    status = 'completed',
    completed_at = NOW(),
    embedding_vector = $2,
    embedding_dimensions = $3,
    processing_time_ms = $4
WHERE id = $1;

-- Transfer embedding to rule
UPDATE rules 
SET embedding = (SELECT embedding_vector FROM embedding_jobs WHERE rule_id = rules.id AND status = 'completed')
WHERE id = (SELECT rule_id FROM embedding_jobs WHERE id = $1);
```

## Job Processing Logic

### Job Priorities
- **urgent**: Critical rules, business priority
- **high**: Important architecture rules  
- **normal**: Standard rules
- **low**: Background/batch processing

### Retry Logic
```python
def should_retry(job):
    if job.attempts >= job.max_attempts:
        return False
    
    # Exponential backoff
    wait_time = min(300, 2 ** job.attempts * 30)  # Max 5 minutes
    return (datetime.now() - job.started_at).seconds > wait_time

def handle_failure(job, error):
    if should_retry(job):
        job.status = 'retrying'
        job.error_message = str(error)
    else:
        job.status = 'failed'
        job.error_message = f"Max attempts exceeded: {error}"
```

### Deduplication
```sql
-- Check if embedding already exists for this text
SELECT id, embedding_vector FROM embedding_jobs 
WHERE text_hash = $1 AND status = 'completed'
LIMIT 1;

-- If found, reuse embedding instead of creating new job
```

## Worker Implementation

### Basic Worker Loop
```python
class EmbeddingWorker:
    def __init__(self, worker_id: str, model: str = "nomic-embed-text"):
        self.worker_id = worker_id
        self.model = model
        self.ollama_client = OllamaClient()
    
    async def process_jobs(self):
        while True:
            job = await self.get_next_job()
            if job:
                await self.process_job(job)
            else:
                await asyncio.sleep(5)  # Poll interval
    
    async def get_next_job(self):
        # Get next pending job with FOR UPDATE SKIP LOCKED
        pass
    
    async def process_job(self, job):
        try:
            # Generate embedding
            embedding = await self.generate_embedding(job.input_text)
            
            # Mark completed
            await self.complete_job(job, embedding)
            
        except Exception as e:
            await self.fail_job(job, e)
```

## Monitoring and Observability

### Job Status Dashboard
```sql
-- Job queue health metrics
SELECT 
    status,
    priority,
    COUNT(*) as count,
    AVG(processing_time_ms) as avg_time_ms,
    MAX(created_at) as newest,
    MIN(created_at) as oldest
FROM embedding_jobs
GROUP BY status, priority
ORDER BY priority DESC, status;
```

### Performance Metrics
```sql
-- Worker performance
SELECT 
    worker_id,
    COUNT(*) as jobs_completed,
    AVG(processing_time_ms) as avg_time,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failures
FROM embedding_jobs
WHERE completed_at > NOW() - INTERVAL '24 hours'
GROUP BY worker_id;
```

## Scaling Considerations

### Horizontal Scaling
- Multiple workers can process jobs concurrently
- `FOR UPDATE SKIP LOCKED` prevents job conflicts
- Worker registration and health checking

### Batch Processing
```sql
-- Process multiple jobs in batch for efficiency
SELECT id, input_text FROM embedding_jobs 
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC
LIMIT 50;
```

### Dead Letter Queue
```sql
-- Move permanently failed jobs to analysis table
CREATE TABLE embedding_job_failures AS 
SELECT * FROM embedding_jobs WHERE status = 'failed';
```

## API Endpoints

### Job Management
- `POST /jobs/embedding` - Create embedding job
- `GET /jobs/embedding/{id}` - Get job status
- `GET /jobs/embedding?status=pending` - List jobs by status
- `DELETE /jobs/embedding/{id}` - Cancel job

### Worker Management  
- `POST /workers/register` - Register worker
- `POST /workers/{id}/heartbeat` - Worker health check
- `GET /workers` - List active workers

## Benefits of This System

1. **Scalability**: Can process thousands of embeddings efficiently
2. **Reliability**: Retry logic and error handling
3. **Monitoring**: Full visibility into job processing
4. **Flexibility**: Different priorities and models
5. **Consistency**: Atomic operations and proper state management
6. **Cost Control**: Batch processing and deduplication
7. **Observability**: Comprehensive metrics and logging