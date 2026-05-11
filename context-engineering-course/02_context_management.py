"""
上下文管理模块 - 代码示例
=========================

本模块展示上下文管理的核心概念和实现：
1. ContextWindow - 上下文窗口管理
2. ContextCompressor - 上下文压缩
3. MemorySystem - 记忆系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import re


# ============================================================
# 1. 上下文状态机
# ============================================================

class ContextState(Enum):
    """上下文状态"""
    INITIAL = "initial"
    BUILDING = "building"
    COMPLETE = "complete"
    TRUNCATED = "truncated"
    COMPRESSED = "compressed"


@dataclass
class Message:
    """对话消息"""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextWindow:
    """
    上下文窗口管理器
    
    跟踪和管理上下文状态，计算Token使用量，
    在达到窗口限制时触发压缩或截断策略。
    """
    
    def __init__(self, max_tokens: int = 128_000, reserved_tokens: int = 4096):
        self.max_tokens = max_tokens
        self.reserved_tokens = reserved_tokens
        self.effective_limit = max_tokens - reserved_tokens
        self.messages: List[Message] = []
        self.state = ContextState.INITIAL
        self.token_count = 0
        self._char_to_token_ratio = 4
    
    def estimate_tokens(self, text: str) -> int:
        """估算Token数量"""
        return len(text) // self._char_to_token_ratio
    
    def add_message(self, role: str, content: str, metadata: Dict = None) -> bool:
        """添加消息到上下文"""
        message = Message(role=role, content=content, metadata=metadata or {})
        msg_tokens = self.estimate_tokens(content)
        
        if self.token_count + msg_tokens > self.effective_limit:
            self.state = ContextState.TRUNCATED
            return False
        
        self.messages.append(message)
        self.token_count += msg_tokens
        self.state = ContextState.BUILDING if len(self.messages) > 1 else ContextState.INITIAL
        return True
    
    def get_context_summary(self) -> Dict[str, Any]:
        """获取上下文摘要"""
        return {
            "state": self.state.value,
            "message_count": len(self.messages),
            "token_count": self.token_count,
            "token_limit": self.effective_limit,
            "utilization": f"{self.token_count / self.effective_limit * 100:.1f}%" if self.effective_limit > 0 else "0%",
        }


# ============================================================
# 2. 上下文压缩器
# ============================================================

@dataclass
class CompressionResult:
    """压缩结果"""
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    method: str


class ContextCompressor:
    """
    上下文压缩器
    
    提供多种压缩策略：
    1. 摘要压缩 - 用摘要替换详细内容
    2. 选择性保留 - 只保留重要消息
    3. 滑动窗口 - 只保留最近N条消息
    """
    
    def __init__(self, tokenizer: Callable[[str], list] = None):
        self.tokenizer = tokenizer or (lambda x: x.split())
    
    def compress_by_sliding_window(
        self, 
        messages: List[Message], 
        keep_recent: int = 10
    ) -> tuple[List[Message], CompressionResult]:
        """
        滑动窗口压缩 - 只保留最近N条消息
        """
        original_tokens = sum(len(self.tokenizer(m.content)) for m in messages)
        
        # 保留系统消息 + 最近N条
        system_msgs = [m for m in messages if m.role == "system"]
        recent_msgs = messages[-keep_recent:] if len(messages) > keep_recent else messages
        
        compressed = system_msgs + recent_msgs
        compressed_tokens = sum(len(self.tokenizer(m.content)) for m in compressed)
        
        return compressed, CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            method="sliding_window"
        )
    
    def compress_selective(
        self,
        messages: List[Message],
        importance_func: Callable[[Message], float],
        target_tokens: int
    ) -> tuple[List[Message], CompressionResult]:
        """
        选择性压缩 - 根据重要性保留消息
        """
        original_tokens = sum(len(self.tokenizer(m.content)) for m in messages)
        
        # 为每条消息计算重要性分数
        scored = [
            (msg, importance_func(msg), len(self.tokenizer(msg.content)))
            for msg in messages
        ]
        
        # 按重要性排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 贪心选择
        selected = []
        current_tokens = 0
        
        for msg, importance, msg_tokens in scored:
            if current_tokens + msg_tokens <= target_tokens:
                selected.append(msg)
                current_tokens += msg_tokens
        
        # 保持原始顺序
        selected.sort(key=lambda m: messages.index(m))
        
        compressed_tokens = sum(len(self.tokenizer(m.content)) for m in selected)
        
        return selected, CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            method="selective"
        )


# ============================================================
# 3. 记忆系统
# ============================================================

class ConversationMemory:
    """对话记忆 - 短期记忆"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def add(self, key: str, value: Any) -> None:
        self._storage[key] = {"value": value, "timestamp": datetime.now()}
    
    def get(self, key: str) -> Optional[Any]:
        entry = self._storage.get(key)
        if entry is None:
            return None
        
        age = (datetime.now() - entry["timestamp"]).total_seconds()
        if age > self.ttl_seconds:
            del self._storage[key]
            return None
        
        return entry["value"]
    
    def get_recent(self, limit: int = 10) -> List[Any]:
        sorted_entries = sorted(
            self._storage.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )
        return [e[1]["value"] for _, e in sorted_entries[:limit]]
    
    def clear(self) -> None:
        self._storage.clear()


