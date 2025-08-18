#!/usr/bin/env python3
"""
Simple embedding generation script for ArchGuard MVP testing
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Generate embeddings for rules without them"""
    load_dotenv()
    
    try:
        from sentence_transformers import SentenceTransformer
        from supabase import create_client
        import numpy as np
        
        # Initialize
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("📥 Loaded embedding model: all-MiniLM-L6-v2")
        
        url = os.getenv('ARCHGUARD_SUPABASE_URL')
        key = os.getenv('ARCHGUARD_SUPABASE_KEY')
        client = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Get rules without embeddings
        result = client.table('rules').select('id, rule_id, title, guidance, rationale').is_('embedding', 'null').execute()
        rules = result.data
        print(f"📋 Found {len(rules)} rules without embeddings")
        
        # Generate embeddings
        for rule in rules:
            rule_id = rule['rule_id']
            title = rule['title']
            guidance = rule['guidance']
            rationale = rule.get('rationale', '')
            
            # Combine text for embedding
            text = f"{title} {guidance} {rationale}".strip()
            print(f"🧠 Processing: {rule_id}")
            
            # Generate embedding
            embedding = model.encode(text).tolist()
            
            # Update rule with embedding
            update_result = client.table('rules').update({
                'embedding': embedding
            }).eq('id', rule['id']).execute()
            
            if update_result.data:
                print(f"✅ Updated {rule_id} with embedding")
            else:
                print(f"❌ Failed to update {rule_id}")
        
        print(f"\n🎉 Embedding generation complete!")
        
        # Test vector search
        print("\n🔍 Testing vector search...")
        test_query = "vector database for storing embeddings"
        query_embedding = model.encode(test_query).tolist()
        
        # Run similarity search
        search_result = client.rpc('match_rules', {
            'query_embedding': query_embedding,
            'match_threshold': 0.1,
            'match_count': 3
        }).execute()
        
        if search_result.data:
            print("✅ Vector search working!")
            for match in search_result.data:
                print(f"  📋 {match['rule_id']}: {match['title']} (similarity: {match['similarity']:.3f})")
        else:
            print("⚠️ Vector search function not available - will need to implement manually")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()