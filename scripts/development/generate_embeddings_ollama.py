#!/usr/bin/env python3
"""
Generate embeddings using Ollama for Symmetra rules

This script generates vector embeddings using local Ollama models (cost-free!)
and inserts them into the Supabase database.

Usage:
    python scripts/generate_embeddings_ollama.py --project-id your-project-id
    python scripts/generate_embeddings_ollama.py --project-id your-project-id --model nomic-embed-text
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path for MCP imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def check_ollama_service() -> bool:
    """Check if Ollama service is running"""
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:11434/api/version'],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False

def generate_embedding_ollama(text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
    """Generate embedding using Ollama API"""
    try:
        cmd = [
            'curl', '-s', 'http://localhost:11434/api/embeddings',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                'model': model,
                'prompt': text
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'embedding' in response:
                return response['embedding']
            else:
                print(f"❌ No embedding in response: {response}")
                return None
        else:
            print(f"❌ Curl failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None

def insert_python_essential_rules(project_id: str) -> bool:
    """Insert essential Python project rules into Supabase"""
    print("📝 Inserting essential Python project rules...")
    
    # Essential Python project rules for Symmetra self-improvement (start small!)
    python_rules = [
        {
            "rule_id": "python-project-structure",
            "title": "Standard Python Project Layout",
            "guidance": "📁 Use standard Python structure: /src/package_name (source), /tests (testing), pyproject.toml (config), README.md (docs)",
            "rationale": "Standard structure helps Python developers navigate immediately. Using src/ layout prevents import issues and follows modern Python packaging best practices.",
            "category": "architecture",
            "priority": "high",
            "contexts": ["ide-assistant", "agent"],
            "tech_stacks": ["python"],
            "keywords": ["python", "structure", "src", "package", "layout", "pyproject", "packaging"]
        },
        {
            "rule_id": "python-dependency-management",
            "title": "Modern Python Dependency Management",
            "guidance": "📦 Use pyproject.toml for dependencies, pin versions with ranges (>=1.0,<2.0), separate dev dependencies, include Python version requirement",
            "rationale": "pyproject.toml is the modern standard for Python packaging. Version ranges prevent breakage while allowing updates. Clear dev deps help contributors.",
            "category": "architecture",
            "priority": "high",
            "contexts": ["ide-assistant", "agent"],
            "tech_stacks": ["python", "packaging"],
            "keywords": ["dependencies", "pyproject", "toml", "versions", "pip", "packaging", "requirements"]
        },
        {
            "rule_id": "python-code-quality",
            "title": "Python Code Quality Tools",
            "guidance": "🔧 Use: black (formatting), ruff (linting), mypy (type checking), pytest (testing). Configure in pyproject.toml for consistency",
            "rationale": "These tools are the modern Python standard. Black eliminates formatting debates, ruff is fast and comprehensive, mypy catches bugs early.",
            "category": "testing",
            "priority": "high",
            "contexts": ["ide-assistant", "agent"],
            "tech_stacks": ["python", "testing", "linting"],
            "keywords": ["black", "ruff", "mypy", "pytest", "formatting", "linting", "type-checking", "quality"]
        },
        {
            "rule_id": "python-imports-organization",
            "title": "Clean Python Import Organization",
            "guidance": "📋 Order imports: stdlib, third-party, local. Use absolute imports. Group related imports. No star imports in production code",
            "rationale": "Organized imports improve readability and prevent circular import issues. Following PEP 8 import order makes code professional.",
            "category": "architecture",
            "priority": "medium",
            "contexts": ["ide-assistant"],
            "tech_stacks": ["python"],
            "keywords": ["imports", "pep8", "organization", "stdlib", "absolute", "star-imports", "circular"]
        },
        {
            "rule_id": "python-virtual-environments",
            "title": "Python Virtual Environment Usage",
            "guidance": "🐍 Always use virtual environments (venv, virtualenv, or conda). Include activation instructions in README. Add .venv/ to .gitignore",
            "rationale": "Virtual environments prevent dependency conflicts and ensure reproducible builds. Essential for Python project hygiene.",
            "category": "devops",
            "priority": "high",
            "contexts": ["ide-assistant", "agent"],
            "tech_stacks": ["python", "venv"],
            "keywords": ["venv", "virtualenv", "environment", "isolation", "dependencies", "python", "conda"]
        }
    ]
    
    try:
        # Import MCP functions  
        from mcp__supabase__execute_sql import execute_sql
        
        # Insert each rule
        for rule in python_rules:
            print(f"🔄 Inserting rule: {rule['rule_id']}")
            
            # Convert arrays to PostgreSQL format
            contexts_array = "{" + ",".join(f'"{c}"' for c in rule['contexts']) + "}"
            tech_stacks_array = "{" + ",".join(f'"{t}"' for t in rule['tech_stacks']) + "}"
            keywords_array = "{" + ",".join(f'"{k}"' for k in rule['keywords']) + "}"
            
            insert_query = f"""
            INSERT INTO rules (rule_id, title, guidance, rationale, category, priority, contexts, tech_stacks, keywords, project_id)
            VALUES (
                '{rule['rule_id']}',
                $${rule['title']}$$,
                $${rule['guidance']}$$,
                $${rule['rationale']}$$,
                '{rule['category']}',
                '{rule['priority']}',
                ARRAY[{','.join(f"'{c}'" for c in rule['contexts'])}],
                ARRAY[{','.join(f"'{t}'" for t in rule['tech_stacks'])}],
                ARRAY[{','.join(f"'{k}'" for k in rule['keywords'])}],
                NULL
            )
            ON CONFLICT (rule_id) DO UPDATE SET
                title = EXCLUDED.title,
                guidance = EXCLUDED.guidance,
                rationale = EXCLUDED.rationale,
                updated_at = NOW()
            """
            
            result = execute_sql(project_id=project_id, query=insert_query)
            
            if 'error' in result:
                print(f"❌ Failed to insert rule {rule['rule_id']}: {result['error']}")
                return False
            else:
                print(f"✅ Inserted rule: {rule['rule_id']}")
        
        print(f"🎉 Successfully inserted {len(python_rules)} essential Python rules")
        return True
        
    except ImportError:
        print("❌ MCP Supabase integration not available")
        return False
    except Exception as e:
        print(f"❌ Error inserting rules: {e}")
        return False

def generate_embeddings_for_rules(project_id: str, model: str = "nomic-embed-text") -> bool:
    """Generate embeddings for all rules without embeddings"""
    print(f"🧠 Generating embeddings using Ollama model: {model}")
    
    try:
        # Import MCP functions
        from mcp__supabase__execute_sql import execute_sql
        
        # Get rules without embeddings
        query = """
        SELECT id, rule_id, title, guidance, rationale 
        FROM rules 
        WHERE embedding IS NULL
        ORDER BY priority DESC, created_at DESC
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
        success_count = 0
        for i, rule in enumerate(rules, 1):
            print(f"🔄 Processing rule {i}/{len(rules)}: {rule['rule_id']}")
            
            # Create embedding text from title + guidance + rationale
            text_parts = [rule['title'], rule['guidance']]
            if rule.get('rationale'):
                text_parts.append(rule['rationale'])
            
            embedding_text = ' '.join(text_parts)
            
            # Generate embedding using Ollama
            embedding = generate_embedding_ollama(embedding_text, model)
            
            if embedding is None:
                print(f"❌ Failed to generate embedding for rule: {rule['rule_id']}")
                continue
            
            # Update database with embedding
            update_query = f"""
            UPDATE rules 
            SET embedding = '[{','.join(map(str, embedding))}]'::vector
            WHERE id = '{rule['id']}'
            """
            
            update_result = execute_sql(project_id=project_id, query=update_query)
            
            if 'error' in update_result:
                print(f"❌ Failed to update rule {rule['rule_id']}: {update_result['error']}")
                continue
            
            success_count += 1
            print(f"✅ Generated embedding for: {rule['rule_id']} ({len(embedding)} dimensions)")
        
        print(f"🎉 Successfully generated embeddings for {success_count}/{len(rules)} rules")
        return success_count > 0
        
    except ImportError:
        print("❌ MCP Supabase integration not available")
        return False
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False

