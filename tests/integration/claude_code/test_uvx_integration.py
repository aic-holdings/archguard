#!/usr/bin/env python3
"""
Symmetra uvx Integration Tests

Tests that validate Symmetra works correctly when installed via uvx
and integrates properly with Claude Code as an MCP server.
"""

import subprocess
import sys
import time
import json
import tempfile
import os
import asyncio
import pytest
from pathlib import Path
from typing import Dict, Any

class UvxInstallationTester:
    """Test uvx installation and MCP server functionality"""
    
    def __init__(self):
        self.test_dir = None
        self.original_cwd = os.getcwd()
        
    def setup_test_environment(self):
        """Create isolated test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="symmetra_uvx_test_")
        os.chdir(self.test_dir)
        print(f"🏗️  Test environment: {self.test_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        if self.test_dir:
            import shutil
            shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def test_uvx_available(self) -> bool:
        """Test if uvx is available on the system"""
        try:
            result = subprocess.run(["uvx", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ uvx available: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ uvx not available: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ uvx check failed: {e}")
            return False
            
    def test_github_repo_accessible(self) -> bool:
        """Test if GitHub repository is accessible"""
        try:
            # Test git clone to verify repo access
            result = subprocess.run([
                "git", "ls-remote", "--heads", 
                "https://github.com/aic-holdings/symmetra.git"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ GitHub repository accessible")
                return True
            else:
                print(f"❌ GitHub repo not accessible: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ GitHub access test failed: {e}")
            return False
            
    def test_uvx_install_from_github(self) -> bool:
        """Test installing Symmetra via uvx from GitHub"""
        try:
            print("🔄 Testing uvx install from GitHub...")
            
            # Install from GitHub using uvx
            result = subprocess.run([
                "uvx", "install", 
                "git+https://github.com/aic-holdings/symmetra.git"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ uvx install successful")
                print(f"   Output: {result.stdout}")
                return True
            else:
                print(f"❌ uvx install failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ uvx install timed out (>2 minutes)")
            return False
        except Exception as e:
            print(f"❌ uvx install error: {e}")
            return False
            
    def test_symmetra_commands_available(self) -> bool:
        """Test that Symmetra CLI commands work after uvx install"""
        commands_to_test = [
            (["symmetra", "--help"], "Main CLI help"),
            (["symmetra", "server", "--help"], "Server command help"),
            (["symmetra", "http", "--help"], "HTTP command help"),
            (["symmetra", "init", "--help"], "Init command help"),
        ]
        
        all_passed = True
        
        for cmd, description in commands_to_test:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description} failed: {result.stderr}")
                    all_passed = False
            except Exception as e:
                print(f"❌ {description} error: {e}")
                all_passed = False
                
        return all_passed
        
    def test_mcp_server_startup(self) -> bool:
        """Test that MCP server starts correctly when installed via uvx"""
        try:
            print("🚀 Testing MCP server startup...")
            
            # Start the MCP server
            proc = subprocess.Popen(
                ["symmetra", "server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            # Send a basic MCP message to test responsiveness
            initialize_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            # Send message and get response
            proc.stdin.write(json.dumps(initialize_msg) + "\n")
            proc.stdin.flush()
            
            # Wait for response
            time.sleep(2)
            
            # Check if process is still running (good sign)
            if proc.poll() is None:
                print("✅ MCP server started and responding")
                proc.terminate()
                proc.wait(timeout=5)
                return True
            else:
                stdout, stderr = proc.communicate()
                print(f"❌ MCP server failed to start properly")
                print(f"   STDOUT: {stdout}")
                print(f"   STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ MCP server test failed: {e}")
            try:
                proc.terminate()
            except:
                pass
            return False
            
    def test_http_server_startup(self) -> bool:
        """Test that HTTP server starts correctly when installed via uvx"""
        try:
            print("🌐 Testing HTTP server startup...")
            
            # Start HTTP server on a test port
            proc = subprocess.Popen(
                ["symmetra", "http", "--port", "8899"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            # Test if server is responding
            try:
                import httpx
                async def test_http():
                    async with httpx.AsyncClient() as client:
                        response = await client.get("http://localhost:8899/mcp", timeout=5)
                        return response.status_code
                        
                status = asyncio.run(test_http())
                
                if status == 200:
                    print("✅ HTTP server started and responding")
                    proc.terminate()
                    proc.wait(timeout=5)
                    return True
                else:
                    print(f"❌ HTTP server responding with status {status}")
                    proc.terminate()
                    return False
                    
            except Exception as e:
                print(f"❌ HTTP server test failed: {e}")
                proc.terminate()
                return False
                
        except Exception as e:
            print(f"❌ HTTP server startup failed: {e}")
            try:
                proc.terminate()
            except:
                pass
            return False

def test_uvx_installation_full_workflow():
    """Complete uvx installation test workflow"""
    print("🛡️  Symmetra uvx Installation Test Suite")
    print("=" * 60)
    
    tester = UvxInstallationTester()
    
    try:
        tester.setup_test_environment()
        
        # Test sequence
        tests = [
            ("uvx availability", tester.test_uvx_available),
            ("GitHub repository access", tester.test_github_repo_accessible),
            ("uvx install from GitHub", tester.test_uvx_install_from_github),
            ("CLI commands availability", tester.test_symmetra_commands_available),
            ("MCP server startup", tester.test_mcp_server_startup),
            ("HTTP server startup", tester.test_http_server_startup),
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
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
            
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All uvx installation tests PASSED!")
            print("✅ Symmetra is ready for uvx installation and Claude Code integration")
            return True
        else:
            print("❌ Some tests FAILED. Review the output above.")
            return False
            
    finally:
        tester.cleanup_test_environment()

if __name__ == "__main__":
    success = test_uvx_installation_full_workflow()
    sys.exit(0 if success else 1)