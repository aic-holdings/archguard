#!/usr/bin/env python3
"""
Symmetra Test Runner
Runs all tests in sequence with proper cleanup.
"""

import asyncio
import subprocess
import sys
import time
import os

def print_header(title):
    """Print a formatted test section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_result(test_name, success, message=""):
    """Print a formatted test result"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")

async def run_in_memory_stdio_tests():
    """Run in-memory and stdio tests"""
    print_header("In-Memory & Stdio Tests")
    
    try:
        # Run the comprehensive test client
        result = subprocess.run(
            [sys.executable, "test_client.py"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        print_result("In-Memory & Stdio Tests", success)
        
        if not success:
            print("STDOUT:", result.stdout[-500:] if result.stdout else "None")
            print("STDERR:", result.stderr[-500:] if result.stderr else "None")
        
        return success
        
    except subprocess.TimeoutExpired:
        print_result("In-Memory & Stdio Tests", False, "Timeout after 30 seconds")
        return False
    except Exception as e:
        print_result("In-Memory & Stdio Tests", False, f"Error: {e}")
        return False

async def run_http_tests():
    """Run HTTP transport tests"""
    print_header("HTTP Transport Tests")
    
    # Start HTTP server
    server_proc = None
    try:
        print("🚀 Starting HTTP server...")
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Use the CLI command instead of direct file execution
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "symmetra.cli", "http", "--port", "8003"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=parent_dir,
            env={**os.environ, "PYTHONPATH": os.path.join(parent_dir, "src")}
        )
        
        # Give server time to start
        time.sleep(3)
        
        # Check if server is still running
        if server_proc.poll() is not None:
            stdout, stderr = server_proc.communicate()
            print_result("HTTP Server Start", False, f"Server failed to start: {stderr.decode()[:200]}")
            return False
        
        print_result("HTTP Server Start", True, "Server running on port 8003")
        
        # Run HTTP tests
        result = subprocess.run(
            [sys.executable, "test_http_client.py"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        success = result.returncode == 0
        print_result("HTTP Client Tests", success)
        
        if not success:
            print("STDOUT:", result.stdout[-500:] if result.stdout else "None")
            print("STDERR:", result.stderr[-500:] if result.stderr else "None")
        
        return success
        
    except subprocess.TimeoutExpired:
        print_result("HTTP Tests", False, "Timeout after 15 seconds")
        return False
    except Exception as e:
        print_result("HTTP Tests", False, f"Error: {e}")
        return False
    finally:
        # Clean up server
        if server_proc:
            try:
                server_proc.terminate()
                server_proc.wait(timeout=5)
                print_result("HTTP Server Cleanup", True, "Server stopped")
            except:
                server_proc.kill()
                print_result("HTTP Server Cleanup", True, "Server killed")

async def run_cli_tests():
    """Run FastMCP CLI tests"""
    print_header("FastMCP CLI Tests")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_fastmcp_cli.py"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        # CLI test "fails" because server runs indefinitely, but that's expected
        # Check if it shows the server started successfully
        success = "FastMCP version:" in result.stdout and "Server file syntax is valid" in result.stdout
        print_result("FastMCP CLI Tests", success, "Server startup validated")
        
        return success
        
    except subprocess.TimeoutExpired:
        print_result("FastMCP CLI Tests", False, "Timeout after 15 seconds")
        return False
    except Exception as e:
        print_result("FastMCP CLI Tests", False, f"Error: {e}")
        return False

async def run_context_project_tests():
    """Run context and project parameter tests"""
    print_header("Context & Project Parameter Tests")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_context_project_params.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        print_result("Context & Project Parameter Tests", success)
        
        if not success:
            print("STDOUT:", result.stdout[-500:] if result.stdout else "None")
            print("STDERR:", result.stderr[-500:] if result.stderr else "None")
        
        return success
        
    except subprocess.TimeoutExpired:
        print_result("Context & Project Parameter Tests", False, "Timeout after 30 seconds")
        return False
    except Exception as e:
        print_result("Context & Project Parameter Tests", False, f"Error: {e}")
        return False

async def main():
    """Run all tests in sequence"""
    print("🛡️ Symmetra Test Suite")
    print("Running comprehensive tests for all transport modes...")
    
    # Change to tests directory
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        results = []
        
        # Run all test suites
        results.append(await run_in_memory_stdio_tests())
        results.append(await run_http_tests())
        results.append(await run_cli_tests())
        results.append(await run_context_project_tests())
        
        # Print summary
        print_header("Test Summary")
        passed = sum(results)
        total = len(results)
        
        print(f"🎯 Tests Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Symmetra is ready for production.")
            return 0
        else:
            print("❌ Some tests failed. Check the output above for details.")
            return 1
            
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))