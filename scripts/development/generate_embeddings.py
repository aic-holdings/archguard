#!/usr/bin/env python3
"""
Generate embeddings for ArchGuard rules

This script generates vector embeddings for all rules that don't have them yet.
Can use either Supabase CLI or MCP integration.

Usage:
    python scripts/generate_embeddings.py --project-id your-project-id
    python scripts/generate_embeddings.py --project-id your-project-id --model all-mpnet-base-v2
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def generate_embeddings_mcp(project_id: str, model_name: str) -> bool:
    """Generate embeddings using MCP Supabase integration"""
    print(f"🧠 Generating embeddings using model: {model_name}")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Initialize model
        model = SentenceTransformer(model_name)
        print(f"📥 Loaded model: {model_name}")
        
        # Import MCP functions
        from mcp__supabase__execute_sql import execute_sql
        
        # Get rules without embeddings
        query = """
        SELECT id, rule_id, title, guidance, rationale 
        FROM rules 
        WHERE embedding IS NULL
        """
        
        result = execute_sql(project_id=project_id, query=query)
        
        if 'error' in result:
            print(f"❌ Failed to fetch rules: {result['error']}")
            return False
        
        rules = result.get('data', [])
        print(f"📋 Found {len(rules)} rules without embeddings")
        
        if not rules:
            print("✅ All rules already have embeddings")
            return True
        
        # Generate embeddings for each rule
        for i, rule in enumerate(rules, 1):
            print(f"🔄 Processing rule {i}/{len(rules)}: {rule['rule_id']}")
            
            # Create embedding text from title + guidance + rationale
            text_parts = [rule['title'], rule['guidance']]
            if rule.get('rationale'):
                text_parts.append(rule['rationale'])
            
            embedding_text = ' '.join(text_parts)
            
            # Generate embedding
            embedding = model.encode(embedding_text).tolist()
            
            # Update database with embedding
            update_query = f"""
            UPDATE rules 
            SET embedding = '[{','.join(map(str, embedding))}]'::vector
            WHERE id = '{rule['id']}'
            """
            
            update_result = execute_sql(project_id=project_id, query=update_query)
            
            if 'error' in update_result:
                print(f"❌ Failed to update rule {rule['rule_id']}: {update_result['error']}")
                return False
            
            print(f"✅ Generated embedding for: {rule['rule_id']}")
        
        print(f"🎉 Successfully generated embeddings for {len(rules)} rules")
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install with: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False

def test_vector_search(project_id: str) -> bool:
    """Test vector search functionality"""
    print("🧪 Testing vector search...")
    
    try:
        from mcp__supabase__execute_sql import execute_sql
        
        # Test semantic search
        test_query = """
        WITH query_embedding AS (
            SELECT embedding FROM rules WHERE rule_id = 'vector-db-choice' LIMIT 1
        )
        SELECT 
            rule_id,
            title,
            1 - (embedding <=> query_embedding.embedding) AS similarity
        FROM rules, query_embedding
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> query_embedding.embedding
        LIMIT 3
        """
        
        result = execute_sql(project_id=project_id, query=test_query)
        
        if 'error' in result:
            print(f"❌ Vector search test failed: {result['error']}")
            return False
        
        results = result.get('data', [])
        
        if results:
            print("✅ Vector search working! Similar rules:")
            for r in results:
                print(f"   - {r['rule_id']}: {r['title']} (similarity: {r['similarity']:.3f})")
        else:
            print("⚠️  No results from vector search test")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector search test error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for ArchGuard rules")
    parser.add_argument("--project-id", required=True, 
                       help="Supabase project ID")
    parser.add_argument("--model", default="all-MiniLM-L6-v2",
                       choices=["all-MiniLM-L6-v2", "all-mpnet-base-v2"],
                       help="Embedding model to use")
    parser.add_argument("--test", action="store_true",
                       help="Run vector search test after generation")
    
    args = parser.parse_args()
    
    print("🚀 Starting embedding generation...")
    print(f"📋 Project ID: {args.project_id}")
    print(f"🤖 Model: {args.model}")
    
    # Generate embeddings
    success = generate_embeddings_mcp(args.project_id, args.model)
    
    if not success:
        print("❌ Embedding generation failed!")
        sys.exit(1)
    
    # Test vector search if requested
    if args.test:
        test_success = test_vector_search(args.project_id)
        if not test_success:
            print("⚠️  Vector search test failed, but embeddings were generated")
    
    print("✅ Embedding generation completed!")
    print("")
    print("Next steps:")
    print("1. Update your environment to use vector search:")
    print("   export ARCHGUARD_ENGINE_TYPE=vector")
    print("2. Test ArchGuard with vector search:")
    print("   python -c \"from archguard.server import get_guidance; print(get_guidance('database design'))\"")

if __name__ == "__main__":
    main()