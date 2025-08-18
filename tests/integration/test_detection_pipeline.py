"""
Integration tests for the complete detection pipeline

Tests the full workflow from code input through detection, analysis,
and report generation.
"""

import pytest
from src.archguard.detectors import create_detection_engine
from src.archguard.analyzers import LLMAnalyzer, ReportGenerator
from src.archguard.detectors.base import Severity, IssueType


class TestDetectionPipeline:
    """Test complete detection pipeline integration"""
    
    def setup_method(self):
        """Set up test components"""
        self.detection_engine = create_detection_engine()
        self.llm_analyzer = LLMAnalyzer()
        self.report_generator = ReportGenerator()
    
    def test_security_issue_detection_pipeline(self):
        """Test complete pipeline for security issues"""
        vulnerable_code = '''
import requests
import sqlite3

# Hardcoded credentials
API_KEY = "sk-1234567890abcdef1234567890abcdef"
DB_PASSWORD = "supersecret123"

def get_user_data(user_id):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = " + user_id
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Insecure HTTP request
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"http://api.example.com/users/{user_id}", headers=headers)
    
    return results, response.json()
        '''
        
        # Step 1: Detection
        result = self.detection_engine.analyze_code(vulnerable_code, "user_service.py")
        
        # Verify detection results
        assert len(result.issues) >= 3  # Should find multiple security issues
        assert result.status == "critical_issues"
        assert len(result.critical_issues) >= 1  # Hardcoded secrets are critical
        
        # Check specific issue types
        issue_types = [issue.type for issue in result.issues]
        assert IssueType.HARDCODED_SECRET in issue_types
        assert IssueType.SQL_INJECTION_RISK in issue_types
        assert IssueType.INSECURE_PROTOCOL in issue_types
        
        # Step 2: Analysis (without LLM for speed)
        analysis_data = None
        
        # Step 3: Report Generation
        report = self.report_generator.generate_report(
            result, 
            analysis_data, 
            report_type="summary"
        )
        
        # Verify report structure
        assert report["report_type"] == "summary"
        assert "file_info" in report
        assert "analysis_results" in report
        assert "key_findings" in report
        assert "recommendations" in report
    
    def test_maintainability_issue_detection_pipeline(self):
        """Test pipeline for maintainability issues"""
        large_file_code = '''
# Large file with maintainability issues

class DataProcessor:
    def __init__(self):
        self.data = []
        
    def process_large_dataset(self, dataset):
        """Very large function with multiple responsibilities"""
        results = []
        
        # Data validation (should be extracted)
        for item in dataset:
            if not item:
                continue
            if not isinstance(item, dict):
                continue
            if 'id' not in item:
                continue
            if 'data' not in item:
                continue
        
        # Data transformation (should be extracted)
        for item in dataset:
            transformed = {}
            transformed['id'] = item['id']
            transformed['processed_data'] = item['data'].upper()
            transformed['timestamp'] = time.time()
            transformed['status'] = 'processed'
            
            # Complex business logic (should be extracted)
            if item['data'].startswith('special_'):
                transformed['category'] = 'special'
                transformed['priority'] = 'high'
                
                # Nested processing
                for char in item['data']:
                    if char.isdigit():
                        transformed['has_numbers'] = True
                        break
                else:
                    transformed['has_numbers'] = False
            else:
                transformed['category'] = 'normal'
                transformed['priority'] = 'medium'
                transformed['has_numbers'] = any(c.isdigit() for c in item['data'])
            
            # Additional processing
            transformed['length'] = len(item['data'])
            transformed['words'] = len(item['data'].split())
            
            results.append(transformed)
        
        # Data aggregation (should be extracted)
        summary = {
            'total_items': len(results),
            'special_items': len([r for r in results if r['category'] == 'special']),
            'high_priority': len([r for r in results if r['priority'] == 'high']),
            'has_numbers': len([r for r in results if r['has_numbers']]),
            'average_length': sum(r['length'] for r in results) / len(results) if results else 0
        }
        
        return results, summary

# Add many more methods to make file large
        ''' + "\n".join([f"    def method_{i}(self):\n        return {i}" for i in range(150)])
        
        # Step 1: Detection
        result = self.detection_engine.analyze_code(large_file_code, "data_processor.py")
        
        # Verify detection results  
        assert len(result.issues) >= 1
        issue_types = [issue.type for issue in result.issues]
        assert IssueType.LARGE_FILE in issue_types or IssueType.LARGE_FUNCTION in issue_types
        
        # Step 2: Generate different report formats
        reports = {}
        for report_type in ["summary", "ide_assistant", "desktop_app"]:
            reports[report_type] = self.report_generator.generate_report(
                result, None, report_type
            )
        
        # Verify different report formats
        assert reports["summary"]["report_type"] == "summary"
        assert reports["ide_assistant"]["report_type"] == "ide_assistant"
        assert reports["desktop_app"]["report_type"] == "desktop_app"
        
        # IDE report should be concise
        assert "guidance" in reports["ide_assistant"]
        assert len(reports["ide_assistant"]["guidance"]) <= 10
        
        # Desktop report should be detailed
        assert "detailed_findings" in reports["desktop_app"]
        assert "learning_opportunities" in reports["desktop_app"]
    
    def test_mixed_issues_pipeline(self):
        """Test pipeline with multiple types of issues"""
        mixed_code = '''
import os
import requests

# Configuration - some issues here
API_KEY = "secret_api_key_12345"  # Hardcoded secret
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")  # Good practice

def fetch_user_profile(user_id, include_sensitive=False):
    """Fetch user profile with optional sensitive data"""
    
    # SQL injection risk
    base_query = "SELECT id, username, email FROM users WHERE id = " + str(user_id)
    
    if include_sensitive:
        # Adding sensitive fields
        base_query = base_query.replace("SELECT id, username, email", 
                                      "SELECT id, username, email, ssn, credit_card")
    
    # This function is getting large - missing error handling
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(base_query)
    user_data = cursor.fetchone()
    
    if user_data:
        # External API call with issues
        api_url = f"http://profile-service.internal.com/enrich/{user_id}"  # HTTP not HTTPS
        headers = {"X-API-Key": API_KEY}
        
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            enrichment_data = response.json()
        except:
            # Poor error handling - catching all exceptions
            enrichment_data = {}
        
        # Data processing
        profile = {
            "id": user_data[0],
            "username": user_data[1], 
            "email": user_data[2],
            "enrichment": enrichment_data
        }
        
        if include_sensitive and len(user_data) > 3:
            profile["ssn"] = user_data[3]
            profile["credit_card"] = user_data[4]
        
        return profile
    
    return None

# Duplicate code pattern - should be detected
def fetch_admin_profile(admin_id):
    """Fetch admin profile - similar to user profile"""
    base_query = "SELECT id, username, email FROM admins WHERE id = " + str(admin_id)
    
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(base_query)
    admin_data = cursor.fetchone()
    
    if admin_data:
        api_url = f"http://profile-service.internal.com/enrich/{admin_id}"
        headers = {"X-API-Key": API_KEY}
        
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            enrichment_data = response.json()
        except:
            enrichment_data = {}
        
        profile = {
            "id": admin_data[0],
            "username": admin_data[1],
            "email": admin_data[2], 
            "enrichment": enrichment_data,
            "role": "admin"
        }
        
        return profile
    
    return None
        '''
        
        # Step 1: Detection
        result = self.detection_engine.analyze_code(mixed_code, "profile_service.py")
        
        # Should detect multiple types of issues
        assert len(result.issues) >= 3
        
        issue_types = [issue.type for issue in result.issues]
        expected_types = [
            IssueType.HARDCODED_SECRET,
            IssueType.SQL_INJECTION_RISK,
            IssueType.INSECURE_PROTOCOL
        ]
        
        for expected_type in expected_types:
            assert expected_type in issue_types, f"Expected {expected_type} not found in {issue_types}"
        
        # Should have critical status due to security issues
        assert result.status in ["critical_issues", "high_issues"]
        
        # Step 2: Generate security audit report
        security_report = self.report_generator.generate_report(
            result, None, "security_audit"
        )
        
        # Verify security-focused report
        assert security_report["report_type"] == "security_audit"
        assert "security_summary" in security_report
        assert "vulnerability_details" in security_report
        assert "remediation_plan" in security_report
        
        # Should identify critical security issues
        assert security_report["security_summary"]["critical_security_issues"] >= 1
    
    def test_clean_code_pipeline(self):
        """Test pipeline with clean, well-written code"""
        clean_code = '''
import os
import logging
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)

class UserService:
    """Service for handling user-related operations"""
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.base_url = "https://api.example.com"
        
        if not self.api_key:
            raise ValueError("API_KEY environment variable is required")
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch user data by ID using parameterized query.
        
        Args:
            user_id: The ID of the user to fetch
            
        Returns:
            User data dictionary or None if not found
            
        Raises:
            ValueError: If user_id is invalid
            RequestException: If API request fails
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        
        try:
            # Secure parameterized query
            query = "SELECT id, username, email FROM users WHERE id = %s"
            user_data = self._execute_query(query, (user_id,))
            
            if not user_data:
                return None
            
            # Secure HTTPS API call
            user_profile = self._fetch_user_profile(user_id)
            
            return {
                "id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
                "profile": user_profile
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch user {user_id}: {e}")
            raise
    
    def _execute_query(self, query: str, params: tuple) -> Optional[tuple]:
        """Execute database query with proper error handling"""
        try:
            # Proper database handling would go here
            # This is a simplified example
            return None
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    def _fetch_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Fetch user profile from external API"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{self.base_url}/users/{user_id}/profile"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Timeout:
            logger.warning(f"Profile fetch timeout for user {user_id}")
            return {}
        except RequestException as e:
            logger.error(f"Profile fetch failed for user {user_id}: {e}")
            return {}
        '''
        
        # Step 1: Detection
        result = self.detection_engine.analyze_code(clean_code, "user_service.py")
        
        # Should detect no major issues
        critical_issues = [i for i in result.issues if i.severity == Severity.CRITICAL]
        high_issues = [i for i in result.issues if i.severity == Severity.HIGH]
        
        assert len(critical_issues) == 0
        assert len(high_issues) == 0
        assert result.status in ["clean", "issues_found"]  # May have minor style issues
        
        # Step 2: Generate summary report
        report = self.report_generator.generate_report(result, None, "summary")
        
        # Should indicate clean code
        assert report["analysis_results"]["total_issues"] <= 2  # Allow minor issues
        assert "✅" in str(report) or "clean" in str(report).lower()
    
    def test_performance_with_large_codebase(self):
        """Test pipeline performance with large code input"""
        # Generate a large but realistic code file
        large_code = '''
"""Large module for performance testing"""
import os
import sys
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "database_url": os.getenv("DATABASE_URL"),
    "api_timeout": int(os.getenv("API_TIMEOUT", "30")),
    "batch_size": int(os.getenv("BATCH_SIZE", "100"))
}

class DataProcessor:
    """Processes data in batches"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.processed_count = 0
        
''' + "\n".join([f'''
    def process_batch_{i}(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process batch {i} of data"""
        results = []
        for item in data:
            if self._validate_item_{i}(item):
                processed = self._transform_item_{i}(item)
                results.append(processed)
        return results
    
    def _validate_item_{i}(self, item: Dict[str, Any]) -> bool:
        """Validate item {i}"""
        required_fields = ["id", "data", "timestamp"]
        return all(field in item for field in required_fields)
    
    def _transform_item_{i}(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform item {i}"""
        return {{
            "id": item["id"],
            "processed_data": item["data"].upper(),
            "processed_at": datetime.now().isoformat(),
            "batch_number": {i}
        }}
''' for i in range(50)])  # 50 similar methods = ~200 lines each
        
        import time
        start_time = time.time()
        
        # Step 1: Detection
        result = self.detection_engine.analyze_code(large_code, "large_processor.py")
        
        detection_time = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds for this size)
        assert detection_time < 5.0
        assert result.analysis_time_ms < 5000
        
        # Should detect large file
        assert result.total_lines > 1000
        large_file_issues = [i for i in result.issues if i.type == IssueType.LARGE_FILE]
        assert len(large_file_issues) >= 1
        
        # Step 2: Report generation should also be fast
        start_time = time.time()
        report = self.report_generator.generate_report(result, None, "summary")
        report_time = time.time() - start_time
        
        assert report_time < 1.0  # Report generation should be very fast
        assert "large_processor.py" in report["file_info"]["path"]
    
    def test_error_handling_in_pipeline(self):
        """Test pipeline error handling with malformed input"""
        test_cases = [
            ("", "empty.py"),  # Empty file
            ("invalid python syntax {{{", "broken.py"),  # Syntax errors
            ("# Just a comment", "comment_only.py"),  # Comment-only file
            ("x" * 100000, "huge_line.py"),  # Extremely long line
        ]
        
        for code, filename in test_cases:
            try:
                # Should not crash on any input
                result = self.detection_engine.analyze_code(code, filename)
                
                # Should always produce valid result structure
                assert hasattr(result, 'status')
                assert hasattr(result, 'issues')
                assert hasattr(result, 'guidance')
                assert result.file_path == filename
                
                # Should be able to generate report
                report = self.report_generator.generate_report(result, None, "summary")
                assert report["report_type"] == "summary"
                
            except Exception as e:
                pytest.fail(f"Pipeline crashed on {filename}: {e}")
    
    def test_context_awareness(self):
        """Test that pipeline considers context information"""
        code_with_test_key = '''
def test_api_integration():
    """Test API integration with test credentials"""
    test_api_key = "test_sk_1234567890abcdef"  # Test key, not production
    client = ApiClient(test_api_key)
    assert client.ping() == "pong"
        '''
        
        # Test in production context
        prod_context = {
            "environment": "production",
            "project_type": "web_service",
            "language": "python"
        }
        
        prod_result = self.detection_engine.analyze_code(
            code_with_test_key, "test_integration.py", prod_context
        )
        
        # Test in development context
        dev_context = {
            "environment": "development", 
            "project_type": "test_suite",
            "language": "python"
        }
        
        dev_result = self.detection_engine.analyze_code(
            code_with_test_key, "test_integration.py", dev_context
        )
        
        # Production context should be more strict
        prod_critical = len([i for i in prod_result.issues if i.severity == Severity.CRITICAL])
        dev_critical = len([i for i in dev_result.issues if i.severity == Severity.CRITICAL])
        
        # Production should have same or more critical issues than dev
        assert prod_critical >= dev_critical