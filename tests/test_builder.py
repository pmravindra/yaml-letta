import pytest
from unittest.mock import Mock, MagicMock, patch
from yaml_letta.builder import YAMLAgentBuilder
from yaml_letta.config import AgentConfig

class TestYAMLAgentBuilder:
    @patch('yaml_letta.builder.LettaAgentFactory')
    @patch('yaml_letta.builder.YAMLAgentParser')
    def test_builder_init(self, mock_parser_class, mock_factory_class):
        """Test builder initialization."""
        mock_parser = Mock()
        mock_factory = Mock()
        mock_parser_class.return_value = mock_parser
        mock_factory_class.return_value = mock_factory
        
        # Test with token
        builder = YAMLAgentBuilder(token="test-token")
        
        mock_parser_class.assert_called_once()
        mock_factory_class.assert_called_once_with(token="test-token", base_url=None)
        assert builder.parser == mock_parser
        assert builder.factory == mock_factory
        
        # Reset mocks
        mock_parser_class.reset_mock()
        mock_factory_class.reset_mock()
        
        # Test with base_url
        builder = YAMLAgentBuilder(base_url="http://custom:8080")
        
        mock_parser_class.assert_called_once()
        mock_factory_class.assert_called_once_with(token=None, base_url="http://custom:8080")
    
    def test_register_tool(self):
        """Test tool registration delegation."""
        builder = YAMLAgentBuilder()
        builder.factory = Mock()
        mock_tool = Mock(id="tool-123")
        builder.factory.register_tool.return_value = mock_tool
        
        def test_func():
            pass
        
        result = builder.register_tool("test_tool", test_func)
        
        assert result == mock_tool
        builder.factory.register_tool.assert_called_once_with("test_tool", test_func)
    
    def test_build_from_file_success(self, temp_yaml_file):
        """Test successful agent building from file."""
        builder = YAMLAgentBuilder()
        
        # Mock parser and factory
        mock_config = Mock(spec=AgentConfig)
        builder.parser = Mock()
        builder.parser.parse_file.return_value = mock_config
        
        mock_agent = Mock(id="agent-123")
        builder.factory = Mock()
        builder.factory.create_agent.return_value = mock_agent
        
        # Build agent
        agent = builder.build_from_file(temp_yaml_file)
        
        assert agent == mock_agent
        builder.parser.parse_file.assert_called_once_with(temp_yaml_file)
        builder.factory.create_agent.assert_called_once_with(mock_config)
    
    def test_build_from_file_parse_error(self):
        """Test handling of parse errors when building from file."""
        builder = YAMLAgentBuilder()
        builder.parser = Mock()
        builder.parser.parse_file.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError) as exc_info:
            builder.build_from_file("missing.yaml")
        
        assert "File not found" in str(exc_info.value)
    
    def test_build_from_file_factory_error(self, temp_yaml_file):
        """Test handling of factory errors when building from file."""
        builder = YAMLAgentBuilder()
        
        mock_config = Mock(spec=AgentConfig)
        builder.parser = Mock()
        builder.parser.parse_file.return_value = mock_config
        
        builder.factory = Mock()
        builder.factory.create_agent.side_effect = ValueError("Tool not registered")
        
        with pytest.raises(ValueError) as exc_info:
            builder.build_from_file(temp_yaml_file)
        
        assert "Tool not registered" in str(exc_info.value)
    
    def test_build_from_dict_success(self, sample_config_dict):
        """Test successful agent building from dictionary."""
        builder = YAMLAgentBuilder()
        
        # Mock parser and factory
        mock_config = Mock(spec=AgentConfig)
        builder.parser = Mock()
        builder.parser.parse_dict.return_value = mock_config
        
        mock_agent = Mock(id="agent-456")
        builder.factory = Mock()
        builder.factory.create_agent.return_value = mock_agent
        
        # Build agent
        agent = builder.build_from_dict(sample_config_dict)
        
        assert agent == mock_agent
        builder.parser.parse_dict.assert_called_once_with(sample_config_dict)
        builder.factory.create_agent.assert_called_once_with(mock_config)
    
    def test_build_from_dict_parse_error(self):
        """Test handling of parse errors when building from dict."""
        builder = YAMLAgentBuilder()
        builder.parser = Mock()
        builder.parser.parse_dict.side_effect = ValueError("Invalid configuration")
        
        with pytest.raises(ValueError) as exc_info:
            builder.build_from_dict({"invalid": "config"})
        
        assert "Invalid configuration" in str(exc_info.value)
    
    def test_send_message(self):
        """Test message sending delegation."""
        builder = YAMLAgentBuilder()
        builder.factory = Mock()
        mock_response = Mock(messages=["Response"])
        builder.factory.send_message.return_value = mock_response
        
        result = builder.send_message("agent-123", "Hello")
        
        assert result == mock_response
        builder.factory.send_message.assert_called_once_with("agent-123", "Hello")
    
    def test_get_client(self):
        """Test getting the underlying Letta client."""
        builder = YAMLAgentBuilder()
        mock_client = Mock()
        builder.factory = Mock()
        builder.factory.client = mock_client
        
        client = builder.get_client()
        
        assert client == mock_client
    
    def test_end_to_end_workflow(self):
        """Test a complete workflow from building to messaging."""
        builder = YAMLAgentBuilder()
        
        # Setup mocks
        mock_config = Mock(spec=AgentConfig, name="test_agent")
        builder.parser = Mock()
        builder.parser.parse_dict.return_value = mock_config
        
        mock_agent = Mock(id="agent-789", name="test_agent")
        builder.factory = Mock()
        builder.factory.create_agent.return_value = mock_agent
        
        mock_response = Mock(messages=["Hello! How can I help?"])
        builder.factory.send_message.return_value = mock_response
        
        # Register a tool
        def helper_tool():
            pass
        
        builder.register_tool("helper", helper_tool)
        
        # Build agent from dict
        agent = builder.build_from_dict({
            "agent": {
                "name": "test_agent",
                "persona": "Helpful assistant"
            }
        })
        
        # Send message
        response = builder.send_message(agent.id, "Hello")
        
        # Verify workflow
        assert agent.id == "agent-789"
        assert response.messages == ["Hello! How can I help?"]
        builder.factory.register_tool.assert_called_once_with("helper", helper_tool)
        builder.parser.parse_dict.assert_called_once()
        builder.factory.create_agent.assert_called_once_with(mock_config)
        builder.factory.send_message.assert_called_once_with("agent-789", "Hello")