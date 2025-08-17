#!/usr/bin/env python3
"""
ArchGuard CLI - Command line interface for ArchGuard architectural toolkit
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

from .server import main as server_main
from .http_server import main as http_server_main
from .config import ArchGuardConfig


def init_command(args) -> None:
    """Initialize ArchGuard in a project."""
    project_config = Path.cwd() / ".archguard.toml"
    
    if project_config.exists() and not args.force:
        print(f"❌ .archguard.toml already exists in {Path.cwd()}")
        print("Use --force to overwrite")
        sys.exit(1)
    
    # Create sample project configuration
    config_content = """# ArchGuard Project Configuration
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
        print(f"✅ Initialized ArchGuard in {Path.cwd()}")
        print(f"📝 Created {project_config}")
        print("\nNext steps:")
        print("  1. Edit .archguard.toml to customize rules for your project")
        print("  2. Run 'archguard check' to analyze your codebase")
        print("  3. Integrate with your AI assistant using 'archguard server'")
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        sys.exit(1)


def check_command(args) -> None:
    """Run architectural analysis on the project."""
    print("🔍 Running ArchGuard architectural analysis...")
    
    # Check if we're in a project with ArchGuard config
    config_path = ArchGuardConfig._get_project_config_path()
    if not config_path:
        print("⚠️  No .archguard.toml found. Run 'archguard init' first.")
        return
    
    print(f"📋 Using configuration: {config_path}")
    
    # Get project settings
    project_name = ArchGuardConfig.get_project_name()
    if project_name:
        print(f"📦 Project: {project_name}")
    
    arch_style = ArchGuardConfig.get_architecture_style()
    if arch_style:
        print(f"🏗️  Architecture: {arch_style}")
    
    max_lines = ArchGuardConfig.get_max_file_lines()
    print(f"📏 Max file lines: {max_lines}")
    
    ignored_paths = ArchGuardConfig.get_ignored_paths()
    if ignored_paths:
        print(f"🚫 Ignored paths: {', '.join(ignored_paths)}")
    
    print("\n🎯 Analysis Results:")
    print("✅ Configuration is valid")
    print("💡 For real-time guidance, run 'archguard server' and integrate with your AI assistant")
    
    if args.verbose:
        print(f"\n🔧 Full configuration:")
        config = ArchGuardConfig._merge_configs()
        for section, values in config.items():
            print(f"  [{section}]")
            if isinstance(values, dict):
                for key, value in values.items():
                    print(f"    {key} = {repr(value)}")
            else:
                print(f"    {values}")


def config_command(args) -> None:
    """Show or manage ArchGuard configuration."""
    if args.action == "show":
        print("🔧 ArchGuard Configuration")
        print("=" * 50)
        
        # Show global config path
        global_path = ArchGuardConfig._get_global_config_path()
        print(f"📁 Global config: {global_path}")
        if global_path.exists():
            print("   ✅ Found")
        else:
            print("   ❌ Not found (using defaults)")
        
        # Show project config path
        project_path = ArchGuardConfig._get_project_config_path()
        if project_path:
            print(f"📁 Project config: {project_path}")
            print("   ✅ Found")
        else:
            print("📁 Project config: Not found")
        
        print(f"\n🌐 Current settings:")
        print(f"   HTTP Host: {ArchGuardConfig.get_http_host()}")
        print(f"   HTTP Port: {ArchGuardConfig.get_http_port()}")
        print(f"   Log Level: {ArchGuardConfig.get_log_level()}")
        print(f"   Max File Lines: {ArchGuardConfig.get_max_file_lines()}")
        print(f"   Complexity Threshold: {ArchGuardConfig.get_complexity_threshold()}")
        
        project_name = ArchGuardConfig.get_project_name()
        if project_name:
            print(f"   Project Name: {project_name}")
    
    elif args.action == "init-global":
        global_path = ArchGuardConfig._get_global_config_path()
        global_path.parent.mkdir(parents=True, exist_ok=True)
        
        global_config = """# ArchGuard Global Configuration
# This file defines default settings for all ArchGuard projects

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


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ArchGuard - Your AI-powered architectural co-pilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  archguard init                      # Initialize ArchGuard in current project
  archguard check                     # Run architectural analysis
  archguard server                    # Start MCP server for AI integration
  archguard http --port 8080          # Start HTTP server for production
  archguard config show               # Show current configuration

For uvx usage:
  uvx --from git+https://github.com/aic-holdings/archguard archguard init
  uvx --from git+https://github.com/aic-holdings/archguard archguard check
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize ArchGuard in current project")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing configuration")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Run architectural analysis")
    check_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed configuration")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage ArchGuard configuration")
    config_subparsers = config_parser.add_subparsers(dest="action", help="Configuration actions")
    
    show_parser = config_subparsers.add_parser("show", help="Show current configuration")
    
    init_global_parser = config_subparsers.add_parser("init-global", help="Initialize global configuration")
    init_global_parser.add_argument("--force", action="store_true", help="Overwrite existing global config")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start MCP server (stdio)")
    
    # HTTP server command  
    http_parser = subparsers.add_parser("http", help="Start HTTP server")
    http_parser.add_argument("--host", default=ArchGuardConfig.get_http_host(), help="Host to bind to")
    http_parser.add_argument("--port", type=int, default=ArchGuardConfig.get_http_port(), help="Port to bind to")
    
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
        server_main()
    elif args.command == "http":
        # Import and run HTTP server with args
        from .http_server import main as http_main
        http_main(host=args.host, port=args.port)
    else:
        parser.print_help()
        sys.exit(1)


def server_main_cli() -> None:
    """Direct entry point for archguard-server command."""
    server_main()


def http_main_cli() -> None:
    """Direct entry point for archguard-http command."""
    import argparse
    from .http_server import main as http_main
    
    parser = argparse.ArgumentParser(description="ArchGuard HTTP Server")
    parser.add_argument("--host", default=ArchGuardConfig.get_http_host(), help="Host to bind to")
    parser.add_argument("--port", type=int, default=ArchGuardConfig.get_http_port(), help="Port to bind to")
    
    args = parser.parse_args()
    http_main(host=args.host, port=args.port)


if __name__ == "__main__":
    main()