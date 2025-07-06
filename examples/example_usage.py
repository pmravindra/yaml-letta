"""
Example usage of yaml-letta library.
"""

import yaml_letta

# Method 1: Simple one-line agent creation
def example_simple():
    """Create an agent with one line (no custom tools)."""
    # For Letta Cloud
    agent = yaml_letta.create_agent_from_yaml(
        "basic_agent.yaml", 
        token="your_letta_api_key"
    )
    
    # For self-hosted
    # agent = yaml_letta.create_agent_from_yaml(
    #     "basic_agent.yaml",
    #     base_url="http://localhost:8283"
    # )
    
    print(f"Created agent: {agent.id}")

# Method 2: With custom tools
def example_with_tools():
    """Create an agent with custom tools registered."""
    
    # Create builder
    builder = yaml_letta.create_builder(base_url="http://localhost:8283")
    
    # Define and register custom tools
    def search_knowledge_base(query: str) -> str:
        """Search the internal knowledge base for relevant information."""
        # Your implementation here
        return f"Found relevant articles about: {query}"
    
    def create_support_ticket(title: str, priority: str) -> str:
        """Create a new support ticket with given title and priority."""
        # Your implementation here
        ticket_id = f"TICKET-{hash(title) % 10000:04d}"
        return f"Created support ticket {ticket_id}: {title} (Priority: {priority})"
    
    # Register tools (names must match YAML)
    builder.register_tool("search_knowledge_base", search_knowledge_base)
    builder.register_tool("create_support_ticket", create_support_ticket)
    
    # Build agent from YAML
    agent = builder.build_from_file("basic_agent.yaml")
    
    # Interact with the agent
    response = builder.send_message(
        agent.id, 
        "Hi, I'm having trouble logging into my account. Can you help?"
    )
    
    print(f"Agent response: {response}")

# Method 3: Using dictionary instead of file
def example_from_dict():
    """Create an agent from a dictionary configuration."""
    
    config = {
        "agent": {
            "name": "simple_agent",
            "persona": "You are a helpful assistant.",
            "memory": {
                "human_name": "User",
                "persona_name": "Assistant"
            },
            "llm": {
                "model": "openai/gpt-4.1",
                "temperature": 0.5
            }
        }
    }
    
    builder = yaml_letta.create_builder(base_url="http://localhost:8283")
    agent = builder.build_from_dict(config)
    
    print(f"Created agent from dict: {agent.id}")

if __name__ == "__main__":
    # Run examples
    print("Example 1: Simple agent creation")
    example_simple()
    
    print("\nExample 2: Agent with custom tools")
    example_with_tools()
    
    print("\nExample 3: Agent from dictionary")
    example_from_dict()