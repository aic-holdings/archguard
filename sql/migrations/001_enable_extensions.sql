-- Enable required PostgreSQL extensions
-- Run with: supabase db reset --with-data=false

-- Enable pgvector for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable additional helpful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text similarity