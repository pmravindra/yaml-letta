# YAML-Letta

[![Tests](https://github.com/pmravindra/yaml-letta/actions/workflows/tests.yml/badge.svg)](https://github.com/pmravindra/yaml-letta/actions/workflows/tests.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

YAML-driven agent configuration for Letta. Define your Letta agents using simple YAML files and create them with a single function call.

## Installation

```bash
pip install yaml-letta
```

## Quick Start

### 1. Define your agent in YAML

Create a file `my_agent.yaml`:

```yaml
agent:
  name: "customer_support_agent"
  persona: "You are a helpful customer support representative."
  
  memory:
    human_name: "Customer"
    persona_name: "SupportBot"
  
  tools:
    - name: "search_knowledge_base"
      description: "Search internal knowledge base"
  
  llm:
    model: "openai/gpt-4.1"
    temperature: 0.7
```

### 2. Create the agent

```python
import yaml_letta

# Simple one-liner (no custom tools)
agent = yaml_letta.create_agent_from_yaml("my_agent.yaml")

# With custom tools
builder = yaml_letta.create_builder()

def search_knowledge_base(query: str) -> str:
    return f"Search results for: {query}"

builder.register_tool("search_knowledge_base", search_knowledge_base)
agent = builder.build_from_file("my_agent.yaml")
```

## Features

- **Simple YAML Configuration**: Define agents declaratively
- **Tool Integration**: Register Python functions as agent tools
- **Validation**: Automatic validation of configurations
- **Letta Cloud & Self-hosted**: Works with both Letta Cloud and self-hosted servers
- **Type Safety**: Full type hints and validation with Pydantic

## Configuration Reference

### Agent Configuration

```yaml
agent:
  name: "agent_name"              # Required: Agent identifier
  description: "Agent description" # Optional: Human-readable description
  persona: "Agent personality"     # Required: Agent's persona/system prompt
  
  memory:                         # Optional: Memory configuration
    human_name: "Human"           # Default: "Human"
    persona_name: "Assistant"     # Default: "Assistant"
    limit: 2000                   # Default: 2000
  
  tools:                          # Optional: List of tools
    - name: "tool_name"
      description: "Tool description"
      parameters:                 # Optional: Parameter definitions
        param_name:
          type: "string"
          description: "Parameter description"
          enum: ["option1", "option2"]  # Optional: Allowed values
  
  llm:                           # Optional: LLM configuration
    model: "openai/gpt-4.1"      # Default: "openai/gpt-4.1"
    temperature: 0.7             # Default: 0.7
    max_tokens: 1000             # Optional
  
  metadata:                      # Optional: Custom metadata
    version: "1.0"
    team: "engineering"
```

## API Reference

### Main Functions

```python
# Simple agent creation
yaml_letta.create_agent_from_yaml(yaml_file, token=None, base_url=None)

# Advanced usage with tools
builder = yaml_letta.create_builder(token=None, base_url=None)
builder.register_tool(name, function)
agent = builder.build_from_file(yaml_file)
```

### Connection Options

```python
# Letta Cloud
agent = yaml_letta.create_agent_from_yaml("agent.yaml", token="your_api_key")

# Self-hosted Letta server
agent = yaml_letta.create_agent_from_yaml("agent.yaml", base_url="http://localhost:8283")
```

## Examples

### Basic Agent

```python
import yaml_letta

# Create agent from YAML
agent = yaml_letta.create_agent_from_yaml("basic_agent.yaml")
print(f"Created agent: {agent.id}")
```

### Agent with Custom Tools

```python
import yaml_letta

# Create builder
builder = yaml_letta.create_builder()

# Define tools
def search_docs(query: str) -> str:
    """Search documentation for relevant information."""
    return f"Documentation results for: {query}"

def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified recipient."""
    return f"Email sent to {to} with subject: {subject}"

# Register tools
builder.register_tool("search_docs", search_docs)
builder.register_tool("send_email", send_email)

# Build agent
agent = builder.build_from_file("agent_with_tools.yaml")

# Interact with agent
response = builder.send_message(agent.id, "Help me find documentation about APIs")
print(response)
```

### Configuration from Dictionary

```python
import yaml_letta

config = {
    "agent": {
        "name": "my_agent",
        "persona": "You are a helpful assistant.",
        "llm": {"model": "openai/gpt-4.1"}
    }
}

builder = yaml_letta.create_builder()
agent = builder.build_from_dict(config)
```

## Error Handling

The library provides detailed error messages for common issues:

```python
try:
    agent = yaml_letta.create_agent_from_yaml("invalid.yaml")
except FileNotFoundError:
    print("YAML file not found")
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Agent creation failed: {e}")
```

## Testing

### Using Docker (Recommended)

```bash
# Run all tests
make test

# Interactive development shell
make test-interactive

# Clean up Docker resources
make clean
```

### Local Testing

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run tests
pytest tests/ -v
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Letta](https://github.com/letta-ai/letta) - The stateful agents framework
- [PraisonAI](https://github.com/MervinPraison/PraisonAI) - Inspiration for YAML-driven agent configuration