import os
from typing import Dict, Any, Optional
import yaml
import json

class ConfigManager:
    """
    Manage application configuration from multiple sources.
    Supports YAML, JSON, and environment variables.
    """
    
    def __init__(self, 
                 config_file: str = 'config.yaml', 
                 env_prefix: str = 'APP_'):
        """
        Initialize configuration manager.
        
        :param config_file: Path to configuration file
        :param env_prefix: Prefix for environment variables
        """
        self.config_file = config_file
        self.env_prefix = env_prefix
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file and environment variables.
        
        :return: Merged configuration dictionary
        """
        # Load file-based configuration
        config = self._load_file_config()
        
        # Override with environment variables
        config = self._override_with_env_vars(config)
        
        return config
    
    def _load_file_config(self) -> Dict[str, Any]:
        """
        Load configuration from file (YAML or JSON).
        
        :return: Configuration dictionary
        """
        if not os.path.exists(self.config_file):
            return {}
        
        file_ext = os.path.splitext(self.config_file)[1].lower()
        
        with open(self.config_file, 'r') as f:
            if file_ext == '.yaml' or file_ext == '.yml':
                return yaml.safe_load(f) or {}
            elif file_ext == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file type: {file_ext}")
    
    def _override_with_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override configuration with environment variables.
        
        :param config: Initial configuration dictionary
        :return: Updated configuration dictionary
        """
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                config_key = key[len(self.env_prefix):].lower()
                try:
                    # Convert string to appropriate type
                    if value.lower() in ['true', 'false']:
                        config[config_key] = value.lower() == 'true'
                    elif value.isdigit():
                        config[config_key] = int(value)
                    elif self._is_float(value):
                        config[config_key] = float(value)
                    else:
                        config[config_key] = value
                except Exception as e:
                    print(f"Error processing env var {key}: {e}")
        
        return config
    
    def _is_float(self, value: str) -> bool:
        """
        Check if a string can be converted to a float.
        
        :param value: String to check
        :return: True if convertible to float, False otherwise
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value.
        
        :param key: Configuration key
        :param default: Default value if key not found
        :return: Configuration value
        """
        return self.config.get(key, default)
    
    def update(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.
        
        :param updates: Dictionary of configuration updates
        """
        self.config.update(updates)
    
    def save(self, file_path: Optional[str] = None):
        """
        Save current configuration to a file.
        
        :param file_path: Path to save configuration file
        """
        save_path = file_path or self.config_file
        file_ext = os.path.splitext(save_path)[1].lower()
        
        with open(save_path, 'w') as f:
            if file_ext in ['.yaml', '.yml']:
                yaml.dump(self.config, f)
            elif file_ext == '.json':
                json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")