"""
ArchGuard Rules Engine - Semantic rule retrieval system

This module provides an abstraction for rule storage and retrieval that supports
both keyword-based matching (for immediate use) and vector-based semantic search
(for future enhancement).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os


class RuleEngine(ABC):
    """Abstract base class for rule engines"""
    
    @abstractmethod
    def find_relevant_rules(self, action: str, code: str = "", context: str = "", 
                          project_context: Optional[Dict] = None) -> List[Dict]:
        """Find rules relevant to the given action and context"""
        pass
    
    @abstractmethod
    def add_rule(self, rule: Dict) -> bool:
        """Add a new rule to the engine"""
        pass
    
    @abstractmethod
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """Get a specific rule by ID"""
        pass
    
    @abstractmethod
    def list_all_rules(self) -> List[Dict]:
        """List all available rules"""
        pass


class KeywordRuleEngine(RuleEngine):
    """Keyword-based rule engine for immediate use"""
    
    def __init__(self):
        self.rules = self._load_bootstrap_rules()
    
    def _load_bootstrap_rules(self) -> List[Dict]:
        """Load initial set of ArchGuard bootstrap rules"""
        return [
            # Vector Database Architecture Rules
            {
                "rule_id": "vector-db-choice",
                "title": "Vector Database Selection",
                "guidance": "🗄️ For vector storage, choose: ChromaDB (development/prototyping), Weaviate (production), or pgvector (PostgreSQL integration)",
                "rationale": "Different vector databases excel in different contexts. ChromaDB is perfect for development, Weaviate scales well in production, and pgvector integrates seamlessly with existing PostgreSQL infrastructure.",
                "keywords": ["vector", "database", "embedding", "storage", "chroma", "weaviate", "pgvector", "chromadb"],
                "contexts": ["ide-assistant", "agent", "desktop-app"],
                "tech_stacks": ["python", "ai", "ml", "database"],
                "priority": "high",
                "category": "architecture",
                "examples": [
                    "When building semantic search: Use ChromaDB for rapid prototyping",
                    "For production AI systems: Consider Weaviate with proper clustering",
                    "If using PostgreSQL: pgvector extension provides vector capabilities"
                ]
            },
            {
                "rule_id": "embedding-model-selection",
                "title": "Text Embedding Model Choice", 
                "guidance": "🧠 Use sentence-transformers for rule embeddings: all-MiniLM-L6-v2 (fast, 384d) or all-mpnet-base-v2 (quality, 768d)",
                "rationale": "Sentence transformers provide high-quality semantic embeddings. MiniLM is faster and smaller, while mpnet provides better semantic understanding for complex texts.",
                "keywords": ["embedding", "model", "sentence", "transformer", "semantic", "similarity", "minilm", "mpnet"],
                "contexts": ["ide-assistant", "agent"],
                "tech_stacks": ["python", "ai", "ml", "nlp"],
                "priority": "medium",
                "category": "ai-ml",
                "examples": [
                    "For real-time applications: all-MiniLM-L6-v2 provides good speed/quality tradeoff",
                    "For high-accuracy semantic search: all-mpnet-base-v2 offers superior understanding",
                    "Consider model size vs. inference speed based on deployment constraints"
                ]
            },
            {
                "rule_id": "sqlite-vector-hybrid",
                "title": "Hybrid SQLite + Vector Storage",
                "guidance": "💾 Store rule metadata in SQLite, vectors in dedicated vector DB. Link via rule_id for best performance and flexibility",
                "rationale": "Hybrid storage leverages SQLite's ACID properties for metadata while using specialized vector databases for semantic search. This provides both relational integrity and vector performance.",
                "keywords": ["sqlite", "database", "metadata", "hybrid", "storage", "relational", "vector", "architecture"],
                "contexts": ["ide-assistant", "agent"],
                "tech_stacks": ["python", "sqlite", "database"],
                "priority": "medium",
                "category": "architecture",
                "examples": [
                    "Store rule text, timestamps, categories in SQLite",
                    "Store embeddings in ChromaDB/Weaviate with rule_id as foreign key",
                    "Use SQLite for complex queries, vector DB for similarity search"
                ]
            },
            {
                "rule_id": "mcp-tool-design",
                "title": "MCP Tool Performance Design",
                "guidance": "🔧 MCP tools should be stateless, fast (<100ms response), and return structured data optimized for AI consumption",
                "rationale": "MCP tools are called frequently during AI workflows. Fast, stateless tools provide better user experience and enable real-time guidance without breaking flow.",
                "keywords": ["mcp", "tool", "design", "performance", "stateless", "fast", "structured", "api"],
                "contexts": ["ide-assistant", "agent"],
                "tech_stacks": ["python", "mcp", "api"],
                "priority": "high",
                "category": "performance",
                "examples": [
                    "Avoid database calls in tool functions - cache data at startup",
                    "Return JSON with consistent structure for AI parsing",
                    "Use async patterns for I/O operations"
                ]
            },
            {
                "rule_id": "archguard-project-structure",
                "title": "ArchGuard Project Organization",
                "guidance": "📁 Organize ArchGuard modules: rules_engine (core logic), server (MCP interface), cli (user interface), config (settings)",
                "rationale": "Clear separation of concerns makes ArchGuard easier to extend and maintain. Each module has a single responsibility.",
                "keywords": ["project", "structure", "organization", "modules", "separation", "concerns", "archguard"],
                "contexts": ["ide-assistant"],
                "tech_stacks": ["python", "project-structure"],
                "priority": "medium",
                "category": "architecture",
                "examples": [
                    "rules_engine/: Core rule matching and retrieval logic",
                    "server/: MCP protocol implementation",
                    "cli/: Command-line interface and user interactions",
                    "config/: Configuration management and rule loading"
                ]
            },
            {
                "rule_id": "config-layered-approach",
                "title": "Layered Configuration System",
                "guidance": "⚙️ Use layered config: global defaults → project .archguard.toml → runtime parameters. Higher layers override lower ones",
                "rationale": "Layered configuration provides flexibility while maintaining sensible defaults. Users can customize at the appropriate level without breaking the system.",
                "keywords": ["config", "configuration", "layered", "toml", "defaults", "override", "settings"],
                "contexts": ["ide-assistant", "agent"],
                "tech_stacks": ["python", "toml", "config"],
                "priority": "medium",
                "category": "architecture",
                "examples": [
                    "Global: ~/.config/archguard/config.toml",
                    "Project: .archguard.toml in project root", 
                    "Runtime: --context, --project CLI parameters"
                ]
            },
            {
                "rule_id": "testing-multiple-transports",
                "title": "Multi-Transport Testing Strategy",
                "guidance": "🧪 Test ArchGuard across all transports: in-memory (fast iteration), stdio (Claude Code), HTTP (production)",
                "rationale": "Different transports have different failure modes. Comprehensive testing ensures reliable operation across all deployment scenarios.",
                "keywords": ["testing", "transport", "stdio", "http", "memory", "mcp", "integration"],
                "contexts": ["ide-assistant"],
                "tech_stacks": ["python", "testing", "mcp"],
                "priority": "high",
                "category": "testing",
                "examples": [
                    "In-memory: Direct function calls for unit testing",
                    "Stdio: Subprocess testing for Claude Code integration",
                    "HTTP: Server testing for production deployment"
                ]
            },
            {
                "rule_id": "context-aware-guidance",
                "title": "Context-Aware Rule Application",
                "guidance": "🎯 Apply different rules based on context: ide-assistant (code completion), agent (automation), desktop-app (conversation)",
                "rationale": "Different contexts have different needs. IDE integration needs precise, actionable advice, while conversational contexts can be more explanatory.",
                "keywords": ["context", "aware", "ide", "assistant", "agent", "desktop", "guidance", "adaptive"],
                "contexts": ["ide-assistant", "agent", "desktop-app"],
                "tech_stacks": ["python", "mcp"],
                "priority": "medium",
                "category": "ux",
                "examples": [
                    "IDE: Terse, actionable suggestions for quick implementation",
                    "Agent: Structured data for programmatic processing",
                    "Desktop: Explanatory guidance with educational context"
                ]
            }
        ]
    
    def find_relevant_rules(self, action: str, code: str = "", context: str = "", 
                          project_context: Optional[Dict] = None) -> List[Dict]:
        """Find rules using keyword matching and context filtering"""
        action_lower = action.lower()
        code_lower = code.lower() if code else ""
        search_text = f"{action_lower} {code_lower}"
        
        relevant_rules = []
        
        for rule in self.rules:
            # Check if context matches (if specified)
            if context and context not in rule.get("contexts", []):
                continue
            
            # Calculate keyword relevance score
            keyword_matches = sum(1 for keyword in rule["keywords"] if keyword in search_text)
            if keyword_matches == 0:
                continue
            
            # Calculate relevance score
            relevance_score = keyword_matches / len(rule["keywords"])
            
            # Boost score for high priority rules
            if rule.get("priority") == "high":
                relevance_score *= 1.5
            elif rule.get("priority") == "medium":
                relevance_score *= 1.2
            
            # Add project context relevance if available
            if project_context:
                server_context = project_context.get("server_context", "")
                if server_context in rule.get("contexts", []):
                    relevance_score *= 1.3
            
            rule_copy = rule.copy()
            rule_copy["relevance_score"] = relevance_score
            relevant_rules.append(rule_copy)
        
        # Sort by relevance score (highest first)
        return sorted(relevant_rules, key=lambda r: r["relevance_score"], reverse=True)
    
    def add_rule(self, rule: Dict) -> bool:
        """Add a new rule to the engine"""
        try:
            # Validate required fields
            required_fields = ["rule_id", "title", "guidance", "keywords", "contexts", "priority", "category"]
            for field in required_fields:
                if field not in rule:
                    return False
            
            # Check for duplicate rule_id
            if any(existing["rule_id"] == rule["rule_id"] for existing in self.rules):
                return False
            
            self.rules.append(rule)
            return True
        except Exception:
            return False
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """Get a specific rule by ID"""
        for rule in self.rules:
            if rule["rule_id"] == rule_id:
                return rule.copy()
        return None
    
    def list_all_rules(self) -> List[Dict]:
        """List all available rules"""
        return [rule.copy() for rule in self.rules]
    
    def get_rules_by_category(self, category: str) -> List[Dict]:
        """Get all rules in a specific category"""
        return [rule.copy() for rule in self.rules if rule.get("category") == category]
    
    def search_rules(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search rules by query text across all fields"""
        query_lower = query.lower()
        scored_rules = []
        
        for rule in self.rules:
            score = 0
            
            # Search in title
            if query_lower in rule.get("title", "").lower():
                score += 3
            
            # Search in guidance
            if query_lower in rule.get("guidance", "").lower():
                score += 2
            
            # Search in keywords
            matching_keywords = sum(1 for keyword in rule.get("keywords", []) 
                                  if query_lower in keyword.lower())
            score += matching_keywords
            
            # Search in rationale
            if query_lower in rule.get("rationale", "").lower():
                score += 1
            
            if score > 0:
                rule_copy = rule.copy()
                rule_copy["search_score"] = score
                scored_rules.append(rule_copy)
        
        # Sort by search score and return top results
        scored_rules.sort(key=lambda r: r["search_score"], reverse=True)
        return scored_rules[:max_results]


