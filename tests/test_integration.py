import pytest
import tempfile
import os
import yaml
from unittest.mock import Mock, patch
from yaml_letta.builder import YAMLAgentBuilder
from yaml_letta.config import AgentConfig, ToolConfig

class TestIntegration:
    """Integration tests for the entire yaml-letta workflow."""
    
    @pytest.fixture
    def complex_yaml_config(self):
        """Complex YAML configuration for integration testing."""
        return """
agent:
  name: "integration_test_agent"
  description: "Agent for integration testing"
  
  persona: |
    You are an integration test agent designed to verify
    the yaml-letta library functionality. You have access
    to multiple tools and should use them appropriately.
  
  memory:
    human_name: "Tester"
    persona_name: "TestAgent"
    limit: 3000
  
  tools:
    - name: "calculate"
      description: "Perform calculations"
      parameters:
        expression:
          type: "string"
          description: "Mathematical expression to evaluate"
    
    - name: "get_data"
      description: "Retrieve data from storage"
      parameters:
        key:
          type: "string"
          description: "Key to retrieve data for"
        default_value:
          type: "string"
          description: "Default if key not found"
  
  llm:
    model: "openai/gpt-4"
    temperature: 0.3
    max_tokens: 1500
  
  metadata:
    environment: "test"
    capabilities: ["math", "data_retrieval"]
    version: "2.0"
"""
    
    @pytest.fixture
    def mock_tools(self):
        """Mock tool functions for testing."""
        def calculate(expression: str) -> str:
            try:
                result = eval(expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def get_data(key: str, default_value: str = None) -> str:
            mock_storage = {
                "user_count": "42",
                "api_version": "1.0.0",
                "status": "active"
            }
            return mock_storage.get(key, default_value or "Not found")
        
        return {
            "calculate": calculate,
            "get_data": get_data
        }
    
    @patch('yaml_letta.factory.Letta')
    def test_complete_workflow(self, mock_letta_class, complex_yaml_config, mock_tools):
        """Test the complete workflow from YAML to agent interaction."""
        # Setup mock Letta client
        mock_client = Mock()
        mock_letta_class.return_value = mock_client
        
        # Mock tool creation
        mock_client.tools.create.side_effect = [
            Mock(id="tool-calc", name="calculate"),
            Mock(id="tool-data", name="get_data")
        ]
        
        # Mock agent creation
        mock_agent = Mock(id="agent-integration", name="integration_test_agent")
        mock_client.agents.create.return_value = mock_agent
        
        # Mock message responses
        mock_client.agents.messages.create.side_effect = [
            Mock(messages=["I'll calculate that for you."]),
            Mock(messages=["The user count is 42."]),
            Mock(messages=["The result is 150."])
        ]
        
        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(complex_yaml_config)
            yaml_path = f.name
        
        try:
            # Initialize builder
            builder = YAMLAgentBuilder(token="test-token")
            
            # Register tools
            for tool_name, tool_func in mock_tools.items():
                builder.register_tool(tool_name, tool_func)
            
            # Build agent from YAML
            agent = builder.build_from_file(yaml_path)
            
            # Verify agent creation
            assert agent.id == "agent-integration"
            assert agent == mock_agent
            
            # Test sending messages
            response1 = builder.send_message(agent.id, "Calculate 5 + 3")
            assert "calculate" in response1.messages[0].lower()
            
            response2 = builder.send_message(agent.id, "What's the user count?")
            assert "42" in response2.messages[0]
            
            response3 = builder.send_message(agent.id, "Calculate 10 * 15")
            assert "150" in response3.messages[0]
            
            # Verify tool registrations
            assert mock_client.tools.create.call_count == 2
            
            # Verify agent creation parameters
            agent_create_call = mock_client.agents.create.call_args
            assert agent_create_call.kwargs['name'] == "integration_test_agent"
            assert agent_create_call.kwargs['model'] == "openai/gpt-4"
            assert agent_create_call.kwargs['tools'] == ["calculate", "get_data"]
            
            memory_blocks = agent_create_call.kwargs['memory_blocks']
            assert any("Tester" in block['value'] for block in memory_blocks)
            assert any("integration test agent" in block['value'] for block in memory_blocks)
            
        finally:
            os.unlink(yaml_path)
    
    @patch('yaml_letta.factory.Letta')
    def test_minimal_configuration_workflow(self, mock_letta_class):
        """Test workflow with minimal configuration."""
        mock_client = Mock()
        mock_letta_class.return_value = mock_client
        
        mock_agent = Mock(id="agent-minimal", name="minimal_agent")
        mock_client.agents.create.return_value = mock_agent
        
        mock_client.agents.messages.create.return_value = Mock(
            messages=["Hello! I'm a minimal agent."]
        )
        
        minimal_config = {
            "agent": {
                "name": "minimal_agent",
                "persona": "I am a minimal test agent with basic functionality."
            }
        }
        
        # Build and test minimal agent
        builder = YAMLAgentBuilder(base_url="http://localhost:8283")
        agent = builder.build_from_dict(minimal_config)
        
        assert agent.id == "agent-minimal"
        
        response = builder.send_message(agent.id, "Hello")
        assert "minimal agent" in response.messages[0].lower()
        
        # Verify defaults were used
        agent_create_call = mock_client.agents.create.call_args
        assert agent_create_call.kwargs['model'] == "openai/gpt-4.1"  # Default
        assert agent_create_call.kwargs['tools'] is None  # No tools
    
    @patch('yaml_letta.factory.Letta')
    def test_error_handling_workflow(self, mock_letta_class):
        """Test error handling throughout the workflow."""
        mock_client = Mock()
        mock_letta_class.return_value = mock_client
        
        builder = YAMLAgentBuilder()
        
        # Test 1: Invalid YAML file
        with pytest.raises(FileNotFoundError):
            builder.build_from_file("non_existent.yaml")
        
        # Test 2: Invalid configuration
        invalid_config = {"agent": {"description": "Missing required fields"}}
        with pytest.raises(ValueError) as exc_info:
            builder.build_from_dict(invalid_config)
        assert "Invalid agent configuration" in str(exc_info.value)
        
        # Test 3: Unregistered tool
        config_with_tool = {
            "agent": {
                "name": "tool_agent",
                "persona": "Agent with unregistered tool",
                "tools": [{"name": "unregistered", "description": "Not registered"}]
            }
        }
        
        # Parse should succeed
        parsed_config = builder.parser.parse_dict(config_with_tool)
        
        # But agent creation should fail
        with pytest.raises(ValueError) as exc_info:
            builder.factory.create_agent(parsed_config)
        assert "Tool 'unregistered' not registered" in str(exc_info.value)
        
        # Test 4: API failure during agent creation
        mock_client.agents.create.side_effect = Exception("API connection failed")
        
        simple_config = {
            "agent": {
                "name": "failing_agent",
                "persona": "This agent will fail to create"
            }
        }
        
        with pytest.raises(RuntimeError) as exc_info:
            builder.build_from_dict(simple_config)
        assert "Failed to create agent" in str(exc_info.value)
    
    def test_yaml_validation_integration(self, complex_yaml_config):
        """Test that YAML validation catches common errors."""
        builder = YAMLAgentBuilder()
        
        # Test various invalid YAML configurations
        invalid_yamls = [
            # Missing agent key
            "other_key: value",
            
            # Empty agent name
            """
agent:
  name: ""
  persona: "Test"
""",
            
            # Invalid tool parameter type
            """
agent:
  name: "test"
  persona: "Test"
  tools:
    - name: "tool"
      description: "desc"
      parameters:
        param:
          type: 123  # Should be string
          description: "desc"
""",
        ]
        
        for yaml_content in invalid_yamls:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_content)
                temp_path = f.name
            
            try:
                with pytest.raises((ValueError, yaml.YAMLError)):
                    builder.build_from_file(temp_path)
            finally:
                os.unlink(temp_path)