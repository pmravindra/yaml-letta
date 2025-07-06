"""
YAML-Letta: YAML-driven agent configuration for Letta

A Python library that allows you to define Letta agents using YAML configuration files.
"""

from .builder import YAMLAgentBuilder
from .config import AgentConfig, ToolConfig, MemoryConfig, LLMConfig
from .parser import YAMLAgentParser
from .factory import LettaAgentFactory

# Main interface - this is what users import
def create_agent_from_yaml(yaml_file: str, token: str = None, base_url: str = None):
    """
    Create a Letta agent from a YAML configuration file.
    
    Args:
        yaml_file: Path to the YAML configuration file
        token: Letta Cloud API token (for cloud usage)
        base_url: Base URL for self-hosted Letta server (default: http://localhost:8283)
    
    Returns:
        Created Letta agent object
    """
    builder = YAMLAgentBuilder(token=token, base_url=base_url)
    return builder.build_from_file(yaml_file)

# For tool registration
def create_builder(token: str = None, base_url: str = None) -> YAMLAgentBuilder:
    """
    Create a YAMLAgentBuilder for registering tools and building multiple agents.
    
    Args:
        token: Letta Cloud API token (for cloud usage) 
        base_url: Base URL for self-hosted Letta server (default: http://localhost:8283)
    
    Returns:
        YAMLAgentBuilder instance
    """
    return YAMLAgentBuilder(token=token, base_url=base_url)

__version__ = "0.1.0"
__all__ = [
    "create_agent_from_yaml",
    "create_builder", 
    "YAMLAgentBuilder",
    "AgentConfig",
    "ToolConfig", 
    "MemoryConfig",
    "LLMConfig"
]