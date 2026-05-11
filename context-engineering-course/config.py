"""
config.py
配置文件
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "openai"  # openai, anthropic, ollama
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    
    def __post_init__(self):
        """自动从环境变量加载API Key"""
        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY") or self.api_key
        elif self.provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY") or self.api_key


@dataclass  
class RAGConfig:
    """RAG系统配置"""
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    embedding_dim: int = 384
    similarity_threshold: float = 0.5


@dataclass
class MemoryConfig:
    """记忆系统配置"""
    working_memory_limit: int = 10
    max_context_tokens: int = 60000
    relevance_threshold: float = 0.3
    context_decay: float = 0.95
