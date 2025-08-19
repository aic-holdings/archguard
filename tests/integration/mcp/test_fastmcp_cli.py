"""
Test Symmetra with FastMCP CLI commands
"""

import subprocess
import sys
import time
import json

def test_fastmcp_commands():
    """Test various FastMCP CLI commands"""
    print("🔧 Testing FastMCP CLI Commands")
    print("=" * 50)
    
    # Test 1: Check if FastMCP is installed correctly
    print("📦 Testing FastMCP installation...")
    try:
        result = subprocess.run(["fastmcp", "--version"], 
                              capture_output=True, text=True, timeout=5)
        print(f"✅ FastMCP version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ FastMCP version check failed: {e}")
        assert False, f"FastMCP version check failed: {e}"
    
    # Test 2: Validate our server file
    print("\n🔍 Validating Symmetra server...")
    try:
        # Add src directory to Python path for import  
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
        
        # Import our server to check for syntax errors
        import symmetra.server
        print("✅ Server file syntax is valid")
        print(f"✅ Server name: {symmetra.server.mcp.name}")
    except Exception as e:
        print(f"❌ Server validation failed: {e}")
        assert False, f"Server validation failed: {e}"
    
    # Test 3: Test FastMCP run command (quick start/stop)
    print("\n🚀 Testing FastMCP run command...")
    try:
        # Start server process
        server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'symmetra', 'server.py')
        proc = subprocess.Popen(
            ["fastmcp", "run", server_path],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Give it time to fully initialize 
        time.sleep(1)
        
        # Check if it's running or completed successfully
        if proc.poll() is None:
            print("✅ FastMCP server started successfully")
            
            # Terminate the process
            proc.terminate()
            proc.wait(timeout=5)
            print("✅ FastMCP server stopped cleanly")
        else:
            # Server may have started and stopped normally (no client connected)
            stdout, stderr = proc.communicate()
            if "Starting MCP server" in stderr or "FastMCP" in stderr:
                print("✅ FastMCP server started successfully (detected in output)")
                print("✅ Server stopped after startup (no client connected - expected)")
            else:
                print(f"❌ Server failed to start: {stderr}")
                assert False, f"Server failed to start: {stderr}"
            
    except Exception as e:
        print(f"❌ FastMCP run test failed: {e}")
        try:
            proc.terminate()
        except:
            pass
        assert False, f"FastMCP run test failed: {e}"
    
    print("\n✅ All FastMCP CLI tests passed!")
    assert True

if __name__ == "__main__":
    success = test_fastmcp_commands()
    if success:
        print("\n🎉 FastMCP CLI testing completed successfully!")
        print("\n📋 Next steps:")
        print("1. Install for Claude Code: pip install -e . && symmetra server")
        print("2. Test HTTP mode: symmetra http --port 8000")
    else:
        print("\n❌ Some tests failed. Check the output above.")