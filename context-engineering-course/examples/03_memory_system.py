"""
examples/03_memory_system.py
记忆系统实现示例
"""

import sys
sys.path.append("..")

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class MemoryType(Enum):
    """记忆类型"""
    WORKING = "working"           # 工作记忆（当前对话）
    EPISODIC = "episodic"         # 情景记忆（过去事件）
    SEMANTIC = "semantic"         # 语义记忆（知识概念）
    PROCEDURAL = "procedural"     # 程序记忆（技能方法）


@dataclass
class Memory:
    """记忆单元"""
    content: str
    memory_type: MemoryType
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    importance: float = 1.0      # 0-1重要性
    tags: List[str] = field(default_factory=list)
    
    def access(self):
        """访问记忆，更新统计"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class MemorySystem:
    """
    多层记忆系统
    
    工作流程:
    1. 用户输入 -> 检索相关记忆 -> 注入上下文
    2. 对话结束 -> 提取新记忆 -> 存储到适当层级
    3. 定期 Consolidation（记忆整合）
    """
    
    def __init__(self, working_memory_limit: int = 10):
        self.working_memory: List[Memory] = []
        self.episodic_memory: List[Memory] = []
        self.semantic_memory: List[Memory] = []
        self.working_memory_limit = working_memory_limit
    
    def add_working_memory(self, content: str, memory_type: MemoryType = MemoryType.WORKING, **kwargs):
        """添加工作记忆"""
        memory = Memory(
            content=content,
            memory_type=memory_type,
            **kwargs
        )
        self.working_memory.append(memory)
        
        if len(self.working_memory) > self.working_memory_limit:
            self._consolidate_oldest()
    
    def _consolidate_oldest(self):
        """将最旧的工作记忆转移到情景记忆"""
        if not self.working_memory:
            return
        
        oldest = self.working_memory.pop(0)
        oldest.memory_type = MemoryType.EPISODIC
        self.episodic_memory.append(oldest)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Memory]:
        """
        检索相关记忆
        
        简化实现：基于关键词匹配
        实际应用应使用向量相似度
        """
        all_memories = (
            self.working_memory + 
            self.episodic_memory + 
            self.semantic_memory
        )
        
        query_words = set(query.lower().split())
        scored = []
        
        for mem in all_memories:
            mem_words = set(mem.content.lower().split())
            overlap = query_words & mem_words
            if overlap:
                score = len(overlap) * mem.importance * (1 + 0.1 * mem.access_count)
                scored.append((score, mem))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [mem for _, mem in scored[:top_k]]
        
        for mem in results:
            mem.access()
        
        return results
    
    def get_context_for_prompt(self, query: str, max_memories: int = 5) -> str:
        """为Prompt构建记忆上下文"""
        relevant = self.retrieve(query, top_k=max_memories)
        
        if not relevant:
            return ""
        
        context_parts = ["【相关记忆】"]
        for i, mem in enumerate(relevant, 1):
            mem_type_name = mem.memory_type.value
            context_parts.append(f"{i}. [{mem_type_name}] {mem.content}")
        
        return "\n".join(context_parts)
    
    def store_semantic_memory(self, content: str, tags: List[str] = None):
        """存储语义记忆（知识性信息）"""
        memory = Memory(
            content=content,
            memory_type=MemoryType.SEMANTIC,
            tags=tags or []
        )
        self.semantic_memory.append(memory)
    
    def store_episodic_memory(self, content: str, importance: float = 1.0):
        """存储情景记忆（事件性信息）"""
        memory = Memory(
            content=content,
            memory_type=MemoryType.EPISODIC,
            importance=importance
        )
        self.episodic_memory.append(memory)
    
    def summary(self) -> str:
        """生成记忆系统状态摘要"""
        return f"""记忆系统状态:
- 工作记忆: {len(self.working_memory)} 条
- 情景记忆: {len(self.episodic_memory)} 条
- 语义记忆: {len(self.semantic_memory)} 条
"""


def demo():
    """演示"""
    
    print("=" * 50)
    print("记忆系统示例")
    print("=" * 50)
    
    memory = MemorySystem(working_memory_limit=5)
    
    # 添加工作记忆（模拟对话）
    memory.add_working_memory(
        "用户询问Python的列表推导式", 
        MemoryType.WORKING,
        importance=0.8
    )
    memory.add_working_memory(
        "用户表示想了解函数式编程", 
        MemoryType.WORKING,
        importance=0.6
    )
    
    # 存储语义记忆（知识库）
    memory.store_semantic_memory(
        "列表推导式是Python的简洁语法: [expr for item in iterable]",
        tags=["python", "语法", "列表"]
    )
    memory.store_semantic_memory(
        "map函数是函数式编程的基础，接受函数和可迭代对象",
        tags=["python", "函数式编程", "map"]
    )
    
    # 存储情景记忆（事件）
    memory.store_episodic_memory(
        "用户之前在学习Python基础语法",
        importance=0.7
    )
    
    print("\n记忆系统状态:")
    print(memory.summary())
    
    # 检索测试
    print("\n检索 '列表' 相关记忆:")
    context = memory.get_context_for_prompt("列表")
    print(context if context else "未找到相关记忆")
    
    print("\n检索 '函数' 相关记忆:")
    context = memory.get_context_for_prompt("函数")
    print(context if context else "未找到相关记忆")


if __name__ == "__main__":
    demo()
