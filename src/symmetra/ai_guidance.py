"""
AI-Powered Architectural Guidance System

This module provides intelligent architectural guidance by leveraging AI analysis
combined with vector-based rule retrieval. The focus is on giving Claude Code
excellent architectural advice based on team-specific rules when needed.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Import vector search engine
from symmetra.vector_search import vector_search_engine

logger = logging.getLogger(__name__)


@dataclass
class GuidanceResponse:
    """Response from AI architectural guidance analysis"""
    guidance: List[str]
    status: str  # "advisory" (never blocking)
    action: str  # Original action for reference
    complexity_score: str  # "low", "medium", "high"
    patterns: List[str] = None  # Suggested architectural patterns
    rules_applied: List[str] = None  # Which rules were used
    code_analysis: Dict[str, Any] = None  # Code analysis metadata
    external_resources: List[Dict[str, str]] = None  # External URLs for fresh documentation
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "guidance": self.guidance,
            "status": self.status,
            "action": self.action,
            "complexity_score": self.complexity_score,
            "patterns": self.patterns or [],
            "rules_applied": self.rules_applied or [],
            "code_analysis": self.code_analysis or {
                "lines_analyzed": len(self.action.split()) if hasattr(self, 'action') else 0,
                "context_provided": bool(self.rules_applied),
                "rules_matched": len(self.rules_applied) if self.rules_applied else 0
            }
        }
        
        # Add external resources if available
        if self.external_resources:
            result["external_resources"] = self.external_resources
            
        return result


class AIGuidanceEngine:
    """
    AI-powered architectural guidance engine
    
    This engine uses AI analysis to provide contextual architectural guidance
    instead of complex deterministic rule systems.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_guidance(self, action: str, code: str = "", context: str = "", project_id: str = None) -> GuidanceResponse:
        """
        Get AI-powered architectural guidance for a coding action
        
        Args:
            action: What you're planning to do (e.g., "create user authentication")
            code: Optional existing code to analyze
            context: Optional additional context about the project
            project_id: Optional project ID for team-specific rules
            
        Returns:
            GuidanceResponse with AI-generated architectural guidance
        """
        try:
            # Use vector search to find relevant rules
            if vector_search_engine.is_available():
                guidance = self._get_vector_guidance(action, code, context, project_id)
            else:
                # Fallback to hardcoded guidance if vector search unavailable
                self.logger.warning("Vector search unavailable, using fallback guidance")
                guidance = self._analyze_action(action, code, context)
            
            complexity = self._assess_complexity(action, code)
            patterns = self._suggest_patterns(action, context)
            
            # Collect metadata for response
            rules_applied = []
            external_resources = []
            if vector_search_engine.is_available() and guidance != self._analyze_action(action, code, context):
                # We used vector search, extract rule names and external URLs
                try:
                    relevant_rules = vector_search_engine.search_rules(f"{action} {context}".strip(), project_id=project_id, limit=3)
                    rules_applied = [rule['title'] for rule in relevant_rules]
                    
                    # Collect external resources from all relevant rules
                    for rule in relevant_rules:
                        if rule.get('external_urls'):
                            for key, url in rule['external_urls'].items():
                                external_resources.append({
                                    "title": key.replace("_", " ").title(),
                                    "url": url,
                                    "why": f"For latest {key.replace('_', ' ')}"
                                })
                except:
                    pass
            
            return GuidanceResponse(
                guidance=guidance,
                status="advisory",
                action=action,
                complexity_score=complexity,
                patterns=patterns,
                rules_applied=rules_applied,
                external_resources=external_resources if external_resources else None,
                code_analysis={
                    "lines_analyzed": len(code.split('\n')) if code else 0,
                    "context_provided": bool(context),
                    "rules_matched": len(rules_applied)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error generating guidance: {e}")
            return GuidanceResponse(
                guidance=["Unable to generate guidance at this time"],
                status="advisory", 
                action=action,
                complexity_score="unknown"
            )
    
    def _get_vector_guidance(self, action: str, code: str, context: str, project_id: str = None) -> List[str]:
        """
        Get guidance using vector search of rules database
        
        Args:
            action: What the user wants to do
            code: Optional existing code
            context: Optional project context
            project_id: Optional project ID for team-specific rules
            
        Returns:
            List of guidance strings synthesized from relevant rules
        """
        try:
            # Search for relevant rules
            query = f"{action} {context}".strip()
            relevant_rules = vector_search_engine.search_rules(query, project_id=project_id, limit=3)
            
            if not relevant_rules:
                # No relevant rules found, use fallback
                self.logger.info("No relevant rules found, using fallback guidance")
                return self._analyze_action(action, code, context)
            
            # Synthesize guidance from relevant rules
            guidance = []
            
            # Add context about which rules are being applied
            rule_names = [rule['title'] for rule in relevant_rules]
            guidance.append(f"🎯 Applying guidance from: {', '.join(rule_names)}")
            guidance.append("")
            
            # Add guidance from each relevant rule
            for rule in relevant_rules:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rule['priority'], "⚪")
                category_emoji = {
                    "architecture": "🏗️", "security": "🔒", "performance": "⚡", 
                    "ai-ml": "🧠", "devops": "🚀", "testing": "🧪"
                }.get(rule['category'], "📋")
                
                guidance.append(f"{priority_emoji} {category_emoji} **{rule['title']}**")
                guidance.append(rule['guidance'])
                
                if rule.get('rationale'):
                    guidance.append(f"*Rationale: {rule['rationale']}*")
                
                guidance.append("")
            
            # Add code-specific analysis if code provided
            if code:
                code_guidance = self._analyze_code_structure(code)
                if code_guidance:
                    guidance.append("📄 **Code Analysis:**")
                    guidance.extend(code_guidance)
            
            return guidance
            
        except Exception as e:
            self.logger.error(f"Vector guidance failed: {e}")
            # Fallback to hardcoded guidance
            return self._analyze_action(action, code, context)
    
    def _analyze_action(self, action: str, code: str, context: str) -> List[str]:
        """Analyze the action and provide contextual guidance"""
        guidance = []
        action_lower = action.lower()
        
        # Authentication guidance - Minimal fallback (detailed guides should be in vector DB)
        if any(word in action_lower for word in ['auth', 'login', 'user', 'password', 'jwt', 'token']):
            guidance.extend([
                "🔐 **Authentication Implementation:**",
                "• Use bcrypt/Argon2 for password hashing",
                "• Implement JWT with proper secret management (RS256 preferred)",
                "• Add rate limiting to prevent brute force attacks",
                "• Use HTTPS everywhere for auth endpoints",
                "• Consider OAuth 2.0 for third-party integrations",
                "",
                "⚠️ **Note**: For comprehensive implementation guides, ensure your team's",
                "authentication patterns are stored in the Symmetra vector database.",
                "This fallback provides basic guidance only."
            ])
            
        # Database guidance  
        elif any(word in action_lower for word in ['database', 'db', 'sql', 'data']):
            guidance.extend([
                "🗄️ For database architecture:",
                "• Use connection pooling for better performance",
                "• Implement proper indexing strategy", 
                "• Use parameterized queries to prevent SQL injection",
                "• Consider read replicas for high-traffic applications",
                "• Plan for database migrations and schema versioning"
            ])
            
        # API guidance
        elif any(word in action_lower for word in ['api', 'endpoint', 'rest', 'graphql']):
            guidance.extend([
                "🌐 For API design:",
                "• Follow RESTful conventions or GraphQL best practices",
                "• Implement proper error handling and status codes",
                "• Add request/response validation",
                "• Use API versioning strategy",
                "• Consider rate limiting and authentication",
                "• Document your API with OpenAPI/Swagger"
            ])
            
        # Performance guidance
        elif any(word in action_lower for word in ['performance', 'optimize', 'cache', 'speed']):
            guidance.extend([
                "⚡ For performance optimization:",
                "• Profile before optimizing - measure actual bottlenecks",
                "• Implement caching at appropriate layers (Redis, CDN)",
                "• Use database query optimization and indexing",
                "• Consider asynchronous processing for heavy operations",
                "• Implement pagination for large data sets"
            ])
            
        # Security guidance
        elif any(word in action_lower for word in ['security', 'secure', 'protection']):
            guidance.extend([
                "🛡️ For security implementation:",
                "• Follow OWASP Top 10 security guidelines", 
                "• Implement input validation and sanitization",
                "• Use HTTPS everywhere and secure headers",
                "• Apply principle of least privilege",
                "• Regular security audits and dependency updates",
                "• Never commit secrets to version control"
            ])
            
        # Architecture guidance
        elif any(word in action_lower for word in ['architecture', 'design', 'structure', 'organize']):
            guidance.extend([
                "🏗️ For architectural design:",
                "• Follow SOLID principles and clean architecture",
                "• Separate concerns into focused modules",
                "• Use dependency injection for better testability", 
                "• Consider microservices vs monolith trade-offs",
                "• Plan for scalability and maintainability",
                "• Document architectural decisions and rationale"
            ])
            
        # Code analysis guidance
        if code:
            code_guidance = self._analyze_code_structure(code)
            guidance.extend(code_guidance)
            
        # Default guidance if no specific pattern matched
        if not guidance:
            guidance.extend([
                "🎯 General architectural guidance:",
                "• Keep it simple - avoid over-engineering",
                "• Write tests for critical functionality",
                "• Use established patterns and libraries",
                "• Consider maintainability and future changes",
                "• Document important decisions and assumptions"
            ])
            
        return guidance
    
    def _analyze_code_structure(self, code: str) -> List[str]:
        """Analyze existing code and provide improvement suggestions"""
        guidance = []
        lines = code.split('\n')
        
        # Basic code analysis
        if len(lines) > 100:
            guidance.append("📄 Consider breaking large files into smaller, focused modules")
            
        if 'TODO' in code or 'FIXME' in code:
            guidance.append("📝 Address TODO/FIXME comments before production")
            
        if 'password' in code.lower() and any(char in code for char in ['"', "'"]):
            guidance.append("⚠️ Potential hardcoded credentials detected - use environment variables")
            
        return guidance
    
    def _assess_complexity(self, action: str, code: str) -> str:
        """Assess the complexity of the action/code"""
        complexity_indicators = [
            'microservice', 'distributed', 'async', 'concurrent',
            'authentication', 'authorization', 'security',
            'database', 'transaction', 'migration',
            'performance', 'optimization', 'scaling'
        ]
        
        action_lower = action.lower()
        matches = sum(1 for indicator in complexity_indicators if indicator in action_lower)
        
        if code and len(code.split('\n')) > 100:
            matches += 1
            
        if matches >= 3:
            return "high"
        elif matches >= 1:
            return "medium"
        else:
            return "low"
    
    def _suggest_patterns(self, action: str, context: str) -> List[str]:
        """Suggest relevant architectural patterns"""
        patterns = []
        action_lower = action.lower()
        context_lower = context.lower()
        
        if 'auth' in action_lower:
            patterns.extend(["JWT Token Pattern", "OAuth 2.0", "Session Management"])
            
        if 'api' in action_lower:
            patterns.extend(["REST API", "Repository Pattern", "DTO Pattern"])
            
        if 'database' in action_lower:
            patterns.extend(["Repository Pattern", "Unit of Work", "Active Record"])
            
        if any(word in action_lower for word in ['large', 'complex', 'enterprise']):
            patterns.extend(["Microservices", "CQRS", "Event Sourcing"])
            
        if 'cache' in action_lower:
            patterns.extend(["Cache-Aside", "Write-Through Cache", "Cache Abstraction"])
            
        return patterns[:3]  # Limit to top 3 suggestions


# Simple secret detection (keep this deterministic)
class SimpleSecretDetector:
    """Simple, focused secret detection"""
    
    SECRET_PATTERNS = [
        r'api[_-]?key["\']?\s*[:=]\s*["\'][^"\']{16,}["\']',
        r'password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']',
        r'secret["\']?\s*[:=]\s*["\'][^"\']{16,}["\']',
        r'token["\']?\s*[:=]\s*["\'][^"\']{20,}["\']',
        r'github[_-]?token["\']?\s*[:=]\s*["\']ghp_[^"\']+["\']',
    ]
    
    def scan_secrets(self, code: str) -> List[Dict[str, Any]]:
        """Scan for potential hardcoded secrets"""
        import re
        
        secrets = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    secrets.append({
                        "type": "hardcoded_secret",
                        "line": line_num,
                        "message": "Potential hardcoded secret detected",
                        "severity": "high",
                        "suggestion": "Use environment variables or secure secret management"
                    })
                    
        return secrets


# Singleton instances
guidance_engine = AIGuidanceEngine()
secret_detector = SimpleSecretDetector()