import pytest
from unittest.mock import Mock, MagicMock, patch
import inspect
from yaml_letta.factory import LettaAgentFactory
from yaml_letta.config import AgentConfig, ToolConfig, MemoryConfig, LLMConfig

class TestLettaAgentFactory:
    @patch('yaml_letta.factory.Letta')
    def test_factory_init_with_token(self, mock_letta_class):
        """Test factory initialization with token (cloud mode)."""
        mock_client = Mock()
        mock_letta_class.return_value = mock_client
        
        factory = LettaAgentFactory(token="test-token")
        
        mock_letta_class.assert_called_once_with(token="test-token")
        assert factory.client == mock_client
        assert factory.created_tools == {}
        assert factory.tool_registry == {}
    
    @patch('yaml_letta.factory.Letta')
    def test_factory_init_without_token(self, mock_letta_class):
        """Test factory initialization without token (self-hosted mode)."""
        mock_client = Mock()
        mock_letta_class.return_value = mock_client
        
        factory = LettaAgentFactory()
        
        mock_letta_class.assert_called_once_with(base_url="http://localhost:8283")
        assert factory.client == mock_client
    
    @patch('yaml_letta.factory.Letta')
    def test_factory_init_with_custom_base_url(self, mock_letta_class):
        """Test factory initialization with custom base URL."""
        mock_client = Mock()
        mock_letta_class.return_value = mock_client
        
        factory = LettaAgentFactory(base_url="http://custom:8080")
        
        mock_letta_class.assert_called_once_with(base_url="http://custom:8080")
        assert factory.client == mock_client
    
    def test_register_tool_success(self, mock_letta_client):
        """Test successful tool registration."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        
        def test_func(x: int) -> int:
            return x * 2
        
        tool = factory.register_tool("test_tool", test_func)
        
        assert tool.id == "tool-123"
        assert "test_tool" in factory.created_tools
        assert factory.created_tools["test_tool"] == tool
        assert "test_tool" in factory.tool_registry
        assert factory.tool_registry["test_tool"] == test_func
        
        # Verify the tool creation call
        mock_letta_client.tools.create.assert_called_once()
        call_args = mock_letta_client.tools.create.call_args
        assert call_args.kwargs['name'] == "test_tool"
        assert "def test_func" in call_args.kwargs['source_code']
    
    def test_register_tool_already_exists(self, mock_letta_client):
        """Test registering a tool that already exists."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        
        def test_func():
            pass
        
        # First registration
        tool1 = factory.register_tool("existing_tool", test_func)
        
        # Second registration with same name
        tool2 = factory.register_tool("existing_tool", test_func)
        
        # Should return the same tool without creating a new one
        assert tool1 == tool2
        assert mock_letta_client.tools.create.call_count == 1
    
    def test_register_tool_failure(self, mock_letta_client):
        """Test tool registration failure."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        mock_letta_client.tools.create.side_effect = Exception("API error")
        
        def test_func():
            pass
        
        with pytest.raises(RuntimeError) as exc_info:
            factory.register_tool("failing_tool", test_func)
        
        assert "Failed to create tool 'failing_tool'" in str(exc_info.value)
        assert "API error" in str(exc_info.value)
    
    def test_create_agent_success(self, mock_letta_client):
        """Test successful agent creation."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        
        # Pre-register a tool
        factory.created_tools["test_tool"] = Mock(id="tool-123")
        
        config = AgentConfig(
            name="test_agent",
            persona="Test persona",
            memory=MemoryConfig(human_name="TestUser", persona_name="TestBot"),
            tools=[ToolConfig(name="test_tool", description="Test tool")],
            llm=LLMConfig(model="gpt-4", temperature=0.5)
        )
        
        agent = factory.create_agent(config)
        
        assert agent.id == "agent-123"
        assert agent == mock_letta_client.agents.create.return_value
        
        # Verify the agent creation call
        mock_letta_client.agents.create.assert_called_once()
        call_args = mock_letta_client.agents.create.call_args
        assert call_args.kwargs['name'] == "test_agent"
        assert call_args.kwargs['model'] == "gpt-4"
        assert call_args.kwargs['tools'] == ["test_tool"]
        
        # Check memory blocks
        memory_blocks = call_args.kwargs['memory_blocks']
        assert len(memory_blocks) == 2
        assert memory_blocks[0]['label'] == "human"
        assert "TestUser" in memory_blocks[0]['value']
        assert memory_blocks[1]['label'] == "persona"
        assert memory_blocks[1]['value'] == "Test persona"
    
    def test_create_agent_missing_tool(self, mock_letta_client):
        """Test agent creation with unregistered tool."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        
        config = AgentConfig(
            name="test_agent",
            persona="Test persona",
            tools=[ToolConfig(name="unregistered_tool", description="Not registered")]
        )
        
        with pytest.raises(ValueError) as exc_info:
            factory.create_agent(config)
        
        assert "Tool 'unregistered_tool' not registered" in str(exc_info.value)
        assert "Use register_tool()" in str(exc_info.value)
    
    def test_create_agent_no_tools(self, mock_letta_client):
        """Test agent creation without tools."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        
        config = AgentConfig(
            name="no_tools_agent",
            persona="Agent without tools"
        )
        
        agent = factory.create_agent(config)
        
        assert agent.id == "agent-123"
        
        # Verify tools parameter is None when no tools
        call_args = mock_letta_client.agents.create.call_args
        assert call_args.kwargs['tools'] is None
    
    def test_create_agent_failure(self, mock_letta_client):
        """Test agent creation failure."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        mock_letta_client.agents.create.side_effect = Exception("Creation failed")
        
        config = AgentConfig(
            name="failing_agent",
            persona="Test persona"
        )
        
        with pytest.raises(RuntimeError) as exc_info:
            factory.create_agent(config)
        
        assert "Failed to create agent 'failing_agent'" in str(exc_info.value)
        assert "Creation failed" in str(exc_info.value)
    
    def test_send_message_success(self, mock_letta_client):
        """Test successful message sending."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        
        response = factory.send_message("agent-123", "Hello")
        
        assert response.messages == ["Hello, I'm a test response"]
        
        # Verify the message call
        mock_letta_client.agents.messages.create.assert_called_once()
        call_args = mock_letta_client.agents.messages.create.call_args
        assert call_args.kwargs['agent_id'] == "agent-123"
        messages = call_args.kwargs['messages']
        assert len(messages) == 1
        assert messages[0]['role'] == "user"
        assert messages[0]['content'][0]['type'] == "text"
        assert messages[0]['content'][0]['text'] == "Hello"
    
    def test_send_message_failure(self, mock_letta_client):
        """Test message sending failure."""
        factory = LettaAgentFactory()
        factory.client = mock_letta_client
        mock_letta_client.agents.messages.create.side_effect = Exception("Message failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            factory.send_message("agent-123", "Hello")
        
        assert "Failed to send message to agent agent-123" in str(exc_info.value)
        assert "Message failed" in str(exc_info.value)