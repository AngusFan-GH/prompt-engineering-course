"""
LLM客户端封装

提供统一的LLM调用接口，支持多种后端
"""

import os
import json
from typing import Any, Optional, Dict, List, Callable
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    usage: Dict[str, int]
    raw_response: Any = None


class LLMClient:
    """
    LLM客户端
    
    支持:
    - OpenAI API
    - 本地模型 (如 vLLM)
    - 模拟模式 (用于测试)
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str = None,
        base_url: str = "https://api.openai.com/v1",
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "mock")
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送对话请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            tools: 工具定义列表
            
        Returns:
            LLMResponse对象
        """
        # 如果是模拟模式
        if self.api_key == "mock":
            return self._mock_response(messages)
        
        # 实际API调用
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            
            request_kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
            
            if tools:
                request_kwargs["tools"] = tools
            
            response = await client.chat.completions.create(**request_kwargs)
            
            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                raw_response=response
            )
        except Exception as e:
            print(f"LLM API调用失败: {e}")
            return self._mock_response(messages)
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """
        模拟LLM响应
        
        用于测试和演示
        """
        last_message = messages[-1]["content"] if messages else ""
        
        # 简单规则匹配
        if "计划" in last_message or "plan" in last_message.lower():
            content = json.dumps({
                "goal": "模拟任务",
                "steps": [
                    {"id": 1, "description": "步骤1", "tool": "tool1", "parameters": {}, "depends_on": []}
                ]
            })
        elif "hello" in last_message.lower() or "你好" in last_message:
            content = "你好！有什么可以帮助你的吗？"
        else:
            content = "这是模拟的回复。实际使用时需要配置真实的API密钥。"
        
        return LLMResponse(
            content=content,
            model="mock-model",
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        )
    
    async def complete(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """
        补全请求 (非对话格式)
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)


# 全局客户端实例
_default_client: Optional[LLMClient] = None


def get_default_client() -> LLMClient:
    """获取默认LLM客户端"""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


def set_default_client(client: LLMClient):
    """设置默认LLM客户端"""
    global _default_client
    _default_client = client
