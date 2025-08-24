# Repository Hygiene Rules for Symmetra

These rules help maintain clean, professional, and contributor-friendly repositories. Perfect for self-bootstrapping Symmetra's own excellence!

## Core Repository Structure Rules

### repo-structure-standards
**Title**: "Standard Repository Structure"
**Guidance**: "📁 Use standard structure: /src (code), /docs (documentation), /tests (testing), /scripts (utilities), /examples (usage samples)"
**Rationale**: "Consistent structure helps contributors navigate quickly and reduces onboarding friction. Following conventions makes your project feel professional and trustworthy."
**Category**: "architecture"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python", "javascript", "typescript", "go", "rust"]
**Keywords**: ["structure", "organization", "folders", "directories", "project-layout", "repository", "standards"]

### documentation-completeness
**Title**: "Complete Documentation Strategy"
**Guidance**: "📚 Essential docs: README.md (overview), CONTRIBUTING.md (contribution guide), docs/ (detailed guides), API.md (API reference)"
**Rationale**: "Documentation is the first impression for contributors and users. Complete documentation reduces support burden and accelerates adoption."
**Category**: "architecture"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent", "desktop-app"]
**Tech Stacks**: ["markdown", "documentation"]
**Keywords**: ["documentation", "readme", "contributing", "api", "guides", "docs", "markdown"]

### ai-friendly-docs
**Title**: "AI-Optimized Documentation"
**Guidance**: "🤖 Create llms.txt file, use 100% markdown (no HTML), structure with clear headings, include code examples in fenced blocks"
**Rationale**: "AI-friendly documentation enables better integration with AI tools, making your project more accessible to modern development workflows."
**Category**: "ux"
**Priority**: "medium" 
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["markdown", "ai", "documentation"]
**Keywords**: ["ai", "llms", "markdown", "documentation", "machine-readable", "ai-friendly", "llms.txt"]

## Code Quality and Maintenance

### dependency-management
**Title**: "Clean Dependency Management"
**Guidance**: "📦 Pin dependencies with ranges, separate dev/prod deps, document why each dependency exists, regular security audits"
**Rationale**: "Clean dependency management prevents supply chain attacks, reduces build failures, and makes security maintenance easier."
**Category**: "security"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python", "javascript", "typescript", "go", "rust"]
**Keywords**: ["dependencies", "packages", "security", "supply-chain", "requirements", "package-lock", "vulnerabilities"]

### environment-configuration
**Title**: "Environment Configuration Standards"
**Guidance**: "⚙️ Use .env.example (template), .env (local, gitignored), document all env vars, validate required vars on startup"
**Rationale**: "Clear environment configuration reduces setup friction for contributors and prevents production misconfigurations."
**Category**: "devops"
**Priority**: "medium"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python", "javascript", "typescript", "docker"]
**Keywords**: ["environment", "config", "env-vars", "configuration", "setup", "deployment"]

### testing-infrastructure
**Title**: "Comprehensive Testing Strategy"
**Guidance**: "🧪 Include unit tests, integration tests, test coverage reporting, CI/CD pipeline, pre-commit hooks"
**Rationale**: "Strong testing infrastructure builds contributor confidence and prevents regressions in open source projects."
**Category**: "testing"
**Priority**: "high"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["python", "javascript", "typescript", "testing", "ci-cd"]
**Keywords**: ["testing", "unit-tests", "integration", "coverage", "ci-cd", "pre-commit", "quality"]

## Community and Contribution

### contribution-workflow
**Title**: "Clear Contribution Process"
**Guidance**: "🤝 Document: how to setup dev env, coding standards, PR process, issue templates, code of conduct"
**Rationale**: "Clear contribution guidelines lower the barrier for new contributors and maintain code quality as the project scales."
**Category**: "ux"
**Priority**: "high"
**Contexts**: ["desktop-app", "agent"]
**Tech Stacks**: ["git", "github", "opensource"]
**Keywords**: ["contributing", "workflow", "pull-request", "issues", "community", "opensource", "guidelines"]

