"""
SecurityDetector - Detect security vulnerabilities and risks

Focuses on high-confidence, definitive security issues that can be detected
with pattern matching and should be fixed immediately.

Detection Categories:
- Hardcoded secrets (API keys, passwords, tokens)
- SQL injection risks (string concatenation in queries)
- Insecure protocols (HTTP in production contexts)
- Weak cryptographic practices
- Authentication bypasses
"""

import re
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from .base import Detector, DetectedIssue, IssueType, Severity


class SecurityDetector(Detector):
    """Security vulnerability detection"""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        
        # Hardcoded secret patterns with confidence scores
        self.secret_patterns = [
            # API Keys (high confidence)
            (r'api[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_\-]{8,})["\']', "api_key", 0.95),
            # OpenAI-style API keys
            (r'["\']sk-[a-zA-Z0-9]{32,}["\']', "openai_api_key", 0.95),
            (r'secret[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_\-]{8,})["\']', "secret_key", 0.95),
            
            # AWS Credentials (very high confidence)
            (r'AKIA[0-9A-Z]{16}', "aws_access_key", 0.98),
            (r'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9/+=]{40})["\']', "aws_secret", 0.95),
            
            # JWT Tokens (high confidence)
            (r'eyJ[A-Za-z0-9_/+\-]{10,}={0,2}', "jwt_token", 0.90),
            
            # Database URLs with passwords (high confidence)
            (r'[a-zA-Z][a-zA-Z0-9+.-]*://[^:]+:([^@\s]{8,})@', "db_password", 0.85),
            
            # GitHub Tokens
            (r'gh[ps]_[a-zA-Z0-9]{36}', "github_token", 0.95),
            
            # Generic password assignments (high confidence)
            (r'["\']?password["\']?\s*[=:]\s*["\']([^"\']{8,})["\']', "hardcoded_password", 0.90),
            
            # Private keys (very high confidence)
            (r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----', "private_key", 0.99),
            
            # Slack tokens
            (r'xox[baprs]-[0-9a-zA-Z\-]{10,}', "slack_token", 0.95),
            
            # Generic high-entropy strings in assignments (low confidence)
            (r'[a-zA-Z_][a-zA-Z0-9_]*\s*[=:]\s*["\']([a-zA-Z0-9/+=]{32,})["\']', "high_entropy_string", 0.40),
        ]
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            # String concatenation with variables - either side can have concatenation
            (r'["\'][^"\']*["\']\s*\+\s*[a-zA-Z_][a-zA-Z0-9_]*', "string_concat_right", 0.80),
            (r'[a-zA-Z_][a-zA-Z0-9_]*\s*\+\s*["\'][^"\']*["\']', "string_concat_left", 0.80),
            # f-string formatting in SQL
            (r'f["\'][^"\']*{[^}]+}[^"\']*["\']\s*', "f_string_sql", 0.85),
            # % formatting in SQL
            (r'["\'][^"\']*%s[^"\']*["\'].*%', "percent_format", 0.80),
            # .format() in SQL
            (r'["\'][^"\']*{[^}]*}[^"\']*["\']\.format\s*\(', "format_method", 0.75),
            # JavaScript template literals with variables
            (r'`[^`]*\$\{[^}]+\}[^`]*`', "template_literal", 0.85),
        ]
        
        # Insecure protocol patterns
        self.protocol_patterns = [
            # HTTP URLs (context-dependent)
            (r'http://[^\s"\'>]+', "http_url", 0.60),
            # FTP URLs
            (r'ftp://[^\s"\'>]+', "ftp_url", 0.85),
            # Telnet
            (r'telnet://[^\s"\'>]+', "telnet_url", 0.90),
        ]
        
        # Weak crypto patterns
        self.crypto_patterns = [
            # MD5 usage
            (r'hashlib\.md5\s*\(|md5\s*\(', "md5_usage", 0.85),
            # SHA1 usage
            (r'hashlib\.sha1\s*\(|sha1\s*\(', "sha1_usage", 0.75),
            # DES encryption
            (r'DES\.|des\.|Cipher\.DES', "des_encryption", 0.95),
            # Hardcoded encryption keys
            (r'key\s*=\s*["\'][a-zA-Z0-9/+=]{16,}["\']', "hardcoded_crypto_key", 0.70),
        ]
    
    def detect(self, code: str, file_path: str, context: Dict[str, Any]) -> List[DetectedIssue]:
        """Detect security issues in code"""
        issues = []
        language = context.get('language', '').lower()
        
        # Skip detection for test files and documentation
        if self._is_test_or_doc_file(file_path):
            return issues
        
        # Detect hardcoded secrets
        issues.extend(self._detect_secrets(code, file_path, language))
        
        # Detect SQL injection risks
        issues.extend(self._detect_sql_injection(code, file_path, language))
        
        # Detect insecure protocols
        issues.extend(self._detect_insecure_protocols(code, file_path, context))
        
        # Detect weak cryptography
        issues.extend(self._detect_weak_crypto(code, file_path, language))
        
        # Detect authentication bypasses
        issues.extend(self._detect_auth_bypasses(code, file_path, language))
        
        # Deduplicate issues on the same line  
        return self._deduplicate_issues(issues)
    
    def _is_test_or_doc_file(self, file_path: str) -> bool:
        """Check if file is likely a test or documentation file"""
        path_lower = file_path.lower()
        test_indicators = [
            'test_', '_test.', '/test/', '/tests/',
            'spec_', '_spec.', '/spec/', '/specs/',
            'example', 'demo', 'sample',
            'readme', 'doc', '.md', '.txt'
        ]
        return any(indicator in path_lower for indicator in test_indicators)
    
    def _detect_secrets(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Detect hardcoded secrets and credentials"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and strings that are clearly examples
            if self._is_comment_or_example(line):
                continue
            
            for pattern, secret_type, confidence in self.secret_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Additional validation for high-entropy strings
                    if secret_type == "high_entropy_string":
                        if not self._is_likely_secret(match.group(1)):
                            continue
                    
                    # Skip obvious false positives - check the captured value if available, else full match
                    check_value = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                    if self._is_false_positive_secret(check_value, secret_type):
                        continue
                    
                    severity = Severity.CRITICAL if confidence > 0.85 else Severity.HIGH
                    
                    issues.append(DetectedIssue(
                        type=IssueType.HARDCODED_SECRET,
                        severity=severity,
                        rule_id=f"SEC-001-{secret_type.upper()}",
                        file_path=file_path,
                        line_number=line_num,
                        evidence=f"Detected {secret_type}: {match.group(0)[:60]}...",
                        message=f"Hardcoded {secret_type.replace('_', ' ')} detected",
                        fix_suggestion=self._get_secret_fix_suggestion(secret_type),
                        confidence=confidence,
                        language=language,
                        pattern_matched=pattern,
                        matched_text=match.group(0)[:50]  # Truncate for safety
                    ))
        
        return issues
    
    def _is_comment_or_example(self, line: str) -> bool:
        """Check if line is a comment or example"""
        stripped = line.strip()
        comment_prefixes = ['#', '//', '/*', '*', '<!--']
        
        # Check for comment syntax
        if any(stripped.startswith(prefix) for prefix in comment_prefixes):
            return True
        
        # Check for specific example indicators that suggest placeholder content
        line_lower = line.lower()
        example_indicators = [
            'your-key-here', 'your_key_here', 'api_key_here',
            'put_your_key_here', 'insert_key_here', 'replace_with',
            'placeholder', 'sample_key', 'demo_key', 'test_key'
        ]
        
        return any(indicator in line_lower for indicator in example_indicators)
    
    def _is_likely_secret(self, value: str) -> bool:
        """Check if a high-entropy string is likely a real secret"""
        if len(value) < 20:
            return False
        
        # Check entropy
        entropy = self._calculate_entropy(value)
        if entropy < 3.5:  # Low entropy threshold
            return False
        
        # Check character distribution
        char_types = {
            'upper': sum(1 for c in value if c.isupper()),
            'lower': sum(1 for c in value if c.islower()),
            'digit': sum(1 for c in value if c.isdigit()),
            'special': sum(1 for c in value if not c.isalnum())
        }
        
        # Real secrets typically have mixed character types
        non_zero_types = sum(1 for count in char_types.values() if count > 0)
        return non_zero_types >= 2
    
    def _calculate_entropy(self, value: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not value:
            return 0
        
        char_counts = {}
        for char in value:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        entropy = 0
        length = len(value)
        for count in char_counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def _is_false_positive_secret(self, matched_text: str, secret_type: str) -> bool:
        """Check for common false positives"""
        text_lower = matched_text.lower()
        
        false_positive_patterns = [
            # Common placeholder values
            'your_key_here', 'api_key_here', 'secret_key_here',
            'put_your_key_here', 'insert_key_here',
            # Example values
            'example', 'sample', 'demo', 
            # Obviously fake values that are standalone
            '"123456"', '"password"', '"secret"', '"key"',
            'xxxxxxxx', 'aaaaaaaa', 'bbbbbbbb',
            # Common development values
            'development', 'dev', 'local', 'localhost',
            # Test indicators that should be more specific
            'test_key', 'test_secret', 'dummy_key'
        ]
        
        return any(pattern in text_lower for pattern in false_positive_patterns)
    
    def _get_secret_fix_suggestion(self, secret_type: str) -> str:
        """Get specific fix suggestion for each secret type"""
        fix_suggestions = {
            "api_key": "Move to environment variable: os.getenv('API_KEY')",
            "secret_key": "Use environment variable: os.getenv('SECRET_KEY')",
            "aws_access_key": "Use AWS credentials file or IAM roles",
            "aws_secret": "Use AWS credentials file or IAM roles",
            "jwt_token": "Generate tokens dynamically, never hardcode",
            "db_password": "Use environment variables or secrets management",
            "github_token": "Use GitHub secrets or environment variables",
            "hardcoded_password": "Store in secure configuration or vault",
            "private_key": "Load from secure file system or secrets manager",
            "slack_token": "Use environment variables for tokens",
            "high_entropy_string": "Verify if secret, move to environment variable if so"
        }
        
        return fix_suggestions.get(secret_type, "Move sensitive value to environment variable")
    
    def _detect_sql_injection(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Detect SQL injection vulnerabilities"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if self._is_comment_or_example(line):
                continue
            
            # Check if line contains SQL keywords
            if not any(keyword in line.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE']):
                continue
            
            for pattern, injection_type, confidence in self.sql_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(DetectedIssue(
                        type=IssueType.SQL_INJECTION_RISK,
                        severity=Severity.HIGH,
                        rule_id=f"SEC-002-{injection_type.upper()}",
                        file_path=file_path,
                        line_number=line_num,
                        evidence=f"SQL query with {injection_type}: {line.strip()[:50]}...",
                        message=f"Potential SQL injection via {injection_type}",
                        fix_suggestion="Use parameterized queries or ORM methods",
                        confidence=confidence,
                        language=language,
                        pattern_matched=pattern,
                        matched_text=line.strip()[:100]
                    ))
        
        return issues
    
    def _detect_insecure_protocols(self, code: str, file_path: str, context: Dict[str, Any]) -> List[DetectedIssue]:
        """Detect usage of insecure protocols"""
        issues = []
        lines = code.split('\n')
        environment = context.get('environment', 'unknown').lower()
        
        for line_num, line in enumerate(lines, 1):
            if self._is_comment_or_example(line):
                continue
            
            for pattern, protocol_type, base_confidence in self.protocol_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Adjust confidence based on context
                    confidence = base_confidence
                    severity = Severity.MEDIUM
                    
                    # HTTP is more critical in production
                    if protocol_type == "http_url" and environment in ['production', 'prod']:
                        confidence = 0.85
                        severity = Severity.HIGH
                    
                    # Skip localhost URLs (likely development)
                    if 'localhost' in match.group(0) or '127.0.0.1' in match.group(0):
                        confidence *= 0.5
                    
                    if confidence > 0.5:  # Only report if confident
                        issues.append(DetectedIssue(
                            type=IssueType.INSECURE_PROTOCOL,
                            severity=severity,
                            rule_id=f"SEC-003-{protocol_type.upper()}",
                            file_path=file_path,
                            line_number=line_num,
                            evidence=f"Insecure protocol: {match.group(0)}",
                            message=f"Usage of insecure {protocol_type.replace('_', ' ')}",
                            fix_suggestion=self._get_protocol_fix_suggestion(protocol_type),
                            confidence=confidence,
                            pattern_matched=pattern,
                            matched_text=match.group(0)
                        ))
        
        return issues
    
    def _get_protocol_fix_suggestion(self, protocol_type: str) -> str:
        """Get fix suggestion for insecure protocols"""
        suggestions = {
            "http_url": "Use HTTPS instead of HTTP for secure communication",
            "ftp_url": "Use SFTP or FTPS instead of plain FTP",
            "telnet_url": "Use SSH instead of Telnet"
        }
        return suggestions.get(protocol_type, "Use secure protocol alternative")
    
    def _deduplicate_issues(self, issues: List[DetectedIssue]) -> List[DetectedIssue]:
        """Remove duplicate issues on the same line, keeping the highest confidence one"""
        if not issues:
            return issues
        
        # Group by file_path and line_number
        issue_groups = {}
        for issue in issues:
            key = (issue.file_path, issue.line_number)
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(issue)
        
        # For each line, keep only the highest confidence issue
        deduplicated = []
        for line_issues in issue_groups.values():
            if len(line_issues) == 1:
                deduplicated.extend(line_issues)
            else:
                # Keep the one with highest confidence
                best_issue = max(line_issues, key=lambda x: x.confidence)
                deduplicated.append(best_issue)
        
        return deduplicated
    
    def _detect_weak_crypto(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Detect weak cryptographic practices"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if self._is_comment_or_example(line):
                continue
            
            for pattern, crypto_type, confidence in self.crypto_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    severity = Severity.HIGH if confidence > 0.8 else Severity.MEDIUM
                    
                    issues.append(DetectedIssue(
                        type=IssueType.INSECURE_PROTOCOL,  # Reusing for crypto
                        severity=severity,
                        rule_id=f"SEC-004-{crypto_type.upper()}",
                        file_path=file_path,
                        line_number=line_num,
                        evidence=f"Weak cryptography: {line.strip()[:50]}...",
                        message=f"Usage of weak {crypto_type.replace('_', ' ')}",
                        fix_suggestion=self._get_crypto_fix_suggestion(crypto_type),
                        confidence=confidence,
                        language=language,
                        pattern_matched=pattern,
                        matched_text=line.strip()[:100]
                    ))
        
        return issues
    
    def _get_crypto_fix_suggestion(self, crypto_type: str) -> str:
        """Get fix suggestion for weak crypto"""
        suggestions = {
            "md5_usage": "Use SHA-256 or bcrypt for hashing",
            "sha1_usage": "Use SHA-256 or stronger hash function",
            "des_encryption": "Use AES encryption instead",
            "hardcoded_crypto_key": "Generate keys dynamically or use key derivation"
        }
        return suggestions.get(crypto_type, "Use modern, secure cryptographic methods")
    
    def _detect_auth_bypasses(self, code: str, file_path: str, language: str) -> List[DetectedIssue]:
        """Detect potential authentication bypasses"""
        issues = []
        lines = code.split('\n')
        
        # Look for suspicious authentication patterns
        auth_bypass_patterns = [
            # Always true conditions
            (r'if\s+True\s*:', "always_true_auth", 0.70),
            # Debug mode bypasses
            (r'if\s+debug\s*:', "debug_bypass", 0.60),
            # Comment out auth
            (r'#.*auth|//.*auth', "commented_auth", 0.50),
            # Hardcoded admin checks
            (r'user.*==.*["\']admin["\']', "hardcoded_admin", 0.75),
        ]
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # Only check lines that seem related to authentication
            if not any(keyword in line_lower for keyword in ['auth', 'login', 'user', 'admin', 'permission']):
                continue
            
            for pattern, bypass_type, confidence in auth_bypass_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(DetectedIssue(
                        type=IssueType.MISSING_ERROR_HANDLING,  # Reusing enum
                        severity=Severity.HIGH,
                        rule_id=f"SEC-005-{bypass_type.upper()}",
                        file_path=file_path,
                        line_number=line_num,
                        evidence=f"Potential auth bypass: {line.strip()[:50]}...",
                        message=f"Potential authentication bypass via {bypass_type}",
                        fix_suggestion="Implement proper authentication checks",
                        confidence=confidence,
                        language=language,
                        pattern_matched=pattern,
                        matched_text=line.strip()[:100]
                    ))
        
        return issues
    
    def get_supported_languages(self) -> List[str]:
        """Languages supported by security detector"""
        return ["python", "javascript", "typescript", "java", "csharp", "php", "ruby", "go", "all"]
    
    def get_detection_patterns(self) -> Dict[str, str]:
        """Get patterns this detector looks for"""
        return {
            "hardcoded_secrets": "API keys, passwords, tokens in source code",
            "sql_injection": "String concatenation in SQL queries", 
            "insecure_protocols": "HTTP, FTP, Telnet usage",
            "weak_crypto": "MD5, SHA1, DES usage",
            "auth_bypasses": "Suspicious authentication patterns",
            "http": "Insecure HTTP protocol detection",
            "secret": "Hardcoded secret detection"
        }
    
    def get_detector_info(self) -> Dict[str, Any]:
        """Get information about this detector"""
        base_info = super().get_detector_info()
        base_info.update({
            "version": "1.0",
            "issue_types": ["hardcoded_secret", "sql_injection_risk", "insecure_protocol"]
        })
        return base_info