# Essential Python Project Rules

Start small with these core rules that will make Symmetra an exemplary Python project.

## Core Python Project Structure

### python-project-structure
**Title**: "Standard Python Project Layout"
**Guidance**: "📁 Use standard Python structure: /src/package_name (source), /tests (testing), pyproject.toml (config), README.md (docs)"
**Rationale**: "Standard structure helps Python developers navigate immediately. Using src/ layout prevents import issues and follows modern Python packaging best practices."
**Category**: "architecture"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python"]
**Keywords**: ["python", "structure", "src", "package", "layout", "pyproject", "packaging"]

### python-dependency-management
**Title**: "Modern Python Dependency Management"
**Guidance**: "📦 Use pyproject.toml for dependencies, pin versions with ranges (>=1.0,<2.0), separate dev dependencies, include Python version requirement"
**Rationale**: "pyproject.toml is the modern standard for Python packaging. Version ranges prevent breakage while allowing updates. Clear dev deps help contributors."
**Category**: "architecture"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python", "packaging"]
**Keywords**: ["dependencies", "pyproject", "toml", "versions", "pip", "packaging", "requirements"]

### python-code-quality
**Title**: "Python Code Quality Tools"
**Guidance**: "🔧 Use: black (formatting), ruff (linting), mypy (type checking), pytest (testing). Configure in pyproject.toml for consistency"
**Rationale**: "These tools are the modern Python standard. Black eliminates formatting debates, ruff is fast and comprehensive, mypy catches bugs early."
**Category**: "testing"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python", "testing", "linting"]
**Keywords**: ["black", "ruff", "mypy", "pytest", "formatting", "linting", "type-checking", "quality"]

## Python-Specific Best Practices

### python-imports-organization
**Title**: "Clean Python Import Organization"
**Guidance**: "📋 Order imports: stdlib, third-party, local. Use absolute imports. Group related imports. No star imports in production code"
**Rationale**: "Organized imports improve readability and prevent circular import issues. Following PEP 8 import order makes code professional."
**Category**: "architecture"
**Priority**: "medium"
**Contexts**: ["ide-assistant"]
**Tech Stacks**: ["python"]
**Keywords**: ["imports", "pep8", "organization", "stdlib", "absolute", "star-imports", "circular"]

### python-virtual-environments
**Title**: "Python Virtual Environment Usage"
**Guidance**: "🐍 Always use virtual environments (venv, virtualenv, or conda). Include activation instructions in README. Add .venv/ to .gitignore"
**Rationale**: "Virtual environments prevent dependency conflicts and ensure reproducible builds. Essential for Python project hygiene."
**Category**: "devops"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python", "venv"]
**Keywords**: ["venv", "virtualenv", "environment", "isolation", "dependencies", "python", "conda"]