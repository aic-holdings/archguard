# Symmetra Documentation

Welcome to the Symmetra documentation! This guide will help you navigate our organized documentation structure.

## 📁 Documentation Structure

### 🎯 [Strategy](strategy/)
Strategic planning and vision documents that guide Symmetra's development:
- [`END_GOALS.md`](strategy/END_GOALS.md) - Symmetra's ultimate vision and success metrics
- [`NEXT_TO_LAST_GOALS.md`](strategy/NEXT_TO_LAST_GOALS.md) - 17 measurable conditions that must be met before achieving end goals
- [`ROADMAP_TO_N_MINUS_1.md`](strategy/ROADMAP_TO_N_MINUS_1.md) - Tactical execution plan to reach the next-to-last state

### 👤 [User Documentation](user/)
Documentation for developers using Symmetra:
- [`quickstart.md`](user/quickstart.md) - Get started with Symmetra in 5 minutes
- [`installation.md`](user/installation.md) - Detailed installation instructions
- [`usage.md`](user/usage.md) - Complete usage guide and examples
- [`configuration.md`](user/configuration.md) - Configuration options and customization
- [`claude-code-config.json`](user/claude-code-config.json) - Claude Code MCP configuration
- [`claude-code-uvx-config.json`](user/claude-code-uvx-config.json) - Claude Code uvx configuration

### 🔧 [Technical Documentation](technical/)
Implementation details and technical specifications:
- [`IMPLEMENTATION.md`](technical/IMPLEMENTATION.md) - Technical implementation details
- [`ORIGINAL_SPEC.md`](technical/ORIGINAL_SPEC.md) - Original system specification
- [`CLAUDE_CODE_INTEGRATION.md`](technical/CLAUDE_CODE_INTEGRATION.md) - Claude Code integration details
- [`TESTING_RESULTS.md`](technical/TESTING_RESULTS.md) - Test results and validation

### 🏗️ [Architecture](architecture/)
System architecture and design documents:
- [`embedding-job-system.md`](architecture/embedding-job-system.md) - Embedding job system design

### 📡 [API Documentation](api/)
API specifications and database schemas:
- [`mcp-tools.md`](api/mcp-tools.md) - MCP tool specifications
- [`database-schema.md`](api/database-schema.md) - Database schema documentation

### 📋 [Rules](rules/)
Architectural rules and guidance patterns:
- [`python-project-essentials.md`](rules/python-project-essentials.md) - Python project rules
- [`repository-hygiene-rules.md`](rules/repository-hygiene-rules.md) - Repository hygiene rules

### 🧪 [Testing](testing/)
Testing strategies, procedures, and troubleshooting:
- [`README.md`](testing/README.md) - Testing overview
- [`integration-testing.md`](testing/integration-testing.md) - Integration testing procedures
- [`manual-validation.md`](testing/manual-validation.md) - Manual testing procedures
- [`mcp-inspector-testing.md`](testing/mcp-inspector-testing.md) - MCP inspector testing
- [`troubleshooting.md`](testing/troubleshooting.md) - Testing troubleshooting

### ⚙️ [Operations](operations/)
Operational setup and maintenance documentation:
- [`supabase-setup.md`](operations/supabase-setup.md) - Supabase database setup
- [`troubleshooting.md`](operations/troubleshooting.md) - General troubleshooting guide

## 🚀 Quick Start Paths

**New Users:** Start with [User Documentation](user/) → [`quickstart.md`](user/quickstart.md)

**Developers:** Check [Technical Documentation](technical/) → [`IMPLEMENTATION.md`](technical/IMPLEMENTATION.md)

**Contributors:** Review [Strategy](strategy/) → [`END_GOALS.md`](strategy/END_GOALS.md) to understand the vision

**Operators:** Follow [Operations](operations/) → [`supabase-setup.md`](operations/supabase-setup.md) for deployment

## 📝 Documentation Guidelines

When adding new documentation:

1. **Strategy docs** go in `strategy/` - high-level vision, planning, and roadmaps
2. **User docs** go in `user/` - anything end users need to know
3. **Technical docs** go in `technical/` - implementation details and specifications  
4. **Architecture docs** go in `architecture/` - system design and architectural decisions
5. **API docs** go in `api/` - API specifications and schemas
6. **Rules docs** go in `rules/` - architectural rules and patterns
7. **Testing docs** go in `testing/` - testing procedures and strategies
8. **Operations docs** go in `operations/` - deployment and maintenance

## 🔄 Keeping Documentation Updated

- Update this README when adding new major documents
- Keep the quick start paths current as the project evolves
- Ensure cross-references between documents remain valid
- Review and update documentation with each major release

---

*This documentation structure follows Symmetra's organizational principles: clear separation of concerns, logical grouping, and easy navigation.*