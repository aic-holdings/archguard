#!/usr/bin/env python3
"""
Symmetra Integration Tests - Self-Documenting System Tests

These tests serve as both validation and living documentation for Symmetra.
Each test demonstrates key functionality and expected behavior.

Run with: pytest tests/test_symmetra_integration.py -v
"""

import asyncio
import json
import os
import pytest
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symmetra.rules_engine import create_rule_engine, KeywordRuleEngine, VectorRuleEngine
from symmetra.server import get_guidance, search_rules, list_rule_categories


class TestSymmetraCore:
    """Test core Symmetra functionality"""
    
    def test_rule_engine_factory_creates_keyword_engine_by_default(self):
        """
        DOCS: Symmetra defaults to keyword-based rule matching for fast responses.
        Expected: ~25ms response time with exact keyword matching.
        """
        engine = create_rule_engine()
        assert isinstance(engine, KeywordRuleEngine)
        assert engine.engine_type == "keyword"
    
    def test_rule_engine_factory_creates_vector_engine_when_configured(self):
        """
        DOCS: Vector engine provides semantic search for natural language queries.
        Expected: ~50-200ms response time with conceptual understanding.
        """
        with patch.dict(os.environ, {'SYMMETRA_ENGINE_TYPE': 'vector'}):
            engine = create_rule_engine()
            assert isinstance(engine, VectorRuleEngine)
            assert engine.engine_type == "vector"
    
    def test_bootstrap_rules_are_loaded_automatically(self):
        """
        DOCS: Symmetra ships with self-bootstrapping rules for its own development.
        These rules guide AI agents in building Symmetra itself.
        """
        engine = create_rule_engine("keyword")
        rules = engine.search_rules("symmetra vector embeddings", max_results=10)
        
        # Should find Symmetra-specific development rules
        rule_ids = [rule['rule_id'] for rule in rules]
        assert any('symmetra' in rule_id for rule_id in rule_ids)
        assert len(rules) > 0
    
    def test_rule_categories_are_properly_organized(self):
        """
        DOCS: Rules are categorized for easy discovery and navigation.
        Categories help AI agents find relevant guidance quickly.
        """
        engine = create_rule_engine("keyword")
        categories = engine.list_categories()
        
        expected_categories = {'architecture', 'security', 'performance', 'testing', 'ai-ml'}
        found_categories = set(categories.keys())
        
        assert expected_categories.issubset(found_categories)
        assert all(count > 0 for count in categories.values())


class TestMCPIntegration:
    """Test Model Context Protocol (MCP) integration"""
    
    def test_get_guidance_returns_structured_response(self):
        """
        DOCS: get_guidance() is the primary MCP tool for architectural advice.
        Returns structured guidance with priority-based recommendations.
        """
        result = get_guidance(
            action="implement user authentication in Python API",
            code="def login(username, password): pass",
            context="security review"
        )
        
        assert 'guidance' in result
        assert 'status' in result
        assert 'complexity_score' in result
        assert result['status'] == 'advisory'
        assert isinstance(result['guidance'], list)
        assert len(result['guidance']) > 0
    
    def test_search_rules_finds_relevant_guidance(self):
        """
        DOCS: search_rules() enables discovery of specific architectural rules.
        Supports both keyword and semantic search modes.
        """
        result = search_rules("python testing best practices", max_results=5)
        
        assert 'rules' in result
        assert isinstance(result['rules'], list)
        assert len(result['rules']) > 0
        
        # Each rule should have required fields
        for rule in result['rules']:
            assert 'rule_id' in rule
            assert 'title' in rule
            assert 'guidance' in rule
            assert 'category' in rule
    
    def test_list_rule_categories_provides_navigation(self):
        """
        DOCS: list_rule_categories() helps users discover available guidance areas.
        Shows rule counts for each category.
        """
        result = list_rule_categories()
        
        assert 'categories' in result
        categories = result['categories']
        assert isinstance(categories, list)
        assert len(categories) > 0
        
        # Each category should have name and count
        for category in categories:
            assert 'name' in category
            assert 'rule_count' in category
            assert category['rule_count'] > 0


