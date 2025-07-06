"""
Configuration classes for YAML agent definitions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, field_validator

class ToolParameter(BaseModel):
    type: str
    description: str
    enum: Optional[List[str]] = None

class ToolConfig(BaseModel):
    name: str
    description: str
    parameters: Optional[Dict[str, ToolParameter]] = {}

class MemoryConfig(BaseModel):
    human_name: str = "Human"
    persona_name: str = "Assistant"
    limit: int = 2000

class LLMConfig(BaseModel):
    model: str = "openai/gpt-4.1"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class AgentConfig(BaseModel):
    name: str
    description: Optional[str] = ""
    persona: str
    memory: MemoryConfig = MemoryConfig()
    tools: List[ToolConfig] = []
    llm: LLMConfig = LLMConfig()
    metadata: Dict[str, Any] = {}
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Agent name cannot be empty')
        return v.strip()
    
    @field_validator('persona')
    @classmethod
    def validate_persona(cls, v):
        if not v or not v.strip():
            raise ValueError('Agent persona cannot be empty')
        return v.strip()