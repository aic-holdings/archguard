"""
Cloud Vector Search Engine for Symmetra Rules

This module provides vector-based semantic search using OpenAI cloud embeddings
instead of local SentenceTransformers, removing infrastructure dependencies.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class CloudVectorSearchEngine:
    """
    Cloud-based vector search engine using OpenAI embeddings API
    """
    
    def __init__(self):
        """Initialize cloud vector search with OpenAI and Supabase connections"""
        load_dotenv()
        
        self._supabase_client = None
        self._openai_client = None
        self.logger = logging.getLogger(__name__)
        
    def _get_supabase_client(self):
        """Lazy initialization of Supabase client"""
        if self._supabase_client is None:
            try:
                from supabase import create_client
                
                url = os.getenv('SYMMETRA_SUPABASE_URL')
                key = os.getenv('SYMMETRA_SUPABASE_KEY')
                
                if not url or not key:
                    self.logger.warning("Supabase credentials not found")
                    return None
                    
                self._supabase_client = create_client(url, key)
                self.logger.info("Connected to Supabase for vector search")
                
            except Exception as e:
                self.logger.error(f"Failed to connect to Supabase: {e}")
                return None
                
        return self._supabase_client
    
    def _get_openai_client(self):
        """Lazy initialization of OpenAI client"""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    self.logger.warning("OPENAI_API_KEY not found, vector search unavailable")
                    return None
                    
                self._openai_client = OpenAI(api_key=api_key)
                self.logger.info("Connected to OpenAI API for embeddings")
                
            except Exception as e:
                self.logger.error(f"Failed to connect to OpenAI: {e}")
                return None
                
        return self._openai_client
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI API"""
        client = self._get_openai_client()
        if not client:
            return None
            
        try:
            # Clean text for better embedding quality
            cleaned_text = text.replace("\n", " ").strip()
            
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=[cleaned_text],
                dimensions=384  # Match database schema
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def search_rules(self, query: str, project_id: Optional[str] = None, limit: int = 5, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        Search for rules semantically similar to the query using cloud embeddings
        
        Args:
            query: Natural language query for architectural guidance
            project_id: Optional project ID to filter team-specific rules
            limit: Maximum number of rules to return
            threshold: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            List of rules with similarity scores
        """
        supabase_client = self._get_supabase_client()
        
        if not supabase_client:
            self.logger.warning("Supabase client unavailable, returning empty results")
            return []
            
        try:
            # Generate query embedding using OpenAI
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                self.logger.warning("Failed to generate query embedding")
                return []
            
            # Use Supabase RPC function for efficient vector search
            try:
                search_result = supabase_client.rpc('match_rules', {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }).execute()
                
                if search_result.data:
                    results = []
                    for match in search_result.data:
                        # Transform to expected format
                        results.append({
                            'rule_id': match['rule_id'],
                            'title': match['title'],
                            'guidance': match['guidance'],
                            'rationale': '',  # Not included in match_rules function
                            'category': match['category'],
                            'priority': match['priority'],
                            'contexts': match.get('contexts', []),
                            'tech_stacks': match.get('tech_stacks', []),
                            'keywords': match.get('keywords', []),
                            'similarity': float(match['similarity']),
                            'external_urls': None,  # Would need to be added to match_rules if needed
                            'freshness_priority': 'medium'  # Default value
                        })
                    
                    # Log retrieval times for retrieved rules
                    if results:
                        self._log_retrieval_times([rule['rule_id'] for rule in results])
                    
                    self.logger.info(f"Found {len(results)} relevant rules for query: '{query[:50]}...'")
                    return results
                
            except Exception as rpc_error:
                self.logger.warning(f"RPC search failed: {rpc_error}, falling back to manual search")
                # Fall back to manual similarity calculation
                return self._manual_vector_search(query_embedding, project_id, limit, threshold)
                
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []
    
    def _manual_vector_search(self, query_embedding: List[float], project_id: Optional[str], limit: int, threshold: float) -> List[Dict[str, Any]]:
        """Fallback manual vector search when RPC function is unavailable"""
        supabase_client = self._get_supabase_client()
        if not supabase_client:
            return []
            
        try:
            # Get all rules with embeddings
            query_builder = supabase_client.table('rules').select(
                'rule_id, title, guidance, rationale, category, priority, contexts, tech_stacks, keywords, embedding'
            )
            
            # Filter by project
            if project_id:
                query_builder = query_builder.or_(f'project_id.is.null,project_id.eq.{project_id}')
            else:
                query_builder = query_builder.is_('project_id', 'null')
            
            query_builder = query_builder.not_.is_('embedding', 'null')
            result = query_builder.execute()
            
            if not result.data:
                return []
            
            # Calculate similarities manually
            import numpy as np
            results = []
            query_vec = np.array(query_embedding, dtype=np.float32)
            
            for rule in result.data:
                try:
                    # Parse embedding
                    if isinstance(rule['embedding'], str):
                        rule_embedding = np.array(json.loads(rule['embedding']), dtype=np.float32)
                    else:
                        rule_embedding = np.array(rule['embedding'], dtype=np.float32)
                    
                    # Cosine similarity
                    similarity = np.dot(query_vec, rule_embedding) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(rule_embedding)
                    )
                    
                    if similarity >= threshold:
                        results.append({
                            'rule_id': rule['rule_id'],
                            'title': rule['title'],
                            'guidance': rule['guidance'],
                            'rationale': rule.get('rationale', ''),
                            'category': rule['category'],
                            'priority': rule['priority'],
                            'contexts': rule.get('contexts', []),
                            'tech_stacks': rule.get('tech_stacks', []),
                            'keywords': rule.get('keywords', []),
                            'similarity': float(similarity),
                            'external_urls': None,
                            'freshness_priority': 'medium'
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Failed to process rule {rule.get('rule_id', 'unknown')}: {e}")
                    continue
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Manual vector search failed: {e}")
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
        """Check if cloud vector search is available"""
        return (self._get_supabase_client() is not None and 
                self._get_openai_client() is not None)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on cloud vector search components"""
        health = {
            'status': 'healthy',
            'components': {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Check Supabase connection
        try:
            client = self._get_supabase_client()
            if client:
                # Try a simple query
                result = client.table('rules').select('count', count='exact').limit(1).execute()
                health['components']['supabase'] = {
                    'status': 'healthy',
                    'rule_count': result.count if hasattr(result, 'count') else 'unknown'
                }
            else:
                health['components']['supabase'] = {'status': 'unavailable', 'error': 'No connection'}
                health['status'] = 'degraded'
        except Exception as e:
            health['components']['supabase'] = {'status': 'error', 'error': str(e)}
            health['status'] = 'degraded'
        
        # Check OpenAI connection
        try:
            client = self._get_openai_client()
            if client:
                # Try a simple embedding request
                embedding = self._generate_embedding("test")
                if embedding and len(embedding) == 384:
                    health['components']['openai'] = {
                        'status': 'healthy',
                        'embedding_dimensions': len(embedding)
                    }
                else:
                    health['components']['openai'] = {'status': 'error', 'error': 'Invalid embedding response'}
                    health['status'] = 'degraded'
            else:
                health['components']['openai'] = {'status': 'unavailable', 'error': 'No API key'}
                health['status'] = 'degraded'
        except Exception as e:
            health['components']['openai'] = {'status': 'error', 'error': str(e)}
            health['status'] = 'degraded'
        
        return health


# Singleton instance
cloud_vector_search_engine = CloudVectorSearchEngine()