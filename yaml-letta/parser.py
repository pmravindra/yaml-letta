"""
YAML parser for agent configurations.
"""

import yaml
from typing import Dict
from .config import AgentConfig

class YAMLAgentParser:
    """Parser that converts YAML files to AgentConfig objects."""
    
    def parse_file(self, file_path: str) -> AgentConfig:
        """
        Parse a YAML file and return an AgentConfig object.
        
        Args:
            file_path: Path to the YAML configuration file
            
        Returns:
            AgentConfig object with validated configuration
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            yaml.YAMLError: If the YAML is malformed
            ValueError: If the configuration is invalid
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {file_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML format in {file_path}: {e}")
        
        return self.parse_dict(data)
    
    def parse_dict(self, data: Dict) -> AgentConfig:
        """
        Parse a dictionary and return an AgentConfig object.
        
        Args:
            data: Dictionary containing agent configuration
            
        Returns:
            AgentConfig object with validated configuration
            
        Raises:
            ValueError: If the configuration is invalid
        """
        if 'agent' not in data:
            raise ValueError("YAML must contain an 'agent' key at the root level")
        
        agent_data = data['agent']
        
        try:
            return AgentConfig(**agent_data)
        except Exception as e:
            raise ValueError(f"Invalid agent configuration: {e}")