#!/usr/bin/env python3
"""
Symmetra Database Setup Script

This script sets up the Symmetra database using:
1. Supabase CLI (preferred method)
2. MCP Supabase integration (fallback)

Usage:
    python scripts/setup_database.py --project-id your-project-id
    python scripts/setup_database.py --project-id your-project-id --force-mcp
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for MCP imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def check_supabase_cli() -> bool:
    """Check if Supabase CLI is available"""
    try:
        result = subprocess.run(['npx', 'supabase', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def run_migration_with_cli(project_id: str, migration_files: List[Path]) -> bool:
    """Run migrations using Supabase CLI"""
    print("🚀 Using Supabase CLI for database setup...")
    
    try:
        # Check if already linked
        result = subprocess.run(['npx', 'supabase', 'status'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"📡 Linking to Supabase project: {project_id}")
            result = subprocess.run(['npx', 'supabase', 'link', '--project-ref', project_id],
                                  check=True)
        
        # Run each migration file
        for migration_file in migration_files:
            print(f"📝 Running migration: {migration_file.name}")
            
            # Read SQL content
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            # Execute via Supabase CLI
            result = subprocess.run(['npx', 'supabase', 'db', 'reset', '--with-data=false'],
                                  input=sql_content, text=True, capture_output=True)
            
            if result.returncode != 0:
                print(f"❌ Migration failed: {migration_file.name}")
                print(f"Error: {result.stderr}")
                return False
            else:
                print(f"✅ Migration completed: {migration_file.name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Supabase CLI error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def run_migration_with_mcp(project_id: str, migration_files: List[Path]) -> bool:
    """Run migrations using MCP Supabase integration"""
    print("🔧 Using MCP Supabase integration for database setup...")
    
    try:
        # Import MCP tools (this requires the MCP server to be available)
        from mcp__supabase__execute_sql import execute_sql
        from mcp__supabase__apply_migration import apply_migration
        
        # Run each migration file
        for migration_file in migration_files:
            print(f"📝 Running migration: {migration_file.name}")
            
            # Read SQL content
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            # Execute via MCP
            if 'CREATE' in sql_content.upper() or 'ALTER' in sql_content.upper():
                # Use apply_migration for DDL
                result = apply_migration(
                    project_id=project_id,
                    name=migration_file.stem,
                    query=sql_content
                )
            else:
                # Use execute_sql for DML
                result = execute_sql(
                    project_id=project_id,
                    query=sql_content
                )
            
            if 'error' in result:
                print(f"❌ Migration failed: {migration_file.name}")
                print(f"Error: {result['error']}")
                return False
            else:
                print(f"✅ Migration completed: {migration_file.name}")
        
        return True
        
    except ImportError:
        print("❌ MCP Supabase integration not available")
        print("   Make sure Claude Code has the Supabase MCP server configured")
        return False
    except Exception as e:
        print(f"❌ MCP error: {e}")
        return False

def get_migration_files() -> List[Path]:
    """Get list of migration files in order"""
    migrations_dir = Path(__file__).parent.parent / "sql" / "migrations"
    
    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        sys.exit(1)
    
    # Get all .sql files and sort by filename
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print(f"❌ No migration files found in: {migrations_dir}")
        sys.exit(1)
    
    return migration_files

def generate_embeddings(project_id: str) -> bool:
    """Generate embeddings for bootstrap rules"""
    print("🧠 Generating embeddings for bootstrap rules...")
    
    try:
        # Try to import required packages
        from sentence_transformers import SentenceTransformer
        
        # Initialize model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("📥 Loaded embedding model: all-MiniLM-L6-v2")
        
        # TODO: Implement embedding generation
        # This would require:
        # 1. Query rules without embeddings
        # 2. Generate embeddings for each rule
        # 3. Update database with embeddings
        
        print("⚠️  Embedding generation not yet implemented")
        print("   Bootstrap rules created without embeddings")
        print("   Vector search will be available after embedding generation")
        
        return True
        
    except ImportError:
        print("⚠️  sentence-transformers not installed")
        print("   Install with: pip install sentence-transformers")
        print("   Bootstrap rules created without embeddings")
        return True
    except Exception as e:
        print(f"⚠️  Embedding generation failed: {e}")
        print("   Bootstrap rules created without embeddings")
        return True

def main():
    parser = argparse.ArgumentParser(description="Set up Symmetra database")
    parser.add_argument("--project-id", required=True, 
                       help="Supabase project ID")
    parser.add_argument("--force-mcp", action="store_true",
                       help="Force use of MCP instead of CLI")
    parser.add_argument("--skip-embeddings", action="store_true",
                       help="Skip embedding generation")
    
    args = parser.parse_args()
    
    print("🏗️  Setting up Symmetra database...")
    print(f"📋 Project ID: {args.project_id}")
    
    # Get migration files
    migration_files = get_migration_files()
    print(f"📁 Found {len(migration_files)} migration files")
    
    # Choose method
    success = False
    if not args.force_mcp and check_supabase_cli():
        success = run_migration_with_cli(args.project_id, migration_files)
    
    if not success:
        print("🔄 Falling back to MCP integration...")
        success = run_migration_with_mcp(args.project_id, migration_files)
    
    if not success:
        print("❌ Database setup failed!")
        sys.exit(1)
    
    # Generate embeddings
    if not args.skip_embeddings:
        generate_embeddings(args.project_id)
    
    print("✅ Database setup completed successfully!")
    print("")
    print("Next steps:")
    print("1. Set environment variables:")
    print(f"   export SYMMETRA_SUPABASE_URL=https://{args.project_id}.supabase.co")
    print("   export SYMMETRA_SUPABASE_KEY=your-anon-key")
    print("   export SYMMETRA_ENGINE_TYPE=vector  # to enable vector search")
    print("2. Generate embeddings:")
    print("   python scripts/generate_embeddings.py")
    print("3. Test the setup:")
    print("   python -c \"from symmetra.rules_engine import create_rule_engine; print('✅ Success')\"")

if __name__ == "__main__":
    main()