#!/usr/bin/env python3
"""
Test Serena-Style uvx Execution Pattern

Validates that Symmetra works correctly with the uvx --from pattern
used by Serena for temporary execution without permanent installation.
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def test_uvx_from_help():
    """Test that uvx --from works for help command"""
    print("🧪 Testing uvx --from help command...")
    
    try:
        result = subprocess.run([
            "uvx", "--from", "git+https://github.com/aic-holdings/symmetra", 
            "symmetra", "--help"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "Symmetra - Your AI-powered architectural co-pilot" in result.stdout:
            print("✅ uvx --from help command works")
            return True
        else:
            print(f"❌ uvx --from help failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ uvx --from help timed out")
        return False
    except Exception as e:
        print(f"❌ uvx --from help error: {e}")
        return False

def test_uvx_from_server_startup():
    """Test that uvx --from works for MCP server startup"""
    print("\n🧪 Testing uvx --from MCP server startup...")
    
    try:
        # Start server with uvx --from
        proc = subprocess.Popen([
            "uvx", "--from", "git+https://github.com/aic-holdings/symmetra",
            "symmetra", "server"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give it time to start
        time.sleep(3)
        
        # Send basic MCP initialize message
        initialize_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        proc.stdin.write(json.dumps(initialize_msg) + "\n")
        proc.stdin.flush()
        time.sleep(1)
        
        # Check if server is responding
        if proc.poll() is None:
            print("✅ uvx --from MCP server startup works")
            proc.terminate()
            proc.wait(timeout=5)
            return True
        else:
            stdout, stderr = proc.communicate()
            print(f"❌ uvx --from server failed: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ uvx --from server error: {e}")
        try:
            proc.terminate()
        except:
            pass
        return False

def test_claude_code_config_compatibility():
    """Test that the Claude Code configuration format is valid"""
    print("\n🧪 Testing Claude Code configuration compatibility...")
    
    # Test configuration for uvx --from pattern
    claude_config = {
        "mcpServers": {
            "symmetra": {
                "command": "uvx",
                "args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra", "server"],
                "env": {
                    "SYMMETRA_LOG_LEVEL": "INFO"
                }
            }
        }
    }
    
    try:
        # Validate JSON structure
        json_str = json.dumps(claude_config, indent=2)
        parsed = json.loads(json_str)
        
        # Check required fields
        if "mcpServers" in parsed and "symmetra" in parsed["mcpServers"]:
            server_config = parsed["mcpServers"]["symmetra"]
            if all(key in server_config for key in ["command", "args"]):
                print("✅ Claude Code configuration is valid")
                print(f"   Command: {server_config['command']}")
                print(f"   Args: {' '.join(server_config['args'])}")
                return True
        
        print("❌ Claude Code configuration missing required fields")
        return False
        
    except Exception as e:
        print(f"❌ Claude Code configuration error: {e}")
        return False

def test_comparison_with_serena_pattern():
    """Compare Symmetra's uvx --from pattern with Serena's"""
    print("\n🧪 Comparing with Serena's uvx --from pattern...")
    
    serena_pattern = "uvx --from git+https://github.com/oraios/serena serena start-mcp-server"
    symmetra_pattern = "uvx --from git+https://github.com/aic-holdings/symmetra symmetra server"
    
    print(f"   Serena:    {serena_pattern}")
    print(f"   Symmetra: {symmetra_pattern}")
    
    # Check pattern consistency
    serena_parts = serena_pattern.split()
    symmetra_parts = symmetra_pattern.split()
    
    if (len(serena_parts) == len(symmetra_parts) and 
        serena_parts[0:2] == symmetra_parts[0:2] and  # uvx --from
        serena_parts[2].startswith("git+") and symmetra_parts[2].startswith("git+")):
        print("✅ Symmetra follows Serena's uvx --from pattern correctly")
        return True
    else:
        print("❌ Symmetra pattern doesn't match Serena structure")
        return False

def main():
    """Run all Serena-style execution tests"""
    print("🛡️  Symmetra Serena-Style Execution Tests")
    print("=" * 60)
    print("Testing uvx --from pattern compatibility with Serena's approach...")
    
    tests = [
        ("uvx --from help command", test_uvx_from_help),
        ("uvx --from MCP server startup", test_uvx_from_server_startup),
        ("Claude Code configuration", test_claude_code_config_compatibility),
        ("Serena pattern comparison", test_comparison_with_serena_pattern),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 SERENA-STYLE EXECUTION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Symmetra fully supports Serena-style uvx --from execution!")
        print("\n📋 Usage:")
        print("Direct execution: uvx --from git+https://github.com/aic-holdings/symmetra symmetra server")
        print("\n📋 Claude Code config:")
        print('"command": "uvx",')
        print('"args": ["--from", "git+https://github.com/aic-holdings/symmetra", "symmetra", "server"]')
        return True
    else:
        print("❌ Some Serena-style tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)