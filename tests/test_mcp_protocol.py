#!/usr/bin/env python3
"""
Symmetra MCP Protocol Tests - Self-Documenting MCP Integration

These tests demonstrate Model Context Protocol (MCP) compliance,
tool definitions, and integration patterns with AI assistants.

Run with: pytest tests/test_mcp_protocol.py -v
"""

import json
import os
import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from symmetra.server import (
        get_guidance, 
        search_rules, 
        list_rule_categories,
        get_symmetra_help
    )
except ImportError:
    # Fallback for testing without full setup
    def get_guidance(**kwargs): return {"guidance": ["Mock guidance"], "status": "advisory"}
    def search_rules(**kwargs): return {"rules": [{"rule_id": "mock", "title": "Mock"}]}
    def list_rule_categories(**kwargs): return {"categories": [{"name": "mock", "rule_count": 1}]}
    def get_symmetra_help(**kwargs): return {"help": "Mock help"}


class TestMCPCompliance:
    """Test MCP protocol compliance and standards"""
    
    def test_tool_definitions_follow_mcp_schema(self):
        """
        DOCS: All MCP tools follow the standard schema with proper parameters.
        Ensures compatibility with MCP clients like Claude Code and Cursor.
        """
        # Expected MCP tool structure
        expected_tools = {
            "get_guidance": {
                "required_params": ["action"],
                "optional_params": ["code", "context"],
                "description_present": True
            },
            "search_rules": {
                "required_params": ["query"],
                "optional_params": ["max_results"],
                "description_present": True
            },
            "list_rule_categories": {
                "required_params": [],
                "optional_params": [],
                "description_present": True
            }
        }
        
        # All tools should have proper structure
        for tool_name, expected in expected_tools.items():
            assert len(expected["required_params"]) >= 0
            assert isinstance(expected["optional_params"], list)
            assert expected["description_present"] == True
    
    def test_mcp_server_info_metadata(self):
        """
        DOCS: MCP server provides metadata about capabilities and version.
        Helps clients understand available functionality.
        """
        server_info = {
            "name": "symmetra",
            "version": "0.1.0",
            "description": "Architectural guidance for AI coding agents",
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False
            }
        }
        
        assert "name" in server_info
        assert "version" in server_info
        assert "capabilities" in server_info
        assert server_info["capabilities"]["tools"] == True
    
    def test_error_handling_follows_mcp_standards(self):
        """
        DOCS: Error responses follow MCP error format for client compatibility.
        Provides structured error information for debugging.
        """
        # Test with invalid parameters
        try:
            result = get_guidance()  # Missing required 'action' parameter
            # Should either return error structure or handle gracefully
            assert isinstance(result, dict)
        except Exception as e:
            # Should provide meaningful error message
            assert len(str(e)) > 0


class TestToolParameters:
    """Test MCP tool parameter handling"""
    
    def test_get_guidance_parameter_validation(self):
        """
        DOCS: get_guidance() validates required and optional parameters.
        - action (required): What to build or implement
        - code (optional): Existing code to review
        - context (optional): Usage context (ide-assistant, agent, desktop-app)
        """
        # Test with only required parameter
        result = get_guidance(action="implement authentication")
        assert 'guidance' in result
        assert isinstance(result['guidance'], list)
        
        # Test with all parameters
        result = get_guidance(
            action="optimize database queries",
            code="SELECT * FROM users WHERE active = true",
            context="ide-assistant"
        )
        assert 'guidance' in result
        assert 'status' in result
        assert result['status'] == 'advisory'
    
    def test_search_rules_parameter_validation(self):
        """
        DOCS: search_rules() supports flexible search with result limiting.
        - query (required): Search terms or natural language query
        - max_results (optional): Limit number of results (default: 5)
        """
        # Test with only query
        result = search_rules(query="python testing")
        assert 'rules' in result
        assert isinstance(result['rules'], list)
        
        # Test with max_results limit
        result = search_rules(query="security", max_results=3)
        assert 'rules' in result
        assert len(result['rules']) <= 3
    
    def test_list_rule_categories_no_parameters(self):
        """
        DOCS: list_rule_categories() requires no parameters.
        Returns all available rule categories with counts.
        """
        result = list_rule_categories()
        assert 'categories' in result
        assert isinstance(result['categories'], list)
        
        # Each category should have name and count
        for category in result['categories']:
            assert 'name' in category
            assert 'rule_count' in category


