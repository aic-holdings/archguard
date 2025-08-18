# ArchGuard Troubleshooting Guide

Comprehensive troubleshooting guide for common ArchGuard issues and their solutions.

## Quick Diagnostics

### System Health Check

Run this diagnostic script to check system health:

```bash
# Create diagnostic script
cat > check_archguard_health.sh << 'EOF'
#!/bin/bash
echo "🔍 ArchGuard System Health Check"
echo "================================"

# Check Python environment
echo "📍 Python Environment:"
python --version
which python

# Check ArchGuard installation
echo -e "\n📦 ArchGuard Installation:"
python -c "import archguard; print('✅ ArchGuard imported successfully')" 2>/dev/null || echo "❌ ArchGuard import failed"

# Check environment variables
echo -e "\n🔧 Environment Configuration:"
env | grep ARCHGUARD | while read line; do
    key=$(echo $line | cut -d= -f1)
    value=$(echo $line | cut -d= -f2-)
    if [[ $key == *"KEY"* ]] || [[ $key == *"SECRET"* ]]; then
        echo "$key=***masked***"
    else
        echo "$line"
    fi
done

# Check Ollama service
echo -e "\n🤖 Ollama Service:"
curl -s http://localhost:11434/api/version > /dev/null && echo "✅ Ollama service is running" || echo "❌ Ollama service not available"

# Check database connection
echo -e "\n💾 Database Connection:"
python -c "
try:
    from mcp__supabase__execute_sql import execute_sql
    result = execute_sql('test-project', 'SELECT 1 as test;')
    if 'error' not in result:
        print('✅ Database connection successful')
    else:
        print('❌ Database connection failed:', result.get('error', 'Unknown error'))
except ImportError:
    print('⚠️  Supabase MCP not available')
except Exception as e:
    print('❌ Database test failed:', str(e))
"

echo -e "\n📊 System Status: Complete"
EOF

chmod +x check_archguard_health.sh
./check_archguard_health.sh
```

## Installation Issues

### Python Environment Problems

#### Issue: `ModuleNotFoundError: No module named 'archguard'`

**Symptoms:**
```bash
python -c "import archguard"
# ModuleNotFoundError: No module named 'archguard'
```

**Solutions:**

1. **Check virtual environment:**
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# Verify ArchGuard is installed
pip list | grep archguard
```

2. **Reinstall ArchGuard:**
```bash
pip uninstall archguard
pip install -e .
```

3. **Check Python path:**
```bash
python -c "import sys; print('\n'.join(sys.path))"
# Should include ArchGuard src directory
```

#### Issue: `Permission denied` during installation

**Symptoms:**
```bash
pip install -e .
# ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. **Fix permissions:**
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/.local/

# Or use user install
pip install --user -e .
```

### Dependency Conflicts

#### Issue: FastMCP version conflicts

**Symptoms:**
```bash
pip install -e .
# ERROR: pip's dependency resolver does not currently consider all the ways that two requirements can conflict
```

**Solutions:**

1. **Clean install:**
```bash
pip uninstall fastmcp
pip install fastmcp==2.11.3
pip install -e .
```

2. **Use pip-tools for dependency management:**
```bash
pip install pip-tools
pip-compile requirements.txt
pip-sync requirements.txt
```

## MCP Integration Issues

### Claude Code Integration

#### Issue: MCP server not starting

**Symptoms:**
```bash
# Claude Code shows: "Failed to start MCP server 'archguard'"
```

**Diagnosis:**
```bash
# Test MCP server directly
cd /path/to/archguard
python -m archguard.server

# Check for errors in output
```

**Solutions:**

1. **Fix environment variables in Claude Code config:**
```json
{
  "mcpServers": {
    "archguard": {
      "command": "python",
      "args": ["-m", "archguard.server"],
      "cwd": "/absolute/path/to/archguard",
      "env": {
        "ARCHGUARD_ENGINE_TYPE": "keyword",
        "ARCHGUARD_SUPABASE_URL": "https://your-project.supabase.co",
        "ARCHGUARD_SUPABASE_KEY": "your-anon-key"
      }
    }
  }
}
```

2. **Use absolute paths:**
```json
{
  "mcpServers": {
    "archguard": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "archguard.server"],
      "cwd": "/absolute/path/to/archguard"
    }
  }
}
```

3. **Check Claude Code logs:**
```bash
# macOS
tail -f ~/.claude/logs/mcp.log