class VectorRuleEngine(RuleEngine):
    """Vector-based rule engine for semantic search using Supabase + pgvector"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None, 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        # Load from environment variables if not provided
        self.supabase_url = supabase_url or os.getenv("ARCHGUARD_SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("ARCHGUARD_SUPABASE_KEY")
        self.embedding_model = embedding_model
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase credentials required. Set ARCHGUARD_SUPABASE_URL and "
                "ARCHGUARD_SUPABASE_KEY environment variables or pass as parameters."
            )
        
        # Initialize Supabase client
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        except ImportError:
            raise ImportError("supabase package required for vector search. Install with: pip install supabase")
        
        # Initialize sentence transformer model
        try:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer(embedding_model)
        except ImportError:
            raise ImportError("sentence-transformers package required for vector search. Install with: pip install sentence-transformers")
    
    def find_relevant_rules(self, action: str, code: str = "", context: str = "", 
                          project_context: Optional[Dict] = None) -> List[Dict]:
        """Find rules using semantic similarity search"""
        # Combine action, code, and context into search query
        query_parts = [action]
        if code:
            query_parts.append(f"Code: {code[:500]}")  # Limit code length
        if context:
            query_parts.append(f"Context: {context}")
        
        query_text = " ".join(query_parts)
        
        # Generate embedding for the query
        query_embedding = self.encoder.encode(query_text).tolist()
        
        # Perform vector similarity search
        try:
            # Use Supabase's vector similarity search
            # The embedding column should be compared using cosine similarity
            response = self.supabase.rpc(
                'match_rules',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.7,
                    'match_count': 10
                }
            ).execute()
            
            rules = response.data if response.data else []
            
        except Exception as e:
            # Fallback to basic SQL query if RPC function doesn't exist
            print(f"Vector search RPC failed, falling back to basic query: {e}")
            response = self.supabase.table('rules').select('*').limit(10).execute()
            rules = response.data if response.data else []
        
        # Convert to expected format
        result_rules = []
        for rule in rules:
            result_rules.append({
                "rule_id": rule.get("rule_id", ""),
                "title": rule.get("title", ""),
                "guidance": rule.get("guidance", ""),
                "category": rule.get("category", "general"),
                "priority": rule.get("priority", "medium"),
                "contexts": rule.get("contexts", []),
                "tech_stacks": rule.get("tech_stacks", []),
                "keywords": rule.get("keywords", []),
                "search_score": rule.get("similarity", 0)
            })
        
        return result_rules
    
    def add_rule(self, rule: Dict) -> bool:
        """Add a new rule and compute its embedding"""
        try:
            # Generate embedding for title + guidance
            text_to_embed = f"{rule.get('title', '')} {rule.get('guidance', '')}"
            embedding = self.encoder.encode(text_to_embed).tolist()
            
            # Add embedding to rule data
            rule_data = rule.copy()
            rule_data['embedding'] = embedding
            
            # Insert into Supabase
            response = self.supabase.table('rules').insert(rule_data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error adding rule: {e}")
            return False
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """Get a specific rule by ID"""
        try:
            response = self.supabase.table('rules').select('*').eq('rule_id', rule_id).execute()
            if response.data:
                rule = response.data[0]
                return {
                    "rule_id": rule.get("rule_id", ""),
                    "title": rule.get("title", ""),
                    "guidance": rule.get("guidance", ""),
                    "category": rule.get("category", "general"),
                    "priority": rule.get("priority", "medium"),
                    "contexts": rule.get("contexts", []),
                    "tech_stacks": rule.get("tech_stacks", []),
                    "keywords": rule.get("keywords", [])
                }
            return None
        except Exception as e:
            print(f"Error getting rule: {e}")
            return None
    
    def list_all_rules(self) -> List[Dict]:
        """List all available rules"""
        try:
            response = self.supabase.table('rules').select('*').execute()
            rules = response.data if response.data else []
            
            result_rules = []
            for rule in rules:
                result_rules.append({
                    "rule_id": rule.get("rule_id", ""),
                    "title": rule.get("title", ""),
                    "guidance": rule.get("guidance", ""),
                    "category": rule.get("category", "general"),
                    "priority": rule.get("priority", "medium"),
                    "contexts": rule.get("contexts", []),
                    "tech_stacks": rule.get("tech_stacks", []),
                    "keywords": rule.get("keywords", [])
                })
            
            return result_rules
        except Exception as e:
            print(f"Error listing rules: {e}")
            return []
    
    def search_rules(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search rules using vector similarity"""
        return self.find_relevant_rules(action=query)[:max_results]


# Factory function for easy engine creation
def create_rule_engine(engine_type: str = None, **kwargs) -> RuleEngine:
    """Create a rule engine of the specified type"""
    # Auto-detect engine type based on environment variables
    if engine_type is None:
        engine_type = os.getenv("ARCHGUARD_ENGINE_TYPE", "keyword")
    
    if engine_type == "keyword":
        return KeywordRuleEngine()
    elif engine_type == "vector":
        return VectorRuleEngine(**kwargs)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}. Use 'keyword' or 'vector'.")