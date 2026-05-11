"""
配置文件
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "qwen"  # openai, anthropic, ollama, qwen
    model: str = "ClawClaw"  # qwen 默认模型
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 8192