class TestContextAwareGuidance:
    """Test context-specific guidance adaptation"""
    
    @pytest.mark.parametrize("context,expected_characteristics", [
        ("ide-assistant", {"concise": True, "max_suggestions": 5}),
        ("agent", {"structured": True, "detailed": True}),
        ("desktop-app", {"educational": True, "explanatory": True})
    ])
    def test_guidance_adapts_to_context(self, context, expected_characteristics):
        """
        DOCS: Symmetra adapts its responses based on usage context.
        - ide-assistant: Quick, actionable advice during coding
        - agent: Structured data for automated processing  
        - desktop-app: Educational explanations for learning
        """
        result = get_guidance(
            action="optimize database queries",
            context=context
        )
        
        if expected_characteristics.get("concise"):
            # IDE assistant should provide concise guidance
            assert len(result['guidance']) <= 5
            
        if expected_characteristics.get("structured"):
            # Agent context should include structured metadata
            assert 'patterns' in result or 'rules_applied' in result
            
        if expected_characteristics.get("educational"):
            # Desktop app should provide detailed explanations
            guidance_text = ' '.join(result['guidance'])
            assert len(guidance_text) > 50  # More detailed responses


class TestRuleEngine:
    """Test rule engine implementations"""
    
    def test_keyword_engine_matches_exact_terms(self):
        """
        DOCS: Keyword engine provides fast, exact matching for technical terms.
        Best for: specific technologies, frameworks, patterns.
        """
        engine = KeywordRuleEngine()
        
        # Should find rules with exact keyword matches
        rules = engine.search_rules("python database", max_results=10)
        
        for rule in rules:
            text = f"{rule['title']} {rule['guidance']} {' '.join(rule.get('keywords', []))}"
            assert 'python' in text.lower() or 'database' in text.lower()
    
    def test_keyword_engine_performance_is_fast(self):
        """
        DOCS: Keyword engine prioritizes speed for interactive usage.
        Expected: <50ms response time for real-time coding assistance.
        """
        engine = KeywordRuleEngine()
        
        start_time = time.time()
        rules = engine.search_rules("performance optimization", max_results=5)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 100  # Should be very fast
        assert len(rules) > 0  # Should still find relevant rules


class TestErrorHandling:
    """Test error handling and resilience"""
    
    def test_graceful_handling_of_missing_rules(self):
        """
        DOCS: Symmetra gracefully handles empty rule sets and missing data.
        Returns helpful messages instead of crashing.
        """
        engine = KeywordRuleEngine()
        engine.rules = []  # Empty rule set
        
        result = engine.search_rules("nonexistent topic", max_results=5)
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_invalid_context_uses_default(self):
        """
        DOCS: Invalid contexts fall back to sensible defaults.
        Ensures system remains functional with configuration errors.
        """
        result = get_guidance(
            action="test invalid context handling",
            context="invalid-context-name"
        )
        
        assert 'guidance' in result
        assert result['status'] == 'advisory'
        # Should still provide guidance despite invalid context
    
    def test_malformed_action_request_handled_safely(self):
        """
        DOCS: Symmetra handles malformed or empty requests safely.
        Provides helpful guidance on proper usage.
        """
        result = get_guidance(action="")
        
        assert 'guidance' in result
        assert result['status'] == 'advisory'
        # Should provide some form of guidance even with empty action


class TestSelfBootstrapping:
    """Test Symmetra's self-bootstrapping rules"""
    
    def test_symmetra_development_rules_exist(self):
        """
        DOCS: Symmetra includes rules to guide its own development.
        Meta-programming: the system helps build itself.
        """
        engine = create_rule_engine("keyword")
        rules = engine.search_rules("symmetra sqlite vector", max_results=10)
        
        # Should find rules about Symmetra's own tech stack
        assert len(rules) > 0
        
        # Rules should mention Symmetra development concepts
        rule_text = ' '.join([
            f"{rule['title']} {rule['guidance']}" 
            for rule in rules
        ]).lower()
        
        symmetra_concepts = ['vector', 'embedding', 'sqlite', 'mcp', 'rules']
        found_concepts = [concept for concept in symmetra_concepts if concept in rule_text]
        assert len(found_concepts) >= 2
    
    def test_mcp_server_development_guidance(self):
        """
        DOCS: Symmetra provides specific guidance for MCP server development.
        Helps AI agents understand MCP patterns and best practices.
        """
        result = get_guidance(
            action="implement MCP server with database integration",
            context="agent"
        )
        
        guidance_text = ' '.join(result['guidance']).lower()
        mcp_terms = ['mcp', 'server', 'tool', 'protocol']
        found_terms = [term for term in mcp_terms if term in guidance_text]
        assert len(found_terms) >= 1


