# Cloud Embeddings Migration Guide

Symmetra has migrated from local embedding generation (Ollama/SentenceTransformers) to cloud-based embedding APIs for improved reliability, consistency, and reduced infrastructure requirements.

## 🌟 Benefits of Cloud Embeddings

### Reliability
- **99.9% uptime** from enterprise cloud providers
- **No local installation** requirements (Ollama, model downloads)
- **Consistent performance** across all environments
- **Automatic scaling** based on demand

### User Experience
- **Zero setup friction** - no multi-GB model downloads
- **Works immediately** with just API key configuration
- **Consistent results** across different hardware
- **No local resource consumption** (CPU, memory, storage)

### Maintenance
- **No model updates** to manage locally
- **No version compatibility** issues
- **Simplified deployment** pipeline
- **Better error handling** and monitoring

## 🔄 Migration Overview

### Before (Local Setup)
```
User Machine Requirements:
- Ollama installation (1-2 GB)
- Model download (nomic-embed-text: 274 MB)
- SentenceTransformers (500 MB)
- Local compute resources
- Manual model management

Issues:
❌ Complex setup process
❌ Hardware-dependent performance
❌ Potential service failures
❌ Large local storage requirements
❌ Model version drift between environments
```

### After (Cloud Setup)
```
User Machine Requirements:
- OpenAI API key (environment variable)
- Internet connection

Benefits:
✅ Instant setup (1 minute)
✅ Consistent performance everywhere
✅ Enterprise-grade reliability
✅ No local storage requirements
✅ Automatic updates and improvements
```

## 🚀 Quick Setup

### 1. Get OpenAI API Key
```bash
# Visit: https://platform.openai.com/api-keys
# Create new key and copy it
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Update Environment Variables
```bash
# Add to your .env file or environment
OPENAI_API_KEY=sk-your-actual-key-here
SYMMETRA_EMBEDDING_BACKEND=openai  # or 'auto' for automatic selection
```

### 3. Migrate Existing Embeddings
```bash
# Re-embed all existing rules with cloud embeddings
python scripts/migrate_to_cloud_embeddings.py --project-id trzfyaopymlgxehhdfqf

# Or just test the migration first
python scripts/migrate_to_cloud_embeddings.py --dry-run
```

## 📊 Embedding Provider Comparison

| Provider | Dimensions | Cost | Setup | Performance | Reliability |
|----------|------------|------|-------|-------------|-------------|
| **OpenAI** | 384 (configurable) | $0.02/1M tokens | 🟢 Simple | 🟢 Excellent | 🟢 Enterprise |
| **Cohere** | 384 (native) | $0.10/1M tokens | 🟢 Simple | 🟢 Excellent | 🟢 Enterprise |
| **Local** | 384 | 🟢 Free | 🔴 Complex | 🟡 Variable | 🔴 Unreliable |

### Recommended: OpenAI
- **Best performance** on semantic tasks
- **Cost-effective** at $0.02 per 1M tokens
- **Configurable dimensions** (perfect for 384D requirement)
- **Proven reliability** and uptime
- **Simple API** with excellent documentation

## 🛠️ Implementation Details

### Automatic Backend Selection
```python
# Symmetra automatically chooses the best available provider:
# 1. OpenAI (if OPENAI_API_KEY is set)
# 2. Cohere (if COHERE_API_KEY is set)  
# 3. Local (fallback to SentenceTransformers)

from symmetra.embedding_config import get_embedding_manager

manager = get_embedding_manager()
embedding = manager.generate_embedding("vector database architecture")
```

### Manual Backend Selection
```python
# Force specific backend
from symmetra.embedding_config import EmbeddingManager, EmbeddingBackend

manager = EmbeddingManager(EmbeddingBackend.OPENAI)
embeddings = manager.generate_batch_embeddings([
    "microservices architecture",
    "database security patterns"
])
```

### Batch Processing
```python
# Efficient batch processing for large datasets
texts = ["rule 1", "rule 2", "rule 3"]
embeddings = generate_batch_embeddings(texts)  # Batches automatically
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Embedding backend selection
SYMMETRA_EMBEDDING_BACKEND=auto    # auto, openai, cohere, local

# Provider API keys
OPENAI_API_KEY=sk-your-key-here
COHERE_API_KEY=your-cohere-key     # Optional alternative

# Legacy local model (fallback only)
SYMMETRA_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Health Check
```python
from symmetra.cloud_vector_search import cloud_vector_search_engine

health = cloud_vector_search_engine.health_check()
print(health)
# {
#   "status": "healthy",
#   "components": {
#     "supabase": {"status": "healthy", "rule_count": 10},
#     "openai": {"status": "healthy", "embedding_dimensions": 384}
#   }
# }
```

