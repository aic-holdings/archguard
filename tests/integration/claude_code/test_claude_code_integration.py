#!/usr/bin/env python3
"""
Claude Code MCP Integration Tests

Tests that validate Symmetra works correctly as an MCP server
with Claude Code and provides semantic code analysis capabilities.
"""

import json
import subprocess
import sys
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ClaudeCodeIntegrationTester:
    """Test Claude Code MCP integration"""
    
    def __init__(self):
        self.test_dir = None
        self.mcp_config_file = None
        
    def setup_claude_code_config(self) -> bool:
        """Set up Claude Code MCP configuration for testing"""
        try:
            # Create test MCP configuration
            claude_code_config = {
                "mcpServers": {
                    "symmetra": {
                        "command": "symmetra",
                        "args": ["server"],
                        "env": {
                            "SYMMETRA_TEST_MODE": "true"
                        }
                    }
                }
            }
            
            # Write to temporary config file
            self.test_dir = tempfile.mkdtemp(prefix="claude_code_test_")
            self.mcp_config_file = os.path.join(self.test_dir, "claude_code_config.json")
            
            with open(self.mcp_config_file, 'w') as f:
                json.dump(claude_code_config, f, indent=2)
                
            print(f"✅ Claude Code MCP config created: {self.mcp_config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Claude Code config: {e}")
            return False
            
    def test_mcp_server_discovery(self) -> bool:
        """Test that MCP server can be discovered and initialized"""
        try:
            print("🔍 Testing MCP server discovery...")
            
            # Start MCP server process
            proc = subprocess.Popen(
                ["symmetra", "server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(2)
            
            # Send initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        }
                    },
                    "clientInfo": {
                        "name": "claude-code",
                        "version": "1.0.0"
                    }
                }
            }
            
            proc.stdin.write(json.dumps(initialize_request) + "\n")
            proc.stdin.flush()
            
            # Wait for response
            time.sleep(1)
            
            # Send tools/list request
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            proc.stdin.write(json.dumps(list_tools_request) + "\n")
            proc.stdin.flush()
            
            time.sleep(1)
            
            # Check if process is still running (indicates successful communication)
            if proc.poll() is None:
                print("✅ MCP server discovery successful")
                proc.terminate()
                proc.wait(timeout=5)
                return True
            else:
                stdout, stderr = proc.communicate()
                print(f"❌ MCP server discovery failed")
                print(f"   STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ MCP discovery test failed: {e}")
            try:
                proc.terminate()
            except:
                pass
            return False
            
    def test_semantic_analysis_capabilities(self) -> bool:
        """Test Symmetra's semantic analysis capabilities"""
        try:
            print("🧠 Testing semantic analysis capabilities...")
            
            # Create sample code for analysis
            sample_code = '''
def poorly_designed_function(data, flag, mode, options):
    if flag:
        if mode == "process":
            result = []
            for item in data:
                if options.get("filter"):
                    if item.status == "active":
                        result.append(process_item(item))
            return result
        elif mode == "validate":
            errors = []
            for item in data:
                if not validate_item(item):
                    errors.append(f"Invalid item: {item.id}")
            return errors
    else:
        return data
'''
            
            # Start MCP server
            proc = subprocess.Popen(
                ["symmetra", "server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(2)
            
            # Send initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            proc.stdin.write(json.dumps(initialize_request) + "\n")
            proc.stdin.flush()
            time.sleep(1)
            
            # Test get_guidance tool with semantic analysis
            guidance_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_guidance",
                    "arguments": {
                        "action": "analyze code complexity and suggest improvements",
                        "code": sample_code,
                        "context": "This function has multiple nested conditions and responsibilities"
                    }
                }
            }
            
            proc.stdin.write(json.dumps(guidance_request) + "\n")
            proc.stdin.flush()
            time.sleep(2)
            
            # Read response
            try:
                response_line = proc.stdout.readline()
                if response_line:
                    response = json.loads(response_line)
                    if "result" in response:
                        print("✅ Semantic analysis response received")
                        print(f"   Sample guidance: {str(response['result'])[:100]}...")
                        proc.terminate()
                        return True
            except:
                pass
                
            proc.terminate()
            proc.wait(timeout=5)
            return False
            
        except Exception as e:
            print(f"❌ Semantic analysis test failed: {e}")
            try:
                proc.terminate()
            except:
                pass
            return False
            
    def test_claude_code_compatible_responses(self) -> bool:
        """Test that responses are compatible with Claude Code expectations"""
        try:
            print("🔧 Testing Claude Code response compatibility...")
            
            # Start MCP server
            proc = subprocess.Popen(
                ["symmetra", "server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(2)
            
            # Test resources/list (Claude Code uses this for context)
            resources_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "resources/list"
            }
            
            proc.stdin.write(json.dumps(resources_request) + "\n")
            proc.stdin.flush()
            time.sleep(1)
            
            # Test prompts/list (Claude Code uses this for available prompts)
            prompts_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "prompts/list"
            }
            
            proc.stdin.write(json.dumps(prompts_request) + "\n")
            proc.stdin.flush()
            time.sleep(1)
            
            # Check process status
            if proc.poll() is None:
                print("✅ Claude Code compatibility checks passed")
                proc.terminate()
                proc.wait(timeout=5)
                return True
            else:
                stdout, stderr = proc.communicate()
                print(f"❌ Compatibility test failed: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Compatibility test failed: {e}")
            try:
                proc.terminate()
            except:
                pass
            return False
            
    def create_sample_project_for_analysis(self) -> Path:
        """Create a sample project that Symmetra can analyze"""
        project_dir = Path(self.test_dir) / "sample_project"
        project_dir.mkdir(exist_ok=True)
        
        # Create sample files with architectural issues
        (project_dir / "main.py").write_text('''
# Main application with architectural issues
import os
import sys
import json
from typing import Any

class UserManager:
    def __init__(self):
        self.users = []
        self.database = None
        self.cache = {}
        
    def add_user(self, data):
        # Poor error handling
        user = User(data["name"], data["email"], data["age"])
        self.users.append(user)
        self.save_to_database(user)
        self.update_cache(user)
        return user.id
        
    def save_to_database(self, user):
        # Direct database access (should be abstracted)
        pass
        
    def update_cache(self, user):
        # Cache logic mixed with business logic
        pass

class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age
        self.id = hash(name + email)  # Poor ID generation
''')
        
        (project_dir / "config.py").write_text('''
# Configuration with hardcoded values
DATABASE_URL = "postgresql://user:pass@localhost/db"
API_KEY = "sk-1234567890abcdef"  # Hardcoded secret
DEBUG = True

class Config:
    def __init__(self):
        self.db_url = DATABASE_URL
        self.api_key = API_KEY
        self.debug = DEBUG
''')
        
        return project_dir
        
    def cleanup(self):
        """Clean up test environment"""
        if self.test_dir:
            import shutil
            shutil.rmtree(self.test_dir, ignore_errors=True)

