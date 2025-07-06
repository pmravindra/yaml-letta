import pytest
from pydantic import ValidationError
from yaml_letta.config import (
    ToolParameter, ToolConfig, MemoryConfig, 
    LLMConfig, AgentConfig
)

class TestToolParameter:
    def test_tool_parameter_creation(self):
        """Test creating a ToolParameter with all fields."""
        param = ToolParameter(
            type="string",
            description="Test parameter",
            enum=["option1", "option2"]
        )
        
        assert param.type == "string"
        assert param.description == "Test parameter"
        assert param.enum == ["option1", "option2"]
    
    def test_tool_parameter_without_enum(self):
        """Test creating a ToolParameter without enum field."""
        param = ToolParameter(
            type="integer",
            description="Count parameter"
        )
        
        assert param.type == "integer"
        assert param.description == "Count parameter"
        assert param.enum is None

class TestToolConfig:
    def test_tool_config_creation(self):
        """Test creating a ToolConfig with parameters."""
        param1 = ToolParameter(type="string", description="First param")
        param2 = ToolParameter(type="number", description="Second param")
        
        tool = ToolConfig(
            name="test_tool",
            description="A test tool",
            parameters={
                "param1": param1,
                "param2": param2
            }
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert len(tool.parameters) == 2
        assert tool.parameters["param1"].type == "string"
        assert tool.parameters["param2"].type == "number"
    
    def test_tool_config_without_parameters(self):
        """Test creating a ToolConfig without parameters."""
        tool = ToolConfig(
            name="simple_tool",
            description="A simple tool"
        )
        
        assert tool.name == "simple_tool"
        assert tool.description == "A simple tool"
        assert tool.parameters == {}

class TestMemoryConfig:
    def test_memory_config_defaults(self):
        """Test MemoryConfig with default values."""
        memory = MemoryConfig()
        
        assert memory.human_name == "Human"
        assert memory.persona_name == "Assistant"
        assert memory.limit == 2000
    
    def test_memory_config_custom_values(self):
        """Test MemoryConfig with custom values."""
        memory = MemoryConfig(
            human_name="Alice",
            persona_name="Bot",
            limit=5000
        )
        
        assert memory.human_name == "Alice"
        assert memory.persona_name == "Bot"
        assert memory.limit == 5000

class TestLLMConfig:
    def test_llm_config_defaults(self):
        """Test LLMConfig with default values."""
        llm = LLMConfig()
        
        assert llm.model == "openai/gpt-4.1"
        assert llm.temperature == 0.7
        assert llm.max_tokens is None
    
    def test_llm_config_custom_values(self):
        """Test LLMConfig with custom values."""
        llm = LLMConfig(
            model="anthropic/claude-3",
            temperature=0.3,
            max_tokens=2000
        )
        
        assert llm.model == "anthropic/claude-3"
        assert llm.temperature == 0.3
        assert llm.max_tokens == 2000

class TestAgentConfig:
    def test_agent_config_minimal(self):
        """Test AgentConfig with minimal required fields."""
        config = AgentConfig(
            name="test_agent",
            persona="I am a test agent"
        )
        
        assert config.name == "test_agent"
        assert config.description == ""
        assert config.persona == "I am a test agent"
        assert isinstance(config.memory, MemoryConfig)
        assert config.tools == []
        assert isinstance(config.llm, LLMConfig)
        assert config.metadata == {}
    
    def test_agent_config_full(self):
        """Test AgentConfig with all fields."""
        tool = ToolConfig(name="tool1", description="Test tool")
        memory = MemoryConfig(human_name="User", persona_name="AI", limit=3000)
        llm = LLMConfig(model="gpt-4", temperature=0.5)
        
        config = AgentConfig(
            name="full_agent",
            description="A fully configured agent",
            persona="I am a complete test agent",
            memory=memory,
            tools=[tool],
            llm=llm,
            metadata={"version": "2.0", "author": "test"}
        )
        
        assert config.name == "full_agent"
        assert config.description == "A fully configured agent"
        assert config.persona == "I am a complete test agent"
        assert config.memory.human_name == "User"
        assert len(config.tools) == 1
        assert config.tools[0].name == "tool1"
        assert config.llm.model == "gpt-4"
        assert config.metadata["version"] == "2.0"
    
    def test_agent_config_name_validation(self):
        """Test name validation - cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(name="", persona="Test persona")
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)
        assert any('cannot be empty' in str(error) for error in errors)
    
    def test_agent_config_name_whitespace_trimming(self):
        """Test that name is trimmed of whitespace."""
        config = AgentConfig(
            name="  test_agent  ",
            persona="Test persona"
        )
        
        assert config.name == "test_agent"
    
    def test_agent_config_persona_validation(self):
        """Test persona validation - cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(name="test_agent", persona="")
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('persona',) for error in errors)
        assert any('cannot be empty' in str(error) for error in errors)
    
    def test_agent_config_persona_whitespace_trimming(self):
        """Test that persona is trimmed of whitespace."""
        config = AgentConfig(
            name="test_agent",
            persona="  Test persona  "
        )
        
        assert config.persona == "Test persona"
    
    def test_agent_config_missing_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(name="test_agent")  # Missing persona
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('persona',) for error in errors)
        
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(persona="Test persona")  # Missing name
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)