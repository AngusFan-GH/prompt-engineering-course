"""
统一LLM调用客户端
"""

import os
from typing import List, Dict, Optional, Any

import sys
sys.path.append("..")
from config import LLMConfig


class LLMClient:
    """统一LLM调用客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._load_api_key()
    
    def _load_api_key(self):
        """从环境变量加载API密钥"""
        if self.config.provider == "openai":
            self.config.api_key = os.getenv("OPENAI_API_KEY") or self.config.api_key
        elif self.config.provider == "anthropic":
            self.config.api_key = os.getenv("ANTHROPIC_API_KEY") or self.config.api_key
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: Optional[float] = None,
             **kwargs) -> str:
        """
        统一聊天接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            **kwargs: 其他参数
        
        Returns:
            str: 模型回复
        """
        if self.config.provider == "openai":
            return self._call_openai(messages, temperature, **kwargs)
        elif self.config.provider == "anthropic":
            return self._call_anthropic(messages, temperature, **kwargs)
        elif self.config.provider == "ollama":
            return self._call_ollama(messages, temperature, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")
    
    def _call_openai(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用OpenAI API"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装openai: pip install openai")
        
        client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        
        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用Anthropic API"""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("请安装anthropic: pip install anthropic")
        
        client = Anthropic(api_key=self.config.api_key)
        
        # 转换消息格式
        system = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered_messages.append(msg)
        
        response = client.messages.create(
            model=self.config.model,
            system=system,
            messages=filtered_messages,
            temperature=temperature or self.config.temperature,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        return response.content[0].text
    
    def _call_ollama(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用Ollama本地模型"""
        import requests
        
        url = (self.config.base_url or "http://localhost:11434") + "/api/chat"
        
        response = requests.post(url, json={
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "stream": False
        })
        response.raise_for_status()
        return response.json()["message"]["content"]


# 辅助函数
def estimate_tokens(text: str) -> int:
    """估算token数量（中英文混合）"""
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.5 + other_chars * 0.25)