class SemanticMemory:
    """语义记忆 - 长期记忆（基于向量）"""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self._vectors: Dict[str, List[float]] = {}
        self._storage: Dict[str, Any] = {}
    
    def _compute_embedding(self, text: str) -> List[float]:
        """计算文本embedding（简化版）"""
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        vector = [0.0] * self.embedding_dim
        for i, (word, freq) in enumerate(word_freq.items()):
            vector[i % self.embedding_dim] += freq
        
        # L2归一化
        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))
    
    def add(self, key: str, value: Any) -> None:
        self._storage[key] = value
        if isinstance(value, str):
            self._vectors[key] = self._compute_embedding(value)
    
    def get(self, key: str) -> Optional[Any]:
        return self._storage.get(key)
    
    def search(self, query: str, limit: int = 5) -> List[tuple[Any, float]]:
        """语义搜索"""
        query_vector = self._compute_embedding(query)
        
        similarities = []
        for key, vec in self._vectors.items():
            sim = self._cosine_similarity(query_vector, vec)
            similarities.append((self._storage[key], sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
    
    def clear(self) -> None:
        self._storage.clear()
        self._vectors.clear()


# ============================================================
# 演示代码
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("上下文管理示例")
    print("="*60)
    
    # 1. 上下文窗口
    print("\n1. 上下文窗口管理")
    print("-"*40)
    
    ctx = ContextWindow(max_tokens=10000, reserved_tokens=1000)
    
    ctx.add_message("system", "你是一个乐于助人的AI助手")
    ctx.add_message("user", "你好，我想了解Python编程")
    ctx.add_message("assistant", "Python是一种高级编程语言，语法简洁易懂...")
    
    summary = ctx.get_context_summary()
    print(f"状态: {summary['state']}")
    print(f"消息数: {summary['message_count']}")
    print(f"Token使用: {summary['token_count']}/{summary['token_limit']}")
    print(f"利用率: {summary['utilization']}")
    
    # 2. 上下文压缩
    print("\n2. 上下文压缩")
    print("-"*40)
    
    compressor = ContextCompressor()
    
    test_messages = [
        Message("system", "你是客服助手"),
        Message("user", "你好，我想咨询产品"),
        Message("assistant", "您好，请问有什么可以帮助您的？"),
        Message("user", "我想买一台笔记本电脑"),
        Message("assistant", "好的，您有什么偏好或预算吗？"),
        Message("user", "预算8000元左右"),
        Message("assistant", "推荐联想ThinkBook 14+..."),
        Message("user", "内存多大？"),
        Message("assistant", "16GB DDR5..."),
    ]
    
    compressed, result = compressor.compress_by_sliding_window(test_messages, keep_recent=4)
    
    print(f"原始消息数: {len(test_messages)}")
    print(f"压缩后消息数: {len(compressed)}")
    print(f"压缩比: {result.compression_ratio:.2%}")
    print(f"方法: {result.method}")
    print("\n保留的消息:")
    for m in compressed:
        print(f"  - {m.role}: {m.content[:30]}...")
    
    # 3. 记忆系统
    print("\n3. 记忆系统")
    print("-"*40)
    
    # 短期记忆
    short_mem = ConversationMemory()
    short_mem.add("user_name", "张三")
    short_mem.add("user_preference", "喜欢简洁的设计")
    
    print(f"用户名称: {short_mem.get('user_name')}")
    print(f"用户偏好: {short_mem.get('user_preference')}")
    
    # 语义记忆
    semantic_mem = SemanticMemory()
    semantic_mem.add("python_intro", "Python是一种高级编程语言")
    semantic_mem.add("java_intro", "Java是一种面向对象编程语言")
    semantic_mem.add("js_intro", "JavaScript主要用于Web前端开发")
    
    results = semantic_mem.search("编程语言", limit=2)
    print("\n语义搜索'编程语言'的结果:")
    for content, score in results:
        print(f"  - {content} (相似度: {score:.4f})")