# Look for ArchGuard-related errors
grep -i archguard ~/.claude/logs/mcp.log
```

#### Issue: Tools not appearing in Claude Code

**Symptoms:**
- MCP server starts successfully
- No ArchGuard tools available in Claude Code

**Solutions:**

1. **Restart Claude Code:**
```bash
# Completely quit and restart Claude Code
# MCP servers are loaded on startup
```

2. **Verify tool registration:**
```bash
python -c "
from archguard.server import get_guidance, search_rules, list_rule_categories
print('Available tools:')
print('- get_guidance')
print('- search_rules') 
print('- list_rule_categories')
"
```

3. **Check MCP protocol compatibility:**
```bash
# Ensure using compatible FastMCP version
pip show fastmcp
# Should be 2.11.3 or compatible
```

### Cursor Integration

#### Issue: Cursor MCP configuration not working

**Symptoms:**
- Cursor doesn't recognize ArchGuard MCP server

**Solutions:**

1. **Update Cursor settings:**
```json
{
  "mcp": {
    "servers": {
      "archguard": {
        "command": "python",
        "args": ["-m", "archguard.server"],
        "cwd": "/path/to/archguard",
        "env": {
          "ARCHGUARD_ENGINE_TYPE": "vector"
        }
      }
    }
  }
}
```

2. **Restart Cursor completely**

3. **Check Cursor version compatibility**

## Database Connection Issues

### Supabase Connection Problems

#### Issue: Database connection timeout

**Symptoms:**
```bash
python -c "from mcp__supabase__execute_sql import execute_sql; execute_sql('project-id', 'SELECT 1')"
# Connection timeout or network error
```

**Diagnosis:**
```bash
# Test basic connectivity
curl -I https://your-project.supabase.co

# Test with curl
curl -X POST https://your-project.supabase.co/rest/v1/rules \
  -H "apikey: your-anon-key" \
  -H "Content-Type: application/json"
```

**Solutions:**

1. **Check environment variables:**
```bash
echo $ARCHGUARD_SUPABASE_URL
echo $ARCHGUARD_SUPABASE_KEY
# Should not be empty
```

2. **Verify project ID and credentials:**
```bash
# Log into Supabase dashboard
# Check project settings for correct URL and keys
```

3. **Test with minimal connection:**
```python
import os
from supabase import create_client

url = os.getenv('ARCHGUARD_SUPABASE_URL')
key = os.getenv('ARCHGUARD_SUPABASE_KEY')

client = create_client(url, key)
result = client.table('rules').select('*').limit(1).execute()
print('✅ Connection successful')
```

#### Issue: `relation "rules" does not exist`

**Symptoms:**
```bash
# ERROR: relation "rules" does not exist
```

**Solutions:**

1. **Run database migrations:**
```bash
python scripts/setup_database.py --project-id your-project-id
```

2. **Check applied migrations:**
```bash
python -c "
from mcp__supabase__execute_sql import execute_sql
result = execute_sql('your-project-id', 'SELECT * FROM supabase_migrations.schema_migrations;')
print(result)
"
```

3. **Manual migration check:**
```sql
-- Connect to your Supabase SQL editor
\dt  -- List tables
-- Should see: rules, embedding_jobs, projects
```

### Database Permission Issues

#### Issue: RLS (Row Level Security) blocking queries

**Symptoms:**
```bash
# No results returned from queries that should have data
```

**Solutions:**

1. **Disable RLS for development:**
```sql
-- In Supabase SQL editor
ALTER TABLE rules DISABLE ROW LEVEL SECURITY;
ALTER TABLE embedding_jobs DISABLE ROW LEVEL SECURITY;
```

2. **Check RLS policies:**
```sql
-- View existing policies
SELECT * FROM pg_policies WHERE tablename IN ('rules', 'embedding_jobs');
```

3. **Use service role for admin operations:**
```bash
# Use service_role key instead of anon key for admin operations
export ARCHGUARD_SUPABASE_KEY="your-service-role-key"
```

## Embedding System Issues

### Ollama Service Problems

#### Issue: Ollama service not running

**Symptoms:**
```bash
curl -s http://localhost:11434/api/version
# Connection refused or timeout
```

**Solutions:**

1. **Start Ollama service:**
```bash
# Method 1: Direct start
ollama serve