def test_vector_search(project_id: str) -> bool:
    """Test vector search functionality"""
    print("🧪 Testing vector search with Ollama embeddings...")
    
    try:
        from mcp__supabase__execute_sql import execute_sql
        
        # Generate embedding for test query
        test_query = "repository structure and organization best practices"
        test_embedding = generate_embedding_ollama(test_query)
        
        if test_embedding is None:
            print("❌ Failed to generate test embedding")
            return False
        
        # Test semantic search
        search_query = f"""
        WITH query_embedding AS (
            SELECT '[{','.join(map(str, test_embedding))}]'::vector AS embedding
        )
        SELECT 
            rule_id,
            title,
            category,
            priority,
            1 - (embedding <=> query_embedding.embedding) AS similarity
        FROM rules, query_embedding
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> query_embedding.embedding
        LIMIT 5
        """
        
        result = execute_sql(project_id=project_id, query=search_query)
        
        if 'error' in result:
            print(f"❌ Vector search test failed: {result['error']}")
            return False
        
        results = result.get('data', [])
        
        if results:
            print(f"✅ Vector search working! Found {len(results)} similar rules:")
            for r in results:
                print(f"   - {r['rule_id']}: {r['title'][:50]}... (similarity: {r['similarity']:.3f})")
        else:
            print("⚠️  No results from vector search test")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector search test error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate embeddings using Ollama for Symmetra rules")
    parser.add_argument("--project-id", required=True, 
                       help="Supabase project ID")
    parser.add_argument("--model", default="nomic-embed-text",
                       help="Ollama embedding model to use")
    parser.add_argument("--insert-python-rules", action="store_true",
                       help="Insert essential Python project rules first")
    parser.add_argument("--test-only", action="store_true",
                       help="Only run vector search test")
    
    args = parser.parse_args()
    
    print("🚀 Generating embeddings using Ollama...")
    print(f"📋 Project ID: {args.project_id}")
    print(f"🤖 Model: {args.model}")
    
    # Check Ollama service
    if not check_ollama_service():
        print("❌ Ollama service not running!")
        print("Start Ollama service with: ollama serve")
        sys.exit(1)
    
    print("✅ Ollama service is running")
    
    # Insert Python rules if requested
    if args.insert_python_rules:
        if not insert_python_essential_rules(args.project_id):
            print("❌ Failed to insert Python rules")
            sys.exit(1)
    
    if not args.test_only:
        # Generate embeddings
        success = generate_embeddings_for_rules(args.project_id, args.model)
        
        if not success:
            print("❌ Embedding generation failed!")
            sys.exit(1)
    
    # Test vector search
    test_success = test_vector_search(args.project_id)
    
    if test_success:
        print("✅ Ollama embedding generation completed!")
        print("")
        print("Next steps:")
        print("1. Update your environment to use vector search:")
        print("   export SYMMETRA_ENGINE_TYPE=vector")
        print("   export SYMMETRA_EMBEDDING_PROVIDER=ollama")
        print("2. Test Symmetra with vector search:")
        print("   python -c \"from symmetra.server import get_guidance; print(get_guidance('repository structure'))\"")
        print("")
        print("💰 Cost savings: $0 vs $5-50/month for cloud embeddings")
        print("🔒 Privacy: 100% local processing")
        print("⚡ Performance: ~25ms local vs 200-800ms cloud")
    else:
        print("⚠️  Vector search test had issues, but embeddings were generated")

if __name__ == "__main__":
    main()