## 💰 Cost Analysis

### OpenAI Pricing Example
```
Text-embedding-3-small: $0.02 per 1M tokens

Typical rule: ~100 tokens
1,000 rules: 100,000 tokens = $0.002
10,000 rules: 1,000,000 tokens = $0.02

Monthly usage (moderate):
- 1,000 new rules: $0.002
- 50,000 searches: $0.001 (queries)
- Total: ~$0.003/month
```

### Cost vs. Infrastructure
```
Local Setup Costs:
- Developer time: 2-4 hours setup per developer
- Ongoing maintenance: 1-2 hours/month
- Infrastructure complexity: High
- Reliability issues: Medium-High

Cloud Setup Costs:
- Developer time: 5 minutes setup
- Ongoing maintenance: 0 hours
- Infrastructure complexity: None
- Reliability issues: None
- API costs: $0.003-0.10/month typical usage
```

**Result: Cloud embeddings are 10-100x more cost-effective when factoring in developer time and reliability.**

## 🔄 Migration Scripts

### Full Migration
```bash
# Re-embed all existing rules with cloud embeddings
python scripts/migrate_to_cloud_embeddings.py \
  --project-id trzfyaopymlgxehhdfqf \
  --batch-size 50

# Expected output:
# 🌐 Connected to OpenAI API
# ✅ Connected to Supabase  
# 📦 Processing batch 1/1 (10 rules)...
# ✅ Generated 10 embeddings via OpenAI
# 🎉 Migration complete!
```

### Test Only
```bash
# Test cloud embeddings without changing data
python scripts/cloud_generate_embeddings.py \
  --project-id trzfyaopymlgxehhdfqf \
  --test-only

# Expected output:
# 🔍 Testing vector search...
# ✅ Vector search working perfectly!
# 🎯 Top matches:
#   1. [architecture] Vector Database Selection
#      Rule: vector-db-choice | Similarity: 0.856
```

### Health Check
```bash
# Verify all components are working
python -c "
from symmetra.cloud_vector_search import cloud_vector_search_engine
import json
health = cloud_vector_search_engine.health_check()
print(json.dumps(health, indent=2))
"
```

## 🚨 Troubleshooting

### Common Issues

#### "OPENAI_API_KEY not found"
```bash
# Solution: Set the API key
export OPENAI_API_KEY="sk-your-actual-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-actual-key-here" >> .env
```

#### "No embedding providers available"
```bash
# Check what's available
python -c "
from symmetra.embedding_config import get_embedding_manager
manager = get_embedding_manager()
print(manager.get_provider_info())
"

# If all providers fail, install missing dependencies
pip install openai cohere sentence-transformers
```

#### "Vector search function not found"
```bash
# Create the match_rules function in Supabase
python scripts/migrate_to_cloud_embeddings.py --project-id trzfyaopymlgxehhdfqf
# This will automatically create the function if missing
```

#### "Embedding dimensions mismatch"
```bash
# This happens when mixing embedding providers
# Solution: Re-embed all rules with consistent provider
python scripts/migrate_to_cloud_embeddings.py --force
```

### Performance Issues

#### Slow embedding generation
```bash
# Use larger batch sizes (if hitting rate limits, reduce batch size)
python scripts/migrate_to_cloud_embeddings.py --batch-size 100

# Or switch to faster provider
export SYMMETRA_EMBEDDING_BACKEND=openai  # Generally fastest
```

#### High API costs
```bash
# Monitor token usage
# OpenAI Dashboard: https://platform.openai.com/usage

# Optimize by:
# 1. Reducing rule text length (remove redundant content)
# 2. Caching embeddings (already implemented)
# 3. Using batch operations (already implemented)
```

## 🎯 Next Steps

### For Development
1. **Set OpenAI API key** in your environment
2. **Run migration script** to update existing embeddings
3. **Test vector search** to verify functionality
4. **Remove local embedding dependencies** (optional cleanup)

### For Production
1. **Secure API key management** (use secret manager)
2. **Monitor API usage** and costs
3. **Set up alerting** for API failures
4. **Consider backup provider** (Cohere) for redundancy

### Future Enhancements
- **Multiple provider support** with automatic failover
- **Embedding caching** for frequently used queries
- **Custom fine-tuned models** for domain-specific accuracy
- **Real-time embedding updates** via webhooks

## 📚 References

- [OpenAI Embeddings Documentation](https://platform.openai.com/docs/guides/embeddings)
- [Cohere Embed API](https://docs.cohere.com/reference/embed)
- [pgvector Performance Tuning](https://github.com/pgvector/pgvector#performance)
- [Symmetra Vector Search Architecture](../architecture/vector-search.md)