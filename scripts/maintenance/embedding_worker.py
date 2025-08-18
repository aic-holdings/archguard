#!/usr/bin/env python3
"""
ArchGuard Embedding Worker

Processes embedding jobs from the job queue using Ollama.
Designed for scalable, reliable embedding generation.

Usage:
    python scripts/embedding_worker.py --project-id your-project-id
    python scripts/embedding_worker.py --project-id your-project-id --worker-id worker-01 --model nomic-embed-text
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingJob:
    id: str
    rule_id: str
    input_text: str
    status: str
    priority: str
    attempts: int
    max_attempts: int
    embedding_model: str
    created_at: datetime
    started_at: Optional[datetime] = None

class OllamaEmbeddingGenerator:
    """Handles embedding generation using Ollama"""
    
    def __init__(self, model: str = "nomic-embed-text", endpoint: str = "http://localhost:11434"):
        self.model = model
        self.endpoint = endpoint
    
    def check_service(self) -> bool:
        """Check if Ollama service is running"""
        try:
            result = subprocess.run(
                ['curl', '-s', f'{self.endpoint}/api/version'],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to check Ollama service: {e}")
            return False
    
    def generate_embedding(self, text: str) -> Tuple[Optional[List[float]], Optional[str]]:
        """Generate embedding for text, returns (embedding, error)"""
        try:
            start_time = time.time()
            
            cmd = [
                'curl', '-s', f'{self.endpoint}/api/embeddings',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    'model': self.model,
                    'prompt': text
                })
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return None, f"Curl failed: {result.stderr}"
            
            response = json.loads(result.stdout)
            
            if 'embedding' not in response:
                return None, f"No embedding in response: {response}"
            
            embedding = response['embedding']
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"Generated {len(embedding)}D embedding in {processing_time}ms")
            return embedding, None
            
        except subprocess.TimeoutExpired:
            return None, "Embedding generation timeout (60s)"
        except json.JSONDecodeError as e:
            return None, f"JSON decode error: {e}"
        except Exception as e:
            return None, f"Unexpected error: {e}"

class EmbeddingWorker:
    """Main worker class for processing embedding jobs"""
    
    def __init__(self, project_id: str, worker_id: str, model: str = "nomic-embed-text"):
        self.project_id = project_id
        self.worker_id = worker_id
        self.model = model
        self.embedding_generator = OllamaEmbeddingGenerator(model)
        self.running = True
        self.jobs_processed = 0
        self.jobs_failed = 0
        
        # Import MCP functions
        try:
            from mcp__supabase__execute_sql import execute_sql
            self.execute_sql = execute_sql
        except ImportError:
            logger.error("MCP Supabase integration not available")
            sys.exit(1)
    
    async def start(self):
        """Start the worker loop"""
        logger.info(f"Starting embedding worker {self.worker_id}")
        logger.info(f"Project: {self.project_id}, Model: {self.model}")
        
        # Check Ollama service
        if not self.embedding_generator.check_service():
            logger.error("Ollama service not available")
            sys.exit(1)
        
        logger.info("✅ Ollama service is available")
        
        try:
            while self.running:
                job = await self.get_next_job()
                if job:
                    await self.process_job(job)
                else:
                    # No jobs available, wait before checking again
                    await asyncio.sleep(5)
                    
        except KeyboardInterrupt:
            logger.info("Worker interrupted by user")
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            logger.info(f"Worker stopping. Processed: {self.jobs_processed}, Failed: {self.jobs_failed}")
    
    async def get_next_job(self) -> Optional[EmbeddingJob]:
        """Get the next pending job from the queue"""
        try:
            # Use FOR UPDATE SKIP LOCKED to safely claim a job
            query = """
            WITH next_job AS (
                SELECT id, rule_id, input_text, status, priority, attempts, max_attempts, 
                       embedding_model, created_at, started_at
                FROM embedding_jobs 
                WHERE status = 'pending' OR (status = 'retrying' AND started_at < NOW() - INTERVAL '5 minutes')
                ORDER BY 
                    CASE priority 
                        WHEN 'urgent' THEN 1 
                        WHEN 'high' THEN 2 
                        WHEN 'normal' THEN 3 
                        WHEN 'low' THEN 4 
                    END,
                    created_at ASC
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            )
            UPDATE embedding_jobs 
            SET 
                status = 'processing',
                started_at = NOW(),
                worker_id = %s,
                attempts = attempts + 1
            WHERE id = (SELECT id FROM next_job)
            RETURNING id, rule_id, input_text, status, priority, attempts, max_attempts, 
                      embedding_model, created_at, started_at;
            """
            
            result = self.execute_sql(
                project_id=self.project_id, 
                query=query.replace('%s', f"'{self.worker_id}'")
            )
            
            if 'error' in result:
                logger.error(f"Failed to get next job: {result['error']}")
                return None
            
            data = result.get('data', [])
            if not data:
                return None
            
            job_data = data[0]
            return EmbeddingJob(
                id=job_data['id'],
                rule_id=job_data['rule_id'],
                input_text=job_data['input_text'],
                status=job_data['status'],
                priority=job_data['priority'],
                attempts=job_data['attempts'],
                max_attempts=job_data['max_attempts'],
                embedding_model=job_data['embedding_model'],
                created_at=datetime.fromisoformat(job_data['created_at'].replace('Z', '+00:00')),
                started_at=datetime.fromisoformat(job_data['started_at'].replace('Z', '+00:00')) if job_data['started_at'] else None
            )
            
        except Exception as e:
            logger.error(f"Error getting next job: {e}")
            return None
    
    async def process_job(self, job: EmbeddingJob):
        """Process a single embedding job"""
        logger.info(f"Processing job {job.id[:8]}... (attempt {job.attempts}/{job.max_attempts})")
        
        start_time = time.time()
        
        try:
            # Generate embedding
            embedding, error = self.embedding_generator.generate_embedding(job.input_text)
            
            if embedding is None:
                await self.fail_job(job, error)
                return
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Mark job as completed
            await self.complete_job(job, embedding, processing_time_ms)
            
            self.jobs_processed += 1
            logger.info(f"✅ Completed job {job.id[:8]} in {processing_time_ms}ms")
            
        except Exception as e:
            await self.fail_job(job, str(e))
    
    async def complete_job(self, job: EmbeddingJob, embedding: List[float], processing_time_ms: int):
        """Mark job as completed and store the embedding"""
        try:
            # Convert embedding to PostgreSQL vector format
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            query = f"""
            UPDATE embedding_jobs 
            SET 
                status = 'completed',
                completed_at = NOW(),
                embedding_vector = '{embedding_str}'::vector,
                embedding_dimensions = {len(embedding)},
                processing_time_ms = {processing_time_ms}
            WHERE id = '{job.id}'
            """
            
            result = self.execute_sql(project_id=self.project_id, query=query)
            
            if 'error' in result:
                logger.error(f"Failed to complete job {job.id}: {result['error']}")
            else:
                logger.debug(f"Job {job.id} marked as completed")
                
        except Exception as e:
            logger.error(f"Error completing job {job.id}: {e}")
    
    async def fail_job(self, job: EmbeddingJob, error_message: str):
        """Mark job as failed or retry if attempts remaining"""
        try:
            if job.attempts >= job.max_attempts:
                # Permanently failed
                status = 'failed'
                logger.error(f"❌ Job {job.id[:8]} permanently failed: {error_message}")
                self.jobs_failed += 1
            else:
                # Will retry later
                status = 'retrying'
                logger.warning(f"⚠️  Job {job.id[:8]} failed, will retry: {error_message}")
            
            # Escape single quotes in error message
            safe_error = error_message.replace("'", "''")
            
            query = f"""
            UPDATE embedding_jobs 
            SET 
                status = '{status}',
                error_message = '{safe_error}'
            WHERE id = '{job.id}'
            """
            
            result = self.execute_sql(project_id=self.project_id, query=query)
            
            if 'error' in result:
                logger.error(f"Failed to update job status for {job.id}: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error failing job {job.id}: {e}")
    
    def stop(self):
        """Stop the worker"""
        self.running = False

async def monitor_job_queue(project_id: str, execute_sql_func):
    """Monitor and log job queue status"""
    try:
        query = """
        SELECT 
            status,
            priority,
            COUNT(*) as job_count,
            AVG(processing_time_ms) as avg_time_ms
        FROM embedding_jobs
        GROUP BY status, priority
        ORDER BY priority DESC, status
        """
        
        result = execute_sql_func(project_id=project_id, query=query)
        
        if 'error' not in result:
            data = result.get('data', [])
            if data:
                logger.info("📊 Job Queue Status:")
                for row in data:
                    avg_time = f"{row['avg_time_ms']:.0f}ms" if row['avg_time_ms'] else "N/A"
                    logger.info(f"  {row['status']:>10} {row['priority']:>6}: {row['job_count']:>3} jobs (avg: {avg_time})")
            else:
                logger.info("📊 Job queue is empty")
        
    except Exception as e:
        logger.error(f"Error monitoring job queue: {e}")

def main():
    parser = argparse.ArgumentParser(description="ArchGuard Embedding Worker")
    parser.add_argument("--project-id", required=True, help="Supabase project ID")
    parser.add_argument("--worker-id", default=None, help="Worker ID (auto-generated if not provided)")
    parser.add_argument("--model", default="nomic-embed-text", help="Ollama embedding model")
    parser.add_argument("--monitor-only", action="store_true", help="Only monitor job queue, don't process")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Generate worker ID if not provided
    worker_id = args.worker_id or f"worker-{uuid.uuid4().hex[:8]}"
    
    if args.monitor_only:
        # Just monitor the queue
        try:
            from mcp__supabase__execute_sql import execute_sql
            asyncio.run(monitor_job_queue(args.project_id, execute_sql))
        except ImportError:
            logger.error("MCP Supabase integration not available")
            sys.exit(1)
    else:
        # Start the worker
        worker = EmbeddingWorker(args.project_id, worker_id, args.model)
        asyncio.run(worker.start())

if __name__ == "__main__":
    main()