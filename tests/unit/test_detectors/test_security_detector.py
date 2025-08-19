"""
Unit tests for SecurityDetector

Tests the security detection capabilities including hardcoded secrets,
SQL injection risks, and insecure protocols.
"""

import pytest
from src.symmetra.detectors.security import SecurityDetector
from src.symmetra.detectors.base import Severity, IssueType


class TestSecurityDetector:
    """Test SecurityDetector functionality"""
    
    def setup_method(self):
        """Set up test instance"""
        self.detector = SecurityDetector()
    
    def test_detector_initialization(self):
        """Test detector initializes correctly"""
        assert self.detector.name == "SecurityDetector"
        assert self.detector.enabled is True
        assert len(self.detector.get_detection_patterns()) > 0
    
    def test_should_run_for_supported_languages(self):
        """Test detector runs for supported languages"""
        assert self.detector.should_run("test.py", "python", {})
        assert self.detector.should_run("test.js", "javascript", {})
        assert self.detector.should_run("test.java", "java", {})
        assert self.detector.should_run("test.unknown", None, {})
    
    def test_hardcoded_api_key_detection(self):
        """Test detection of hardcoded API keys"""
        code = '''
        def get_data():
            api_key = "sk-1234567890abcdef1234567890abcdef"
            headers = {"Authorization": f"Bearer {api_key}"}
            return requests.get("https://api.example.com", headers=headers)
        '''
        
        issues = self.detector.detect(code, "test.py", {"language": "python"})
        
        assert len(issues) == 1
        issue = issues[0]
        assert issue.type == IssueType.HARDCODED_SECRET
        assert issue.severity == Severity.CRITICAL
        assert "sk-" in issue.evidence
        assert "environment variable" in issue.fix_suggestion.lower()
        assert issue.confidence >= 0.9
    
    def test_hardcoded_password_detection(self):
        """Test detection of hardcoded passwords"""
        code = '''
        database_config = {
            "host": "localhost",
            "user": "admin", 
            "password": "super_secret_password_123",
            "database": "myapp"
        }
        '''
        
        issues = self.detector.detect(code, "config.py", {"language": "python"})
        
        assert len(issues) == 1
        issue = issues[0]
        assert issue.type == IssueType.HARDCODED_SECRET
        assert issue.severity == Severity.CRITICAL
        assert "super_secret_password_123" in issue.evidence
    
    def test_github_token_detection(self):
        """Test detection of GitHub tokens"""
        code = '''
        const config = {
            githubToken: "ghp_1234567890abcdef1234567890abcdef123456",
            apiUrl: "https://api.github.com"
        };
        '''
        
        issues = self.detector.detect(code, "config.js", {"language": "javascript"})
        
        assert len(issues) == 1
        issue = issues[0]
        assert issue.type == IssueType.HARDCODED_SECRET
        assert "ghp_" in issue.evidence
        assert issue.confidence >= 0.95  # GitHub tokens have high confidence
    
    def test_sql_injection_string_concatenation(self):
        """Test detection of SQL injection via string concatenation"""
        code = '''
        def get_user(user_id):
            query = "SELECT * FROM users WHERE id = " + user_id
            return execute_query(query)
        '''
        
        issues = self.detector.detect(code, "database.py", {"language": "python"})
        
        assert len(issues) == 1
        issue = issues[0]
        assert issue.type == IssueType.SQL_INJECTION_RISK
        assert issue.severity == Severity.HIGH
        assert "parameterized" in issue.fix_suggestion.lower()
    
    def test_sql_injection_format_string(self):
        """Test detection of SQL injection via format strings"""
        code = '''
        function getUserData(username) {
            const query = `SELECT * FROM users WHERE username = '${username}'`;
            return db.query(query);
        }
        '''
        
        issues = self.detector.detect(code, "user.js", {"language": "javascript"})
        
        assert len(issues) == 1
        issue = issues[0]
        assert issue.type == IssueType.SQL_INJECTION_RISK
        assert issue.severity == Severity.HIGH
    
    def test_insecure_http_protocol(self):
        """Test detection of insecure HTTP protocols"""
        code = '''
        def fetch_data():
            response = requests.get("http://api.example.com/data")
            return response.json()
        '''
        
        issues = self.detector.detect(code, "api.py", {"language": "python"})
        
        assert len(issues) == 1
        issue = issues[0]
        assert issue.type == IssueType.INSECURE_PROTOCOL
        assert issue.severity == Severity.MEDIUM
        assert "https" in issue.fix_suggestion.lower()
    
    def test_multiple_security_issues(self):
        """Test detection of multiple security issues in one file"""
        code = '''
        import requests
        
        API_KEY = "secret_key_12345"
        
        def get_user_data(user_id):
            # SQL injection risk
            query = "SELECT * FROM users WHERE id = " + user_id
            result = execute_query(query)
            
            # Insecure protocol
            api_url = "http://api.example.com/user/" + user_id
            response = requests.get(api_url, headers={"X-API-Key": API_KEY})
            
            return result, response.json()
        '''
        
        issues = self.detector.detect(code, "user_service.py", {"language": "python"})
        
        # Should detect: hardcoded secret, SQL injection, insecure protocol
        assert len(issues) == 3
        
        issue_types = [issue.type for issue in issues]
        assert IssueType.HARDCODED_SECRET in issue_types
        assert IssueType.SQL_INJECTION_RISK in issue_types
        assert IssueType.INSECURE_PROTOCOL in issue_types
    
    def test_false_positive_avoidance_comments(self):
        """Test that comments don't trigger false positives"""
        code = '''
        # Example: api_key = "sk-1234567890abcdef"
        # This is just documentation, not actual code
        def setup_api():
            # TODO: Load API key from environment
            api_key = os.getenv("API_KEY")
            return api_key
        '''
        
        issues = self.detector.detect(code, "setup.py", {"language": "python"})
        
        # Should not detect the commented example as a real secret
        hardcoded_secrets = [i for i in issues if i.type == IssueType.HARDCODED_SECRET]
        assert len(hardcoded_secrets) == 0
    
    def test_false_positive_avoidance_test_files(self):
        """Test reduced severity for test files"""
        code = '''
        def test_api_integration():
            api_key = "test_key_12345"  # Test key
            client = ApiClient(api_key)
            assert client.is_valid()
        '''
        
        issues = self.detector.detect(code, "test_api.py", {"language": "python"})
        
        if issues:  # May or may not detect, but if it does, should be lower severity
            for issue in issues:
                if issue.type == IssueType.HARDCODED_SECRET:
                    # Test files should have reduced severity or confidence
                    assert issue.severity in [Severity.LOW, Severity.MEDIUM] or issue.confidence < 0.8
    
    def test_confidence_scoring(self):
        """Test confidence scoring for different patterns"""
        # High confidence case - clear API key pattern
        high_confidence_code = 'api_key = "sk-1234567890abcdef1234567890abcdef"'
        issues = self.detector.detect(high_confidence_code, "config.py", {"language": "python"})
        if issues:
            assert issues[0].confidence >= 0.9
        
        # Lower confidence case - generic secret
        low_confidence_code = 'secret = "mysecret123"'
        issues = self.detector.detect(low_confidence_code, "config.py", {"language": "python"})
        if issues:
            assert issues[0].confidence <= 0.7
    
    def test_environment_context_severity_adjustment(self):
        """Test severity adjustment based on environment context"""
        code = 'password = "hardcoded_password"'
        
        # Production environment should have higher severity
        prod_context = {"environment": "production", "language": "python"}
        issues = self.detector.detect(code, "config.py", prod_context)
        if issues:
            prod_severity = issues[0].severity
        
        # Development environment should have lower severity
        dev_context = {"environment": "development", "language": "python"}  
        issues = self.detector.detect(code, "config.py", dev_context)
        if issues:
            dev_severity = issues[0].severity
            # Production should be more severe than development
            severity_order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
            assert severity_order.index(prod_severity) >= severity_order.index(dev_severity)
    
    def test_no_issues_in_clean_code(self):
        """Test that clean, secure code produces no issues"""
        clean_code = '''
        import os
        import requests
        
        def get_user_data(user_id):
            # Properly parameterized query
            query = "SELECT * FROM users WHERE id = %s"
            result = execute_query(query, (user_id,))
            
            # Secure HTTPS protocol
            api_key = os.getenv("API_KEY")
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get("https://api.example.com/user", headers=headers)
            
            return result, response.json()
        '''
        
        issues = self.detector.detect(clean_code, "secure_service.py", {"language": "python"})
        assert len(issues) == 0
    
    def test_detector_info(self):
        """Test detector provides proper information"""
        info = self.detector.get_detector_info()
        
        assert info["name"] == "SecurityDetector"
        assert info["version"] == "1.0"
        assert "Security vulnerability detection" in info["description"]
        assert len(info["supported_languages"]) > 0
        assert len(info["issue_types"]) > 0
        assert "hardcoded_secret" in info["issue_types"]
        assert "sql_injection_risk" in info["issue_types"]
        assert "insecure_protocol" in info["issue_types"]
    
    def test_pattern_access(self):
        """Test access to detection patterns"""
        patterns = self.detector.get_detection_patterns()
        
        assert len(patterns) > 0
        assert any("secret" in pattern.lower() for pattern in patterns)
        assert any("sql" in pattern.lower() for pattern in patterns)
        assert any("http" in pattern.lower() for pattern in patterns)