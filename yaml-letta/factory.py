"""
Factory for creating Letta agents from configuration objects.
"""

import inspect
from typing import Dict, Any
from letta_client import Letta
from .config import AgentConfig

class LettaAgentFactory:
    """Factory that creates Letta agents from AgentConfig objects."""
    
    def __init__(self, token: str = None, base_url: str = None):
        """
        Initialize the Letta client.
        
        Args:
            token: Letta Cloud API token (for cloud usage)
            base_url: Base URL for self-hosted Letta server
        """
        if token:
            # Letta Cloud
            self.client = Letta(token=token)
        else:
            # Self-hosted
            self.client = Letta(base_url=base_url or "http://localhost:8283")
        
        self.created_tools = {}
        self.tool_registry = {}
    
    def register_tool(self, name: str, func: callable):
        """
        Register a tool function and create it in Letta.
        
        Args:
            name: Name of the tool
            func: Python function to register as a tool
            
        Returns:
            Created tool object from Letta
        """
        if name in self.created_tools:
            return self.created_tools[name]
        
        # Store the function for reference
        self.tool_registry[name] = func
        
        # Create tool in Letta
        try:
            tool = self.client.tools.create(
                source_code=inspect.getsource(func),
                name=name
            )
            self.created_tools[name] = tool
            return tool
        except Exception as e:
            raise RuntimeError(f"Failed to create tool '{name}': {e}")
    
    def create_agent(self, config: AgentConfig):
        """
        Create a Letta agent from an AgentConfig object.
        
        Args:
            config: AgentConfig object with agent configuration
            
        Returns:
            Created Letta agent object
            
        Raises:
            ValueError: If a required tool is not registered
            RuntimeError: If agent creation fails
        """
        # Validate that all required tools are registered
        tool_names = []
        for tool_config in config.tools:
            if tool_config.name not in self.created_tools:
                raise ValueError(
                    f"Tool '{tool_config.name}' not registered. "
                    f"Use register_tool() before creating the agent."
                )
            tool_names.append(tool_config.name)
        
        # Prepare memory blocks
        memory_blocks = [
            {
                "label": "human",
                "value": f"The human's name is {config.memory.human_name}."
            },
            {
                "label": "persona", 
                "value": config.persona
            }
        ]
        
        # Create agent using Letta client
        try:
            agent = self.client.agents.create(
                name=config.name,
                model=config.llm.model,
                embedding="openai/text-embedding-3-small",  # Default embedding
                memory_blocks=memory_blocks,
                tools=tool_names if tool_names else None,
                # Add other parameters as supported by Letta API
            )
            return agent
        except Exception as e:
            raise RuntimeError(f"Failed to create agent '{config.name}': {e}")
    
    def send_message(self, agent_id: str, message: str):
        """
        Send a message to an agent.
        
        Args:
            agent_id: ID of the agent
            message: Message to send
            
        Returns:
            Agent response
        """
        try:
            return self.client.agents.messages.create(
                agent_id=agent_id,
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": message}]
                }]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to send message to agent {agent_id}: {e}")