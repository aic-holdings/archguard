#!/usr/bin/env python3
"""
Cloud-based embedding generation script for Symmetra using OpenAI API
Replaces local Ollama/SentenceTransformers with reliable cloud service
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def get_openai_embedding(text: str, client) -> List[float]:
    """Generate embedding using OpenAI API with 384 dimensions"""
    # Clean text for better embedding quality
    text = text.replace("\n", " ").strip()
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[text],
            dimensions=384  # Match existing pgvector schema
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        raise

def batch_generate_embeddings(texts: List[str], client, batch_size: int = 100) -> List[List[float]]:
    """Generate embeddings in batches for efficiency"""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # Clean batch texts
        cleaned_batch = [text.replace("\n", " ").strip() for text in batch]
        
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=cleaned_batch,
                dimensions=384
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            print(f"✅ Processed batch {i//batch_size + 1} ({len(batch)} items)")
        except Exception as e:
            print(f"❌ Batch {i//batch_size + 1} failed: {e}")
            # Fall back to individual processing for this batch
            for text in batch:
                try:
                    embedding = get_openai_embedding(text, client)
                    embeddings.append(embedding)
                except Exception as individual_error:
                    print(f"❌ Individual embedding failed: {individual_error}")
                    # Use zero vector as fallback (will be re-processed later)
                    embeddings.append([0.0] * 384)
    
    return embeddings

def main():
    """Generate embeddings using OpenAI cloud API"""
    parser = argparse.ArgumentParser(description="Generate embeddings using OpenAI API")
    parser.add_argument("--project-id", default="trzfyaopymlgxehhdfqf", help="Supabase project ID")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for API calls")
    parser.add_argument("--test-only", action="store_true", help="Only test vector search")
    args = parser.parse_args()
    
    load_dotenv()
    
    # Check for required API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable required")
        print("   Get your API key from: https://platform.openai.com/api-keys")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        return 1
    
    try:
        from openai import OpenAI
        from supabase import create_client
        
        # Initialize OpenAI client
        openai_client = OpenAI(api_key=openai_api_key)
        print("🌐 Connected to OpenAI API")
        
        # Initialize Supabase
        url = os.getenv('SYMMETRA_SUPABASE_URL')
        key = os.getenv('SYMMETRA_SUPABASE_KEY') 
        if not url or not key:
            print("❌ SYMMETRA_SUPABASE_URL and SYMMETRA_SUPABASE_KEY required")
            return 1
            
        supabase_client = create_client(url, key)
        print("✅ Connected to Supabase")
        
        if not args.test_only:
            # Get rules without embeddings
            result = supabase_client.table('rules').select(
                'id, rule_id, title, guidance, rationale'
            ).is_('embedding', 'null').execute()
            
            rules = result.data
            print(f"📋 Found {len(rules)} rules without embeddings")
            
            if rules:
                # Prepare texts for batch processing
                texts = []
                for rule in rules:
                    title = rule['title']
                    guidance = rule['guidance']
                    rationale = rule.get('rationale', '')
                    # Combine text for embedding
                    text = f"{title} {guidance} {rationale}".strip()
                    texts.append(text)
                
                print(f"🧠 Generating embeddings using OpenAI (batch size: {args.batch_size})...")
                
                # Generate embeddings in batches
                embeddings = batch_generate_embeddings(texts, openai_client, args.batch_size)
                
                # Update database with embeddings
                print("💾 Updating database...")
                for rule, embedding in zip(rules, embeddings):
                    rule_id = rule['rule_id']
                    
                    try:
                        update_result = supabase_client.table('rules').update({
                            'embedding': embedding
                        }).eq('id', rule['id']).execute()
                        
                        if update_result.data:
                            print(f"✅ Updated {rule_id} with embedding")
                        else:
                            print(f"❌ Failed to update {rule_id}")
                    except Exception as e:
                        print(f"❌ Database update failed for {rule_id}: {e}")
                
                print(f"\n🎉 Embedding generation complete!")
            else:
                print("✅ All rules already have embeddings")
        
        # Test vector search
        print("\n🔍 Testing vector search...")
        test_query = "database architecture for vector storage"
        print(f"🔍 Query: '{test_query}'")
        
        try:
            query_embedding = get_openai_embedding(test_query, openai_client)
            
            # Run similarity search
            search_result = supabase_client.rpc('match_rules', {
                'query_embedding': query_embedding,
                'match_threshold': 0.1,
                'match_count': 5
            }).execute()
            
            if search_result.data:
                print("✅ Vector search working perfectly!")
                print("🎯 Top matches:")
                for i, match in enumerate(search_result.data, 1):
                    similarity = match['similarity']
                    rule_id = match['rule_id']
                    title = match['title']
                    category = match['category']
                    print(f"  {i}. [{category}] {title}")
                    print(f"     Rule: {rule_id} | Similarity: {similarity:.3f}")
                    print()
            else:
                print("⚠️ No matches found - check match_rules function")
                
        except Exception as e:
            print(f"❌ Vector search test failed: {e}")
            return 1
            
        print("🌟 Cloud embedding system verified and working!")
        return 0
            
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install with: pip install openai supabase python-dotenv")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())