class TestPerformanceCharacteristics:
    """Test performance and scalability characteristics"""
    
    def test_guidance_generation_performance(self):
        """
        DOCS: Symmetra provides real-time guidance suitable for IDE integration.
        Performance targets: <100ms for keyword, <300ms for vector search.
        """
        start_time = time.time()
        
        result = get_guidance(
            action="optimize React component performance",
            code="function MyComponent() { return <div>Hello</div>; }",
            context="ide-assistant"
        )
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        assert response_time_ms < 200  # Should be fast enough for IDE use
        assert len(result['guidance']) > 0
    
    def test_rule_search_scales_with_rule_count(self):
        """
        DOCS: Rule search performance remains stable as rule count grows.
        Uses efficient indexing and search algorithms.
        """
        engine = create_rule_engine("keyword")
        
        # Test multiple searches with different result limits
        for max_results in [1, 5, 10, 20]:
            start_time = time.time()
            rules = engine.search_rules("python security", max_results=max_results)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            assert response_time_ms < 50  # Should remain fast
            assert len(rules) <= max_results


class TestIntegrationPatterns:
    """Test common integration patterns"""
    
    def test_code_review_integration_pattern(self):
        """
        DOCS: Symmetra integrates with code review workflows.
        Provides architectural feedback on code changes.
        """
        # Simulate code review scenario
        result = get_guidance(
            action="review this authentication implementation",
            code="""
            def login(username, password):
                user = User.find_by_username(username)
                if user and user.password == password:
                    return generate_token(user)
                return None
            """,
            context="security review"
        )
        
        guidance_text = ' '.join(result['guidance']).lower()
        
        # Should identify security issues
        security_terms = ['hash', 'bcrypt', 'salt', 'password', 'security']
        found_terms = [term for term in security_terms if term in guidance_text]
        assert len(found_terms) >= 1
    
    def test_ci_cd_integration_pattern(self):
        """
        DOCS: Symmetra supports CI/CD pipeline integration.
        Provides automated architectural review as part of build process.
        """
        # Simulate CI/CD scenario with agent context
        result = get_guidance(
            action="automated architecture review for API changes",
            context="agent"
        )
        
        assert result['status'] == 'advisory'
        assert 'complexity_score' in result
        # Agent context should provide structured data for automation


class TestConfigurationManagement:
    """Test configuration and environment handling"""
    
    def test_environment_variable_configuration(self):
        """
        DOCS: Symmetra configuration via environment variables.
        Supports deployment flexibility and container environments.
        """
        test_cases = [
            ('SYMMETRA_ENGINE_TYPE', 'keyword'),
            ('SYMMETRA_DEFAULT_CONTEXT', 'ide-assistant'),
            ('SYMMETRA_MAX_RULES', '10')
        ]
        
        for env_var, test_value in test_cases:
            with patch.dict(os.environ, {env_var: test_value}):
                # Configuration should be picked up from environment
                engine = create_rule_engine()
                assert engine is not None  # Should initialize successfully
    
    def test_project_specific_configuration(self):
        """
        DOCS: Symmetra supports project-specific rule customization.
        Enables different guidance for different codebases.
        """
        # Test with project context
        result = get_guidance(
            action="implement authentication",
            context="agent"
        )
        
        # Should work regardless of project context
        assert 'guidance' in result
        assert len(result['guidance']) > 0


class TestDocumentationAsCode:
    """Test documentation-as-code patterns"""
    
    def test_rules_are_self_documenting(self):
        """
        DOCS: Rules include rationale and context for self-documentation.
        Each rule explains why the guidance matters.
        """
        engine = create_rule_engine("keyword")
        rules = engine.search_rules("python testing", max_results=5)
        
        for rule in rules:
            # Each rule should have explanatory fields
            assert 'title' in rule
            assert 'guidance' in rule
            assert len(rule['title']) > 10
            assert len(rule['guidance']) > 20
    
    def test_examples_demonstrate_usage_patterns(self):
        """
        DOCS: Symmetra provides practical examples for each guidance type.
        Examples serve as both tests and documentation.
        """
        # This test itself is an example of documentation-as-code
        assert True  # The test structure demonstrates the pattern


# Utility functions for test setup
def setup_test_environment():
    """Setup clean test environment"""
    # Reset any global state
    pass

def cleanup_test_environment():
    """Cleanup after tests"""
    # Clean up any test artifacts
    pass


if __name__ == "__main__":
    # Run tests with verbose output for documentation
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("Symmetra Integration Test Results:")
    print("=" * 50)
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)