# Method 2: Background service
nohup ollama serve > /dev/null 2>&1 &

# Method 3: System service (Linux)
sudo systemctl start ollama
```

2. **Check Ollama installation:**
```bash
which ollama
ollama --version

# If not installed:
curl -fsSL https://ollama.com/install.sh | sh
```

3. **Check port availability:**
```bash
# Check if port 11434 is available
netstat -tlnp | grep 11434

# Or use different port
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

#### Issue: `nomic-embed-text` model not available

**Symptoms:**
```bash
# Model not found error when generating embeddings
```

**Solutions:**

1. **Pull the model:**
```bash
ollama pull nomic-embed-text

# Verify model is available
ollama list
```

2. **Check model size and disk space:**
```bash
df -h  # Check available disk space
# nomic-embed-text requires ~274MB
```

3. **Use alternative model:**
```bash
# Try smaller model if space is limited
ollama pull all-minilm
export ARCHGUARD_EMBEDDING_MODEL=all-minilm
```

### Embedding Generation Issues

#### Issue: Embedding jobs stuck in "processing" status

**Symptoms:**
```bash
python scripts/embedding_worker.py --project-id your-project-id --monitor-only
# Shows jobs stuck in processing
```

**Diagnosis:**
```bash
# Check for zombie workers
python -c "
from mcp__supabase__execute_sql import execute_sql
result = execute_sql('your-project-id', '''
    SELECT worker_id, started_at, NOW() - started_at as duration
    FROM embedding_jobs 
    WHERE status = \'processing\'
    ORDER BY started_at;
''')
print(result)
"
```

**Solutions:**

1. **Reset stuck jobs:**
```sql
-- In Supabase SQL editor
UPDATE embedding_jobs 
SET status = 'pending', worker_id = NULL, started_at = NULL
WHERE status = 'processing' 
  AND started_at < NOW() - INTERVAL '10 minutes';
```

2. **Kill zombie workers:**
```bash
# Find and kill stuck processes
ps aux | grep embedding_worker
kill <process_id>
```

3. **Restart worker with cleanup:**
```bash
python scripts/embedding_worker.py --project-id your-project-id --cleanup-stuck-jobs
```

#### Issue: High embedding generation failure rate

**Symptoms:**
```bash
# Many jobs in "failed" status
```

**Diagnosis:**
```bash
python -c "
from mcp__supabase__execute_sql import execute_sql
result = execute_sql('your-project-id', '''
    SELECT error_message, COUNT(*) as count
    FROM embedding_jobs 
    WHERE status = \'failed\'
    GROUP BY error_message
    ORDER BY count DESC;
''')
print(result)
"
```

**Solutions:**

1. **Common error fixes:**

   **Timeout errors:**
   ```bash
   # Increase timeout in worker
   export ARCHGUARD_EMBEDDING_TIMEOUT=120  # 2 minutes
   ```

   **Memory errors:**
   ```bash
   # Reduce batch size
   export ARCHGUARD_BATCH_SIZE=10
   ```

   **Model errors:**
   ```bash
   # Restart Ollama service
   ollama serve
   ```

2. **Retry failed jobs:**
```sql
-- Reset failed jobs for retry
UPDATE embedding_jobs 
SET status = 'pending', attempts = 0, error_message = NULL
WHERE status = 'failed' AND attempts < max_attempts;
```

## Performance Issues

### Slow Response Times

#### Issue: get_guidance() taking too long

**Symptoms:**
```bash
# Responses taking >1 second
```

