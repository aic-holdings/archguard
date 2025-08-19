"""
Test Symmetra CLI --context and --project parameters
"""

import subprocess
import sys
import os
import tempfile
import json
import time

def test_context_parameter():
    """Test --context parameter functionality"""
    print("🎯 Testing --context parameter")
    print("=" * 50)
    
    # Add src directory to Python path for import  
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
    
    # Test 1: Test CLI help shows context parameter
    print("📚 Testing CLI help for --context parameter...")
    try:
        # Use PYTHONPATH to run from source
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
        
        result = subprocess.run([
            sys.executable, "-c", 
            "from symmetra.cli import main; main()", 
            "server", "--help"
        ], capture_output=True, text=True, timeout=10, env=env)
        
        if "--context" in result.stdout:
            print("✅ --context parameter found in help")
        else:
            print(f"❌ --context parameter not found in help: {result.stdout}")
            assert False, "--context parameter not found in help"
            
        # Check if choices are shown
        if "ide-assistant" in result.stdout and "desktop-app" in result.stdout:
            print("✅ Context choices shown in help")
        else:
            print(f"❌ Context choices not shown properly: {result.stdout}")
            assert False, "Context choices not shown properly"
            
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        assert False, f"CLI help test failed: {e}"
    
    # Test 2: Test context parameter is passed to server
    print("\n🚀 Testing context parameter passing...")
    for context in ["desktop-app", "ide-assistant", "agent"]:
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
            
            proc = subprocess.Popen([
                sys.executable, "-c", 
                f"from symmetra.cli import main; main()", 
                "server", "--context", context
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            
            # Give it time to start and show context
            time.sleep(2)
            
            # Terminate gracefully
            proc.terminate()
            stdout, stderr = proc.communicate(timeout=5)
            
            # Check if context is shown in output (could be in stdout or stderr)
            output = stdout + stderr
            if f"Context: {context}" in output:
                print(f"✅ Context '{context}' correctly passed and displayed")
            else:
                print(f"❌ Context '{context}' not displayed correctly")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                assert False, f"Context '{context}' not displayed correctly"
                
        except Exception as e:
            print(f"❌ Context test for '{context}' failed: {e}")
            try:
                proc.terminate()
            except:
                pass
            assert False, f"Context test for '{context}' failed: {e}"
    
    print("\n✅ All context parameter tests passed!")


def test_project_parameter():
    """Test --project parameter functionality"""
    print("\n📁 Testing --project parameter")
    print("=" * 50)
    
    # Add src directory to Python path for import  
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
    
    # Test 1: Test CLI help shows project parameter
    print("📚 Testing CLI help for --project parameter...")
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
        
        result = subprocess.run([
            sys.executable, "-c", 
            "from symmetra.cli import main; main()", 
            "server", "--help"
        ], capture_output=True, text=True, timeout=10, env=env)
        
        if "--project" in result.stdout:
            print("✅ --project parameter found in help")
        else:
            print(f"❌ --project parameter not found in help: {result.stdout}")
            assert False, "--project parameter not found in help"
            
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        assert False, f"CLI help test failed: {e}"
    
    # Test 2: Test project parameter with different project paths
    print("\n🚀 Testing project parameter passing...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_projects = [
            temp_dir,
            "/tmp/test-project",
            "my-project"
        ]
        
        for project in test_projects:
            try:
                env = os.environ.copy()
                env['PYTHONPATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
                
                proc = subprocess.Popen([
                    sys.executable, "-c", 
                    f"from symmetra.cli import main; main()", 
                    "server", "--project", project
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
                
                # Give it time to start and show project
                time.sleep(2)
                
                # Terminate gracefully
                proc.terminate()
                stdout, stderr = proc.communicate(timeout=5)
                
                # Check if project is shown in output (could be in stdout or stderr)
                output = stdout + stderr
                if f"Project: {project}" in output:
                    print(f"✅ Project '{project}' correctly passed and displayed")
                else:
                    print(f"❌ Project '{project}' not displayed correctly")
                    print(f"stdout: {stdout}")
                    print(f"stderr: {stderr}")
                    assert False, f"Project '{project}' not displayed correctly"
                    
            except Exception as e:
                print(f"❌ Project test for '{project}' failed: {e}")
                try:
                    proc.terminate()
                except:
                    pass
                assert False, f"Project test for '{project}' failed: {e}"
    
    print("\n✅ All project parameter tests passed!")


def test_combined_parameters():
    """Test using both --context and --project parameters together"""
    print("\n🔧 Testing combined --context and --project parameters")
    print("=" * 50)
    
    # Add src directory to Python path for import  
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
            
            proc = subprocess.Popen([
                sys.executable, "-c", 
                f"from symmetra.cli import main; main()", 
                "server", "--context", "ide-assistant", "--project", temp_dir
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            
            # Give it time to start
            time.sleep(2)
            
            # Terminate gracefully
            proc.terminate()
            stdout, stderr = proc.communicate(timeout=5)
            
            # Check if both parameters are shown in output (could be in stdout or stderr)
            output = stdout + stderr
            context_shown = "Context: ide-assistant" in output
            project_shown = f"Project: {temp_dir}" in output
            
            if context_shown and project_shown:
                print("✅ Both context and project parameters correctly passed and displayed")
            else:
                print(f"❌ Combined parameters not displayed correctly")
                print(f"Context shown: {context_shown}")
                print(f"Project shown: {project_shown}")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                assert False, "Combined parameters not displayed correctly"
                
        except Exception as e:
            print(f"❌ Combined parameters test failed: {e}")
            try:
                proc.terminate()
            except:
                pass
            assert False, f"Combined parameters test failed: {e}"
    
    print("\n✅ Combined parameters test passed!")


def test_server_context_in_guidance():
    """Test that server context affects guidance output"""
    print("\n🎯 Testing server context affects guidance")
    print("=" * 50)
    
    # Add src directory to Python path for import  
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
    
    try:
        # Import and create server with different contexts
        import symmetra.server
        
        # Test with different contexts
        for context in ["desktop-app", "ide-assistant", "agent"]:
            # Get guidance using test helper function
            result = symmetra.server.test_guidance_with_context("create a new component", server_context=context)
            
            # Check if context-specific guidance is included
            guidance_text = " ".join(result["guidance"])
            
            if context == "ide-assistant":
                if "IDE Integration" in guidance_text:
                    print(f"✅ IDE-specific guidance found for context '{context}'")
                else:
                    print(f"❌ IDE-specific guidance not found for context '{context}'")
                    assert False, f"IDE-specific guidance not found for context '{context}'"
            elif context == "agent":
                if "Agent Mode" in guidance_text:
                    print(f"✅ Agent-specific guidance found for context '{context}'")
                else:
                    print(f"❌ Agent-specific guidance not found for context '{context}'")
                    assert False, f"Agent-specific guidance not found for context '{context}'"
            else:  # desktop-app
                # Desktop app shouldn't have specific guidance
                if "IDE Integration" not in guidance_text and "Agent Mode" not in guidance_text:
                    print(f"✅ No specific guidance for context '{context}' (expected)")
                else:
                    print(f"❌ Unexpected specific guidance for context '{context}'")
                    assert False, f"Unexpected specific guidance for context '{context}'"
    
    except Exception as e:
        print(f"❌ Server context guidance test failed: {e}")
        assert False, f"Server context guidance test failed: {e}"
    
    print("\n✅ Server context guidance test passed!")


def run_all_tests():
    """Run all context and project parameter tests"""
    print("🧪 Running all context and project parameter tests")
    print("=" * 70)
    
    try:
        test_context_parameter()
        test_project_parameter()
        test_combined_parameters()
        test_server_context_in_guidance()
        
        print("\n🎉 All context and project parameter tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n🎯 Context and project parameter implementation is working correctly!")
        print("\n📋 Ready for:")
        print("1. Integration with Claude Code MCP")
        print("2. Production usage with context-aware guidance")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)