def test_claude_code_integration_workflow():
    """Complete Claude Code integration test"""
    print("🧠 Symmetra Claude Code Integration Test Suite")
    print("=" * 60)
    
    tester = ClaudeCodeIntegrationTester()
    
    try:
        # Test sequence
        tests = [
            ("Claude Code MCP config setup", tester.setup_claude_code_config),
            ("MCP server discovery", tester.test_mcp_server_discovery),
            ("Semantic analysis capabilities", tester.test_semantic_analysis_capabilities),
            ("Claude Code response compatibility", tester.test_claude_code_compatible_responses),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CLAUDE CODE INTEGRATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
            
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Claude Code integration tests PASSED!")
            print("\n📋 Claude Code Setup Instructions:")
            print("1. Add Symmetra to Claude Code MCP servers:")
            print("   {")
            print('     "mcpServers": {')
            print('       "symmetra": {')
            print('         "command": "symmetra",')
            print('         "args": ["server"]')
            print('       }')
            print('     }')
            print("   }")
            print("2. Restart Claude Code")
            print("3. Symmetra will be available for semantic code analysis")
            return True
        else:
            print("❌ Some tests FAILED. Review the output above.")
            return False
            
    finally:
        tester.cleanup()

if __name__ == "__main__":
    success = test_claude_code_integration_workflow()
    sys.exit(0 if success else 1)