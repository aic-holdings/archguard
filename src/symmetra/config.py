"""
Symmetra Configuration Management
Layered configuration system with global and project-specific settings.
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional


class SymmetraConfig:
    """Layered configuration management for Symmetra."""
    
    _global_config: Optional[Dict[str, Any]] = None
    _project_config: Optional[Dict[str, Any]] = None
    _merged_config: Optional[Dict[str, Any]] = None
    
    @classmethod
    def _get_global_config_path(cls) -> Path:
        """Get global configuration file path."""
        config_dir = Path.home() / ".config" / "symmetra"
        return config_dir / "config.toml"
    
    @classmethod
    def _get_project_config_path(cls, start_path: Optional[str] = None) -> Optional[Path]:
        """Find project configuration file by walking up directory tree."""
        if start_path:
            current = Path(start_path).resolve()
        else:
            current = Path.cwd().resolve()
        
        # Walk up the directory tree looking for .symmetra.toml
        for parent in [current] + list(current.parents):
            config_file = parent / ".symmetra.toml"
            if config_file.exists():
                return config_file
        return None
    
    @classmethod
    def _load_global_config(cls) -> Dict[str, Any]:
        """Load global configuration from ~/.config/symmetra/config.toml"""
        if cls._global_config is not None:
            return cls._global_config
        
        config_path = cls._get_global_config_path()
        if config_path.exists():
            try:
                cls._global_config = toml.load(config_path)
            except Exception:
                cls._global_config = {}
        else:
            cls._global_config = {}
        
        return cls._global_config
    
    @classmethod
    def _load_project_config(cls, start_path: Optional[str] = None) -> Dict[str, Any]:
        """Load project configuration from .symmetra.toml"""
        if cls._project_config is not None:
            return cls._project_config
        
        config_path = cls._get_project_config_path(start_path)
        if config_path:
            try:
                cls._project_config = toml.load(config_path)
            except Exception:
                cls._project_config = {}
        else:
            cls._project_config = {}
        
        return cls._project_config
    
    @classmethod
    def _merge_configs(cls, start_path: Optional[str] = None) -> Dict[str, Any]:
        """Merge global and project configurations, with project overriding global."""
        if cls._merged_config is not None:
            return cls._merged_config
        
        global_config = cls._load_global_config()
        project_config = cls._load_project_config(start_path)
        
        # Deep merge configs with project config taking precedence
        merged = {}
        
        # Start with global config
        for section, values in global_config.items():
            if isinstance(values, dict):
                merged[section] = values.copy()
            else:
                merged[section] = values
        
        # Override with project config
        for section, values in project_config.items():
            if isinstance(values, dict) and section in merged and isinstance(merged[section], dict):
                merged[section].update(values)
            else:
                merged[section] = values
        
        cls._merged_config = merged
        return cls._merged_config
    
    @classmethod
    def get_config_value(cls, section: str, key: str, default: Any = None, env_var: Optional[str] = None) -> Any:
        """Get configuration value with precedence: env var > project config > global config > default"""
        # Check environment variable first
        if env_var:
            env_value = os.getenv(env_var)
            if env_value is not None:
                return env_value
        
        # Check merged config
        config = cls._merge_configs()
        if section in config and key in config[section]:
            return config[section][key]
        
        return default
    
    @classmethod
    def get_http_host(cls) -> str:
        """Get HTTP server host."""
        return cls.get_config_value("server", "http_host", "0.0.0.0", "SYMMETRA_HTTP_HOST")
    
    @classmethod
    def get_http_port(cls) -> int:
        """Get HTTP server port."""
        port = cls.get_config_value("server", "http_port", 8080, "SYMMETRA_HTTP_PORT")
        return int(port)
    
    @classmethod
    def get_http_path(cls) -> str:
        """Get HTTP server path."""
        return cls.get_config_value("server", "http_path", "/mcp", "SYMMETRA_HTTP_PATH")
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get logging level."""
        return cls.get_config_value("general", "log_level", "INFO", "SYMMETRA_LOG_LEVEL")
    
    @classmethod
    def get_max_file_lines(cls) -> int:
        """Get maximum file lines recommendation."""
        lines = cls.get_config_value("rules", "max_file_lines", 300, "SYMMETRA_MAX_FILE_LINES")
        return int(lines)
    
    @classmethod
    def get_max_function_lines(cls) -> int:
        """Get maximum function lines recommendation."""
        lines = cls.get_config_value("rules", "max_function_lines", 50, "SYMMETRA_MAX_FUNCTION_LINES")
        return int(lines)
    
    @classmethod
    def get_complexity_threshold(cls) -> str:
        """Get complexity threshold level."""
        return cls.get_config_value("rules", "complexity_threshold", "medium", "SYMMETRA_COMPLEXITY_THRESHOLD")
    
    @classmethod
    def get_project_name(cls) -> Optional[str]:
        """Get project name from project config."""
        return cls.get_config_value("project", "name", None)
    
    @classmethod
    def get_architecture_style(cls) -> Optional[str]:
        """Get architecture style from project config."""
        return cls.get_config_value("project", "architecture_style", None)
    
    @classmethod
    def get_ignored_paths(cls) -> list:
        """Get list of ignored paths."""
        ignored = cls.get_config_value("ignore", "paths", [])
        if isinstance(ignored, str):
            return [ignored]
        return ignored or []
    
    @classmethod
    def get_openai_api_key(cls) -> Optional[str]:
        """Get OpenAI API key from project config or environment."""
        return cls.get_config_value("api", "openai_api_key", None, "OPENAI_API_KEY")
    
    @classmethod
    def get_supabase_url(cls) -> Optional[str]:
        """Get Supabase URL from project config or environment."""
        return cls.get_config_value("api", "supabase_url", None, "SYMMETRA_SUPABASE_URL")
    
    @classmethod
    def get_supabase_key(cls) -> Optional[str]:
        """Get Supabase key from project config or environment."""
        return cls.get_config_value("api", "supabase_key", None, "SYMMETRA_SUPABASE_KEY")
    
    @classmethod
    def reset_cache(cls):
        """Reset configuration cache - useful for testing."""
        cls._global_config = None
        cls._project_config = None
        cls._merged_config = None