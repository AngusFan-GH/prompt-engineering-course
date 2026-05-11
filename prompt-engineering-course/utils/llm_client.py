"""
统一 LLM 调用客户端
支持：OpenAI, Anthropic, Ollama, Qwen
"""

import os
import re
import warnings
from typing import List, Dict, Optional, Any
import requests

from config import LLMConfig


class LLMClient:
    """统一 LLM 调用客户端"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._load_api_key()

    def _load_api_key(self):
        """从环境变量加载 API 密钥"""
        if self.config.provider == "openai":
            self.config.api_key = os.getenv("OPENAI_API_KEY") or self.config.api_key
            self.config.base_url = os.getenv("OPENAI_BASE_URL") or self.config.base_url
        elif self.config.provider == "anthropic":
            self.config.api_key = os.getenv("ANTHROPIC_API_KEY") or self.config.api_key
        elif self.config.provider == "qwen":
            self.config.api_key = os.getenv("QWEN_API_KEY") or self.config.api_key
            self.config.base_url = os.getenv("QWEN_BASE_URL") or self.config.base_url

    def _temperature(self, temperature: Optional[float]) -> float:
        """保留 temperature=0 这种有效配置。"""
        return self.config.temperature if temperature is None else temperature

    def _clean_content(self, content: Optional[str], finish_reason: Optional[str] = None) -> str:
        """清理 Qwen/ClawClaw 可能混入正文的思考标签，并提示截断。"""
        if content is None:
            content = ""

        content = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL).strip()

        if finish_reason == "length":
            warnings.warn(
                "模型输出因 max_tokens 不足被截断。请调大 max_tokens，或关闭 thinking/reasoning。",
                RuntimeWarning,
                stacklevel=2,
            )

        return content

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
        elif self.config.provider == "qwen":
            return self._call_qwen(messages, temperature, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")

    def _call_openai(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用 OpenAI API"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

        client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)

        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self._temperature(temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        choice = response.choices[0]
        return self._clean_content(choice.message.content, choice.finish_reason)

    def _call_anthropic(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用 Anthropic API"""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("请安装 anthropic: pip install anthropic")

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
            temperature=self._temperature(temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        return response.content[0].text

    def _call_ollama(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用 Ollama 本地模型"""
        url = (self.config.base_url or "http://localhost:11434") + "/api/chat"

        response = requests.post(url, json={
            "model": self.config.model,
            "messages": messages,
            "temperature": self._temperature(temperature),
            "stream": False
        })
        response.raise_for_status()
        return response.json()["message"]["content"]

    def _call_qwen(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """
        调用 Qwen API (OpenAI 兼容格式)

        Qwen API 使用 OpenAI 兼容的接口
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

        # Qwen 使用 OpenAI 兼容的 API
        client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)

        extra_body = kwargs.get(
            "extra_body",
            {"chat_template_kwargs": {"enable_thinking": False}},
        )

        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self._temperature(temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            extra_body=extra_body,
        )
        choice = response.choices[0]
        return self._clean_content(choice.message.content, choice.finish_reason)


# 辅助函数
def estimate_tokens(text: str) -> int:
    """估算 token 数量（中英文混合）"""
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.5 + other_chars * 0.25)
