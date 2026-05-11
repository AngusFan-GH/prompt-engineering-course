"""
examples/01_basic_chat.py
基础对话示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient


def basic_chat_example():
    """最基础的对话调用"""
    
    config = LLMConfig(
        provider="minimax",
        model="MiniMax-M2.7",
        temperature=0.7
    )
    
    client = LLMClient(config)
    
    messages = [
        {"role": "user", "content": "你好，介绍一下Python的列表推导式"}
    ]
    
    response = client.chat(messages)
    print("=" * 50)
    print("基础对话示例")
    print("=" * 50)
    print(f"问题: {messages[0]['content']}")
    print(f"\n回答:\n{response}")


def simple_prompt_template():
    """简单的Prompt模板"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    # 模板化Prompt
    template = """请用{style}风格介绍{topic}。

要求：
- 长度：{length}
- 目标读者：{audience}
"""
    
    prompt = template.format(
        style="技术科普",
        topic="Python装饰器",
        length="200字以内",
        audience="有编程基础的初学者"
    )
    
    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages)
    
    print("\n" + "=" * 50)
    print("Prompt模板示例")
    print("=" * 50)
    print(f"问题: {prompt}")
    print(f"\n回答:\n{response}")


if __name__ == "__main__":
    basic_chat_example()
    simple_prompt_template()
