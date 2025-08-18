-- Bootstrap ArchGuard with initial rule set
-- These are global rules that help build ArchGuard itself

INSERT INTO rules (rule_id, title, guidance, rationale, category, priority, contexts, tech_stacks, keywords, project_id)
VALUES 
    -- Vector Database Architecture Rules
    (
        'vector-db-choice',
        'Vector Database Selection',
        '🗄️ For vector storage, choose: ChromaDB (development/prototyping), Weaviate (production), or pgvector (PostgreSQL integration)',
        'Different vector databases excel in different contexts. ChromaDB is perfect for development, Weaviate scales well in production, and pgvector integrates seamlessly with existing PostgreSQL infrastructure.',
        'architecture',
        'high',
        ARRAY['ide-assistant', 'agent', 'desktop-app'],
        ARRAY['python', 'ai', 'ml', 'database'],
        ARRAY['vector', 'database', 'embedding', 'storage', 'chroma', 'weaviate', 'pgvector', 'chromadb'],
        NULL  -- Global rule
    ),
    (
        'embedding-model-selection',
        'Text Embedding Model Choice',
        '🧠 Use sentence-transformers for rule embeddings: all-MiniLM-L6-v2 (fast, 384d) or all-mpnet-base-v2 (quality, 768d)',
        'Sentence transformers provide high-quality semantic embeddings. MiniLM is faster and smaller, while mpnet provides better semantic understanding for complex texts.',
        'ai-ml',
        'medium',
        ARRAY['ide-assistant', 'agent'],
        ARRAY['python', 'ai', 'ml', 'nlp'],
        ARRAY['embedding', 'model', 'sentence', 'transformer', 'semantic', 'similarity', 'minilm', 'mpnet'],
        NULL
    ),
    (
        'sqlite-vector-hybrid',
        'Hybrid SQLite + Vector Storage',
        '💾 Store rule metadata in SQLite, vectors in dedicated vector DB. Link via rule_id for best performance and flexibility',
        'Hybrid storage leverages SQLite''s ACID properties for metadata while using specialized vector databases for semantic search. This provides both relational integrity and vector performance.',
        'architecture',
        'medium',
        ARRAY['ide-assistant', 'agent'],
        ARRAY['python', 'sqlite', 'database'],
        ARRAY['sqlite', 'database', 'metadata', 'hybrid', 'storage', 'relational', 'vector', 'architecture'],
        NULL
    ),
    (
        'mcp-tool-design',
        'MCP Tool Performance Design',
        '🔧 MCP tools should be stateless, fast (<100ms response), and return structured data optimized for AI consumption',
        'MCP tools are called frequently during AI workflows. Fast, stateless tools provide better user experience and enable real-time guidance without breaking flow.',
        'performance',
        'high',
        ARRAY['ide-assistant', 'agent'],
        ARRAY['python', 'mcp', 'api'],
        ARRAY['mcp', 'tool', 'design', 'performance', 'stateless', 'fast', 'structured', 'api'],
        NULL
    ),
    (
        'archguard-project-structure',
        'ArchGuard Project Organization',
        '📁 Organize ArchGuard modules: rules_engine (core logic), server (MCP interface), cli (user interface), config (settings)',
        'Clear separation of concerns makes ArchGuard easier to extend and maintain. Each module has a single responsibility.',
        'architecture',
        'medium',
        ARRAY['ide-assistant'],
        ARRAY['python', 'project-structure'],
        ARRAY['project', 'structure', 'organization', 'modules', 'separation', 'concerns', 'archguard'],
        NULL
    ),
    (
        'config-layered-approach',
        'Layered Configuration System',
        '⚙️ Use layered config: global defaults → project .archguard.toml → runtime parameters. Higher layers override lower ones',
        'Layered configuration provides flexibility while maintaining sensible defaults. Users can customize at the appropriate level without breaking the system.',
        'architecture',
        'medium',
        ARRAY['ide-assistant', 'agent'],
        ARRAY['python', 'toml', 'config'],
        ARRAY['config', 'configuration', 'layered', 'toml', 'defaults', 'override', 'settings'],
        NULL
    ),
    (
        'testing-multiple-transports',
        'Multi-Transport Testing Strategy',
        '🧪 Test ArchGuard across all transports: in-memory (fast iteration), stdio (Claude Code), HTTP (production)',
        'Different transports have different failure modes. Comprehensive testing ensures reliable operation across all deployment scenarios.',
        'testing',
        'high',
        ARRAY['ide-assistant'],
        ARRAY['python', 'testing', 'mcp'],
        ARRAY['testing', 'transport', 'stdio', 'http', 'memory', 'mcp', 'integration'],
        NULL
    ),
    (
        'context-aware-guidance',
        'Context-Aware Rule Application',
        '🎯 Apply different rules based on context: ide-assistant (code completion), agent (automation), desktop-app (conversation)',
        'Different contexts have different needs. IDE integration needs precise, actionable advice, while conversational contexts can be more explanatory.',
        'ux',
        'medium',
        ARRAY['ide-assistant', 'agent', 'desktop-app'],
        ARRAY['python', 'mcp'],
        ARRAY['context', 'aware', 'ide', 'assistant', 'agent', 'desktop', 'guidance', 'adaptive'],
        NULL
    ),
    (
        'supabase-rls-security',
        'Supabase Row Level Security Design',
        '🔒 Use RLS policies for project-based access control. Structure as: global rules (visible to all) + project rules (scoped by user access)',
        'Row Level Security provides automatic, database-level access control that cannot be bypassed by application code. Essential for multi-tenant rule management.',
        'security',
        'high',
        ARRAY['ide-assistant', 'agent'],
        ARRAY['supabase', 'postgresql', 'security'],
        ARRAY['rls', 'security', 'access', 'control', 'project', 'scoped', 'supabase', 'postgres'],
        NULL
    ),
    (
        'pgvector-performance-tuning',
        'pgvector Index Optimization',
        '⚡ Use ivfflat index with lists=100 for vector similarity. Cosine distance for normalized embeddings, L2 for absolute similarity',
        'pgvector performance depends heavily on proper indexing. IVFFLAT provides good balance of speed and accuracy for most use cases.',
        'performance',
        'medium',
        ARRAY['ide-assistant', 'agent'],
        ARRAY['postgresql', 'vector', 'database'],
        ARRAY['pgvector', 'index', 'performance', 'ivfflat', 'cosine', 'similarity', 'optimization'],
        NULL
    )
ON CONFLICT (rule_id) DO UPDATE SET
    title = EXCLUDED.title,
    guidance = EXCLUDED.guidance,
    rationale = EXCLUDED.rationale,
    updated_at = NOW();