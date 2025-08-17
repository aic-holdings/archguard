"""
Test ArchGuard with FastMCP CLI commands
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
        return False
    
    # Test 2: Validate our server file
    print("\n🔍 Validating ArchGuard server...")
    try:
        # Add parent directory to Python path for import
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Import our server to check for syntax errors
        import archguard_server
        print("✅ Server file syntax is valid")
        print(f"✅ Server name: {archguard_server.mcp.name}")
    except Exception as e:
        print(f"❌ Server validation failed: {e}")
        return False
    
    # Test 3: Test FastMCP run command (quick start/stop)
    print("\n🚀 Testing FastMCP run command...")
    try:
        # Start server process
        proc = subprocess.Popen(
            ["fastmcp", "run", "../archguard_server.py"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if it's running
        if proc.poll() is None:
            print("✅ FastMCP server started successfully")
            
            # Terminate the process
            proc.terminate()
            proc.wait(timeout=5)
            print("✅ FastMCP server stopped cleanly")
        else:
            stdout, stderr = proc.communicate()
            print(f"❌ Server failed to start: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ FastMCP run test failed: {e}")
        try:
            proc.terminate()
        except:
            pass
        return False
    
    print("\n✅ All FastMCP CLI tests passed!")
    return True

if __name__ == "__main__":
    success = test_fastmcp_commands()
    if success:
        print("\n🎉 FastMCP CLI testing completed successfully!")
        print("\n📋 Next steps:")
        print("1. Install for Claude Code: fastmcp install archguard_server.py")
        print("2. Test HTTP mode: python archguard_server.py (then modify for HTTP)")
    else:
        print("\n❌ Some tests failed. Check the output above.")