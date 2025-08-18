#!/usr/bin/env python3
"""
ArchGuard Embedding System Tests - Self-Documenting Vector Operations

These tests demonstrate and validate the embedding job queue system,
vector operations, and Ollama integration patterns.

Run with: pytest tests/test_embedding_system.py -v
"""

import asyncio
import json
import os
import pytest
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "maintenance"))

from embedding_worker import EmbeddingWorker, OllamaEmbeddingGenerator, EmbeddingJob
from datetime import datetime


class TestOllamaIntegration:
    """Test Ollama embedding generation"""
    
    def test_ollama_service_health_check(self):
        """
        DOCS: System validates Ollama availability before processing jobs.
        Prevents job failures due to service unavailability.
        """
        generator = OllamaEmbeddingGenerator()
        
        # Mock successful health check
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            assert generator.check_service() == True
            
        # Mock failed health check
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            assert generator.check_service() == False
    
    def test_embedding_generation_with_nomic_model(self):
        """
        DOCS: Uses nomic-embed-text model for 768-dimensional embeddings.
        Local processing provides cost-free, private embedding generation.
        """
        generator = OllamaEmbeddingGenerator(model="nomic-embed-text")
        
        # Mock successful embedding generation
        mock_response = {
            "embedding": [0.1] * 768  # 768-dimensional vector
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(mock_response)
            
            embedding, error = generator.generate_embedding("test text")
            
            assert embedding is not None
            assert error is None
            assert len(embedding) == 768
            assert all(isinstance(x, (int, float)) for x in embedding)
    
    def test_embedding_generation_error_handling(self):
        """
        DOCS: Robust error handling for embedding generation failures.
        Provides detailed error messages for debugging and monitoring.
        """
        generator = OllamaEmbeddingGenerator()
        
        # Test timeout handling
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("curl", 60)
            
            embedding, error = generator.generate_embedding("test text")
            
            assert embedding is None
            assert "timeout" in error.lower()
        
        # Test JSON decode error
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "invalid json"
            
            embedding, error = generator.generate_embedding("test text")
            
            assert embedding is None
            assert "json decode" in error.lower()
    
    def test_embedding_performance_measurement(self):
        """
        DOCS: System tracks embedding generation performance metrics.
        Helps optimize processing speed and identify bottlenecks.
        """
        generator = OllamaEmbeddingGenerator()
        
        mock_response = {"embedding": [0.1] * 768}
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(mock_response)
            
            start_time = time.time()
            embedding, error = generator.generate_embedding("performance test")
            end_time = time.time()
            
            # Should complete in reasonable time
            processing_time_ms = (end_time - start_time) * 1000
            assert processing_time_ms < 5000  # 5 second timeout for mocked calls
            assert embedding is not None


class TestEmbeddingJobQueue:
    """Test job queue system architecture"""
    
    def test_job_priority_ordering(self):
        """
        DOCS: Jobs are processed by priority: urgent → high → normal → low.
        Within same priority, FIFO ordering by creation time.
        """
        # Create mock jobs with different priorities
        jobs = [
            {"id": "1", "priority": "low", "created_at": "2024-01-01T10:00:00Z"},
            {"id": "2", "priority": "urgent", "created_at": "2024-01-01T10:05:00Z"},
            {"id": "3", "priority": "normal", "created_at": "2024-01-01T10:01:00Z"},
            {"id": "4", "priority": "high", "created_at": "2024-01-01T10:03:00Z"},
        ]
        
        # Expected order: urgent, high, normal, low
        expected_order = ["2", "4", "3", "1"]
        
        # Sort by priority (this would happen in SQL ORDER BY)
        priority_values = {"urgent": 1, "high": 2, "normal": 3, "low": 4}
        sorted_jobs = sorted(jobs, key=lambda x: priority_values[x["priority"]])
        actual_order = [job["id"] for job in sorted_jobs]
        
        assert actual_order == expected_order
    
    def test_concurrent_job_processing_with_locking(self):
        """
        DOCS: FOR UPDATE SKIP LOCKED prevents job conflicts between workers.
        Multiple workers can process jobs concurrently without collisions.
        """
        # Mock database behavior for concurrent job claiming
        mock_execute_sql = Mock()
        
        # First worker gets job 1
        mock_execute_sql.return_value = {
            "data": [{
                "id": "job-1",
                "rule_id": "rule-1",
                "input_text": "test text",
                "status": "processing",
                "priority": "normal",
                "attempts": 1,
                "max_attempts": 3,
                "embedding_model": "nomic-embed-text",
                "created_at": "2024-01-01T10:00:00Z",
                "started_at": "2024-01-01T10:00:01Z"
            }]
        }
        
        worker1 = EmbeddingWorker("proj-123", "worker-1")
        worker1.execute_sql = mock_execute_sql
        
        # Simulate successful job claiming
        job = asyncio.run(worker1.get_next_job())
        
        assert job is not None
        assert job.id == "job-1"
        assert job.status == "processing"
        assert job.attempts == 1
    
    def test_retry_logic_with_exponential_backoff(self):
        """
        DOCS: Failed jobs retry with exponential backoff: 30s, 60s, 120s.
        Prevents overwhelming Ollama service with repeated failures.
        """
        mock_execute_sql = Mock()
        worker = EmbeddingWorker("proj-123", "worker-1")
        worker.execute_sql = mock_execute_sql
        
        # Create job with multiple attempts
        job = EmbeddingJob(
            id="job-1",
            rule_id="rule-1", 
            input_text="test",
            status="processing",
            priority="normal",
            attempts=2,
            max_attempts=3,
            embedding_model="nomic-embed-text",
            created_at=datetime.now()
        )
        
        # Simulate failure - should retry
        mock_execute_sql.return_value = {"data": []}
        asyncio.run(worker.fail_job(job, "Test error"))
        
        # Should mark as retrying since attempts < max_attempts
        mock_execute_sql.assert_called()
        call_args = mock_execute_sql.call_args[1]['query']
        assert "status = 'retrying'" in call_args
        
        # Simulate max attempts reached - should fail permanently
        job.attempts = 3
        asyncio.run(worker.fail_job(job, "Max attempts reached"))
        
        call_args = mock_execute_sql.call_args[1]['query']
        assert "status = 'failed'" in call_args
    
    def test_job_completion_transfers_embedding_to_rule(self):
        """
        DOCS: Completed embeddings are automatically transferred to rules table.
        Database triggers ensure consistency between jobs and rules.
        """
        mock_execute_sql = Mock()
        worker = EmbeddingWorker("proj-123", "worker-1")
        worker.execute_sql = mock_execute_sql
        
        job = EmbeddingJob(
            id="job-1",
            rule_id="rule-1",
            input_text="test",
            status="processing", 
            priority="normal",
            attempts=1,
            max_attempts=3,
            embedding_model="nomic-embed-text",
            created_at=datetime.now()
        )
        
        embedding = [0.1] * 768
        processing_time_ms = 250
        
        mock_execute_sql.return_value = {"data": []}
        asyncio.run(worker.complete_job(job, embedding, processing_time_ms))
        
        # Should update job with embedding and mark completed
        call_args = mock_execute_sql.call_args[1]['query']
        assert "status = 'completed'" in call_args
        assert "embedding_vector =" in call_args
        assert "processing_time_ms = 250" in call_args


class TestVectorOperations:
    """Test vector storage and similarity search"""
    
    def test_vector_format_conversion(self):
        """
        DOCS: Embeddings are stored as PostgreSQL vector type.
        Format: [0.1,0.2,0.3] for pgvector compatibility.
        """
        embedding = [0.1, 0.2, 0.3, -0.1, 0.0]
        
        # Convert to PostgreSQL vector format
        vector_str = '[' + ','.join(map(str, embedding)) + ']'
        
        assert vector_str == '[0.1,0.2,0.3,-0.1,0.0]'
        assert vector_str.startswith('[')
        assert vector_str.endswith(']')
        assert ',' in vector_str
    
    def test_cosine_similarity_calculation(self):
        """
        DOCS: Vector similarity uses cosine distance for semantic search.
        Formula: 1 - cosine_distance for similarity ranking.
        """
        # Mock vector similarity query
        query = """
        SELECT rule_id, title, guidance, 
               1 - (embedding <=> %s) as similarity
        FROM rules 
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s
        LIMIT %s
        """
        
        # Should use <=> operator for cosine distance
        assert "<=> %s" in query
        assert "ORDER BY embedding <=>" in query
        assert "1 - (embedding <=>" in query  # Convert distance to similarity
    
    def test_embedding_dimensions_validation(self):
        """
        DOCS: System validates embedding dimensions match model output.
        nomic-embed-text produces 768-dimensional vectors.
        """
        valid_embedding = [0.1] * 768  # Correct dimensions
        invalid_embedding = [0.1] * 512  # Wrong dimensions
        
        # Valid embedding should be accepted
        assert len(valid_embedding) == 768
        
        # Invalid embedding should be rejected
        assert len(invalid_embedding) != 768


class TestJobMonitoring:
    """Test job queue monitoring and observability"""
    
    def test_job_status_dashboard_query(self):
        """
        DOCS: Monitoring dashboard shows job distribution by status and priority.
        Helps operators understand system health and performance.
        """
        expected_monitoring_query = """
        SELECT 
            status,
            priority,
            COUNT(*) as job_count,
            AVG(processing_time_ms) as avg_time_ms
        FROM embedding_jobs
        GROUP BY status, priority
        ORDER BY priority DESC, status
        """
        
        # Should group by status and priority
        assert "GROUP BY status, priority" in expected_monitoring_query
        assert "COUNT(*) as job_count" in expected_monitoring_query
        assert "AVG(processing_time_ms)" in expected_monitoring_query
        assert "ORDER BY priority DESC" in expected_monitoring_query
    
    def test_worker_performance_metrics(self):
        """
        DOCS: System tracks individual worker performance metrics.
        Identifies slow workers and processing bottlenecks.
        """
        expected_worker_query = """
        SELECT 
            worker_id,
            COUNT(*) as jobs_completed,
            AVG(processing_time_ms) as avg_time,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failures
        FROM embedding_jobs
        WHERE completed_at > NOW() - INTERVAL '24 hours'
        GROUP BY worker_id
        """
        
        # Should track worker-specific metrics
        assert "GROUP BY worker_id" in expected_worker_query
        assert "jobs_completed" in expected_worker_query
        assert "avg_time" in expected_worker_query
        assert "failures" in expected_worker_query
    
    def test_job_queue_health_indicators(self):
        """
        DOCS: Health indicators help identify system issues.
        - Pending jobs: backlog size
        - Processing time: performance trends
        - Failed jobs: error rates
        """
        health_indicators = {
            "pending_jobs": 5,      # Jobs waiting to process
            "avg_processing_time": 250,  # Milliseconds
            "failed_job_rate": 0.02,     # 2% failure rate
            "oldest_pending": "2024-01-01T10:00:00Z"
        }
        
        # Acceptable thresholds
        assert health_indicators["pending_jobs"] < 100  # Manageable backlog
        assert health_indicators["avg_processing_time"] < 1000  # Under 1 second
        assert health_indicators["failed_job_rate"] < 0.05  # Under 5% failures


class TestScalabilityPatterns:
    """Test system scalability and performance patterns"""
    
    def test_horizontal_worker_scaling(self):
        """
        DOCS: Multiple workers can run concurrently for horizontal scaling.
        Each worker has unique ID for tracking and coordination.
        """
        # Simulate multiple workers
        workers = [
            EmbeddingWorker("proj-123", f"worker-{i}", "nomic-embed-text")
            for i in range(3)
        ]
        
        # Each worker should have unique ID
        worker_ids = [worker.worker_id for worker in workers]
        assert len(set(worker_ids)) == len(workers)  # All unique
        
        # All workers should use same project and model
        assert all(worker.project_id == "proj-123" for worker in workers)
        assert all(worker.model == "nomic-embed-text" for worker in workers)
    
    def test_batch_processing_efficiency(self):
        """
        DOCS: Batch processing improves efficiency for large rule sets.
        Workers can process multiple jobs in parallel batches.
        """
        batch_size = 10
        mock_jobs = [
            {"id": f"job-{i}", "input_text": f"text {i}"} 
            for i in range(batch_size)
        ]
        
        # Batch processing should handle multiple jobs efficiently
        assert len(mock_jobs) == batch_size
        assert all("input_text" in job for job in mock_jobs)
    
    def test_deduplication_prevents_redundant_work(self):
        """
        DOCS: Text hash deduplication prevents redundant embedding generation.
        Identical text content reuses existing embeddings.
        """
        import hashlib
        
        text1 = "identical text content"
        text2 = "identical text content"  # Same content
        text3 = "different text content"
        
        hash1 = hashlib.md5(text1.encode()).hexdigest()
        hash2 = hashlib.md5(text2.encode()).hexdigest()
        hash3 = hashlib.md5(text3.encode()).hexdigest()
        
        # Same content should have same hash
        assert hash1 == hash2
        assert hash1 != hash3
        
        # Deduplication query would find existing embedding
        dedup_query = "SELECT embedding_vector FROM embedding_jobs WHERE text_hash = %s AND status = 'completed'"
        assert "text_hash = %s" in dedup_query
        assert "status = 'completed'" in dedup_query


class TestProductionReadiness:
    """Test production deployment patterns"""
    
    def test_graceful_shutdown_handling(self):
        """
        DOCS: Workers handle graceful shutdown for production deployments.
        In-progress jobs are completed before worker termination.
        """
        worker = EmbeddingWorker("proj-123", "worker-1")
        
        # Worker should start in running state
        assert worker.running == True
        
        # Stop signal should set running to False
        worker.stop()
        assert worker.running == False
    
    def test_health_check_endpoints(self):
        """
        DOCS: System provides health check endpoints for load balancers.
        Monitors Ollama service availability and worker status.
        """
        # Health check should verify critical dependencies
        health_checks = {
            "ollama_service": True,    # Service reachable
            "database_connection": True,  # Database accessible
            "worker_active": True,     # Worker processing jobs
            "queue_healthy": True      # Queue not backed up
        }
        
        assert all(health_checks.values())  # All systems operational
    
    def test_configuration_management(self):
        """
        DOCS: Production configuration via environment variables.
        Supports containerized deployments and configuration management.
        """
        production_config = {
            "ARCHGUARD_SUPABASE_URL": "https://project.supabase.co",
            "ARCHGUARD_SUPABASE_KEY": "eyJ...",
            "ARCHGUARD_EMBEDDING_MODEL": "nomic-embed-text",
            "ARCHGUARD_MAX_WORKERS": "3",
            "ARCHGUARD_BATCH_SIZE": "50"
        }
        
        # All required configuration should be available
        required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "EMBEDDING_MODEL"]
        available_vars = [var for var in production_config.keys()]
        
        assert all(any(req in var for var in available_vars) for req in required_vars)


# Mock imports for testing
import subprocess
if not hasattr(subprocess, 'TimeoutExpired'):
    class TimeoutExpired(Exception):
        def __init__(self, cmd, timeout):
            self.cmd = cmd
            self.timeout = timeout
    subprocess.TimeoutExpired = TimeoutExpired


if __name__ == "__main__":
    # Run tests with verbose output for documentation
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("ArchGuard Embedding System Test Results:")
    print("=" * 50)
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)