### github-templates
**Title**: "GitHub Issue and PR Templates"
**Guidance**: "📋 Create .github/ISSUE_TEMPLATE/ and .github/pull_request_template.md with structured forms for bugs, features, and PRs"
**Rationale**: "Templates ensure consistent information collection, making it easier to triage issues and review PRs effectively."
**Category**: "ux"
**Priority**: "medium"
**Contexts**: ["agent"]
**Tech Stacks**: ["github", "git"]
**Keywords**: ["github", "templates", "issues", "pull-requests", "forms", "bug-reports"]

### licensing-clarity
**Title**: "Clear Licensing and Attribution"
**Guidance**: "⚖️ Include LICENSE file, document third-party licenses, add copyright headers where appropriate, clarify commercial usage"
**Rationale**: "Clear licensing removes adoption barriers for companies and ensures proper attribution for contributors' work."
**Category**: "architecture"
**Priority**: "medium"
**Contexts**: ["agent", "desktop-app"]
**Tech Stacks**: ["opensource", "legal"]
**Keywords**: ["license", "copyright", "legal", "attribution", "opensource", "commercial"]

## Security and Maintenance

### secrets-management
**Title**: "Secrets and Sensitive Data Protection"
**Guidance**: "🔒 Never commit secrets, use .gitignore patterns, scan for leaked credentials, rotate keys regularly, document key management"
**Rationale**: "Proper secrets management prevents security breaches and maintains user trust in your project."
**Category**: "security"
**Priority**: "critical"
**Contexts**: ["ide-assistant", "agent"]
**Tech Stacks**: ["git", "security", "devops"]
**Keywords**: ["secrets", "credentials", "api-keys", "security", "gitignore", "sensitive-data"]

### version-management
**Title**: "Semantic Versioning and Release Process"
**Guidance**: "🔢 Use semantic versioning (MAJOR.MINOR.PATCH), maintain CHANGELOG.md, tag releases, automate release notes"
**Rationale**: "Clear versioning helps users understand compatibility and changes, making your project more trustworthy and professional."
**Category**: "devops"
**Priority**: "medium"
**Contexts**: ["agent"]
**Tech Stacks**: ["git", "semver", "releases"]
**Keywords**: ["versioning", "semver", "releases", "changelog", "tags", "compatibility"]

### repository-maintenance
**Title**: "Regular Repository Maintenance"
**Guidance**: "🧹 Regular tasks: update dependencies, remove dead code, fix broken links, update docs, security audits, performance monitoring"
**Rationale**: "Regular maintenance prevents technical debt accumulation and keeps the project healthy for long-term sustainability."
**Category**: "devops"
**Priority**: "medium"
**Contexts**: ["agent"]
**Tech Stacks**: ["maintenance", "automation"]
**Keywords**: ["maintenance", "cleanup", "updates", "refactoring", "debt", "health", "sustainability"]

## Performance and Monitoring

### performance-monitoring
**Title**: "Repository Performance Metrics"
**Guidance**: "📊 Monitor: build times, test execution time, dependency size, startup time, memory usage. Set performance budgets."
**Rationale**: "Performance monitoring prevents gradual degradation and ensures good developer experience as the project grows."
**Category**: "performance"
**Priority**: "medium"
**Contexts**: ["agent"]
**Tech Stacks**: ["monitoring", "performance", "ci-cd"]
**Keywords**: ["performance", "monitoring", "metrics", "build-time", "benchmarks", "budgets"]

### automation-excellence
**Title**: "Repository Automation Standards"
**Guidance**: "🤖 Automate: code formatting, linting, testing, security scans, dependency updates, release process"
**Rationale**: "Automation reduces manual work, prevents human error, and ensures consistent quality across all contributions."
**Category**: "devops"
**Priority**: "high"
**Contexts**: ["agent"]
**Tech Stacks**: ["automation", "ci-cd", "github-actions"]
**Keywords**: ["automation", "ci-cd", "formatting", "linting", "security-scans", "workflows"]