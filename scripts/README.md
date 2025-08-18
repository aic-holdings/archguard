# ArchGuard Scripts

This directory contains utility scripts organized by purpose for ArchGuard development and deployment.

## 📁 Directory Structure

### 🚀 [`setup/`](setup/)
Scripts for initial system setup and installation:
- [`setup_database.py`](setup/setup_database.py) - Initialize Supabase database with schema and bootstrap data
- [`setup_ollama_embeddings.py`](setup/setup_ollama_embeddings.py) - Configure Ollama for embedding generation

### 🔧 [`maintenance/`](maintenance/)
Scripts for ongoing system maintenance and operations:
- [`embedding_worker.py`](maintenance/embedding_worker.py) - Background worker for processing embedding jobs

### 🛠️ [`development/`](development/)
Development utilities and tools:
- [`generate_embeddings.py`](development/generate_embeddings.py) - Generate embeddings for rules (generic)
- [`generate_embeddings_ollama.py`](development/generate_embeddings_ollama.py) - Generate embeddings using Ollama

## 🎯 Usage Guidelines

### First-Time Setup
1. Run setup scripts in order for new installations
2. Ensure dependencies are installed before running scripts
3. Check environment variables are configured

### Development Workflow
1. Use development scripts for testing and experimentation
2. Maintenance scripts for background operations
3. Always test scripts in development before production use

### Script Requirements
- Python 3.8+ required for all scripts
- Environment variables may be required (see individual script documentation)
- Some scripts require external services (Supabase, Ollama)

## 🔒 Security Notes

- Never commit secrets or API keys in scripts
- Use environment variables for sensitive configuration
- Review scripts before running in production environments
- Ensure proper permissions and access controls

## 📚 Adding New Scripts

When adding new scripts:
1. Choose appropriate directory based on purpose
2. Add clear docstrings and usage instructions
3. Update this README with script description
4. Follow existing naming conventions
5. Include error handling and logging

---

*Scripts are organized to support ArchGuard's development workflow and operational needs.*