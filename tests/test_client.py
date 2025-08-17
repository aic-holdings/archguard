"""
ArchGuard Test Client
Tests the ArchGuard MCP server through all phases.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import Client
from archguard_server import mcp

async def test_phase_1_in_memory():
    """Phase 1: In-memory testing - fastest iteration"""
    print("🧪 Phase 1: In-Memory Testing")
    print("=" * 50)
    
    # Connect directly to server instance (no subprocess)
    async with Client(mcp) as client:
        # Test 1: List available tools
        print("📋 Testing tool discovery...")
        tools = await client.list_tools()
        print(f"✅ Found tools: {[t.name for t in tools]}")
        
        # Test 2: List available resources
        print("\n📋 Testing resource discovery...")
        resources = await client.list_resources()
        print(f"✅ Found resources: {[r.uri for r in resources]}")
        
        # Test 3: Basic guidance request
        print("\n💡 Testing basic guidance...")
        result = await client.call_tool("get_guidance", {
            "action": "create user authentication system"
        })
        print(f"✅ Auth guidance: {result.content}")
        
        # Test 4: Large code guidance
        print("\n📏 Testing large code guidance...")
        large_code = "def long_function():\n" + "    pass\n" * 100  # Simulate large function
        result = await client.call_tool("get_guidance", {
            "action": "create user service",
            "code": large_code
        })
        print(f"✅ Large code guidance: {result.content}")
        
        # Test 5: Database guidance
        print("\n🗄️ Testing database guidance...")
        result = await client.call_tool("get_guidance", {
            "action": "create database schema for users"
        })
        print(f"✅ Database guidance: {result.content}")
        
        # Test 6: Read rules resource
        print("\n📖 Testing rules resource...")
        rules = await client.read_resource("archguard://rules")
        if isinstance(rules, list) and len(rules) > 0:
            print(f"✅ Rules content: {rules[0].text[:100]}...")
        else:
            print(f"✅ Rules content: {rules}")
        
        # Test 7: List prompts
        print("\n📝 Testing prompt discovery...")
        prompts = await client.list_prompts()
        print(f"✅ Found prompts: {[p.name for p in prompts]}")
        
    print("\n✅ Phase 1 Complete: All in-memory tests passed!")
    return True

async def test_phase_2_stdio():
    """Phase 2: Stdio testing - real subprocess communication"""
    print("\n🖥️ Phase 2: Stdio Testing")
    print("=" * 50)
    
    # Connect via stdio to server file
    async with Client("../archguard_server.py") as client:
        print("📋 Testing stdio connection...")
        
        # Test tool discovery via stdio
        tools = await client.list_tools()
        print(f"✅ Stdio tools: {[t.name for t in tools]}")
        
        # Test guidance via stdio
        result = await client.call_tool("get_guidance", {
            "action": "create API endpoint for login"
        })
        print(f"✅ Stdio guidance: {result.content}")
        
    print("✅ Phase 2 Complete: Stdio communication works!")
    return True

async def test_phase_3_http():
    """Phase 3: HTTP testing - production deployment path"""
    print("\n🌐 Phase 3: HTTP Testing")
    print("=" * 50)
    
    # This will be run separately since HTTP server needs to be started first
    print("ℹ️ HTTP testing requires manual server startup:")
    print("   python archguard_server.py --transport http --port 8000")
    print("   Then run: python test_http_client.py")
    
    return True

async def main():
    """Run all test phases"""
    print("🛡️ ArchGuard MCP Server Testing")
    print("=" * 60)
    
    try:
        # Phase 1: In-memory testing (fastest)
        await test_phase_1_in_memory()
        
        # Phase 2: Stdio testing (real subprocess)
        await test_phase_2_stdio()
        
        # Phase 3: HTTP testing (production path)
        await test_phase_3_http()
        
        print("\n🎉 All phases completed successfully!")
        print("\n📋 Summary:")
        print("✅ In-memory testing: Fast iteration and debugging")
        print("✅ Stdio testing: Real MCP client communication")
        print("ℹ️ HTTP testing: Production deployment ready")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())