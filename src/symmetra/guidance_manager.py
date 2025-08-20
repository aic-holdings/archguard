"""
Guidance Manager for adding and managing architectural guidance rules
"""

import os
import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from .config import SymmetraConfig
from .cloud_vector_search import CloudVectorSearchEngine

logger = logging.getLogger(__name__)

class GuidanceManager:
    """Manages adding and updating architectural guidance rules"""
    
    def __init__(self):
        self.vector_engine = CloudVectorSearchEngine()
        self.logger = logging.getLogger(__name__)
    
    def add_guidance(
        self,
        title: str,
        guidance: str,
        category: str = "architecture",
        priority: str = "medium",
        rationale: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        tech_stacks: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add new architectural guidance to the database
        
        Args:
            title: Short descriptive title for the guidance
            guidance: The actual guidance/pattern description
            category: Rule category (architecture, security, performance, testing, ai-ml, ux, devops, data)
            priority: Rule priority (low, medium, high, critical)
            rationale: Optional explanation of why this guidance is important
            contexts: Optional list of contexts where this applies
            tech_stacks: Optional list of technology stacks this applies to
            keywords: Optional list of keywords for better searchability
            project_id: Optional project ID (None for global rules)
            
        Returns:
            Dict with success status and created rule details
        """
        try:
            # Basic validation
            if not title or not title.strip():
                return {"success": False, "error": "Title is required"}
            
            if not guidance or not guidance.strip():
                return {"success": False, "error": "Guidance text is required"}
            
            # Validate category
            valid_categories = ["architecture", "security", "performance", "testing", "ai-ml", "ux", "devops", "data"]
            if category not in valid_categories:
                return {"success": False, "error": f"Category must be one of: {', '.join(valid_categories)}"}
            
            # Validate priority
            valid_priorities = ["low", "medium", "high", "critical"]
            if priority not in valid_priorities:
                return {"success": False, "error": f"Priority must be one of: {', '.join(valid_priorities)}"}
            
            # Generate rule_id from title
            rule_id = self._generate_rule_id(title)
            
            # Check if rule_id already exists
            if self._rule_id_exists(rule_id):
                return {"success": False, "error": f"A rule with similar title already exists (rule_id: {rule_id})"}
            
            # Generate embedding for the guidance
            embedding_text = f"{title} {guidance}"
            if rationale:
                embedding_text += f" {rationale}"
            
            embedding = self.vector_engine._generate_embedding(embedding_text)
            if not embedding:
                self.logger.warning("Failed to generate embedding, proceeding without it")
            
            # Get Supabase client
            supabase_client = self.vector_engine._get_supabase_client()
            if not supabase_client:
                return {"success": False, "error": "Database connection unavailable"}
            
            # Prepare rule data
            rule_data = {
                "rule_id": rule_id,
                "project_id": project_id,
                "title": title.strip(),
                "guidance": guidance.strip(),
                "rationale": rationale.strip() if rationale else None,
                "category": category,
                "priority": priority,
                "contexts": contexts or [],
                "tech_stacks": tech_stacks or [],
                "keywords": keywords or [],
                "embedding": embedding
            }
            
            # Insert into database
            result = supabase_client.table('rules').insert(rule_data).execute()
            
            if result.data:
                created_rule = result.data[0]
                self.logger.info(f"Successfully added guidance rule: {rule_id}")
                return {
                    "success": True,
                    "rule_id": rule_id,
                    "id": created_rule['id'],
                    "title": title,
                    "category": category,
                    "priority": priority,
                    "message": f"Guidance '{title}' added successfully!"
                }
            else:
                return {"success": False, "error": "Failed to insert rule into database"}
                
        except Exception as e:
            self.logger.error(f"Failed to add guidance: {e}")
            return {"success": False, "error": f"Database error: {str(e)}"}
    
    def _generate_rule_id(self, title: str) -> str:
        """Generate a URL-safe rule ID from the title"""
        # Convert to lowercase, replace spaces/special chars with hyphens
        rule_id = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())
        # Remove leading/trailing hyphens and limit length
        rule_id = rule_id.strip('-')[:50]
        # Ensure it ends cleanly
        rule_id = rule_id.rstrip('-')
        
        # Add timestamp suffix if too short or generic
        if len(rule_id) < 3 or rule_id in ['rule', 'guidance', 'pattern']:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            rule_id = f"{rule_id}-{timestamp}"
        
        return rule_id
    
    def _rule_id_exists(self, rule_id: str) -> bool:
        """Check if a rule_id already exists in the database"""
        try:
            supabase_client = self.vector_engine._get_supabase_client()
            if not supabase_client:
                return False
            
            result = supabase_client.table('rules').select('rule_id').eq('rule_id', rule_id).limit(1).execute()
            return len(result.data) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to check rule_id existence: {e}")
            return False
    
    def search_guidance(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for existing guidance using the vector search engine"""
        return self.vector_engine.search_rules(query, limit=limit)
    
    def quick_add(self, description: str, category: str = "architecture") -> Dict[str, Any]:
        """
        Quick way to add guidance with minimal input - for the "sweet pattern!" use case
        
        Args:
            description: Combined title and guidance description
            category: Rule category (defaults to architecture)
        
        Returns:
            Result dict with success status
        """
        # Split description into title and guidance if it's long
        if len(description) > 100:
            # Use first sentence as title, rest as guidance
            sentences = description.split('.')
            title = sentences[0].strip()
            guidance = '.'.join(sentences[1:]).strip() if len(sentences) > 1 else description
            if not guidance:
                guidance = description
        else:
            # Short description becomes both title and guidance
            title = description
            guidance = description
        
        return self.add_guidance(
            title=title,
            guidance=guidance,
            category=category,
            rationale="Added as a discovered pattern during development"
        )


# Global instance
guidance_manager = GuidanceManager()