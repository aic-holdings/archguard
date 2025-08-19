#!/usr/bin/env python3
"""
Migration script to re-embed all rules using OpenAI cloud API
This replaces local SentenceTransformer embeddings with OpenAI embeddings
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Migrate all existing rules to use OpenAI embeddings"""
    parser = argparse.ArgumentParser(description="Migrate to OpenAI cloud embeddings")
    parser.add_argument("--project-id", default="trzfyaopymlgxehhdfqf", help="Supabase project ID")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for API calls")
    parser.add_argument("--force", action="store_true", help="Re-embed all rules (even those with embeddings)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
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
        
        # Initialize clients
        openai_client = OpenAI(api_key=openai_api_key)
        print("🌐 Connected to OpenAI API")
        
        url = os.getenv('SYMMETRA_SUPABASE_URL')
        key = os.getenv('SYMMETRA_SUPABASE_KEY') 
        if not url or not key:
            print("❌ SYMMETRA_SUPABASE_URL and SYMMETRA_SUPABASE_KEY required")
            return 1
            
        supabase_client = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Get rules to process
        if args.force:
            print("🔄 Force mode: Re-embedding ALL rules")
            result = supabase_client.table('rules').select(
                'id, rule_id, title, guidance, rationale, embedding'
            ).execute()
        else:
            print("📋 Normal mode: Embedding rules without embeddings")
            result = supabase_client.table('rules').select(
                'id, rule_id, title, guidance, rationale, embedding'
            ).is_('embedding', 'null').execute()
        
        rules = result.data
        print(f"📊 Found {len(rules)} rules to process")
        
        if not rules:
            print("✅ No rules need processing")
            return 0
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            for rule in rules:
                rule_id = rule['rule_id']
                title = rule['title']
                has_embedding = rule['embedding'] is not None
                status = "re-embed" if has_embedding else "new embedding"
                print(f"  📋 {rule_id}: {title} ({status})")
            print(f"\n📊 Total cost estimate: ~${len(rules) * 0.02 / 1000:.4f}")
            print("💡 Run without --dry-run to execute")
            return 0
        
        # Process rules in batches
        print(f"🧠 Processing {len(rules)} rules with batch size {args.batch_size}")
        
        for i in range(0, len(rules), args.batch_size):
            batch = rules[i:i + args.batch_size]
            batch_num = i // args.batch_size + 1
            total_batches = (len(rules) + args.batch_size - 1) // args.batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} rules)...")
            
            # Prepare texts for embedding
            texts = []
            for rule in batch:
                title = rule['title']
                guidance = rule['guidance']
                rationale = rule.get('rationale', '') or ''
                # Combine text for embedding
                text = f"{title} {guidance} {rationale}".strip()
                texts.append(text)
            
            # Generate embeddings via OpenAI
            try:
                # Clean texts
                cleaned_texts = [text.replace("\n", " ").strip() for text in texts]
                
                response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=cleaned_texts,
                    dimensions=384  # Match existing schema
                )
                
                embeddings = [item.embedding for item in response.data]
                print(f"✅ Generated {len(embeddings)} embeddings via OpenAI")
                
                # Update database
                for rule, embedding in zip(batch, embeddings):
                    rule_id = rule['rule_id']
                    
                    try:
                        update_result = supabase_client.table('rules').update({
                            'embedding': embedding
                        }).eq('id', rule['id']).execute()
                        
                        if update_result.data:
                            print(f"  ✅ {rule_id}")
                        else:
                            print(f"  ❌ Failed to update {rule_id}")
                            
                    except Exception as e:
                        print(f"  ❌ Database error for {rule_id}: {e}")
                
            except Exception as e:
                print(f"❌ Batch {batch_num} failed: {e}")
                # Fall back to individual processing
                print("🔄 Falling back to individual processing...")
                
                for rule in batch:
                    rule_id = rule['rule_id']
                    title = rule['title']
                    guidance = rule['guidance']
                    rationale = rule.get('rationale', '') or ''
                    text = f"{title} {guidance} {rationale}".strip().replace("\n", " ")
                    
                    try:
                        response = openai_client.embeddings.create(
                            model="text-embedding-3-small",
                            input=[text],
                            dimensions=384
                        )
                        
                        embedding = response.data[0].embedding
                        
                        update_result = supabase_client.table('rules').update({
                            'embedding': embedding
                        }).eq('id', rule['id']).execute()
                        
                        if update_result.data:
                            print(f"  ✅ {rule_id} (individual)")
                        else:
                            print(f"  ❌ Failed to update {rule_id}")
                            
                    except Exception as individual_error:
                        print(f"  ❌ Individual error for {rule_id}: {individual_error}")
        
        print(f"\n🎉 Migration complete!")
        
        # Test the new embeddings
        print("\n🔍 Testing vector search with new embeddings...")
        test_query = "vector database architecture guidance"
        
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=[test_query],
                dimensions=384
            )
            query_embedding = response.data[0].embedding
            
            # Run similarity search
            search_result = supabase_client.rpc('match_rules', {
                'query_embedding': query_embedding,
                'match_threshold': 0.1,
                'match_count': 3
            }).execute()
            
            if search_result.data:
                print("✅ Vector search working with new cloud embeddings!")
                print("🎯 Sample results:")
                for match in search_result.data:
                    similarity = match['similarity']
                    rule_id = match['rule_id']
                    title = match['title']
                    print(f"  📋 {rule_id}: {title} ({similarity:.3f})")
            else:
                print("⚠️ No matches found - check configuration")
                
        except Exception as e:
            print(f"❌ Vector search test failed: {e}")
        
        print("\n🌟 Migration to cloud embeddings completed successfully!")
        print("💡 Benefits:")
        print("  - No local Ollama installation required")
        print("  - Consistent embeddings across all environments") 
        print("  - Reliable cloud infrastructure")
        print("  - Better semantic understanding")
        
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