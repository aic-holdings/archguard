"""
LLM Analyzer - Contextual analysis using language models

Provides intelligent analysis of detected issues using LLM capabilities
for nuanced understanding and context-specific recommendations.

Features:
- Context-aware analysis of detected issues
- Project-specific guidance adaptation
- Severity assessment refinement
- Actionable fix recommendations
- Impact analysis and prioritization
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from ..detectors.base import DetectedIssue, IssueType, Severity


class LLMAnalyzer:
    """Provides contextual LLM analysis for detected issues"""
    
    def __init__(self, llm_client=None):
        """
        Initialize LLM analyzer.
        
        Args:
            llm_client: Optional LLM client. If None, will use local analysis.
        """
        self.llm_client = llm_client
        self.analysis_cache = {}
    
    def analyze_issue(
        self, 
        issue: DetectedIssue, 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a specific detected issue with context.
        
        Args:
            issue: The detected issue to analyze
            code_context: Code context around the issue
            project_context: Project-level context information
            
        Returns:
            Enhanced analysis with recommendations
        """
        # Create cache key
        cache_key = self._create_cache_key(issue, code_context, project_context)
        
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Perform analysis based on issue type
        if issue.type == IssueType.HARDCODED_SECRET:
            analysis = self._analyze_secret_issue(issue, code_context, project_context)
        elif issue.type == IssueType.SQL_INJECTION_RISK:
            analysis = self._analyze_sql_injection(issue, code_context, project_context)
        elif issue.type == IssueType.LARGE_FILE:
            analysis = self._analyze_large_file(issue, code_context, project_context)
        elif issue.type == IssueType.LARGE_FUNCTION:
            analysis = self._analyze_large_function(issue, code_context, project_context)
        elif issue.type == IssueType.MISSING_ERROR_HANDLING:
            analysis = self._analyze_error_handling(issue, code_context, project_context)
        else:
            analysis = self._generic_analysis(issue, code_context, project_context)
        
        # Cache the result
        self.analysis_cache[cache_key] = analysis
        
        return analysis
    
    def _create_cache_key(self, issue: DetectedIssue, code_context: str, project_context: Dict[str, Any]) -> str:
        """Create a cache key for the analysis"""
        import hashlib
        
        key_parts = [
            issue.type.value,
            issue.severity.value,
            issue.rule_id,
            str(issue.line_number),
            code_context[:200],  # First 200 chars of context
            str(project_context.get('project_type', '')),
            str(project_context.get('environment', ''))
        ]
        
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _analyze_secret_issue(
        self, 
        issue: DetectedIssue, 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze hardcoded secret issues"""
        
        # Determine secret type and criticality
        secret_criticality = self._assess_secret_criticality(issue, project_context)
        
        # Generate specific fix steps
        fix_steps = self._generate_secret_fix_steps(issue, project_context)
        
        # Assess immediate impact
        impact_assessment = self._assess_secret_impact(issue, project_context)
        
        return {
            "analysis_type": "security_critical",
            "impact_level": secret_criticality["level"],
            "immediate_actions": secret_criticality["immediate_actions"],
            "fix_steps": fix_steps,
            "security_implications": impact_assessment["implications"],
            "recommended_timeline": impact_assessment["timeline"],
            "additional_measures": self._get_secret_additional_measures(issue, project_context),
            "estimated_effort": "15-30 minutes",
            "confidence_adjustment": 0.0  # No adjustment needed for secrets
        }
    
    def _assess_secret_criticality(self, issue: DetectedIssue, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how critical a hardcoded secret is"""
        evidence_lower = issue.evidence.lower()
        environment = project_context.get('environment', 'unknown').lower()
        
        # High criticality indicators
        high_criticality_keywords = [
            'aws_access_key', 'aws_secret', 'private_key', 'jwt_token',
            'api_key', 'secret_key', 'github_token', 'slack_token'
        ]
        
        # Production environment increases criticality
        is_production = environment in ['production', 'prod', 'live']
        
        if any(keyword in evidence_lower for keyword in high_criticality_keywords):
            level = "critical" if is_production else "high"
            actions = [
                "Rotate the secret immediately",
                "Check git history for exposure",
                "Review access logs for unauthorized usage"
            ]
        else:
            level = "high" if is_production else "medium"
            actions = [
                "Move to environment variable",
                "Review exposure scope"
            ]
        
        if is_production:
            actions.append("Consider emergency deployment if widely exposed")
        
        return {
            "level": level,
            "immediate_actions": actions
        }
    
    def _generate_secret_fix_steps(self, issue: DetectedIssue, project_context: Dict[str, Any]) -> List[str]:
        """Generate specific steps to fix secret issues"""
        language = project_context.get('language', 'unknown').lower()
        framework = project_context.get('framework', '').lower()
        
        steps = []
        
        # Step 1: Create environment variable
        secret_name = self._extract_secret_name(issue)
        steps.append(f"Create environment variable: {secret_name}")
        
        # Step 2: Language-specific loading
        if language == 'python':
            steps.append(f"Replace with: os.getenv('{secret_name}')")
            if 'django' in framework:
                steps.append("Add to Django settings.py using django-environ")
            elif 'flask' in framework:
                steps.append("Use python-dotenv to load .env file")
        elif language in ['javascript', 'typescript']:
            steps.append(f"Replace with: process.env.{secret_name}")
            if 'node' in framework:
                steps.append("Use dotenv package to load environment variables")
        elif language == 'java':
            steps.append(f"Replace with: System.getenv(\"{secret_name}\")")
        else:
            steps.append("Use language-appropriate environment variable loading")
        
        # Step 3: Configuration
        steps.append("Add to .env file for local development")
        steps.append("Configure in deployment environment")
        
        # Step 4: Security
        steps.append("Add .env to .gitignore")
        steps.append("Document required environment variables")
        
        return steps
    
    def _extract_secret_name(self, issue: DetectedIssue) -> str:
        """Extract appropriate environment variable name"""
        evidence = issue.evidence.lower()
        
        if 'api_key' in evidence:
            return 'API_KEY'
        elif 'secret_key' in evidence:
            return 'SECRET_KEY'
        elif 'aws_access' in evidence:
            return 'AWS_ACCESS_KEY_ID'
        elif 'aws_secret' in evidence:
            return 'AWS_SECRET_ACCESS_KEY'
        elif 'github' in evidence:
            return 'GITHUB_TOKEN'
        elif 'slack' in evidence:
            return 'SLACK_TOKEN'
        elif 'database' in evidence or 'db' in evidence:
            return 'DATABASE_PASSWORD'
        else:
            return 'SECRET_VALUE'
    
    def _assess_secret_impact(self, issue: DetectedIssue, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of the hardcoded secret"""
        evidence_lower = issue.evidence.lower()
        
        # Determine potential impact
        if any(keyword in evidence_lower for keyword in ['aws', 'cloud', 'database']):
            implications = [
                "Potential unauthorized access to cloud resources",
                "Risk of data breach or service disruption",
                "Possible financial impact from unauthorized usage"
            ]
            timeline = "immediate"
        elif any(keyword in evidence_lower for keyword in ['api_key', 'token']):
            implications = [
                "API rate limiting or service denial",
                "Unauthorized access to external services",
                "Potential data exposure"
            ]
            timeline = "within 24 hours"
        else:
            implications = [
                "Security vulnerability",
                "Potential unauthorized access"
            ]
            timeline = "within 48 hours"
        
        return {
            "implications": implications,
            "timeline": timeline
        }
    
    def _get_secret_additional_measures(self, issue: DetectedIssue, project_context: Dict[str, Any]) -> List[str]:
        """Get additional security measures for secret issues"""
        measures = [
            "Implement secrets scanning in CI/CD pipeline",
            "Consider using a secrets management service",
            "Set up monitoring for unusual API usage"
        ]
        
        environment = project_context.get('environment', '').lower()
        if environment in ['production', 'prod']:
            measures.extend([
                "Audit all deployments containing this secret",
                "Review monitoring logs for suspicious activity",
                "Consider incident response procedures"
            ])
        
        return measures
    
    def _analyze_sql_injection(
        self, 
        issue: DetectedIssue, 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze SQL injection vulnerabilities"""
        
        # Assess the type of SQL injection risk
        injection_type = self._classify_sql_injection(issue, code_context)
        
        # Generate specific fixes
        fix_recommendations = self._get_sql_injection_fixes(issue, project_context)
        
        return {
            "analysis_type": "security_vulnerability",
            "injection_type": injection_type["type"],
            "risk_level": injection_type["risk_level"],
            "fix_recommendations": fix_recommendations,
            "prevention_measures": [
                "Use parameterized queries or prepared statements",
                "Implement input validation and sanitization",
                "Use ORM methods instead of raw SQL",
                "Apply principle of least privilege for database access"
            ],
            "testing_suggestions": [
                "Test with SQL injection payloads",
                "Use automated security scanning tools",
                "Perform code review focused on data access"
            ],
            "estimated_effort": "30-60 minutes"
        }
    
    def _classify_sql_injection(self, issue: DetectedIssue, code_context: str) -> Dict[str, Any]:
        """Classify the type of SQL injection vulnerability"""
        context_lower = code_context.lower()
        
        if 'select' in context_lower:
            if 'where' in context_lower:
                return {
                    "type": "WHERE clause injection",
                    "risk_level": "high",
                    "description": "User input in WHERE clause can modify query logic"
                }
            else:
                return {
                    "type": "SELECT injection",
                    "risk_level": "medium",
                    "description": "User input in SELECT statement"
                }
        elif any(keyword in context_lower for keyword in ['insert', 'update', 'delete']):
            return {
                "type": "Data modification injection",
                "risk_level": "critical",
                "description": "User input in data modification statements"
            }
        else:
            return {
                "type": "Generic SQL injection",
                "risk_level": "high",
                "description": "String concatenation in SQL query"
            }
    
    def _get_sql_injection_fixes(self, issue: DetectedIssue, project_context: Dict[str, Any]) -> List[str]:
        """Get specific SQL injection fix recommendations"""
        language = project_context.get('language', '').lower()
        framework = project_context.get('framework', '').lower()
        
        fixes = []
        
        if language == 'python':
            if 'django' in framework:
                fixes.extend([
                    "Use Django ORM: Model.objects.filter(field=value)",
                    "Use parameterized queries: cursor.execute(query, [param])"
                ])
            elif 'sqlalchemy' in framework:
                fixes.extend([
                    "Use SQLAlchemy ORM: session.query(Model).filter(Model.field == value)",
                    "Use text() with bound parameters: text('SELECT * FROM table WHERE id = :id').params(id=value)"
                ])
            else:
                fixes.append("Use parameterized queries: cursor.execute('SELECT * FROM table WHERE id = %s', (value,))")
        
        elif language in ['javascript', 'typescript']:
            fixes.extend([
                "Use parameterized queries: db.query('SELECT * FROM table WHERE id = $1', [value])",
                "Use query builder: knex('table').where('id', value)",
                "Use ORM: Model.findOne({ where: { id: value } })"
            ])
        
        else:
            fixes.append("Use parameterized queries appropriate for your language/framework")
        
        return fixes
    
    def _analyze_large_file(
        self, 
        issue: DetectedIssue, 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze large file issues"""
        
        lines = int(issue.context.get('total_lines', 0))
        split_suggestions = issue.context.get('split_suggestions', [])
        
        # Determine refactoring approach
        refactoring_strategy = self._determine_refactoring_strategy(lines, split_suggestions, project_context)
        
        return {
            "analysis_type": "maintainability",
            "refactoring_strategy": refactoring_strategy,
            "estimated_effort": self._estimate_refactoring_effort(lines),
            "priority_assessment": self._assess_refactoring_priority(lines, project_context),
            "implementation_steps": self._get_refactoring_steps(split_suggestions, project_context),
            "testing_considerations": [
                "Ensure existing functionality is preserved",
                "Add unit tests for extracted components",
                "Test integration between split modules"
            ]
        }
    
    def _determine_refactoring_strategy(
        self, 
        lines: int, 
        split_suggestions: List[str], 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the best refactoring strategy"""
        
        if lines > 1000:
            strategy = "aggressive_splitting"
            description = "File is very large, requires immediate splitting"
        elif lines > 500:
            strategy = "incremental_splitting"
            description = "File is large, plan incremental refactoring"
        else:
            strategy = "minor_cleanup"
            description = "File is moderately large, consider minor improvements"
        
        return {
            "strategy": strategy,
            "description": description,
            "suggestions": split_suggestions[:3]  # Top 3 suggestions
        }
    
    def _estimate_refactoring_effort(self, lines: int) -> str:
        """Estimate effort required for refactoring"""
        if lines > 1000:
            return "4-8 hours (major refactoring)"
        elif lines > 500:
            return "2-4 hours (moderate refactoring)"
        else:
            return "1-2 hours (minor refactoring)"
    
    def _assess_refactoring_priority(self, lines: int, project_context: Dict[str, Any]) -> str:
        """Assess the priority of refactoring"""
        team_size = project_context.get('team_size', 'unknown')
        development_stage = project_context.get('development_stage', 'unknown')
        
        if lines > 1000:
            return "high"
        elif lines > 700 and team_size in ['large', 'medium']:
            return "medium"
        elif development_stage in ['maintenance', 'mature']:
            return "medium"
        else:
            return "low"
    
    def _get_refactoring_steps(self, split_suggestions: List[str], project_context: Dict[str, Any]) -> List[str]:
        """Get specific refactoring implementation steps"""
        if not split_suggestions:
            return [
                "Identify logical groupings in the file",
                "Extract related functions into modules",
                "Update import statements",
                "Test functionality after each extraction"
            ]
        
        steps = [f"Implement suggestion: {split_suggestions[0]}"]
        steps.extend([
            "Create new files for extracted components",
            "Move related functions and classes",
            "Update import statements throughout project",
            "Run tests to ensure functionality is preserved",
            "Update documentation and comments"
        ])
        
        return steps
    
    def _analyze_large_function(
        self, 
        issue: DetectedIssue, 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze large function issues"""
        
        function_name = issue.context.get('function_name', 'unknown')
        function_lines = issue.context.get('lines', 0)
        
        return {
            "analysis_type": "complexity_reduction",
            "function_name": function_name,
            "complexity_indicators": self._analyze_function_complexity(code_context),
            "decomposition_strategy": self._suggest_function_decomposition(code_context),
            "estimated_effort": f"1-2 hours for {function_name}",
            "testing_requirements": [
                f"Write unit tests for {function_name} before refactoring",
                "Test each extracted function independently",
                "Ensure original behavior is preserved"
            ]
        }
    
    def _analyze_function_complexity(self, code_context: str) -> List[str]:
        """Analyze what makes the function complex"""
        indicators = []
        
        if code_context.count('if ') > 5:
            indicators.append("Multiple conditional branches")
        
        if code_context.count('for ') + code_context.count('while ') > 3:
            indicators.append("Multiple loops")
        
        if code_context.count('try:') > 1:
            indicators.append("Multiple error handling blocks")
        
        if len(code_context.split('\n')) > 50:
            indicators.append("High line count")
        
        return indicators if indicators else ["General complexity"]
    
    def _suggest_function_decomposition(self, code_context: str) -> List[str]:
        """Suggest how to decompose the function"""
        suggestions = []
        
        if 'validation' in code_context.lower() or 'validate' in code_context.lower():
            suggestions.append("Extract validation logic into separate function")
        
        if 'calculate' in code_context.lower() or 'compute' in code_context.lower():
            suggestions.append("Extract calculation logic into utility function")
        
        if code_context.count('if ') > 3:
            suggestions.append("Extract complex conditional logic into helper functions")
        
        if 'format' in code_context.lower() or 'transform' in code_context.lower():
            suggestions.append("Extract formatting/transformation logic")
        
        if not suggestions:
            suggestions.append("Break into logical steps with descriptive function names")
        
        return suggestions
    
    def _analyze_error_handling(
        self, 
        issue: DetectedIssue, 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze missing error handling issues"""
        
        operation = issue.context.get('operation', 'unknown')
        
        return {
            "analysis_type": "robustness_improvement",
            "operation_type": operation,
            "error_scenarios": self._identify_error_scenarios(operation, code_context),
            "handling_recommendations": self._get_error_handling_recommendations(operation, project_context),
            "estimated_effort": "15-30 minutes"
        }
    
    def _identify_error_scenarios(self, operation: str, code_context: str) -> List[str]:
        """Identify potential error scenarios"""
        scenarios = []
        
        if 'file' in operation or 'open(' in code_context:
            scenarios.extend([
                "File not found",
                "Permission denied",
                "Disk space issues"
            ])
        
        if 'network' in operation or 'request' in code_context:
            scenarios.extend([
                "Network connectivity issues",
                "Timeout errors",
                "Invalid responses"
            ])
        
        if 'parse' in operation or 'json' in code_context:
            scenarios.extend([
                "Invalid JSON format",
                "Missing required fields",
                "Type conversion errors"
            ])
        
        return scenarios if scenarios else ["General operation failure"]
    
    def _get_error_handling_recommendations(self, operation: str, project_context: Dict[str, Any]) -> List[str]:
        """Get specific error handling recommendations"""
        language = project_context.get('language', '').lower()
        
        recommendations = []
        
        if language == 'python':
            recommendations.extend([
                "Use specific exception types in except clauses",
                "Log errors with appropriate detail level",
                "Consider using contextlib for resource management"
            ])
        elif language in ['javascript', 'typescript']:
            recommendations.extend([
                "Use try/catch blocks for synchronous operations",
                "Use .catch() for Promise-based operations",
                "Implement proper error logging"
            ])
        
        recommendations.extend([
            "Provide meaningful error messages to users",
            "Implement graceful degradation where possible",
            "Consider retry logic for transient failures"
        ])
        
        return recommendations
    
    def _generic_analysis(
        self, 
        issue: DetectedIssue, 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generic analysis for unspecified issue types"""
        
        return {
            "analysis_type": "general_improvement",
            "issue_category": issue.type.value.replace('_', ' ').title(),
            "general_recommendations": [
                issue.fix_suggestion,
                "Review similar patterns in codebase",
                "Consider automated detection in CI/CD"
            ],
            "estimated_effort": "15-45 minutes",
            "follow_up_actions": [
                "Test the fix thoroughly",
                "Update coding standards if needed",
                "Share learnings with team"
            ]
        }
    
    def batch_analyze(
        self, 
        issues: List[DetectedIssue], 
        code_context: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze multiple issues together for better insights"""
        
        if not issues:
            return {"batch_analysis": "no_issues"}
        
        # Analyze individual issues
        individual_analyses = []
        for issue in issues[:5]:  # Limit to top 5 for performance
            analysis = self.analyze_issue(issue, code_context, project_context)
            individual_analyses.append({
                "issue": issue,
                "analysis": analysis
            })
        
        # Provide batch insights
        batch_insights = self._generate_batch_insights(issues, individual_analyses, project_context)
        
        return {
            "individual_analyses": individual_analyses,
            "batch_insights": batch_insights,
            "overall_recommendations": self._generate_overall_recommendations(issues, project_context)
        }
    
    def _generate_batch_insights(
        self, 
        issues: List[DetectedIssue], 
        analyses: List[Dict[str, Any]], 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from analyzing multiple issues together"""
        
        # Categorize issues
        issue_categories = {}
        for issue in issues:
            category = issue.type.value
            issue_categories[category] = issue_categories.get(category, 0) + 1
        
        # Find patterns
        patterns = []
        if issue_categories.get('hardcoded_secret', 0) > 1:
            patterns.append("Multiple hardcoded secrets suggest need for secrets management strategy")
        
        if issue_categories.get('large_file', 0) + issue_categories.get('large_function', 0) > 2:
            patterns.append("Size-related issues indicate need for refactoring strategy")
        
        if issue_categories.get('missing_error_handling', 0) > 2:
            patterns.append("Missing error handling suggests need for defensive programming practices")
        
        return {
            "issue_distribution": issue_categories,
            "identified_patterns": patterns,
            "priority_focus": self._determine_priority_focus(issue_categories)
        }
    
    def _determine_priority_focus(self, issue_categories: Dict[str, int]) -> str:
        """Determine what to focus on first"""
        if issue_categories.get('hardcoded_secret', 0) > 0:
            return "security_first"
        elif issue_categories.get('sql_injection_risk', 0) > 0:
            return "security_first"
        elif issue_categories.get('large_file', 0) + issue_categories.get('large_function', 0) > 3:
            return "maintainability_focus"
        else:
            return "general_improvements"
    
    def _generate_overall_recommendations(
        self, 
        issues: List[DetectedIssue], 
        project_context: Dict[str, Any]
    ) -> List[str]:
        """Generate overall recommendations for the entire analysis"""
        
        recommendations = []
        
        # Security recommendations
        security_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        if security_issues:
            recommendations.append("🔒 Implement secrets management and security scanning in CI/CD")
        
        # Architecture recommendations
        size_issues = [i for i in issues if 'large' in i.type.value]
        if len(size_issues) > 2:
            recommendations.append("🏗️ Plan architecture refactoring to improve maintainability")
        
        # Process improvements
        if len(issues) > 10:
            recommendations.append("📋 Consider implementing automated code quality checks")
        
        # Team recommendations
        team_size = project_context.get('team_size', '')
        if team_size in ['medium', 'large']:
            recommendations.append("👥 Share findings with team and update coding standards")
        
        return recommendations