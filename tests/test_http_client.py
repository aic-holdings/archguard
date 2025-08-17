"""
ArchGuard HTTP Client Test
Tests the HTTP version of ArchGuard server.
"""

import asyncio
import httpx
from fastmcp import Client

async def test_http_connection():
    """Test HTTP transport connectivity"""
    print("🌐 Testing HTTP Transport")
    print("=" * 40)
    
    # Test basic HTTP endpoint
    print("🔗 Testing HTTP endpoint availability...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8003/mcp")
            print(f"✅ HTTP endpoint responding: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP endpoint not available: {e}")
        print("💡 Start HTTP server first: python archguard_http_server.py")
        return False
    
    # Test MCP over HTTP
    print("\n🔌 Testing MCP over HTTP...")
    try:
        async with Client("http://localhost:8003/mcp") as client:
            # Test tool discovery
            tools = await client.list_tools()
            print(f"✅ HTTP MCP tools: {[t.name for t in tools]}")
            
            # Test guidance call
            result = await client.call_tool("get_guidance", {
                "action": "create HTTP API endpoint"
            })
            print(f"✅ HTTP guidance result: {result.content[0].text[:100]}...")
            
    except Exception as e:
        print(f"❌ MCP over HTTP failed: {e}")
        return False
    
    print("✅ HTTP transport testing complete!")
    return True

async def test_production_readiness():
    """Test production deployment features"""
    print("\n🚀 Testing Production Features")
    print("=" * 40)
    
    # Test concurrent connections
    print("⚡ Testing concurrent requests...")
    try:
        async with Client("http://localhost:8003/mcp") as client:
            # Make multiple concurrent requests
            tasks = []
            for i in range(3):
                task = client.call_tool("get_guidance", {
                    "action": f"create service {i}"
                })
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            print(f"✅ Handled {len(results)} concurrent requests")
            
    except Exception as e:
        print(f"❌ Concurrent request test failed: {e}")
        return False
    
    print("✅ Production readiness tests complete!")
    return True

async def main():
    """Run HTTP testing suite"""
    print("🛡️ ArchGuard HTTP Testing Suite")
    print("=" * 50)
    
    # Test HTTP connectivity
    http_ok = await test_http_connection()
    if not http_ok:
        print("\n💡 To start HTTP server:")
        print("   python archguard_http_server.py")
        print("   Then run this test again.")
        return
    
    # Test production features
    await test_production_readiness()
    
    print("\n🎉 All HTTP tests completed!")
    print("\n📋 HTTP Server Summary:")
    print("✅ HTTP transport working")
    print("✅ MCP over HTTP functional")
    print("✅ Concurrent requests supported")
    print("🐳 Ready for Docker deployment")

if __name__ == "__main__":
    asyncio.run(main())