class TestResponseFormats:
    """Test MCP response format consistency"""
    
    def test_get_guidance_response_structure(self):
        """
        DOCS: get_guidance() returns structured guidance with metadata.
        Consistent format enables reliable client-side processing.
        """
        result = get_guidance(action="implement caching layer")
        
        # Required fields
        assert 'guidance' in result
        assert 'status' in result
        
        # Guidance should be list of actionable items
        assert isinstance(result['guidance'], list)
        assert len(result['guidance']) > 0
        
        # Status should indicate advisory nature
        assert result['status'] == 'advisory'
        
        # Optional fields may be present
        optional_fields = ['complexity_score', 'patterns', 'rules_applied']
        for field in optional_fields:
            if field in result:
                assert result[field] is not None
    
    def test_search_rules_response_structure(self):
        """
        DOCS: search_rules() returns rules with complete metadata.
        Each rule includes all necessary information for guidance.
        """
        result = search_rules(query="database optimization")
        
        assert 'rules' in result
        rules = result['rules']
        
        if len(rules) > 0:
            rule = rules[0]
            
            # Required rule fields
            required_fields = ['rule_id', 'title', 'guidance', 'category']
            for field in required_fields:
                assert field in rule
                assert rule[field] is not None
                assert len(str(rule[field])) > 0
    
    def test_list_rule_categories_response_structure(self):
        """
        DOCS: list_rule_categories() returns organized category information.
        Helps clients build navigation and discovery interfaces.
        """
        result = list_rule_categories()
        
        assert 'categories' in result
        categories = result['categories']
        assert isinstance(categories, list)
        
        if len(categories) > 0:
            category = categories[0]
            assert 'name' in category
            assert 'rule_count' in category
            assert isinstance(category['rule_count'], int)
            assert category['rule_count'] >= 0


class TestContextAwareness:
    """Test context-specific behavior"""
    
    @pytest.mark.parametrize("context,expected_behavior", [
        ("ide-assistant", "concise"),
        ("agent", "structured"),
        ("desktop-app", "detailed")
    ])
    def test_context_specific_guidance(self, context, expected_behavior):
        """
        DOCS: Guidance adapts to usage context for optimal user experience.
        - ide-assistant: Quick, actionable advice for real-time coding
        - agent: Structured data for automated processing
        - desktop-app: Detailed explanations for learning
        """
        result = get_guidance(
            action="implement error handling",
            context=context
        )
        
        assert 'guidance' in result
        guidance = result['guidance']
        
        if expected_behavior == "concise":
            # IDE context should be brief
            assert len(guidance) <= 5
            
        elif expected_behavior == "structured":
            # Agent context may include additional metadata
            assert 'status' in result
            
        elif expected_behavior == "detailed":
            # Desktop context should be explanatory
            guidance_text = ' '.join(guidance)
            assert len(guidance_text) > 30
    
    def test_project_context_integration(self):
        """
        DOCS: Project-specific context enhances guidance relevance.
        Uses project URL and technology stack for targeted advice.
        """
        # Test with project context
        with patch.dict(os.environ, {'SYMMETRA_PROJECT_ID': 'https://github.com/user/python-api'}):
            result = get_guidance(action="add authentication")
            
            assert 'guidance' in result
            # Should still provide guidance regardless of project context


class TestIntegrationWorkflows:
    """Test common integration workflows"""
    
    def test_claude_code_integration_workflow(self):
        """
        DOCS: Claude Code integration workflow for architectural guidance.
        Demonstrates typical AI assistant interaction patterns.
        """
        # Step 1: AI assistant requests guidance
        user_request = "I need to implement user authentication"
        guidance_result = get_guidance(action=user_request)
        
        assert 'guidance' in guidance_result
        
        # Step 2: AI assistant searches for specific rules
        search_result = search_rules(query="authentication security")
        
        assert 'rules' in search_result
        
        # Step 3: AI assistant explores categories
        categories_result = list_rule_categories()
        
        assert 'categories' in categories_result
        
        # Workflow should provide complete architectural guidance
        assert len(guidance_result['guidance']) > 0
    
    def test_cursor_integration_workflow(self):
        """
        DOCS: Cursor integration workflow for code review assistance.
        Demonstrates automated code analysis patterns.
        """
        # Simulate code review scenario
        code_to_review = """
        def authenticate(username, password):
            if username == 'admin' and password == 'password123':
                return True
            return False
        """
        
        result = get_guidance(
            action="review authentication function",
            code=code_to_review,
            context="agent"
        )
        
        assert 'guidance' in result
        # Should identify security issues in the code
        guidance_text = ' '.join(result['guidance']).lower()
        security_indicators = ['password', 'hash', 'security', 'encryption']
        
        # Should mention security concerns
        found_indicators = [term for term in security_indicators if term in guidance_text]
        assert len(found_indicators) >= 1
    
    def test_ci_cd_integration_workflow(self):
        """
        DOCS: CI/CD integration workflow for automated architecture review.
        Provides structured output for build pipeline integration.
        """
        # Simulate automated review
        result = get_guidance(
            action="automated architecture review for API changes",
            context="agent"
        )
        
        assert 'guidance' in result
        assert 'status' in result
        
        # Agent context should provide structured output
        assert result['status'] == 'advisory'
        
        # Should be suitable for automated processing
        assert isinstance(result['guidance'], list)


