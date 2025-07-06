import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock

@pytest.fixture
def sample_yaml_config():
    """Sample YAML configuration for testing."""
    return """
agent:
  name: "test_agent"
  description: "Test agent for unit tests"
  
  persona: |
    You are a test agent used for unit testing.
    Be helpful and concise.
  
  memory:
    human_name: "TestUser"
    persona_name: "TestBot"
    limit: 1000
  
  tools:
    - name: "test_tool"
      description: "A test tool"
      parameters:
        param1:
          type: "string"
          description: "Test parameter"
  
  llm:
    model: "openai/gpt-3.5-turbo"
    temperature: 0.5
    max_tokens: 500
  
  metadata:
    version: "1.0"
    test: true
"""

@pytest.fixture
def temp_yaml_file(sample_yaml_config):
    """Create a temporary YAML file with sample configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(sample_yaml_config)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)

@pytest.fixture
def mock_letta_client():
    """Mock Letta client for testing."""
    mock_client = Mock()
    
    # Mock tools
    mock_client.tools.create = MagicMock(return_value=Mock(id="tool-123"))
    
    # Mock agents
    mock_agent = Mock(id="agent-123", name="test_agent")
    mock_client.agents.create = MagicMock(return_value=mock_agent)
    
    # Mock messages
    mock_response = Mock(messages=["Hello, I'm a test response"])
    mock_client.agents.messages.create = MagicMock(return_value=mock_response)
    
    return mock_client

@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary for testing."""
    return {
        "agent": {
            "name": "dict_test_agent",
            "persona": "Test persona from dict",
            "memory": {
                "human_name": "DictUser",
                "persona_name": "DictBot",
                "limit": 1500
            },
            "tools": [],
            "llm": {
                "model": "openai/gpt-4",
                "temperature": 0.8
            }
        }
    }

def test_tool_function(param1: str) -> str:
    """Sample tool function for testing."""
    return f"Processed: {param1}"