**Diagnosis:**
```bash
# Time the operations
time python -c "from archguard.server import get_guidance; get_guidance(action='test')"
```

**Solutions:**

1. **Use keyword engine for speed:**
```bash
export ARCHGUARD_ENGINE_TYPE=keyword
```

2. **Reduce rule set size:**
```bash
export ARCHGUARD_MAX_RULES=10
```

3. **Enable caching:**
```bash
export ARCHGUARD_CACHE_TTL=3600  # 1 hour
```

#### Issue: Vector search very slow

**Symptoms:**
```bash
# Vector-based search taking >5 seconds
```

**Solutions:**

1. **Check embedding dimensions:**
```sql
-- Verify embeddings have correct dimensions
SELECT embedding_dimensions, COUNT(*) 
FROM embedding_jobs 
WHERE status = 'completed'
GROUP BY embedding_dimensions;
```

2. **Add vector indexes:**
```sql
-- Create HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_rules_embedding_cosine 
ON rules USING hnsw (embedding vector_cosine_ops);
```

3. **Use smaller embedding model:**
```bash
export ARCHGUARD_EMBEDDING_MODEL=all-minilm  # 384D instead of 768D
```

### Memory Usage Issues

#### Issue: High memory consumption

**Symptoms:**
```bash
# System running out of memory during embedding generation
```

**Solutions:**

1. **Limit concurrent workers:**
```bash
# Run only one worker per machine
pkill -f embedding_worker
python scripts/embedding_worker.py --project-id your-project-id
```

2. **Reduce batch sizes:**
```bash
export ARCHGUARD_BATCH_SIZE=10  # Smaller batches
```

3. **Monitor memory usage:**
```bash
# Monitor embedding worker memory
while true; do
    ps -o pid,ppid,%mem,%cpu,cmd -C python | grep embedding_worker
    sleep 5
done
```

## Configuration Issues

### Environment Variable Problems

#### Issue: Configuration not being picked up

**Symptoms:**
```bash
# ArchGuard ignoring environment variables
```

**Diagnosis:**
```bash
# Check which variables are set
env | grep ARCHGUARD | sort

# Test variable access
python -c "import os; print('ENGINE_TYPE:', os.getenv('ARCHGUARD_ENGINE_TYPE', 'NOT_SET'))"
```

**Solutions:**

1. **Source environment file:**
```bash
# Make sure .env is sourced
source .env
env | grep ARCHGUARD
```

2. **Check variable names:**
```bash
# Correct variable names
export ARCHGUARD_ENGINE_TYPE=vector     # Not ARCHGUARD_ENGINE
export ARCHGUARD_SUPABASE_URL=...       # Not SUPABASE_URL
```

3. **Use absolute paths:**
```bash
export ARCHGUARD_CONFIG_PATH=/absolute/path/to/config
```

### Logging Issues

#### Issue: No log output or too verbose

**Symptoms:**
```bash
# No debugging information available
```

**Solutions:**

1. **Set appropriate log level:**
```bash
export ARCHGUARD_LOG_LEVEL=DEBUG    # For troubleshooting
export ARCHGUARD_LOG_LEVEL=INFO     # For normal operation
export ARCHGUARD_LOG_LEVEL=WARNING  # For production
```

2. **Check log output:**
```bash
# Run with explicit logging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from archguard.server import get_guidance
get_guidance(action='debug test')
"
```

3. **Log to file:**
```bash
python scripts/embedding_worker.py --project-id your-project-id 2>&1 | tee worker.log
```

## Network and Security Issues

### Firewall and Network

#### Issue: Cannot connect to Supabase

**Symptoms:**
```bash
# Network timeouts or connection refused
```

**Solutions:**

1. **Check firewall:**
```bash
# Test HTTPS connectivity
curl -I https://your-project.supabase.co

# Check corporate firewall/proxy
export https_proxy=http://proxy.company.com:8080
```

2. **Verify DNS resolution:**
```bash
nslookup your-project.supabase.co
dig your-project.supabase.co
```

