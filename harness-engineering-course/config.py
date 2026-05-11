"""
配置信息
"""

import os


# LLM配置
LLM_CONFIG = {
    "model": os.getenv("LLM_MODEL", "gpt-4o"),
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    "max_tokens": 4096,
    "temperature": 0.7,
}

# Agent配置
AGENT_CONFIG = {
    "max_iterations": 10,
    "max_replan": 2,
    "tool_timeout": 30,
}

# 上下文配置
CONTEXT_CONFIG = {
    "max_context_length": 128000,
    "reserved_tokens": 2000,
    "compression_threshold": 0.7,
}

# 验证配置
VALIDATION_CONFIG = {
    "enable_validation": True,
    "fail_fast": False,
    "max_validation_errors": 5,
}
