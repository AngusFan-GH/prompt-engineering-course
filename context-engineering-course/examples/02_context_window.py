"""
examples/02_context_window.py
上下文窗口管理示例
"""

import sys
sys.path.append("..")

from dataclasses import dataclass
from typing import List, Dict, Optional


# 常见模型的上下文窗口
CONTEXT_WINDOWS = {
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "claude-3-5-sonnet": 200000,
    "gemini-1.5-pro": 1000000,
}


def estimate_tokens(text: str) -> int:
    """
    估算token数量
    
    规则:
    - 英文: 约4字符 ≈ 1 token
    - 中文: 约1.5字符 ≈ 1 token
    """
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.5 + other_chars * 0.25)


class ContextWindowManager:
    """上下文窗口管理器"""
    
    def __init__(self, max_tokens: int = 128000, reserved_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.available_tokens = max_tokens - reserved_tokens
    
    def estimate_messages_tokens(self, messages: list) -> int:
        """估算消息列表的总token数"""
        total = 0
        for msg in messages:
            total += estimate_tokens(msg.get("content", ""))
            total += 10  # role和格式的固定开销
        return total
    
    def can_fit(self, messages: list) -> bool:
        """检查消息是否能在窗口内容纳"""
        return self.estimate_messages_tokens(messages) <= self.available_tokens
    
    def truncate_messages(
        self, 
        messages: list, 
        strategy: str = "tail"
    ) -> list:
        """
        如果超出窗口，进行截断
        
        策略:
        - "tail": 保留系统提示 + 最新消息
        - "head": 保留系统提示 + 最早的消息
        - "summary": 生成摘要后保留
        """
        if self.can_fit(messages):
            return messages
        
        if strategy == "tail":
            return self._truncate_tail(messages)
        elif strategy == "head":
            return self._truncate_head(messages)
        else:
            return self._truncate_tail(messages)
    
    def _truncate_tail(self, messages: list) -> list:
        """保留系统提示 + 最新消息"""
        system_msg = [msg for msg in messages if msg.get("role") == "system"]
        other_msgs = [msg for msg in messages if msg.get("role") != "system"]
        
        result = system_msg.copy()
        current_tokens = self.estimate_messages_tokens(system_msg)
        
        # 从最新往最早添加
        for msg in reversed(other_msgs):
            msg_tokens = self.estimate_messages_tokens([msg])
            if current_tokens + msg_tokens <= self.available_tokens:
                result.insert(len(system_msg), msg)
                current_tokens += msg_tokens
            else:
                break
        
        return result
    
    def _truncate_head(self, messages: list) -> list:
        """保留系统提示 + 最早的消息"""
        system_msg = [msg for msg in messages if msg.get("role") == "system"]
        other_msgs = [msg for msg in messages if msg.get("role") != "system"]
        
        result = system_msg.copy()
        current_tokens = self.estimate_messages_tokens(system_msg)
        
        # 从最早往最新添加
        for msg in other_msgs:
            msg_tokens = self.estimate_messages_tokens([msg])
            if current_tokens + msg_tokens <= self.available_tokens:
                result.append(msg)
                current_tokens += msg_tokens
            else:
                break
        
        return result


def demo():
    """演示"""
    
    print("=" * 50)
    print("上下文窗口管理示例")
    print("=" * 50)
    
    manager = ContextWindowManager(max_tokens=1000, reserved_tokens=200)
    
    # 模拟长对话
    messages = [
        {"role": "system", "content": "你是一个有用的AI助手。"},
    ]
    
    # 添加对话历史
    for i in range(20):
        messages.append({
            "role": "user", 
            "content": f"这是第{i+1}轮对话的用户输入，内容比较长一些以便测试。" * 5
        })
        messages.append({
            "role": "assistant", 
            "content": f"这是第{i+1}轮对话的助手回复，内容也比较长。" * 5
        })
    
    original_tokens = manager.estimate_messages_tokens(messages)
    print(f"原始消息数: {len(messages)}")
    print(f"原始Token估算: {original_tokens}")
    print(f"可用Token: {manager.available_tokens}")
    
    # 截断
    truncated = manager.truncate_messages(messages, strategy="tail")
    truncated_tokens = manager.estimate_messages_tokens(truncated)
    
    print(f"\n截断后消息数: {len(truncated)}")
    print(f"截断后Token估算: {truncated_tokens}")
    
    print("\n保留的消息结构:")
    for i, msg in enumerate(truncated[:5]):
        role = msg["role"]
        content = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
        print(f"  {i+1}. [{role}]: {content}")


if __name__ == "__main__":
    demo()
