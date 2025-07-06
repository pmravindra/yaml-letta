"""
Main orchestrator that coordinates all components.
"""

from .parser import YAMLAgentParser
from .factory import LettaAgentFactory
from .config import AgentConfig

class YAMLAgentBuilder:
    """Main orchestrator for building Letta agents from YAML configurations."""
    
    def __init__(self, token: str = None, base_url: str = None):
        """
        Initialize the builder with Letta connection details.
        
        Args:
            token: Letta Cloud API token (for cloud usage)
            base_url: Base URL for self-hosted Letta server
        """
        self.parser = YAMLAgentParser()
        self.factory = LettaAgentFactory(token=token, base_url=base_url)
    
    def register_tool(self, name: str, func: callable):
        """
        Register a tool that can be used by agents.
        
        Args:
            name: Name of the tool (must match YAML configuration)
            func: Python function to register as a tool
            
        Returns:
            Created tool object from Letta
        """
        return self.factory.register_tool(name, func)
    
    def build_from_file(self, yaml_file: str):
        """
        Build a Letta agent from a YAML configuration file.
        
        Args:
            yaml_file: Path to the YAML configuration file
            
        Returns:
            Created Letta agent object
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            ValueError: If the configuration is invalid or tools are missing
            RuntimeError: If agent creation fails
        """
        # Step 1: Parse YAML to configuration object
        config = self.parser.parse_file(yaml_file)
        
        # Step 2: Create agent using the factory
        return self.factory.create_agent(config)
    
    def build_from_dict(self, data: dict):
        """
        Build a Letta agent from a dictionary configuration.
        
        Args:
            data: Dictionary containing agent configuration
            
        Returns:
            Created Letta agent object
        """
        # Step 1: Parse dictionary to configuration object
        config = self.parser.parse_dict(data)
        
        # Step 2: Create agent using the factory
        return self.factory.create_agent(config)
    
    def send_message(self, agent_id: str, message: str):
        """
        Send a message to an agent.
        
        Args:
            agent_id: ID of the agent
            message: Message to send
            
        Returns:
            Agent response
        """
        return self.factory.send_message(agent_id, message)
    
    def get_client(self):
        """
        Get the underlying Letta client for advanced operations.
        
        Returns:
            Letta client instance
        """
        return self.factory.client