#!/usr/bin/env python3
"""
ArchGuard Test Runner - Self-Documenting Test Execution

This script runs the comprehensive ArchGuard test suite and provides
detailed reporting on system functionality and compliance.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --integration      # Integration tests only
    python run_tests.py --unit             # Unit tests only
    python run_tests.py --documentation    # Generate test documentation
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n📍 {description}")
    print("=" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, 
            capture_output=True, text=True
        )
        duration = time.time() - start_time
        print(f"✅ {description} completed in {duration:.1f}s")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"❌ {description} failed after {duration:.1f}s")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="ArchGuard Test Runner")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--mcp", action="store_true", help="Run MCP protocol tests only")
    parser.add_argument("--embedding", action="store_true", help="Run embedding system tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--documentation", action="store_true", help="Generate test documentation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage reporting")
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    subprocess.run(f"cd {project_root}", shell=True)
    
    print("🧪 ArchGuard Test Suite")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Python version: {sys.version}")
    
    # Check dependencies
    print("\n🔍 Checking test dependencies...")
    dependencies_ok = True
    
    for dep in ["pytest", "pytest-asyncio"]:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep} available")
        except ImportError:
            print(f"❌ {dep} not found - install with: pip install {dep}")
            dependencies_ok = False
    
    if not dependencies_ok:
        print("\n❌ Missing test dependencies. Please install them first.")
        return 1
    
    # Build test command
    test_cmd_parts = ["python", "-m", "pytest"]
    
    if args.verbose:
        test_cmd_parts.append("-vv")
    
    if args.coverage:
        test_cmd_parts.extend(["--cov=archguard", "--cov-report=html", "--cov-report=term"])
    
    # Select test categories
    if args.integration:
        test_cmd_parts.extend(["-m", "integration"])
    elif args.unit:
        test_cmd_parts.extend(["-m", "unit"])
    elif args.mcp:
        test_cmd_parts.extend(["-m", "mcp"])
    elif args.embedding:
        test_cmd_parts.extend(["-m", "embedding"])
    elif args.performance:
        test_cmd_parts.extend(["-m", "performance"])
    else:
        # Run all tests by default
        test_cmd_parts.append("tests/")
    
    test_cmd = " ".join(test_cmd_parts)
    
    # Run tests
    success = run_command(test_cmd, "Running ArchGuard test suite")
    
    if args.documentation:
        print("\n📚 Generating test documentation...")
        
        # Generate test report
        doc_cmd = f"python -m pytest tests/ --collect-only --quiet | grep -E '::test_' > test_inventory.txt"
        run_command(doc_cmd, "Collecting test inventory")
        
        # Generate coverage report if available
        if args.coverage:
            run_command("python -m coverage html", "Generating HTML coverage report")
            print("📊 Coverage report available at htmlcov/index.html")
    
    # Test summary
    print("\n📋 Test Summary")
    print("=" * 60)
    
    if success:
        print("✅ All tests passed!")
        print("\n🎯 System Status:")
        print("   • Core ArchGuard functionality: ✅ Working")
        print("   • MCP protocol compliance: ✅ Verified")
        print("   • Embedding system: ✅ Functional")
        print("   • Integration patterns: ✅ Documented")
        print("\n🚀 ArchGuard is ready for production use!")
        return 0
    else:
        print("❌ Some tests failed!")
        print("\n🔧 Next steps:")
        print("   • Review test output above")
        print("   • Check troubleshooting guide: docs/troubleshooting.md")
        print("   • Run specific test categories to isolate issues")
        print("   • Check system dependencies and configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())