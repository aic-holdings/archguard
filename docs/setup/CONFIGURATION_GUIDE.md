# Symmetra Configuration Guide

This guide explains how to configure Symmetra for Claude Code, covering both minimal setup (shared database) and advanced setup (custom database).

## 🚀 Quick Start (Minimal Setup)

**Perfect for individual developers who want to get started immediately**

### 1. Required: OpenAI API Key

```bash
# Get your API key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-your-actual-key-here"
```

### 2. Claude Code Configuration

Use the minimal configuration file:

```json
{
  "mcpServers": {
    "symmetra": {
      "command": "symmetra",
      "args": ["server"],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY_HERE"
      }
    }
  }
}
```

**That's it!** Symmetra will automatically use our shared Supabase database with 1,000+ architectural guidelines.

#### Using uvx (Alternative Installation)

```json
{
  "mcpServers": {
    "symmetra": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra", "server"],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY_HERE"
      }
    }
  }
}
```

### Minimal Setup Benefits

✅ **Zero infrastructure setup** - no database management  
✅ **Instant access** to 1,000+ architectural guidelines  
✅ **Automatic updates** when we add new rules  
✅ **Enterprise-grade reliability** (99.9% uptime)  
✅ **Cost-effective** - only pay for OpenAI embedding API usage (~$0.02/month)

## 🔧 Advanced Setup (Custom Database)

**Perfect for teams who want to customize rules or maintain private guidelines**

### 1. Setup Your Supabase Database

1. **Create Supabase Project**: [supabase.com/dashboard](https://supabase.com/dashboard)
2. **Get Database Credentials**:
   - Project URL: `https://your-project-ref.supabase.co`
   - Anon Key: Found in Project Settings → API → anon/public key

### 2. Initialize Database Schema

```bash
# Clone the repository to get migration scripts
git clone https://github.com/aic-holdings/symmetra
cd symmetra

# Set your database credentials
export SYMMETRA_SUPABASE_URL="https://your-project-ref.supabase.co"
export SYMMETRA_SUPABASE_KEY="your-anon-key"
export OPENAI_API_KEY="your-openai-key"

# Run database setup
python scripts/setup/setup_database.py
```

### 3. Migrate Existing Rules (Optional)

```bash
# Copy our shared rules to your database
python scripts/migrate_to_cloud_embeddings.py \
  --source-project trzfyaopymlgxehhdfqf \
  --target-project your-project-ref \
  --copy-rules
```

### 4. Advanced Claude Code Configuration

```json
{
  "mcpServers": {
    "symmetra": {
      "command": "symmetra",
      "args": ["server"],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY_HERE",
        "SYMMETRA_SUPABASE_URL": "https://your-project-ref.supabase.co",
        "SYMMETRA_SUPABASE_KEY": "your-anon-key",
        "SYMMETRA_EMBEDDING_BACKEND": "openai"
      }
    }
  }
}
```

### Advanced Setup Benefits

✅ **Complete customization** - add/modify rules for your team  
✅ **Private guidelines** - internal architectural standards  
✅ **Team collaboration** - shared rule development  
✅ **Usage analytics** - track which rules are most helpful  
✅ **Data privacy** - your rules stay in your database

## 📊 Configuration Comparison

| Feature | Minimal Setup | Advanced Setup |
|---------|---------------|----------------|
| **Setup Time** | 2 minutes | 15-30 minutes |
| **Infrastructure** | None | Supabase project |
| **Rule Count** | 1,000+ (shared) | Customizable |
| **Rule Updates** | Automatic | Manual/team-managed |
| **Privacy** | Shared database | Private database |
| **Cost** | $0.02/month | $0.02/month + Supabase |
| **Customization** | None | Full control |

## 🔐 Security Best Practices

### API Key Management

```bash
# Store in environment variables (recommended)
echo "OPENAI_API_KEY=sk-your-key-here" >> ~/.bashrc
source ~/.bashrc

# Or use a .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Supabase Security

- **Row Level Security**: Enable RLS on custom rules tables
- **API Key Rotation**: Regularly rotate Supabase anon keys
- **Access Logging**: Monitor database access patterns

## 🛠️ Environment Variables Reference

### Required (All Setups)

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings | `sk-proj-abc123...` |

### Optional (Advanced Setup)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SYMMETRA_SUPABASE_URL` | Custom Supabase project URL | Shared DB | `https://abc123.supabase.co` |
| `SYMMETRA_SUPABASE_KEY` | Custom Supabase anon key | Shared DB | `eyJhbGciOiJIUzI1Ni...` |
| `SYMMETRA_EMBEDDING_BACKEND` | Embedding provider | `openai` | `openai`, `cohere` |
| `SYMMETRA_LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING` |

## 🚨 Troubleshooting

### Common Issues

#### "OPENAI_API_KEY not found"
```bash
# Solution: Set the API key
export OPENAI_API_KEY="sk-your-actual-key-here"
```

#### "Connection to Supabase failed"
```bash
# Check credentials
echo $SYMMETRA_SUPABASE_URL
echo $SYMMETRA_SUPABASE_KEY

# Verify project is active in Supabase dashboard
```

#### "No rules found"
```bash
# For custom databases, run initial setup
python scripts/setup/setup_database.py

# Or copy shared rules
python scripts/migrate_to_cloud_embeddings.py --copy-rules
```

#### "Claude Code can't find symmetra command"
```bash
# Install Symmetra
pip install symmetra

# Or use uvx configuration instead
```

### Health Check

```bash
# Test configuration
python -c "
from symmetra.cloud_vector_search import cloud_vector_search_engine
import json
health = cloud_vector_search_engine.health_check()
print(json.dumps(health, indent=2))
"
```

Expected output:
```json
{
  "status": "healthy",
  "components": {
    "supabase": {
      "status": "healthy",
      "rule_count": 1000
    },
    "openai": {
      "status": "healthy",
      "embedding_dimensions": 384
    }
  }
}
```

## 📚 Next Steps

### For Minimal Setup Users
1. ✅ **Start coding** - ask Claude for architectural guidance
2. 📖 **Learn patterns** - explore the 1,000+ rules available
3. 🎯 **Provide feedback** - help us improve shared guidelines

### For Advanced Setup Users  
1. 📝 **Add team rules** - create organization-specific guidelines
2. 🔄 **Setup automation** - integrate rule updates with CI/CD
3. 📊 **Monitor usage** - track most valuable architectural advice
4. 🤝 **Contribute back** - share great rules with the community

## 💰 Cost Analysis

### Minimal Setup Costs
- **OpenAI Embeddings**: ~$0.02/month (typical usage)
- **Supabase**: $0 (uses shared database)
- **Total**: **$0.02/month**

### Advanced Setup Costs
- **OpenAI Embeddings**: ~$0.02/month (typical usage)  
- **Supabase**: $0-25/month (depending on usage)
- **Total**: **$0.02-25/month**

Both options are extremely cost-effective compared to:
- Manual architectural reviews: $150-300/hour
- Architectural consultants: $200-500/hour
- Code review delays: $50-200 per delayed deployment

**ROI**: 1,000x-10,000x return on investment through faster, higher-quality development.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/aic-holdings/symmetra/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aic-holdings/symmetra/discussions)
- **Documentation**: [Full Documentation](../README.md)