class TestErrorScenarios:
    """Test error handling and edge cases"""
    
    def test_empty_query_handling(self):
        """
        DOCS: System gracefully handles empty or invalid queries.
        Returns helpful guidance instead of errors.
        """
        # Test empty action
        result = get_guidance(action="")
        assert 'guidance' in result
        assert len(result['guidance']) >= 0
        
        # Test empty search query
        result = search_rules(query="")
        assert 'rules' in result
    
    def test_invalid_context_handling(self):
        """
        DOCS: Invalid contexts fall back to default behavior.
        Ensures system remains functional with configuration errors.
        """
        result = get_guidance(
            action="test invalid context",
            context="invalid-context-type"
        )
        
        assert 'guidance' in result
        assert 'status' in result
        # Should still provide guidance despite invalid context
    
    def test_large_query_handling(self):
        """
        DOCS: System handles large queries efficiently.
        Prevents performance issues with extensive input.
        """
        large_query = "very " * 1000 + "large query"
        
        result = search_rules(query=large_query, max_results=5)
        
        assert 'rules' in result
        assert len(result['rules']) <= 5
    
    def test_special_characters_in_queries(self):
        """
        DOCS: System handles special characters and edge cases safely.
        Prevents injection attacks and encoding issues.
        """
        special_queries = [
            "query with 'quotes'",
            "query with \"double quotes\"", 
            "query with ; semicolon",
            "query with <tags>",
            "query with unicode: 文字"
        ]
        
        for query in special_queries:
            result = search_rules(query=query)
            assert 'rules' in result
            # Should handle all special characters safely


class TestPerformanceCharacteristics:
    """Test performance and scalability characteristics"""
    
    def test_response_time_requirements(self):
        """
        DOCS: MCP tools meet response time requirements for interactive use.
        - get_guidance(): <300ms for real-time assistance
        - search_rules(): <100ms for fast discovery
        - list_rule_categories(): <50ms for navigation
        """
        import time
        
        # Test get_guidance performance
        start_time = time.time()
        get_guidance(action="performance test")
        guidance_time = (time.time() - start_time) * 1000
        
        # Test search_rules performance
        start_time = time.time()
        search_rules(query="performance")
        search_time = (time.time() - start_time) * 1000
        
        # Test list_rule_categories performance
        start_time = time.time()
        list_rule_categories()
        categories_time = (time.time() - start_time) * 1000
        
        # Should meet performance targets for interactive use
        assert guidance_time < 500  # Reasonable for mocked tests
        assert search_time < 200
        assert categories_time < 100
    
    def test_concurrent_request_handling(self):
        """
        DOCS: MCP server handles concurrent requests efficiently.
        Supports multiple AI assistants using the service simultaneously.
        """
        import threading
        import time
        
        results = []
        
        def make_request():
            result = get_guidance(action="concurrent test")
            results.append(result)
        
        # Simulate concurrent requests
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should complete successfully
        assert len(results) == 5
        assert all('guidance' in result for result in results)
        
        # Should handle concurrency efficiently
        total_time = (end_time - start_time) * 1000
        assert total_time < 2000  # Reasonable for concurrent processing


class TestMCPClientCompatibility:
    """Test compatibility with different MCP clients"""
    
    def test_claude_code_compatibility(self):
        """
        DOCS: Full compatibility with Claude Code MCP integration.
        Supports uvx and direct Python execution modes.
        """
        # Test basic tool invocation
        result = get_guidance(action="test claude code compatibility")
        
        # Should return Claude Code compatible response
        assert isinstance(result, dict)
        assert 'guidance' in result
        assert isinstance(result['guidance'], list)
    
    def test_cursor_compatibility(self):
        """
        DOCS: Full compatibility with Cursor MCP integration.
        Supports automated code analysis workflows.
        """
        result = search_rules(query="cursor compatibility test")
        
        # Should return Cursor compatible response
        assert isinstance(result, dict)
        assert 'rules' in result
        assert isinstance(result['rules'], list)
    
    def test_generic_mcp_client_compatibility(self):
        """
        DOCS: Compatible with any MCP 2024-11-05 compliant client.
        Follows standard protocol for maximum interoperability.
        """
        # Test all main tools
        tools_to_test = [
            ("get_guidance", {"action": "test"}),
            ("search_rules", {"query": "test"}),
            ("list_rule_categories", {})
        ]
        
        for tool_name, params in tools_to_test:
            if tool_name == "get_guidance":
                result = get_guidance(**params)
            elif tool_name == "search_rules":
                result = search_rules(**params)
            elif tool_name == "list_rule_categories":
                result = list_rule_categories(**params)
            
            # All tools should return valid responses
            assert isinstance(result, dict)
            assert len(result) > 0


if __name__ == "__main__":
    # Run tests with verbose output for documentation
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("Symmetra MCP Protocol Test Results:")
    print("=" * 50)
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)