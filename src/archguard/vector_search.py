"""
Vector Search Engine for ArchGuard Rules

This module provides vector-based semantic search for architectural rules
stored in Supabase with pgvector.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timezone
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class VectorSearchEngine:
    """
    Vector search engine for semantic rule retrieval
    """
    
    def __init__(self):
        """Initialize vector search with Supabase connection and embedding model"""
        load_dotenv()
        
        self._client = None
        self._model = None
        self.logger = logging.getLogger(__name__)
        
    def _get_supabase_client(self):
        """Lazy initialization of Supabase client"""
        if self._client is None:
            try:
                from supabase import create_client
                
                url = os.getenv('ARCHGUARD_SUPABASE_URL')
                key = os.getenv('ARCHGUARD_SUPABASE_KEY')
                
                if not url or not key:
                    self.logger.warning("Supabase credentials not found, falling back to local mode")
                    return None
                    
                self._client = create_client(url, key)
                self.logger.info("Connected to Supabase for vector search")
                
            except Exception as e:
                self.logger.error(f"Failed to connect to Supabase: {e}")
                return None
                
        return self._client
    
    def _get_embedding_model(self):
        """Lazy initialization of embedding model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                
                model_name = os.getenv('ARCHGUARD_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
                self._model = SentenceTransformer(model_name)
                self.logger.info(f"Loaded embedding model: {model_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to load embedding model: {e}")
                return None
                
        return self._model
    
    def search_rules(self, query: str, project_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for rules semantically similar to the query
        
        Args:
            query: Natural language query for architectural guidance
            project_id: Optional project ID to filter team-specific rules
            limit: Maximum number of rules to return
            
        Returns:
            List of rules with similarity scores
        """
        client = self._get_supabase_client()
        model = self._get_embedding_model()
        
        if not client or not model:
            self.logger.warning("Vector search unavailable, returning empty results")
            return []
            
        try:
            # Generate query embedding
            query_embedding = model.encode(query)
            
            # Get all rules (with project filtering if specified)
            query_builder = client.table('rules').select('rule_id, title, guidance, rationale, category, priority, embedding')
            
            # Filter by project - include global rules (project_id IS NULL) and project-specific rules
            if project_id:
                query_builder = query_builder.or_(f'project_id.is.null,project_id.eq.{project_id}')
            else:
                # If no project specified, only return global rules
                query_builder = query_builder.is_('project_id', 'null')
            
            # Only get rules that have embeddings
            query_builder = query_builder.not_.is_('embedding', 'null')
            
            result = query_builder.execute()
            
            if not result.data:
                self.logger.info("No rules found with embeddings")
                return []
            
            # Calculate similarities
            results = []
            for rule in result.data:
                try:
                    # Parse embedding from JSON string
                    rule_embedding = np.array(json.loads(rule['embedding']), dtype=np.float32)
                    query_vec = np.array(query_embedding, dtype=np.float32)
                    
                    # Cosine similarity
                    similarity = np.dot(query_vec, rule_embedding) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(rule_embedding)
                    )
                    
                    results.append({
                        'rule_id': rule['rule_id'],
                        'title': rule['title'],
                        'guidance': rule['guidance'],
                        'rationale': rule.get('rationale', ''),
                        'category': rule['category'],
                        'priority': rule['priority'],
                        'similarity': float(similarity)
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process rule {rule.get('rule_id', 'unknown')}: {e}")
                    continue
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            top_results = results[:limit]
            
            # Log retrieval times for each retrieved rule
            if top_results:
                self._log_retrieval_times([rule['rule_id'] for rule in top_results])
            
            self.logger.info(f"Found {len(top_results)} relevant rules for query: '{query[:50]}...'")
            
            return top_results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []
    
    def _log_retrieval_times(self, rule_ids: List[str]):
        """Log retrieval times for rules"""
        client = self._get_supabase_client()
        if not client:
            return
            
        try:
            current_time = datetime.now(timezone.utc).isoformat()
            
            # Update last_retrieved timestamp for each rule
            for rule_id in rule_ids:
                try:
                    client.table('rules').update({
                        'last_retrieved': current_time
                    }).eq('rule_id', rule_id).execute()
                    
                    self.logger.debug(f"Updated retrieval time for rule: {rule_id}")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to update retrieval time for rule {rule_id}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to log retrieval times: {e}")
    
    def is_available(self) -> bool:
        """Check if vector search is available"""
        return self._get_supabase_client() is not None and self._get_embedding_model() is not None


# Singleton instance
vector_search_engine = VectorSearchEngine()