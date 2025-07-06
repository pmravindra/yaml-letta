import pytest
import yaml
import tempfile
import os
from yaml_letta.parser import YAMLAgentParser
from yaml_letta.config import AgentConfig

class TestYAMLAgentParser:
    def setup_method(self):
        self.parser = YAMLAgentParser()
    
    def test_parse_file_success(self, temp_yaml_file):
        """Test successful parsing of a valid YAML file."""
        config = self.parser.parse_file(temp_yaml_file)
        
        assert isinstance(config, AgentConfig)
        assert config.name == "test_agent"
        assert config.description == "Test agent for unit tests"
        assert "test agent" in config.persona
        assert config.memory.human_name == "TestUser"
        assert config.memory.persona_name == "TestBot"
        assert config.memory.limit == 1000
        assert len(config.tools) == 1
        assert config.tools[0].name == "test_tool"
        assert config.llm.model == "openai/gpt-3.5-turbo"
        assert config.llm.temperature == 0.5
        assert config.llm.max_tokens == 500
        assert config.metadata["version"] == "1.0"
        assert config.metadata["test"] is True
    
    def test_parse_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            self.parser.parse_file("/non/existent/file.yaml")
        assert "YAML file not found" in str(exc_info.value)
    
    def test_parse_file_invalid_yaml(self):
        """Test handling of malformed YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: ][")
            temp_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError) as exc_info:
                self.parser.parse_file(temp_path)
            assert "Invalid YAML format" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_parse_file_missing_agent_key(self):
        """Test handling of YAML without 'agent' key."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("other_key: value")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                self.parser.parse_file(temp_path)
            assert "YAML must contain an 'agent' key" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_parse_dict_success(self, sample_config_dict):
        """Test successful parsing of a valid dictionary."""
        config = self.parser.parse_dict(sample_config_dict)
        
        assert isinstance(config, AgentConfig)
        assert config.name == "dict_test_agent"
        assert config.persona == "Test persona from dict"
        assert config.memory.human_name == "DictUser"
        assert config.memory.persona_name == "DictBot"
        assert config.memory.limit == 1500
        assert len(config.tools) == 0
        assert config.llm.model == "openai/gpt-4"
        assert config.llm.temperature == 0.8
    
    def test_parse_dict_missing_agent_key(self):
        """Test handling of dictionary without 'agent' key."""
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_dict({"other_key": "value"})
        assert "YAML must contain an 'agent' key" in str(exc_info.value)
    
    def test_parse_dict_invalid_config(self):
        """Test handling of invalid agent configuration."""
        invalid_dict = {
            "agent": {
                # Missing required fields like 'name' and 'persona'
                "description": "Invalid agent"
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_dict(invalid_dict)
        assert "Invalid agent configuration" in str(exc_info.value)
    
    def test_parse_dict_with_minimal_config(self):
        """Test parsing with minimal required configuration."""
        minimal_dict = {
            "agent": {
                "name": "minimal_agent",
                "persona": "I am a minimal test agent"
            }
        }
        
        config = self.parser.parse_dict(minimal_dict)
        
        assert config.name == "minimal_agent"
        assert config.persona == "I am a minimal test agent"
        assert config.description == ""  # Default value
        assert config.memory.human_name == "Human"  # Default value
        assert config.memory.persona_name == "Assistant"  # Default value
        assert config.memory.limit == 2000  # Default value
        assert len(config.tools) == 0  # Default value
        assert config.llm.model == "openai/gpt-4.1"  # Default value
        assert config.llm.temperature == 0.7  # Default value
        assert config.llm.max_tokens is None  # Default value
        assert config.metadata == {}  # Default value