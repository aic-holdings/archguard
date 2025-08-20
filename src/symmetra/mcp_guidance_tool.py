"""
MCP tool for conversational guidance capture within Claude Code
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from .guidance_manager import guidance_manager
from .cloud_vector_search import CloudVectorSearchEngine

logger = logging.getLogger(__name__)

class GuidanceCaptureTool:
    """MCP tool for capturing architectural guidance conversationally"""
    
    def __init__(self):
        self.guidance_manager = guidance_manager
        self.vector_engine = CloudVectorSearchEngine()
        self.logger = logging.getLogger(__name__)
    
    def capture_guidance(
        self,
        description: str,
        current_files: Optional[List[str]] = None,
        context_info: Optional[str] = None,
        suggested_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start the conversational guidance capture process
        
        Args:
            description: User's description of the pattern/guidance
            current_files: List of file paths user is currently working with  
            context_info: Additional context about what they're working on
            suggested_category: AI's suggested category based on context
            
        Returns:
            Dict with guidance analysis and conversation prompts
        """
        try:
            # Analyze the description and context
            analysis = self._analyze_guidance_request(
                description, current_files, context_info
            )
            
            # Search for similar existing guidance
            similar_guidance = self._find_similar_guidance(description)
            
            # Generate conversation prompts to refine the guidance
            conversation_prompts = self._generate_conversation_prompts(
                description, analysis, similar_guidance
            )
            
            return {
                "success": True,
                "analysis": analysis,
                "similar_guidance": similar_guidance,
                "conversation_prompts": conversation_prompts,
                "next_step": "refine_guidance",
                "capture_id": self._generate_capture_id()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start guidance capture: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def refine_guidance(
        self,
        capture_id: str,
        title: str,
        guidance: str,
        category: str,
        priority: str = "medium",
        rationale: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        tech_stacks: Optional[List[str]] = None,
        code_examples: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Finalize and store the refined guidance
        
        Args:
            capture_id: ID from the initial capture request
            title: Refined title for the guidance
            guidance: Detailed guidance text
            category: Selected category
            priority: Priority level
            rationale: Why this guidance is important
            contexts: List of contexts where this applies
            tech_stacks: Relevant technology stacks
            code_examples: Code examples to include
            
        Returns:
            Dict with storage result
        """
        try:
            # Store the guidance
            result = self.guidance_manager.add_guidance(
                title=title,
                guidance=guidance,
                category=category,
                priority=priority,
                rationale=rationale,
                contexts=contexts,
                tech_stacks=tech_stacks
            )
            
            if result['success'] and code_examples:
                # TODO: Store code examples in rule_examples table
                self.logger.info(f"Code examples provided but not yet stored: {len(code_examples)} examples")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to refine guidance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_guidance_request(
        self, 
        description: str, 
        current_files: Optional[List[str]], 
        context_info: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze the guidance request and extract insights"""
        
        analysis = {
            "description_length": len(description.split()),
            "complexity": "simple" if len(description.split()) < 20 else "detailed",
            "suggested_categories": [],
            "extracted_keywords": [],
            "file_context": {}
        }
        
        # Simple keyword-based category suggestions
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['async', 'promise', 'await', 'concurrent']):
            analysis["suggested_categories"].append("architecture")
        if any(word in description_lower for word in ['security', 'auth', 'token', 'encrypt']):
            analysis["suggested_categories"].append("security")
        if any(word in description_lower for word in ['performance', 'cache', 'optimize', 'fast']):
            analysis["suggested_categories"].append("performance")
        if any(word in description_lower for word in ['test', 'mock', 'spec', 'unit']):
            analysis["suggested_categories"].append("testing")
        if any(word in description_lower for word in ['ui', 'ux', 'user', 'interface']):
            analysis["suggested_categories"].append("ux")
        
        # Default to architecture if no specific category detected
        if not analysis["suggested_categories"]:
            analysis["suggested_categories"] = ["architecture"]
        
        # Analyze current files if provided
        if current_files:
            analysis["file_context"] = {
                "file_count": len(current_files),
                "file_types": list(set(Path(f).suffix for f in current_files if Path(f).suffix)),
                "files": current_files[:5]  # Limit to first 5 for brevity
            }
        
        return analysis
    
    def _find_similar_guidance(self, description: str) -> List[Dict[str, Any]]:
        """Find similar existing guidance"""
        try:
            results = self.vector_engine.search_rules(description, limit=3, threshold=0.7)
            return results
        except Exception as e:
            self.logger.error(f"Failed to search similar guidance: {e}")
            return []
    
    def _generate_conversation_prompts(
        self, 
        description: str, 
        analysis: Dict[str, Any], 
        similar_guidance: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate conversation prompts to help refine the guidance"""
        
        prompts = []
        
        # Basic refinement questions
        if analysis["complexity"] == "simple":
            prompts.append("Can you provide more details about this pattern? What specific problem does it solve?")
        
        prompts.append("What are the key benefits of this approach over alternatives?")
        prompts.append("Are there any important gotchas or limitations to mention?")
        
        # Category-specific questions
        suggested_cats = analysis.get("suggested_categories", [])
        if "performance" in suggested_cats:
            prompts.append("What performance improvements does this provide? Any benchmarks or measurements?")
        if "security" in suggested_cats:
            prompts.append("What security risks does this pattern address? Any compliance considerations?")
        if "architecture" in suggested_cats:
            prompts.append("How does this fit into the overall architecture? What components does it affect?")
        
        # Context questions
        if analysis.get("file_context", {}).get("file_types"):
            file_types = analysis["file_context"]["file_types"]
            prompts.append(f"I see you're working with {', '.join(file_types)} files. Does this pattern apply to specific file types or frameworks?")
        
        # Similar guidance check
        if similar_guidance:
            prompts.append(f"I found {len(similar_guidance)} similar guidance rules. Should we update an existing rule or create a new one?")
        
        return prompts
    
    def _generate_capture_id(self) -> str:
        """Generate a unique capture session ID"""
        from datetime import datetime
        import uuid
        return f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"


# MCP tool interface
guidance_capture_tool = GuidanceCaptureTool()

def mcp_capture_guidance(**kwargs) -> str:
    """MCP interface for capturing guidance"""
    result = guidance_capture_tool.capture_guidance(**kwargs)
    return json.dumps(result, indent=2)

def mcp_refine_guidance(**kwargs) -> str:
    """MCP interface for refining and storing guidance"""
    result = guidance_capture_tool.refine_guidance(**kwargs)
    return json.dumps(result, indent=2)