3. **Test from different network:**
```bash
# Try from mobile hotspot or different location
```

### API Key Issues

#### Issue: Invalid API key errors

**Symptoms:**
```bash
# 401 Unauthorized or API key invalid
```

**Solutions:**

1. **Regenerate API keys:**
```bash
# Go to Supabase dashboard
# Settings > API > Regenerate keys
```

2. **Use correct key type:**
```bash
# Use anon key for general access
export ARCHGUARD_SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use service_role key for admin operations (be careful!)
export ARCHGUARD_SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

3. **Check key format:**
```bash
# Keys should start with "eyJ"
echo $ARCHGUARD_SUPABASE_KEY | head -c 10
# Should output: eyJhbGciOi
```

## Recovery Procedures

### Complete System Reset

If everything is broken, follow this recovery procedure:

```bash
# 1. Stop all processes
pkill -f archguard
pkill -f embedding_worker

# 2. Clean Python environment
deactivate  # Exit virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# 3. Fresh installation
pip install --upgrade pip
pip install -e .

# 4. Reset configuration
cp .env.example .env
# Edit .env with correct values

# 5. Test basic functionality
python -c "from archguard.server import get_guidance; print(get_guidance(action='recovery test'))"

# 6. Rebuild database (if needed)
python scripts/setup_database.py --project-id your-project-id --force-rebuild

# 7. Restart services
ollama serve &
python scripts/embedding_worker.py --project-id your-project-id &
```

### Database Recovery

```sql
-- Reset all embedding jobs
UPDATE embedding_jobs SET status = 'pending', worker_id = NULL, started_at = NULL WHERE status IN ('processing', 'retrying');

-- Clear failed jobs
DELETE FROM embedding_jobs WHERE status = 'failed' AND attempts >= max_attempts;

-- Rebuild embeddings
UPDATE rules SET embedding = NULL WHERE embedding IS NOT NULL;
```

## Getting Additional Help

### Debug Information Collection

Before requesting help, collect this information:

```bash
# Create debug report
cat > debug_report.txt << 'EOF'
ArchGuard Debug Report
=====================

System Information:
- OS: $(uname -a)
- Python: $(python --version)
- ArchGuard: $(python -c "import archguard; print(archguard.__version__)" 2>/dev/null || echo "Not installed")

Environment Variables:
$(env | grep ARCHGUARD | sed 's/\(KEY.*=\).*/\1***masked***/')

MCP Configuration:
$(cat ~/.claude/mcp.json 2>/dev/null | jq .mcpServers.archguard 2>/dev/null || echo "Not found")

Recent Logs:
$(tail -20 ~/.claude/logs/mcp.log 2>/dev/null | grep -i archguard || echo "No MCP logs found")

Database Status:
$(python -c "
try:
    from mcp__supabase__execute_sql import execute_sql
    result = execute_sql('test', 'SELECT COUNT(*) FROM rules;')
    print('Rules count:', result)
except Exception as e:
    print('Database error:', str(e))
" 2>/dev/null)

Test Results:
$(python -c "
try:
    from archguard.server import get_guidance
    result = get_guidance(action='debug test')
    print('✅ get_guidance working')
except Exception as e:
    print('❌ get_guidance error:', str(e))
")
EOF

echo "Debug report saved to debug_report.txt"
```

### Support Channels

- **GitHub Issues**: [archguard/issues](https://github.com/aic-holdings/archguard/issues)
- **GitHub Discussions**: [archguard/discussions](https://github.com/aic-holdings/archguard/discussions)
- **Documentation**: [docs/](https://github.com/aic-holdings/archguard/tree/main/docs)

When reporting issues, include:
1. Your debug report (above)
2. Expected vs actual behavior
3. Steps to reproduce
4. Error messages (full stack traces)
5. Your configuration (with sensitive data masked)

### Emergency Contacts

For critical production issues, follow this escalation:

1. Check [GitHub Issues](https://github.com/aic-holdings/archguard/issues) for similar problems
2. Create detailed issue with debug information
3. Tag as `urgent` if system is completely down
4. Include recovery timeline requirements