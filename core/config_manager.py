"""
Configuration management for linters

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Handles loading and managing hierarchical configuration for linters and rules.
             Supports linking individual linter configurations from a root configuration.
"""

import json
import os
from typing import Dict, Optional, Any
from pathlib import Path


class ConfigManager:
    """
    Manages hierarchical configuration loading and access
    
    Supports:
    - Root configuration with linter enable/disable flags
    - Linked individual linter configuration files
    - JSON configuration files
    - Default configurations
    - Per-linter configurations
    - Per-rule configurations
    
    Hierarchical Structure:
        root_config.json:
        {
            "linters": {
                "naturaldocs": {
                    "enabled": true,
                    "config_file": "configs/naturaldocs.json"
                },
                "verible": {
                    "enabled": false,
                    "config_file": "configs/verible.json"
                }
            }
        }
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager with hierarchical support
        
        Args:
            config_file: Path to root configuration file (JSON)
        """
        self.config_file = config_file
        self.config_dir = Path(config_file).parent if config_file else Path.cwd()
        self.loaded_configs = {}  # Cache for loaded linked configs
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """
        Load hierarchical configuration from file or use defaults
        
        Supports loading a root config that links to individual linter configs.
        
        Returns:
            Configuration dictionary
        """
        # Try to load from specified file
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Process hierarchical structure if present
                    return self._process_hierarchical_config(config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config from {self.config_file}: {e}")
        
        # Try to find default config in configs directory
        script_dir = Path(__file__).parent.parent
        default_config = script_dir / 'configs' / 'lint_config.json'
        
        if default_config.exists():
            try:
                with open(default_config, 'r') as f:
                    config = json.load(f)
                    return self._process_hierarchical_config(config)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return minimal default configuration
        return self._get_default_config()
    
    def _process_hierarchical_config(self, config: dict) -> dict:
        """
        Process hierarchical configuration structure
        
        This method checks if linters have linked config files and merges them.
        
        Args:
            config: Root configuration dictionary
        
        Returns:
            Processed configuration with linked configs merged
        """
        if "linters" not in config:
            return config
        
        linters = config["linters"]
        
        for linter_name, linter_config in linters.items():
            # Check if this linter has a linked config file
            if isinstance(linter_config, dict) and "config_file" in linter_config:
                linked_config_path = linter_config["config_file"]
                
                # Resolve relative path from config directory
                if not os.path.isabs(linked_config_path):
                    linked_config_path = os.path.join(self.config_dir, linked_config_path)
                
                # Load linked configuration
                linked_config = self._load_linked_config(linked_config_path)
                
                if linked_config:
                    # Merge linked config into linter config
                    # Root config settings take precedence (especially 'enabled')
                    enabled = linter_config.get("enabled", True)
                    merged_config = {**linked_config, **linter_config}
                    merged_config["enabled"] = enabled
                    
                    # Remove config_file from final config to avoid confusion
                    if "config_file" in merged_config:
                        merged_config["_source_config"] = merged_config.pop("config_file")
                    
                    config["linters"][linter_name] = merged_config
        
        return config
    
    def _load_linked_config(self, config_path: str) -> Optional[dict]:
        """
        Load a linked configuration file
        
        Args:
            config_path: Path to linked configuration file
        
        Returns:
            Configuration dictionary or None if loading fails
        """
        # Check cache first
        if config_path in self.loaded_configs:
            return self.loaded_configs[config_path]
        
        if not os.path.exists(config_path):
            print(f"Warning: Linked config file not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.loaded_configs[config_path] = config
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load linked config from {config_path}: {e}")
            return None
    
    def _get_default_config(self) -> dict:
        """
        Get default configuration structure
        
        Returns:
            Default configuration dictionary with empty strings for project info
        """
        return {
            "project": {
                "name": "",
                "company": "",
                "description": ""
            },
            "linters": {},
            "global": {
                "strict_mode": False,
                "use_color": False
            }
        }
    
    def get_linter_config(self, linter_name: str) -> dict:
        """
        Get configuration for a specific linter
        
        Args:
            linter_name: Name of the linter
        
        Returns:
            Configuration dictionary for the linter (merged from linked configs if present)
        """
        return self.config.get("linters", {}).get(linter_name, {})
    
    def is_linter_enabled(self, linter_name: str) -> bool:
        """
        Check if a linter is enabled in the configuration
        
        Args:
            linter_name: Name of the linter
        
        Returns:
            True if linter is enabled (default: True)
        """
        linter_config = self.get_linter_config(linter_name)
        return linter_config.get("enabled", True)
    
    def get_rule_config(self, linter_name: str, rule_id: str) -> dict:
        """
        Get configuration for a specific rule
        
        Args:
            linter_name: Name of the linter
            rule_id: ID of the rule
        
        Returns:
            Configuration dictionary for the rule
        """
        linter_config = self.get_linter_config(linter_name)
        rules_config = linter_config.get("rules", {})
        return rules_config.get(rule_id, {})
    
    def is_rule_enabled(self, linter_name: str, rule_id: str) -> bool:
        """
        Check if a rule is enabled
        
        Args:
            linter_name: Name of the linter
            rule_id: ID of the rule
        
        Returns:
            True if rule is enabled (default: True)
        """
        rule_config = self.get_rule_config(linter_name, rule_id)
        return rule_config.get("enabled", True)
    
    def get_rule_severity(self, linter_name: str, rule_id: str, default: str = "ERROR") -> str:
        """
        Get severity level for a rule
        
        Checks both 'rules' and 'severity_levels' sections for compatibility
        
        Args:
            linter_name: Name of the linter
            rule_id: ID of the rule
            default: Default severity if not configured
        
        Returns:
            Severity string ("ERROR", "WARNING", or "INFO")
        """
        linter_config = self.get_linter_config(linter_name)
        
        # Check 'rules' section first (new format)
        rule_config = self.get_rule_config(linter_name, rule_id)
        if 'severity' in rule_config:
            return rule_config['severity']
        
        # Check 'severity_levels' section (NaturalDocs format)
        severity_levels = linter_config.get('severity_levels', {})
        if rule_id in severity_levels:
            return severity_levels[rule_id]
        
        return default
    
    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a global setting
        
        Args:
            key: Setting key
            default: Default value if not found
        
        Returns:
            Setting value or default
        """
        return self.config.get("global", {}).get(key, default)
    
    def get_project_info(self) -> dict:
        """
        Get project information
        
        Returns:
            Project info dictionary
        """
        return self.config.get("project", {})
    
    def save_config(self, output_path: str):
        """
        Save current configuration to file
        
        Args:
            output_path: Path to save configuration
        """
        with open(output_path, 'w') as f:
            json.dump(self.config, f, indent=2)

