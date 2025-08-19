#!/usr/bin/env python3
"""
Setup Ollama for Symmetra embeddings

This script sets up Ollama with nomic-embed-text for local, cost-free embedding generation.
Provides significant cost savings compared to cloud embedding APIs.

Usage:
    python scripts/setup_ollama_embeddings.py
    python scripts/setup_ollama_embeddings.py --model nomic-embed-text:latest
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

def check_ollama_installed() -> bool:
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ollama_instructions():
    """Provide Ollama installation instructions"""
    print("📦 Ollama not found. Please install Ollama:")
    print("")
    print("macOS/Linux:")
    print("  curl -fsSL https://ollama.com/install.sh | sh")
    print("")
    print("Windows:")
    print("  Download from https://ollama.com/download")
    print("")
    print("After installation, restart your terminal and run this script again.")

def pull_embedding_model(model_name: str) -> bool:
    """Pull the embedding model from Ollama"""
    print(f"📥 Pulling embedding model: {model_name}")
    print("This may take a few minutes for first-time download...")
    
    try:
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"❌ Failed to pull {model_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def test_embedding_generation(model_name: str) -> bool:
    """Test embedding generation with Ollama"""
    print(f"🧪 Testing embedding generation with {model_name}")
    
    test_text = "Vector database selection for machine learning applications"
    
    try:
        # Use Ollama API directly for embeddings
        cmd = [
            'curl', '-s', 'http://localhost:11434/api/embeddings',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                'model': model_name,
                'prompt': test_text
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'embedding' in response:
                embedding_length = len(response['embedding'])
                print(f"✅ Generated embedding with {embedding_length} dimensions")
                print(f"📊 First 5 values: {response['embedding'][:5]}")
                return True
            else:
                print(f"❌ No embedding in response: {response}")
                return False
        else:
            print(f"❌ Curl failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing embeddings: {e}")
        return False

def create_ollama_config():
    """Create Ollama configuration for Symmetra"""
    config = {
        "embedding": {
            "provider": "ollama",
            "model": "nomic-embed-text:latest",
            "endpoint": "http://localhost:11434",
            "dimensions": 768,  # nomic-embed-text dimensions
            "max_tokens": 8192,
            "local": True,
            "cost_per_token": 0.0  # Free!
        },
        "fallback": {
            "provider": "sentence-transformers",
            "model": "all-MiniLM-L6-v2",
            "dimensions": 384,
            "note": "Fallback if Ollama unavailable"
        }
    }
    
    config_path = Path(__file__).parent.parent / "config" / "embedding.json"
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📝 Created embedding config: {config_path}")
    return config_path

def update_env_file(model_name: str):
    """Update .env file with Ollama configuration"""
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print("⚠️  .env file not found, creating one...")
        env_path.touch()
    
    # Read existing content
    env_content = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.readlines()
    
    # Update or add Ollama settings
    ollama_settings = [
        "# Ollama Embedding Configuration\n",
        "SYMMETRA_EMBEDDING_PROVIDER=ollama\n",
        f"SYMMETRA_EMBEDDING_MODEL={model_name}\n",
        "SYMMETRA_OLLAMA_ENDPOINT=http://localhost:11434\n",
        "SYMMETRA_EMBEDDING_DIMENSIONS=768\n",
        "\n"
    ]
    
    # Remove existing Ollama settings
    env_content = [line for line in env_content 
                   if not line.startswith('SYMMETRA_EMBEDDING_') 
                   and not line.startswith('SYMMETRA_OLLAMA_')]
    
    # Add new settings
    env_content.extend(ollama_settings)
    
    with open(env_path, 'w') as f:
        f.writelines(env_content)
    
    print(f"✅ Updated {env_path} with Ollama configuration")

def main():
    parser = argparse.ArgumentParser(description="Setup Ollama embeddings for Symmetra")
    parser.add_argument("--model", default="nomic-embed-text:latest",
                       help="Embedding model to use (default: nomic-embed-text:latest)")
    parser.add_argument("--test-only", action="store_true",
                       help="Only test existing setup")
    
    args = parser.parse_args()
    
    print("🚀 Setting up Ollama embeddings for Symmetra...")
    print(f"📋 Target model: {args.model}")
    
    # Check Ollama installation
    if not check_ollama_installed():
        install_ollama_instructions()
        sys.exit(1)
    
    print("✅ Ollama is installed")
    
    if not args.test_only:
        # Pull embedding model
        if not pull_embedding_model(args.model):
            print("❌ Failed to pull embedding model")
            sys.exit(1)
        
        # Create configuration
        create_ollama_config()
        update_env_file(args.model)
    
    # Test embedding generation
    print("\n" + "="*50)
    print("🧪 Testing embedding generation...")
    
    # Give Ollama a moment to be ready
    time.sleep(2)
    
    if test_embedding_generation(args.model):
        print("\n🎉 Ollama embeddings setup complete!")
        print("\nNext steps:")
        print("1. Generate embeddings for Symmetra rules:")
        print("   python scripts/generate_embeddings_ollama.py")
        print("2. Update Symmetra to use vector search:")
        print("   export SYMMETRA_ENGINE_TYPE=vector")
        print("3. Test the system:")
        print("   python -c \"from symmetra.rules_engine import create_rule_engine; print('✅ Ready!')\"")
        
        print(f"\n💰 Cost savings: $0/month vs ~$5-50/month for cloud embeddings")
        print(f"📈 Performance: 15-50ms local vs 200-800ms cloud")
        print(f"🔒 Privacy: 100% local processing, no data leaves your machine")
        
    else:
        print("\n❌ Embedding test failed!")
        print("Troubleshooting:")
        print("1. Ensure Ollama service is running: ollama serve")
        print("2. Check model availability: ollama list")
        print("3. Try pulling model again: ollama pull nomic-embed-text")
        sys.exit(1)

if __name__ == "__main__":
    main()