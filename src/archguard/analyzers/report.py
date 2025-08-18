"""
Report Generator - Format analysis results for different audiences

Creates formatted reports from detection and analysis results,
tailored for different contexts and audiences.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from ..detectors.base import DetectedIssue, DetectionResult, Severity


class ReportGenerator:
    """Generate formatted reports from analysis results"""
    
    def __init__(self):
        self.report_templates = {
            'ide_assistant': self._generate_ide_report,
            'agent': self._generate_agent_report,
            'desktop_app': self._generate_desktop_report,
            'security_audit': self._generate_security_report,
            'summary': self._generate_summary_report
        }
    
    def generate_report(
        self, 
        result: DetectionResult, 
        analysis_data: Optional[Dict[str, Any]] = None,
        report_type: str = 'summary',
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a formatted report from detection results.
        
        Args:
            result: Detection result to report on
            analysis_data: Optional LLM analysis data
            report_type: Type of report to generate
            context: Additional context for report generation
            
        Returns:
            Formatted report dictionary
        """
        if context is None:
            context = {}
        
        generator = self.report_templates.get(report_type, self._generate_summary_report)
        
        return generator(result, analysis_data, context)
    
    def _generate_ide_report(
        self, 
        result: DetectionResult, 
        analysis_data: Optional[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate concise report for IDE integration"""
        
        # Focus on actionable items
        actionable_issues = [
            issue for issue in result.issues 
            if issue.severity in [Severity.CRITICAL, Severity.HIGH]
        ][:3]  # Limit to top 3
        
        guidance = []
        
        if not actionable_issues:
            guidance.extend([
                "✅ No critical issues detected",
                "🚀 Code is ready for commit"
            ])
        else:
            for issue in actionable_issues:
                guidance.append(f"🔴 Line {issue.line_number}: {issue.message}")
                guidance.append(f"   💡 {issue.fix_suggestion}")
        
        return {
            "report_type": "ide_assistant",
            "status": result.status,
            "issues_count": len(result.issues),
            "critical_issues_count": len(result.critical_issues),
            "guidance": guidance,
            "next_action": self._get_next_action(result),
            "estimated_fix_time": self._estimate_total_fix_time(actionable_issues)
        }
    
    def _generate_agent_report(
        self, 
        result: DetectionResult, 
        analysis_data: Optional[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured report for agent processing"""
        
        # Detailed structured data
        report = {
            "report_type": "agent",
            "analysis_metadata": {
                "file_path": result.file_path,
                "language": result.language,
                "total_lines": result.total_lines,
                "analysis_time_ms": result.analysis_time_ms,
                "detectors_run": result.detectors_run,
                "patterns_checked": result.patterns_checked,
                "timestamp": datetime.utcnow().isoformat()
            },
            "issue_summary": result.issue_count_by_severity,
            "status_assessment": {
                "overall_status": result.status,
                "complexity_score": result.complexity_score,
                "has_blocking_issues": result.has_blocking_issues,
                "deployment_ready": len(result.critical_issues) == 0
            },
            "issues_by_category": self._categorize_issues(result.issues),
            "priority_actions": self._generate_priority_actions(result.issues),
            "recommendations": {
                "immediate": [],
                "short_term": [],
                "long_term": []
            }
        }
        
        # Add LLM analysis if available
        if analysis_data:
            report["llm_analysis"] = analysis_data
            report["enhanced_recommendations"] = self._extract_enhanced_recommendations(analysis_data)
        
        # Categorize recommendations by timeline
        report["recommendations"] = self._categorize_recommendations(result.issues, analysis_data)
        
        return report
    
    def _generate_desktop_report(
        self, 
        result: DetectionResult, 
        analysis_data: Optional[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed educational report for desktop app"""
        
        report = {
            "report_type": "desktop_app",
            "file_analysis": {
                "file_path": result.file_path,
                "language": result.language,
                "total_lines": result.total_lines,
                "complexity_assessment": result.complexity_score
            },
            "detailed_findings": [],
            "learning_opportunities": [],
            "code_quality_insights": self._generate_quality_insights(result),
            "improvement_roadmap": self._generate_improvement_roadmap(result.issues),
            "resources_and_references": self._get_educational_resources(result.issues)
        }
        
        # Add detailed issue explanations
        for issue in result.issues[:10]:  # Top 10 issues
            detailed_finding = {
                "issue": issue.to_dict(),
                "explanation": self._explain_issue(issue),
                "impact_analysis": self._analyze_issue_impact(issue),
                "learning_points": self._extract_learning_points(issue),
                "related_concepts": self._get_related_concepts(issue)
            }
            
            if analysis_data:
                # Add LLM insights if available
                issue_analysis = self._find_issue_analysis(issue, analysis_data)
                if issue_analysis:
                    detailed_finding["expert_analysis"] = issue_analysis
            
            report["detailed_findings"].append(detailed_finding)
        
        return report
    
    def _generate_security_report(
        self, 
        result: DetectionResult, 
        analysis_data: Optional[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate focused security audit report"""
        
        security_issues = [
            issue for issue in result.issues 
            if issue.type.value in ['hardcoded_secret', 'sql_injection_risk', 'insecure_protocol']
        ]
        
        report = {
            "report_type": "security_audit",
            "security_summary": {
                "total_security_issues": len(security_issues),
                "critical_security_issues": len([i for i in security_issues if i.severity == Severity.CRITICAL]),
                "risk_level": self._assess_overall_risk(security_issues),
                "compliance_status": self._assess_compliance_status(security_issues, context)
            },
            "vulnerability_details": [],
            "remediation_plan": self._generate_remediation_plan(security_issues),
            "security_recommendations": self._generate_security_recommendations(security_issues, context),
            "compliance_notes": self._generate_compliance_notes(security_issues, context)
        }
        
        # Detail each security issue
        for issue in security_issues:
            vulnerability = {
                "type": issue.type.value,
                "severity": issue.severity.value,
                "location": f"Line {issue.line_number}",
                "description": issue.message,
                "evidence": issue.evidence,
                "cvss_equivalent": self._estimate_cvss_score(issue),
                "remediation": issue.fix_suggestion,
                "verification_steps": self._get_verification_steps(issue)
            }
            
            report["vulnerability_details"].append(vulnerability)
        
        return report
    
    def _generate_summary_report(
        self, 
        result: DetectionResult, 
        analysis_data: Optional[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate balanced summary report"""
        
        return {
            "report_type": "summary",
            "file_info": {
                "path": result.file_path,
                "language": result.language,
                "lines": result.total_lines
            },
            "analysis_results": {
                "status": result.status,
                "total_issues": len(result.issues),
                "issue_breakdown": result.issue_count_by_severity,
                "complexity": result.complexity_score,
                "analysis_time": f"{result.analysis_time_ms:.0f}ms"
            },
            "key_findings": self._extract_key_findings(result.issues),
            "recommendations": result.guidance,
            "next_steps": self._generate_next_steps(result),
            "detailed_issues": [issue.to_dict() for issue in result.issues[:5]]  # Top 5
        }
    
    def _categorize_issues(self, issues: List[DetectedIssue]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize issues by type"""
        categories = {}
        
        for issue in issues:
            category = issue.type.value
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                "line_number": issue.line_number,
                "severity": issue.severity.value,
                "message": issue.message,
                "confidence": issue.confidence
            })
        
        return categories
    
    def _generate_priority_actions(self, issues: List[DetectedIssue]) -> List[Dict[str, Any]]:
        """Generate prioritized action items"""
        actions = []
        
        # Critical issues first
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        for issue in critical_issues[:3]:
            actions.append({
                "priority": "critical",
                "action": f"Fix {issue.type.value} on line {issue.line_number}",
                "reason": issue.message,
                "estimated_effort": "15-30 minutes"
            })
        
        # High issues next
        high_issues = [i for i in issues if i.severity == Severity.HIGH]
        for issue in high_issues[:2]:
            actions.append({
                "priority": "high",
                "action": f"Address {issue.type.value} on line {issue.line_number}",
                "reason": issue.message,
                "estimated_effort": "30-60 minutes"
            })
        
        return actions
    
    def _categorize_recommendations(
        self, 
        issues: List[DetectedIssue], 
        analysis_data: Optional[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Categorize recommendations by timeline"""
        
        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }
        
        # Immediate (critical/high security issues)
        security_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        for issue in security_issues:
            recommendations["immediate"].append(f"Fix {issue.type.value}: {issue.fix_suggestion}")
        
        # Short-term (high priority issues)
        high_issues = [i for i in issues if i.severity == Severity.HIGH]
        for issue in high_issues[:3]:
            recommendations["short_term"].append(f"Address {issue.type.value}: {issue.fix_suggestion}")
        
        # Long-term (architectural improvements)
        arch_issues = [i for i in issues if 'large' in i.type.value or 'duplicate' in i.type.value]
        for issue in arch_issues[:2]:
            recommendations["long_term"].append(f"Improve {issue.type.value}: {issue.fix_suggestion}")
        
        return recommendations
    
    def _extract_enhanced_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Extract enhanced recommendations from LLM analysis"""
        recommendations = []
        
        if "individual_analyses" in analysis_data:
            for analysis in analysis_data["individual_analyses"]:
                issue_analysis = analysis.get("analysis", {})
                
                if "fix_steps" in issue_analysis:
                    recommendations.extend(issue_analysis["fix_steps"][:2])
                
                if "additional_measures" in issue_analysis:
                    recommendations.extend(issue_analysis["additional_measures"][:1])
        
        if "overall_recommendations" in analysis_data:
            recommendations.extend(analysis_data["overall_recommendations"])
        
        return recommendations[:10]  # Limit to top 10
    
    def _generate_quality_insights(self, result: DetectionResult) -> Dict[str, Any]:
        """Generate code quality insights"""
        insights = {
            "maintainability_score": self._calculate_maintainability_score(result),
            "security_posture": self._assess_security_posture(result),
            "complexity_analysis": self._analyze_complexity_distribution(result),
            "improvement_areas": self._identify_improvement_areas(result)
        }
        
        return insights
    
    def _calculate_maintainability_score(self, result: DetectionResult) -> Dict[str, Any]:
        """Calculate maintainability score"""
        size_issues = len([i for i in result.issues if 'large' in i.type.value])
        duplicate_issues = len([i for i in result.issues if 'duplicate' in i.type.value])
        total_issues = len(result.issues)
        
        # Simple scoring algorithm
        base_score = 100
        size_penalty = size_issues * 10
        duplicate_penalty = duplicate_issues * 15
        general_penalty = (total_issues - size_issues - duplicate_issues) * 5
        
        score = max(0, base_score - size_penalty - duplicate_penalty - general_penalty)
        
        if score >= 80:
            grade = "A"
            description = "Excellent maintainability"
        elif score >= 60:
            grade = "B"
            description = "Good maintainability"
        elif score >= 40:
            grade = "C"
            description = "Fair maintainability"
        else:
            grade = "D"
            description = "Poor maintainability"
        
        return {
            "score": score,
            "grade": grade,
            "description": description,
            "factors": {
                "size_issues": size_issues,
                "duplication_issues": duplicate_issues,
                "other_issues": total_issues - size_issues - duplicate_issues
            }
        }
    
    def _assess_security_posture(self, result: DetectionResult) -> Dict[str, Any]:
        """Assess security posture"""
        security_issues = [
            i for i in result.issues 
            if i.type.value in ['hardcoded_secret', 'sql_injection_risk', 'insecure_protocol']
        ]
        
        critical_security = len([i for i in security_issues if i.severity == Severity.CRITICAL])
        
        if critical_security > 0:
            posture = "critical"
            description = "Immediate security attention required"
        elif len(security_issues) > 0:
            posture = "concerning"
            description = "Security improvements needed"
        else:
            posture = "good"
            description = "No obvious security issues detected"
        
        return {
            "posture": posture,
            "description": description,
            "security_issues_count": len(security_issues),
            "critical_count": critical_security
        }
    
    def _analyze_complexity_distribution(self, result: DetectionResult) -> Dict[str, Any]:
        """Analyze complexity distribution"""
        complexity_indicators = {
            "large_files": len([i for i in result.issues if i.type.value == 'large_file']),
            "large_functions": len([i for i in result.issues if i.type.value == 'large_function']),
            "deep_nesting": len([i for i in result.issues if i.type.value == 'deep_nesting']),
            "god_objects": len([i for i in result.issues if i.type.value == 'god_object'])
        }
        
        total_complexity_issues = sum(complexity_indicators.values())
        
        return {
            "indicators": complexity_indicators,
            "total_complexity_issues": total_complexity_issues,
            "complexity_score": result.complexity_score,
            "primary_concern": max(complexity_indicators.items(), key=lambda x: x[1])[0] if total_complexity_issues > 0 else None
        }
    
    def _identify_improvement_areas(self, result: DetectionResult) -> List[str]:
        """Identify key improvement areas"""
        areas = []
        
        issue_counts = result.issue_count_by_severity
        
        if issue_counts.get("critical", 0) > 0:
            areas.append("Security vulnerabilities need immediate attention")
        
        if issue_counts.get("high", 0) > 2:
            areas.append("Multiple high-priority issues affecting code quality")
        
        size_issues = len([i for i in result.issues if 'large' in i.type.value])
        if size_issues > 1:
            areas.append("Code organization and file structure")
        
        duplicate_issues = len([i for i in result.issues if 'duplicate' in i.type.value])
        if duplicate_issues > 0:
            areas.append("Code duplication and reusability")
        
        error_handling_issues = len([i for i in result.issues if 'error_handling' in i.type.value])
        if error_handling_issues > 1:
            areas.append("Error handling and robustness")
        
        return areas[:5]  # Top 5 areas
    
    def _generate_improvement_roadmap(self, issues: List[DetectedIssue]) -> Dict[str, List[str]]:
        """Generate improvement roadmap"""
        roadmap = {
            "week_1": [],
            "month_1": [],
            "quarter_1": []
        }
        
        # Week 1: Critical and high priority
        critical_and_high = [i for i in issues if i.severity in [Severity.CRITICAL, Severity.HIGH]]
        roadmap["week_1"] = [f"Fix {issue.type.value}" for issue in critical_and_high[:3]]
        
        # Month 1: Medium priority and architectural improvements
        medium_issues = [i for i in issues if i.severity == Severity.MEDIUM]
        roadmap["month_1"] = [f"Address {issue.type.value}" for issue in medium_issues[:3]]
        
        # Quarter 1: Low priority and preventive measures
        roadmap["quarter_1"] = [
            "Implement automated code quality checks",
            "Set up security scanning in CI/CD",
            "Establish coding standards and guidelines"
        ]
        
        return roadmap
    
    def _get_educational_resources(self, issues: List[DetectedIssue]) -> Dict[str, List[str]]:
        """Get educational resources related to found issues"""
        resources = {
            "documentation": [],
            "best_practices": [],
            "tools": []
        }
        
        issue_types = set(issue.type.value for issue in issues)
        
        if 'hardcoded_secret' in issue_types:
            resources["best_practices"].append("OWASP Secure Coding Practices - Secrets Management")
            resources["tools"].append("git-secrets for preventing secret commits")
        
        if 'sql_injection_risk' in issue_types:
            resources["best_practices"].append("OWASP SQL Injection Prevention")
            resources["tools"].append("Static analysis tools for SQL injection detection")
        
        if any('large' in issue_type for issue_type in issue_types):
            resources["best_practices"].append("Clean Code principles for function and class design")
            resources["tools"].append("Code complexity measurement tools")
        
        return resources
    
    def _explain_issue(self, issue: DetectedIssue) -> str:
        """Provide detailed explanation of an issue"""
        explanations = {
            "hardcoded_secret": "Hardcoded secrets in source code can be easily discovered by anyone with access to the code repository, including potential attackers. This creates a significant security vulnerability.",
            "sql_injection_risk": "SQL injection occurs when user input is directly concatenated into SQL queries without proper sanitization, allowing attackers to manipulate database queries.",
            "large_file": "Large files are harder to understand, maintain, and test. They often indicate that the file has too many responsibilities and should be split into smaller, focused modules.",
            "large_function": "Large functions are difficult to understand, test, and maintain. They often violate the Single Responsibility Principle and should be broken into smaller, focused functions.",
            "missing_error_handling": "Missing error handling can lead to application crashes, poor user experience, and potential security vulnerabilities when unexpected conditions occur."
        }
        
        return explanations.get(issue.type.value, "This pattern may impact code quality, security, or maintainability.")
    
    def _analyze_issue_impact(self, issue: DetectedIssue) -> Dict[str, str]:
        """Analyze the impact of an issue"""
        impact_analysis = {
            "security_impact": "None",
            "maintainability_impact": "Low",
            "performance_impact": "None",
            "user_impact": "None"
        }
        
        if issue.type.value in ['hardcoded_secret', 'sql_injection_risk', 'insecure_protocol']:
            impact_analysis["security_impact"] = "High" if issue.severity == Severity.CRITICAL else "Medium"
            impact_analysis["user_impact"] = "High"
        
        if issue.type.value in ['large_file', 'large_function', 'duplicate_code']:
            impact_analysis["maintainability_impact"] = "High"
        
        if issue.type.value in ['deep_nesting', 'large_function']:
            impact_analysis["performance_impact"] = "Low"
        
        return impact_analysis
    
    def _extract_learning_points(self, issue: DetectedIssue) -> List[str]:
        """Extract learning points from an issue"""
        learning_points = {
            "hardcoded_secret": [
                "Always use environment variables for sensitive data",
                "Never commit secrets to version control",
                "Use secrets management systems in production"
            ],
            "sql_injection_risk": [
                "Always use parameterized queries",
                "Validate and sanitize user input",
                "Use ORM methods when possible"
            ],
            "large_file": [
                "Apply Single Responsibility Principle",
                "Extract related functionality into modules",
                "Consider using design patterns for organization"
            ],
            "large_function": [
                "Functions should do one thing well",
                "Extract complex logic into helper functions",
                "Use descriptive function names"
            ]
        }
        
        return learning_points.get(issue.type.value, ["Follow established coding best practices"])
    
    def _get_related_concepts(self, issue: DetectedIssue) -> List[str]:
        """Get related concepts for learning"""
        concepts = {
            "hardcoded_secret": ["Secrets Management", "Environment Variables", "Security by Design"],
            "sql_injection_risk": ["Input Validation", "Parameterized Queries", "Database Security"],
            "large_file": ["Single Responsibility Principle", "Module Design", "Code Organization"],
            "large_function": ["Function Design", "Code Readability", "Cyclomatic Complexity"],
            "missing_error_handling": ["Defensive Programming", "Exception Handling", "Robustness"]
        }
        
        return concepts.get(issue.type.value, ["Software Engineering Best Practices"])
    
    def _find_issue_analysis(self, issue: DetectedIssue, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find LLM analysis for a specific issue"""
        if "individual_analyses" not in analysis_data:
            return None
        
        for analysis in analysis_data["individual_analyses"]:
            analyzed_issue = analysis.get("issue")
            if analyzed_issue and analyzed_issue.rule_id == issue.rule_id and analyzed_issue.line_number == issue.line_number:
                return analysis.get("analysis")
        
        return None
    
    def _assess_overall_risk(self, security_issues: List[DetectedIssue]) -> str:
        """Assess overall security risk level"""
        if not security_issues:
            return "low"
        
        critical_count = len([i for i in security_issues if i.severity == Severity.CRITICAL])
        high_count = len([i for i in security_issues if i.severity == Severity.HIGH])
        
        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"
    
    def _assess_compliance_status(self, security_issues: List[DetectedIssue], context: Dict[str, Any]) -> str:
        """Assess compliance status"""
        if not security_issues:
            return "compliant"
        
        critical_count = len([i for i in security_issues if i.severity == Severity.CRITICAL])
        
        if critical_count > 0:
            return "non_compliant"
        else:
            return "requires_review"
    
    def _generate_remediation_plan(self, security_issues: List[DetectedIssue]) -> List[Dict[str, Any]]:
        """Generate security remediation plan"""
        plan = []
        
        for i, issue in enumerate(security_issues[:5], 1):
            plan.append({
                "step": i,
                "issue_type": issue.type.value,
                "location": f"Line {issue.line_number}",
                "action": issue.fix_suggestion,
                "priority": issue.severity.value,
                "estimated_time": "15-30 minutes"
            })
        
        return plan
    
    def _generate_security_recommendations(self, security_issues: List[DetectedIssue], context: Dict[str, Any]) -> List[str]:
        """Generate security-specific recommendations"""
        recommendations = []
        
        if any(issue.type.value == 'hardcoded_secret' for issue in security_issues):
            recommendations.extend([
                "Implement secrets scanning in CI/CD pipeline",
                "Use a secrets management service",
                "Rotate any exposed secrets immediately"
            ])
        
        if any(issue.type.value == 'sql_injection_risk' for issue in security_issues):
            recommendations.extend([
                "Implement parameterized queries throughout application",
                "Add SQL injection testing to security test suite",
                "Review all database interaction code"
            ])
        
        recommendations.append("Conduct regular security code reviews")
        recommendations.append("Implement automated security scanning")
        
        return recommendations
    
    def _generate_compliance_notes(self, security_issues: List[DetectedIssue], context: Dict[str, Any]) -> List[str]:
        """Generate compliance-related notes"""
        notes = []
        
        if security_issues:
            notes.append("Security issues found may impact compliance with security standards")
            
            if any(issue.severity == Severity.CRITICAL for issue in security_issues):
                notes.append("Critical security issues require immediate remediation")
        
        return notes
    
    def _estimate_cvss_score(self, issue: DetectedIssue) -> float:
        """Estimate CVSS equivalent score"""
        base_scores = {
            "hardcoded_secret": 7.5,
            "sql_injection_risk": 8.5,
            "insecure_protocol": 5.0
        }
        
        base_score = base_scores.get(issue.type.value, 4.0)
        
        # Adjust based on confidence
        adjusted_score = base_score * issue.confidence
        
        return round(adjusted_score, 1)
    
    def _get_verification_steps(self, issue: DetectedIssue) -> List[str]:
        """Get verification steps for security fixes"""
        verification_steps = {
            "hardcoded_secret": [
                "Verify secret is removed from code",
                "Confirm environment variable is properly loaded",
                "Test application functionality with new configuration"
            ],
            "sql_injection_risk": [
                "Verify parameterized query implementation",
                "Test with SQL injection payloads",
                "Confirm no user input reaches SQL directly"
            ],
            "insecure_protocol": [
                "Verify secure protocol is used",
                "Test connection security",
                "Confirm no fallback to insecure protocol"
            ]
        }
        
        return verification_steps.get(issue.type.value, ["Verify fix implementation", "Test functionality"])
    
    def _extract_key_findings(self, issues: List[DetectedIssue]) -> List[str]:
        """Extract key findings from issues"""
        findings = []
        
        # Group by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.type.value
            if issue_type not in issue_types:
                issue_types[issue_type] = 0
            issue_types[issue_type] += 1
        
        # Generate findings
        for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
            if count == 1:
                findings.append(f"Found {issue_type.replace('_', ' ')}")
            else:
                findings.append(f"Found {count} instances of {issue_type.replace('_', ' ')}")
        
        return findings[:5]  # Top 5 findings
    
    def _generate_next_steps(self, result: DetectionResult) -> List[str]:
        """Generate next steps based on results"""
        steps = []
        
        if result.has_blocking_issues:
            steps.append("🚨 Address critical issues before deployment")
        
        if len(result.high_issues) > 0:
            steps.append("⚠️ Review and fix high-priority issues")
        
        if len(result.issues) > 5:
            steps.append("📋 Prioritize issues by business impact")
        
        steps.append("✅ Run tests after each fix")
        steps.append("🔄 Re-run analysis to verify improvements")
        
        return steps
    
    def _get_next_action(self, result: DetectionResult) -> str:
        """Get the single most important next action"""
        if result.has_blocking_issues:
            critical_issue = result.critical_issues[0]
            return f"Fix critical {critical_issue.type.value} on line {critical_issue.line_number}"
        
        if result.high_issues:
            high_issue = result.high_issues[0]
            return f"Address {high_issue.type.value} on line {high_issue.line_number}"
        
        if result.issues:
            return "Review and prioritize remaining issues"
        
        return "Code analysis complete - ready for review"
    
    def _estimate_total_fix_time(self, issues: List[DetectedIssue]) -> str:
        """Estimate total time to fix issues"""
        if not issues:
            return "No fixes needed"
        
        time_estimates = {
            "hardcoded_secret": 20,
            "sql_injection_risk": 30,
            "large_function": 60,
            "missing_error_handling": 25
        }
        
        total_minutes = sum(time_estimates.get(issue.type.value, 15) for issue in issues)
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"