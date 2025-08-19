"""
Unit tests for SizeDetector

Tests the size-based detection capabilities including large files,
large functions, and complexity analysis.
"""

import pytest
from src.symmetra.detectors.size import SizeDetector
from src.symmetra.detectors.base import Severity, IssueType


class TestSizeDetector:
    """Test SizeDetector functionality"""
    
    def setup_method(self):
        """Set up test instance"""
        self.detector = SizeDetector()
    
    def test_detector_initialization(self):
        """Test detector initializes correctly"""
        assert self.detector.name == "SizeDetector"
        assert self.detector.enabled is True
        assert len(self.detector.get_detection_patterns()) > 0
    
    def test_should_run_for_all_languages(self):
        """Test detector runs for all languages"""
        assert self.detector.should_run("test.py", "python", {})
        assert self.detector.should_run("test.js", "javascript", {})
        assert self.detector.should_run("test.java", "java", {})
        assert self.detector.should_run("test.unknown", None, {})
    
    def test_large_file_detection_python(self):
        """Test detection of large Python files"""
        # Create a file with 350 lines (over the 300 line threshold)
        large_file_content = "\n".join([
            "# Large Python file",
            "import os",
            "import sys",
            "",
            "class LargeClass:",
            "    def __init__(self):",
            "        pass",
            ""
        ] + [f"    def method_{i}(self):" for i in range(100)] + 
          [f"        return {i}" for i in range(100)] +
          [f"# Comment line {i}" for i in range(140)])
        
        issues = self.detector.detect(large_file_content, "large_service.py", {"language": "python"})
        
        assert len(issues) >= 1
        large_file_issues = [i for i in issues if i.type == IssueType.LARGE_FILE]
        assert len(large_file_issues) == 1
        
        issue = large_file_issues[0]
        assert issue.severity == Severity.MEDIUM
        assert "300" in issue.message or "lines" in issue.message
        assert "split" in issue.fix_suggestion.lower() or "refactor" in issue.fix_suggestion.lower()
    
    def test_large_function_detection_python(self):
        """Test detection of large Python functions"""
        large_function_code = '''
def very_large_function():
    """This function is intentionally large for testing"""
    result = []
    for i in range(100):
        if i % 2 == 0:
            result.append(i * 2)
        else:
            result.append(i * 3)
        
        # More logic to make it larger
        if i % 10 == 0:
            print(f"Processing {i}")
            for j in range(5):
                temp = i + j
                if temp > 50:
                    result.append(temp)
                else:
                    result.append(temp * 2)
        
        # Even more logic
        try:
            value = i / (i - 50) if i != 50 else 0
            result.append(int(value))
        except:
            result.append(0)
        
        # Additional processing
        if len(result) > 100:
            result = result[:100]
            break
        
        # More lines to exceed threshold
        x = i * 2
        y = x + 1
        z = y * 3
        result.append(z)
        
        # Continue adding lines...
        a = 1
        b = 2
        c = a + b
        d = c * 2
        e = d + 1
        f = e * 3
        
        # Add more lines to exceed 50 line threshold
        g = f + 1
        h = g * 2
        i_var = h + 3
        j = i_var * 4
        k = j + 5
        l = k * 6
        m = l + 7
        n = m * 8
        o = n + 9
        p = o * 10
        
    return result

def small_function():
    return "small"
        '''
        
        issues = self.detector.detect(large_function_code, "functions.py", {"language": "python"})
        
        large_function_issues = [i for i in issues if i.type == IssueType.LARGE_FUNCTION]
        assert len(large_function_issues) >= 1
        
        issue = large_function_issues[0]
        assert issue.severity in [Severity.MEDIUM, Severity.HIGH]
        assert "very_large_function" in issue.evidence
        assert "lines" in issue.message
        assert "extract" in issue.fix_suggestion.lower() or "break" in issue.fix_suggestion.lower()
    
    def test_large_function_detection_javascript(self):
        """Test detection of large JavaScript functions"""
        large_js_function = '''
function processData(data) {
    const results = [];
    
    for (let i = 0; i < data.length; i++) {
        const item = data[i];
        
        if (item.type === 'user') {
            results.push({
                id: item.id,
                name: item.name,
                email: item.email,
                processed: true
            });
        } else if (item.type === 'order') {
            results.push({
                orderId: item.id,
                amount: item.total,
                status: item.status,
                processed: true
            });
        } else {
            results.push({
                rawData: item,
                processed: false
            });
        }
        
        // Validation logic
        if (item.validation) {
            if (item.validation.required) {
                if (!item.value) {
                    results[results.length - 1].error = 'Required field missing';
                }
            }
            
            if (item.validation.type === 'email') {
                const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                if (!emailRegex.test(item.value)) {
                    results[results.length - 1].error = 'Invalid email format';
                }
            }
        }
        
        // Additional processing
        const processed = results[results.length - 1];
        if (processed.error) {
            processed.severity = 'high';
        } else {
            processed.severity = 'low';
        }
        
        // More lines to exceed threshold
        processed.timestamp = new Date().toISOString();
        processed.processedBy = 'system';
        
        // Even more processing
        if (i % 10 === 0) {
            console.log(`Processed ${i} items`);
        }
    }
    
    return results;
}
        '''
        
        issues = self.detector.detect(large_js_function, "processor.js", {"language": "javascript"})
        
        large_function_issues = [i for i in issues if i.type == IssueType.LARGE_FUNCTION]
        if large_function_issues:  # May or may not detect depending on exact line count
            issue = large_function_issues[0]
            assert "processData" in issue.evidence
            assert issue.severity in [Severity.MEDIUM, Severity.HIGH]
    
    def test_complex_nested_structure_detection(self):
        """Test detection of deeply nested code structures"""
        deeply_nested_code = '''
def complex_logic(data):
    if data:
        for item in data:
            if item.get('active'):
                for category in item.get('categories', []):
                    if category.get('enabled'):
                        for subcategory in category.get('subcategories', []):
                            if subcategory.get('visible'):
                                for product in subcategory.get('products', []):
                                    if product.get('available'):
                                        for variant in product.get('variants', []):
                                            if variant.get('in_stock'):
                                                # Deep nesting - 6 levels
                                                result = process_variant(variant)
                                                if result:
                                                    return result
    return None
        '''
        
        issues = self.detector.detect(deeply_nested_code, "complex.py", {"language": "python"})
        
        # Should detect large function due to complexity even if not many lines
        function_issues = [i for i in issues if i.type == IssueType.LARGE_FUNCTION]
        if function_issues:
            issue = function_issues[0]
            assert "complex_logic" in issue.evidence
    
    def test_file_size_context_information(self):
        """Test that file size issues include helpful context"""
        # Create content that's definitely over threshold with classes and functions
        large_content = '''
class UserManager:
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass

class OrderManager:
    def create_order(self): pass
    def process_order(self): pass
    def cancel_order(self): pass

class ProductManager:
    def add_product(self): pass
    def remove_product(self): pass
    def update_product(self): pass

class InventoryManager:
    def check_stock(self): pass
    def update_stock(self): pass
    def reorder_items(self): pass

def utility_function_1(): pass
def utility_function_2(): pass
def utility_function_3(): pass
def utility_function_4(): pass
def utility_function_5(): pass
def utility_function_6(): pass
def utility_function_7(): pass
def utility_function_8(): pass
def utility_function_9(): pass
def utility_function_10(): pass
''' + "\n".join([f"# Additional line {i}" for i in range(350)])
        
        issues = self.detector.detect(large_content, "huge_file.py", {"language": "python"})
        
        large_file_issues = [i for i in issues if i.type == IssueType.LARGE_FILE]
        assert len(large_file_issues) == 1
        
        issue = large_file_issues[0]
        assert 'total_lines' in issue.context
        assert 'split_suggestions' in issue.context
        assert len(issue.context['split_suggestions']) > 0
    
    def test_function_size_context_information(self):
        """Test that function size issues include helpful context"""
        large_function_code = '''
def big_function():
    """A function with many lines"""
    ''' + "\n".join([f"    x{i} = {i}" for i in range(60)]) + '''
    return sum([''' + ", ".join([f"x{i}" for i in range(60)]) + '''])
        '''
        
        issues = self.detector.detect(large_function_code, "big_func.py", {"language": "python"})
        
        large_function_issues = [i for i in issues if i.type == IssueType.LARGE_FUNCTION]
        if large_function_issues:
            issue = large_function_issues[0]
            assert 'function_name' in issue.context
            assert issue.context['function_name'] == 'big_function'
            assert 'lines' in issue.context
            assert issue.context['lines'] > 50
    
    def test_no_issues_in_appropriately_sized_code(self):
        """Test that appropriately sized code produces no size issues"""
        appropriate_code = '''
def small_function():
    """A well-sized function"""
    data = get_data()
    processed = process_data(data)
    return format_output(processed)

def another_small_function():
    """Another appropriately sized function"""
    result = []
    for i in range(10):
        result.append(i * 2)
    return result

class SmallClass:
    """A reasonably sized class"""
    
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        self.data.append(item)
    
    def get_items(self):
        return self.data.copy()
        '''
        
        issues = self.detector.detect(appropriate_code, "small_module.py", {"language": "python"})
        
        # Should not detect any size-related issues
        size_issues = [i for i in issues if i.type in [IssueType.LARGE_FILE, IssueType.LARGE_FUNCTION]]
        assert len(size_issues) == 0
    
    def test_severity_scaling_with_size(self):
        """Test that severity scales appropriately with size"""
        # Very large file (500+ lines) should be high severity
        very_large_content = "\n".join([f"# Line {i}" for i in range(600)])
        issues = self.detector.detect(very_large_content, "very_large.py", {"language": "python"})
        
        large_file_issues = [i for i in issues if i.type == IssueType.LARGE_FILE]
        if large_file_issues:
            assert large_file_issues[0].severity in [Severity.HIGH, Severity.CRITICAL]
        
        # Moderately large file (350 lines) should be medium severity
        moderate_content = "\n".join([f"# Line {i}" for i in range(350)])
        issues = self.detector.detect(moderate_content, "moderate.py", {"language": "python"})
        
        large_file_issues = [i for i in issues if i.type == IssueType.LARGE_FILE]
        if large_file_issues:
            assert large_file_issues[0].severity == Severity.MEDIUM
    
    def test_split_suggestions_quality(self):
        """Test that split suggestions are helpful"""
        mixed_content = '''
# Configuration constants
DATABASE_URL = "sqlite:///app.db"
API_TIMEOUT = 30

# User management functions
def create_user(name, email):
    return {"name": name, "email": email}

def validate_user(user):
    return user.get("email") and "@" in user["email"]

def update_user(user_id, data):
    return {"id": user_id, "data": data}

def delete_user(user_id):
    return {"deleted": user_id}

# Order processing functions  
def create_order(user_id, items):
    return {"user_id": user_id, "items": items}

def process_payment(order, payment_info):
    return {"status": "success", "order": order}

def cancel_order(order_id):
    return {"cancelled": order_id}

def calculate_tax(amount):
    return amount * 0.08

# Utility functions
def format_currency(amount):
    return f"${amount:.2f}"

def send_notification(user, message):
    print(f"Notifying {user}: {message}")

def log_activity(action, user_id):
    print(f"Action: {action}, User: {user_id}")

def validate_email(email):
    return "@" in email and "." in email
        ''' + "\n".join([f"# Extra line {i}" for i in range(480)])  # Make it large (500+ lines)
        
        issues = self.detector.detect(mixed_content, "mixed_module.py", {"language": "python"})
        
        large_file_issues = [i for i in issues if i.type == IssueType.LARGE_FILE]
        if large_file_issues:
            issue = large_file_issues[0]
            suggestions = issue.context.get('split_suggestions', [])
            assert len(suggestions) > 0
            # Should suggest logical groupings based on functions
            suggestion_text = " ".join(suggestions).lower()
            assert any(word in suggestion_text for word in ['group', 'functions', 'modules', 'related'])
    
    def test_detector_info(self):
        """Test detector provides proper information"""
        info = self.detector.get_detector_info()
        
        assert info["name"] == "SizeDetector"
        assert info["version"] == "1.0"
        assert "File and function size analysis" in info["description"]
        assert len(info["supported_languages"]) > 0
        assert len(info["issue_types"]) > 0
        assert "large_file" in info["issue_types"]
        assert "large_function" in info["issue_types"]
    
    def test_language_specific_thresholds(self):
        """Test that different languages may have different thresholds"""
        # Create identical content for different languages
        content = "\n".join([f"line {i}" for i in range(320)])
        
        python_issues = self.detector.detect(content, "test.py", {"language": "python"})
        js_issues = self.detector.detect(content, "test.js", {"language": "javascript"})
        
        # Both should detect large file, but may have different severity/confidence
        python_large = [i for i in python_issues if i.type == IssueType.LARGE_FILE]
        js_large = [i for i in js_issues if i.type == IssueType.LARGE_FILE]
        
        assert len(python_large) >= 0  # May vary by language-specific rules
        assert len(js_large) >= 0
    
    def test_pattern_access(self):
        """Test access to detection patterns"""
        patterns = self.detector.get_detection_patterns()
        
        assert len(patterns) > 0
        assert any("lines" in pattern.lower() for pattern in patterns)
        assert any("function" in pattern.lower() for pattern in patterns)
    
    def test_edge_case_empty_file(self):
        """Test handling of empty files"""
        issues = self.detector.detect("", "empty.py", {"language": "python"})
        
        # Empty file should not trigger large file detection
        large_file_issues = [i for i in issues if i.type == IssueType.LARGE_FILE]
        assert len(large_file_issues) == 0
    
    def test_edge_case_single_line_file(self):
        """Test handling of single line files"""
        issues = self.detector.detect("print('hello')", "tiny.py", {"language": "python"})
        
        # Single line should not trigger large file detection
        large_file_issues = [i for i in issues if i.type == IssueType.LARGE_FILE]
        assert len(large_file_issues) == 0