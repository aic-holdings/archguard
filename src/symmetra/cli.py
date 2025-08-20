#!/usr/bin/env python3
"""
Symmetra CLI - Command line interface for Symmetra architectural toolkit
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

# Use absolute imports to avoid issues with direct module execution
try:
    from symmetra.server import main as server_main
    from symmetra.simple_server import run_server as simple_server_main
    from symmetra.http_server import main as http_server_main
    from symmetra.config import SymmetraConfig
    from symmetra.guidance_manager import guidance_manager
except ImportError:
    # Fallback for development/direct execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from symmetra.server import main as server_main
    from symmetra.simple_server import run_server as simple_server_main
    from symmetra.http_server import main as http_server_main
    from symmetra.config import SymmetraConfig
    from symmetra.guidance_manager import guidance_manager


def init_command(args) -> None:
    """Initialize Symmetra in a project."""
    project_config = Path.cwd() / ".symmetra.toml"
    
    if project_config.exists() and not args.force:
        print(f"❌ .symmetra.toml already exists in {Path.cwd()}")
        print("Use --force to overwrite")
        sys.exit(1)
    
    # Create sample project configuration
    config_content = """# Symmetra Project Configuration
# This file defines architectural rules and settings for your project

[project]
name = "{project_name}"
# architecture_style = "clean_architecture"  # Options: clean_architecture, layered, microservices

[rules]
max_file_lines = 300
max_function_lines = 50
complexity_threshold = "medium"  # Options: low, medium, high
enforce_type_hints = true

[ignore]
paths = [
    "migrations/",
    "node_modules/",
    ".git/",
    "__pycache__/",
    "*.pyc"
]

# [custom_rules]
# no_god_objects = true
# single_responsibility = true
""".format(project_name=Path.cwd().name)
    
    try:
        with open(project_config, 'w') as f:
            f.write(config_content)
        print(f"✅ Initialized Symmetra in {Path.cwd()}")
        print(f"📝 Created {project_config}")
        print("\nNext steps:")
        print("  1. Edit .symmetra.toml to customize rules for your project")
        print("  2. Run 'symmetra check' to analyze your codebase")
        print("  3. Integrate with your AI assistant using 'symmetra server'")
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        sys.exit(1)


def check_command(args) -> None:
    """Run architectural analysis on the project."""
    print("🔍 Running Symmetra architectural analysis...")
    
    # Check if we're in a project with Symmetra config
    config_path = SymmetraConfig._get_project_config_path()
    if not config_path:
        print("⚠️  No .symmetra.toml found. Run 'symmetra init' first.")
        return
    
    print(f"📋 Using configuration: {config_path}")
    
    # Get project settings
    project_name = SymmetraConfig.get_project_name()
    if project_name:
        print(f"📦 Project: {project_name}")
    
    arch_style = SymmetraConfig.get_architecture_style()
    if arch_style:
        print(f"🏗️  Architecture: {arch_style}")
    
    max_lines = SymmetraConfig.get_max_file_lines()
    print(f"📏 Max file lines: {max_lines}")
    
    ignored_paths = SymmetraConfig.get_ignored_paths()
    if ignored_paths:
        print(f"🚫 Ignored paths: {', '.join(ignored_paths)}")
    
    print("\n🎯 Analysis Results:")
    print("✅ Configuration is valid")
    print("💡 For real-time guidance, run 'symmetra server' and integrate with your AI assistant")
    
    if args.verbose:
        print(f"\n🔧 Full configuration:")
        config = SymmetraConfig._merge_configs()
        for section, values in config.items():
            print(f"  [{section}]")
            if isinstance(values, dict):
                for key, value in values.items():
                    print(f"    {key} = {repr(value)}")
            else:
                print(f"    {values}")


def config_command(args) -> None:
    """Show or manage Symmetra configuration."""
    if args.action == "show":
        print("🔧 Symmetra Configuration")
        print("=" * 50)
        
        # Show global config path
        global_path = SymmetraConfig._get_global_config_path()
        print(f"📁 Global config: {global_path}")
        if global_path.exists():
            print("   ✅ Found")
        else:
            print("   ❌ Not found (using defaults)")
        
        # Show project config path
        project_path = SymmetraConfig._get_project_config_path()
        if project_path:
            print(f"📁 Project config: {project_path}")
            print("   ✅ Found")
        else:
            print("📁 Project config: Not found")
        
        print(f"\n🌐 Current settings:")
        print(f"   HTTP Host: {SymmetraConfig.get_http_host()}")
        print(f"   HTTP Port: {SymmetraConfig.get_http_port()}")
        print(f"   Log Level: {SymmetraConfig.get_log_level()}")
        print(f"   Max File Lines: {SymmetraConfig.get_max_file_lines()}")
        print(f"   Complexity Threshold: {SymmetraConfig.get_complexity_threshold()}")
        
        project_name = SymmetraConfig.get_project_name()
        if project_name:
            print(f"   Project Name: {project_name}")
    
    elif args.action == "init-global":
        global_path = SymmetraConfig._get_global_config_path()
        global_path.parent.mkdir(parents=True, exist_ok=True)
        
        global_config = """# Symmetra Global Configuration
