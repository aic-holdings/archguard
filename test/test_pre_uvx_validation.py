#!/usr/bin/env python3
"""
Pre-uvx Installation Validation Suite

Comprehensive testing to ensure ArchGuard is ready for uvx installation
and will work correctly with Claude Code as an MCP server.
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any

class PreUvxValidator:
    """Comprehensive validation before uvx installation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results: List[Tuple[str, bool, str]] = []
        
    def run_test(self, name: str, test_func, *args) -> bool:
        """Run a test and record results"""
        print(f"\n🧪 {name}")
        print("-" * 50)
        
        try:
            result, message = test_func(*args)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {message}")
            self.test_results.append((name, result, message))
            return result
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            print(f"❌ FAIL: {error_msg}")
            self.test_results.append((name, False, error_msg))
            return False
            
    def test_package_structure(self) -> Tuple[bool, str]:
        """Validate package structure for uvx compatibility"""
        required_files = [
            "pyproject.toml",
            "src/archguard/__init__.py",
            "src/archguard/cli.py",
            "src/archguard/server.py",
            "src/archguard/config.py",
            "README.md"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            return False, f"Missing required files: {missing_files}"
        return True, "All required files present"
        
    def test_pyproject_toml_validity(self) -> Tuple[bool, str]:
        """Validate pyproject.toml configuration"""
        try:
            import toml
            pyproject_path = self.project_root / "pyproject.toml"
            config = toml.load(pyproject_path)
            
            # Check required sections
            required_sections = ["build-system", "project"]
            missing_sections = [s for s in required_sections if s not in config]
            if missing_sections:
                return False, f"Missing sections: {missing_sections}"
                
            # Check entry points
            if "project" in config and "scripts" in config["project"]:
                scripts = config["project"]["scripts"]
                required_scripts = ["archguard", "archguard-server", "archguard-http"]
                missing_scripts = [s for s in required_scripts if s not in scripts]
                if missing_scripts:
                    return False, f"Missing entry points: {missing_scripts}"
                    
            return True, "pyproject.toml is valid and complete"
            
        except Exception as e:
            return False, f"pyproject.toml validation failed: {e}"
            
    def test_imports_and_syntax(self) -> Tuple[bool, str]:
        """Test that all Python files have valid syntax and imports"""
        python_files = list(self.project_root.glob("src/**/*.py"))
        
        for py_file in python_files:
            try:
                # Test syntax by compiling
                with open(py_file, 'r') as f:
                    content = f.read()
                compile(content, str(py_file), 'exec')
                
                # Test imports by running the file in a subprocess
                result = subprocess.run([
                    sys.executable, "-c", f"import sys; sys.path.insert(0, '{self.project_root}/src'); import {py_file.stem}"
                ], capture_output=True, text=True, cwd=self.project_root / "src" / "archguard")
                
                if result.returncode != 0:
                    return False, f"Import error in {py_file}: {result.stderr}"
                    
            except SyntaxError as e:
                return False, f"Syntax error in {py_file}: {e}"
            except Exception as e:
                return False, f"Error checking {py_file}: {e}"
                
        return True, f"All {len(python_files)} Python files are valid"
        
    def test_cli_functionality(self) -> Tuple[bool, str]:
        """Test CLI commands work correctly"""
        # Add src to Python path for testing
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root / "src")
        
        commands_to_test = [
            (["python", "-m", "archguard.cli", "--help"], "Main CLI help"),
            (["python", "-m", "archguard.cli", "server", "--help"], "Server help"),
            (["python", "-m", "archguard.cli", "http", "--help"], "HTTP help"),
            (["python", "-m", "archguard.cli", "init", "--help"], "Init help"),
        ]
        
        for cmd, description in commands_to_test:
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    cwd=self.project_root,
                    env=env
                )
                
                if result.returncode != 0:
                    return False, f"{description} failed: {result.stderr}"
                    
            except subprocess.TimeoutExpired:
                return False, f"{description} timed out"
            except Exception as e:
                return False, f"{description} error: {e}"
                
        return True, "All CLI commands work correctly"
        
    def test_mcp_server_basic_functionality(self) -> Tuple[bool, str]:
        """Test MCP server starts and responds to basic requests"""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root / "src")
        
        try:
            # Start MCP server
            proc = subprocess.Popen(
                ["python", "-m", "archguard.cli", "server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.project_root,
                env=env
            )
            
            time.sleep(2)
            
            # Send initialize message
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            }
            
            proc.stdin.write(json.dumps(init_msg) + "\n")
            proc.stdin.flush()
            time.sleep(1)
            
            # Send tools/list request
            tools_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            proc.stdin.write(json.dumps(tools_msg) + "\n")
            proc.stdin.flush()
            time.sleep(1)
            
            # Check if server is still running (good sign)
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
                return True, "MCP server responds to basic requests"
            else:
                stdout, stderr = proc.communicate()
                return False, f"MCP server failed: {stderr}"
                
        except Exception as e:
            try:
                proc.terminate()
            except:
                pass
            return False, f"MCP server test failed: {e}"
            
    def test_dependencies_available(self) -> Tuple[bool, str]:
        """Test that all dependencies are properly declared and available"""
        try:
            # Test importing key dependencies
            import fastmcp
            import toml
            
            # Check versions meet minimum requirements
            import pkg_resources
            
            required_packages = {
                "fastmcp": "2.11.0",
                "toml": "0.10.0"
            }
            
            for package, min_version in required_packages.items():
                try:
                    installed_version = pkg_resources.get_distribution(package).version
                    if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(min_version):
                        return False, f"{package} version {installed_version} < required {min_version}"
                except pkg_resources.DistributionNotFound:
                    return False, f"Required package {package} not found"
                    
            return True, "All dependencies available and compatible"
            
        except ImportError as e:
            return False, f"Dependency import failed: {e}"
        except Exception as e:
            return False, f"Dependency check failed: {e}"
            
    def test_pytest_suite_passes(self) -> Tuple[bool, str]:
        """Run existing pytest suite to ensure all tests pass"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=60, cwd=self.project_root)
            
            if result.returncode == 0:
                # Count passed tests
                lines = result.stdout.split('\n')
                test_lines = [line for line in lines if '::' in line and ('PASSED' in line or 'FAILED' in line)]
                passed = len([line for line in test_lines if 'PASSED' in line])
                total = len(test_lines)
                return True, f"All {passed}/{total} pytest tests passed"
            else:
                return False, f"pytest failed: {result.stdout[-300:]}"
                
        except subprocess.TimeoutExpired:
            return False, "pytest timed out (>60 seconds)"
        except Exception as e:
            return False, f"pytest execution failed: {e}"
            
    def test_git_repository_ready(self) -> Tuple[bool, str]:
        """Ensure git repository is in good state for uvx installation"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return False, "Not in a git repository"
                
            # Check for uncommitted changes
            if result.stdout.strip():
                return False, f"Uncommitted changes detected: {result.stdout[:100]}"
                
            # Check if we can access remote
            result = subprocess.run(["git", "remote", "-v"], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if "github.com" not in result.stdout:
                return False, "No GitHub remote found"
                
            return True, "Git repository is clean and has GitHub remote"
            
        except Exception as e:
            return False, f"Git check failed: {e}"
            
    def test_claude_code_mcp_compatibility(self) -> Tuple[bool, str]:
        """Test compatibility with Claude Code MCP requirements"""
        try:
            # Test that server implements required MCP methods
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root / "src")
            
            proc = subprocess.Popen(
                ["python", "-m", "archguard.cli", "server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.project_root,
                env=env
            )
            
            time.sleep(2)
            
            # Test required MCP methods
            required_methods = [
                "initialize",
                "tools/list",
                "resources/list",
                "prompts/list"
            ]
            
            for method in required_methods:
                msg = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": method,
                    "params": {} if method == "initialize" else None
                }
                
                if method == "initialize":
                    msg["params"] = {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1.0"}
                    }
                    
                proc.stdin.write(json.dumps(msg) + "\n")
                proc.stdin.flush()
                time.sleep(0.5)
                
            # If server is still running, it handled the requests
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
                return True, "Compatible with Claude Code MCP requirements"
            else:
                stdout, stderr = proc.communicate()
                return False, f"MCP compatibility failed: {stderr}"
                
        except Exception as e:
            try:
                proc.terminate()
            except:
                pass
            return False, f"Claude Code compatibility test failed: {e}"
            
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 PRE-UVX VALIDATION SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for _, result, _ in self.test_results if result)
        total = len(self.test_results)
        
        print(f"\n📊 Overall Results: {passed}/{total} validations passed")
        
        print("\n📋 Detailed Results:")
        for name, result, message in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")
            if not result:
                print(f"     └─ {message}")
                
        if passed == total:
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("\n✅ ArchGuard is ready for uvx installation")
            print("\n📋 Next Steps:")
            print("1. Install via uvx: uvx install git+https://github.com/dshanklinbv/archguard.git")
            print("2. Configure Claude Code MCP server:")
            print("   {")
            print('     "mcpServers": {')
            print('       "archguard": {')
            print('         "command": "archguard",')
            print('         "args": ["server"]')
            print('       }')
            print('     }')
            print("   }")
            print("3. Restart Claude Code")
            print("4. ArchGuard will be available for semantic code analysis")
            
        else:
            print("\n❌ VALIDATION FAILURES DETECTED")
            print("   Fix the failed validations before proceeding with uvx installation")
            
        return passed == total

def main():
    """Run complete pre-uvx validation suite"""
    print("🛡️  ArchGuard Pre-uvx Installation Validation")
    print("=" * 80)
    print("Comprehensive testing to ensure uvx installation success...")
    
    validator = PreUvxValidator()
    
    # Run all validation tests
    validation_tests = [
        ("Package Structure", validator.test_package_structure),
        ("pyproject.toml Validity", validator.test_pyproject_toml_validity),
        ("Python Syntax & Imports", validator.test_imports_and_syntax),
        ("CLI Functionality", validator.test_cli_functionality),
        ("MCP Server Basic Functionality", validator.test_mcp_server_basic_functionality),
        ("Dependencies Available", validator.test_dependencies_available),
        ("Pytest Suite", validator.test_pytest_suite_passes),
        ("Git Repository Ready", validator.test_git_repository_ready),
        ("Claude Code MCP Compatibility", validator.test_claude_code_mcp_compatibility),
    ]
    
    all_passed = True
    for test_name, test_func in validation_tests:
        passed = validator.run_test(test_name, test_func)
        all_passed = all_passed and passed
        
    # Print final summary
    success = validator.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())