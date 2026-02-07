"""Configuration management for bio-sim package."""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """
    Configuration manager for the bio-sim package.

    Supports loading from YAML files and environment variables.

    Example:
        >>> config = Config()
        >>> config.load_from_file("config.yaml")
        >>> value = config.get("simulation.width", default=800)
    """

    def __init__(self):
        """Initialize empty configuration."""
        self._config: Dict[str, Any] = {}

    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a YAML file.

        Args:
            file_path: Path to the YAML configuration file

        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the YAML is invalid
        """
        config_path = Path(file_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f) or {}

    def load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Load configuration from a dictionary.

        Args:
            config_dict: Dictionary containing configuration
        """
        self._config.update(config_dict)

    def load_from_env(self, prefix: str = "BIO_SIM_") -> None:
        """
        Load configuration from environment variables.

        Args:
            prefix: Prefix for environment variables (default: BIO_SIM_)

        Example:
            If env var BIO_SIM_WIDTH=800, it can be accessed as config.get("width")
        """
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self._config[config_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Supports nested keys with dot notation.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key is not found

        Returns:
            Configuration value or default

        Example:
            >>> config.get("simulation.width")
            >>> config.get("simulation.width", default=800)
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration as a dictionary.

        Returns:
            Dictionary containing all configuration
        """
        return self._config.copy()

    def save_to_file(self, file_path: str) -> None:
        """
        Save current configuration to a YAML file.

        Args:
            file_path: Path to save the configuration file
        """
        config_path = Path(file_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False)


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Global Config instance
    """
    global _global_config

    if _global_config is None:
        _global_config = Config()

        # Try to load default config files
        default_paths = ["config.yaml", "config/config.yaml", ".bio-sim.yaml"]
        for path in default_paths:
            if Path(path).exists():
                try:
                    _global_config.load_from_file(path)
                    break
                except Exception:
                    pass

    return _global_config