# This file defines default settings for all Symmetra projects

[general]
log_level = "INFO"
auto_format_suggestions = true

[server]
http_host = "0.0.0.0"
http_port = 8080
http_path = "/mcp"

[rules]
max_file_lines = 300
max_function_lines = 50
complexity_threshold = "medium"
enforce_type_hints = true
"""
        
        if global_path.exists() and not args.force:
            print(f"❌ Global config already exists at {global_path}")
            print("Use --force to overwrite")
            sys.exit(1)
        
        try:
            with open(global_path, 'w') as f:
                f.write(global_config)
            print(f"✅ Created global configuration at {global_path}")
        except Exception as e:
            print(f"❌ Failed to create global config: {e}")
            sys.exit(1)


def add_command(args) -> None:
    """Add new architectural guidance."""
    description = args.description
    category = args.category
    priority = args.priority
    
    if not description.strip():
        print("❌ Description cannot be empty")
        sys.exit(1)
    
    print("💡 Adding guidance...")
    
    # Use quick_add for simple one-liner descriptions  
    if len(description.split()) < 10 and not args.detailed:
        result = guidance_manager.quick_add(description, category)
    else:
        # Split into title and guidance for longer descriptions
        lines = description.split('\n')
        if len(lines) > 1:
            title = lines[0].strip()
            guidance = '\n'.join(lines[1:]).strip()
        else:
            # Use first few words as title
            words = description.split()
            if len(words) > 8:
                title = ' '.join(words[:8]) + "..."
                guidance = description
            else:
                title = description
                guidance = description
        
        result = guidance_manager.add_guidance(
            title=title,
            guidance=guidance,
            category=category,
            priority=priority,
            rationale=args.rationale
        )
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"🔖 Rule ID: {result['rule_id']}")
        print(f"📂 Category: {result['category']}")
        print(f"⭐ Priority: {result['priority']}")
        
        if args.test:
            print(f"\n🔍 Testing searchability...")
            test_results = guidance_manager.search_guidance(description[:50], limit=3)
            if any(r['rule_id'] == result['rule_id'] for r in test_results):
                print("✅ Guidance is searchable!")
            else:
                print("⚠️  Guidance might not be immediately searchable (embedding processing)")
    else:
        print(f"❌ Failed to add guidance: {result['error']}")
        sys.exit(1)


def search_command(args) -> None:
    """Search existing architectural guidance."""
    query = args.query
    limit = args.limit
    
    if not query.strip():
        print("❌ Search query cannot be empty")
        sys.exit(1)
    
    print(f"🔍 Searching for: '{query}'")
    results = guidance_manager.search_guidance(query, limit=limit)
    
    if not results:
        print("❌ No guidance found matching your query")
        print("💡 Try different keywords or add new guidance with 'symmetra add'")
        return
    
    print(f"\n📋 Found {len(results)} relevant guidance:")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   🔖 ID: {result['rule_id']}")
        print(f"   📂 Category: {result['category']}")
        print(f"   ⭐ Priority: {result['priority']}")
        print(f"   🎯 Similarity: {result['similarity']:.3f}")
        print(f"   💡 Guidance: {result['guidance'][:200]}{'...' if len(result['guidance']) > 200 else ''}")
        if result.get('contexts'):
            print(f"   🏷️  Contexts: {', '.join(result['contexts'])}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Symmetra - Your AI-powered architectural co-pilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  symmetra init                      # Initialize Symmetra in current project
  symmetra check                     # Run architectural analysis
  symmetra server                    # Start MCP server for AI integration
  symmetra http --port 8080          # Start HTTP server for production
  symmetra config show               # Show current configuration

For uvx usage:
  uvx --from git+https://github.com/aic-holdings/symmetra symmetra init
  uvx --from git+https://github.com/aic-holdings/symmetra symmetra check
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Symmetra in current project")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing configuration")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Run architectural analysis")
    check_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed configuration")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage Symmetra configuration")
    config_subparsers = config_parser.add_subparsers(dest="action", help="Configuration actions")
    
    show_parser = config_subparsers.add_parser("show", help="Show current configuration")
    
    init_global_parser = config_subparsers.add_parser("init-global", help="Initialize global configuration")
    init_global_parser.add_argument("--force", action="store_true", help="Overwrite existing global config")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start MCP server (stdio)")
    server_parser.add_argument("--mode", 
                              choices=["simple", "complex"], 
                              default="simple",
                              help="Server mode: 'simple' (AI-first) or 'complex' (full detectors) (default: simple)")
    server_parser.add_argument("--context", 
                              choices=["desktop-app", "agent", "ide-assistant"], 
                              default="desktop-app",
                              help="Context for the server environment (default: desktop-app)")
    server_parser.add_argument("--project", 
                              type=str,
                              help="Project directory path or name to activate")
    
    # HTTP server command  
    http_parser = subparsers.add_parser("http", help="Start HTTP server")
    http_parser.add_argument("--host", default=SymmetraConfig.get_http_host(), help="Host to bind to")
    http_parser.add_argument("--port", type=int, default=SymmetraConfig.get_http_port(), help="Port to bind to")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "init":
        init_command(args)
    elif args.command == "check":
        check_command(args)
    elif args.command == "config":
        if not args.action:
            config_parser.print_help()
            sys.exit(1)
        config_command(args)
    elif args.command == "server":
        mode = getattr(args, 'mode', 'simple')
        if mode == "simple":
            print("🚀 Starting Symmetra Simple Server (AI-first mode)")
            simple_server_main()
        else:
            print("🔧 Starting Symmetra Complex Server (full detectors mode)")
            server_main(context=getattr(args, 'context', 'desktop-app'), 
                       project=getattr(args, 'project', None))
    elif args.command == "http":
        # Import and run HTTP server with args
        from .http_server import main as http_main
        http_main(host=args.host, port=args.port)
    else:
        parser.print_help()
        sys.exit(1)


def server_main_cli() -> None:
    """Direct entry point for symmetra-server command."""
    simple_server_main()


def http_main_cli() -> None:
    """Direct entry point for symmetra-http command."""
    import argparse
    from .http_server import main as http_main
    
    parser = argparse.ArgumentParser(description="Symmetra HTTP Server")
    parser.add_argument("--host", default=SymmetraConfig.get_http_host(), help="Host to bind to")
    parser.add_argument("--port", type=int, default=SymmetraConfig.get_http_port(), help="Port to bind to")
    
    args = parser.parse_args()
    http_main(host=args.host, port=args.port)


if __name__ == "__main__":
    main()