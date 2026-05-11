"""
examples/01_basic_context.py
基础上下文管理示例
"""

import sys
sys.path.append("..")

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ContextBlock:
    """上下文块"""
    id: str
    content: str
    block_type: str = "general"  # system, knowledge, history, user
    priority: int = 1           # 优先级 1-5
    metadata: Dict = field(default_factory=dict)


class BasicContextManager:
    """
    基础上下文管理器
    
    功能:
    1. 管理多种类型的上下文块
    2. 按优先级和类型组织
    3. 生成完整的Prompt
    """
    
    def __init__(self, max_tokens: int = 100000):
        self.blocks: List[ContextBlock] = []
        self.max_tokens = max_tokens
    
    def add_block(self, block: ContextBlock):
        """添加上下文块"""
        self.blocks.append(block)
    
    def add_system(self, content: str):
        """添加系统级上下文"""
        self.blocks.insert(0, ContextBlock(
            id="system",
            content=content,
            block_type="system",
            priority=5
        ))
    
    def add_knowledge(self, content: str, source: str = ""):
        """添加知识上下文"""
        block = ContextBlock(
            id=f"knowledge_{len([b for b in self.blocks if b.block_type == 'knowledge'])}",
            content=content,
            block_type="knowledge",
            priority=3,
            metadata={"source": source}
        )
        # 知识块放在系统之后
        insert_idx = 1
        for i, b in enumerate(self.blocks):
            if b.block_type != "system":
                insert_idx = i
                break
        self.blocks.insert(insert_idx, block)
    
    def add_history(self, role: str, content: str):
        """添加历史对话"""
        block = ContextBlock(
            id=f"history_{len([b for b in self.blocks if b.block_type == 'history'])}",
            content=f"{role}: {content}",
            block_type="history",
            priority=2
        )
        self.blocks.append(block)
    
    def build_prompt(self, user_input: str) -> List[Dict[str, str]]:
        """构建完整Prompt"""
        messages = []
        
        # 收集所有上下文
        context_parts = []
        for block in self.blocks:
            if block.block_type == "system":
                continue
            context_parts.append(block.content)
        
        # System Prompt
        system_parts = []
        for block in self.blocks:
            if block.block_type == "system":
                system_parts.append(block.content)
        
        system_prompt = "\n\n".join(system_parts)
        if context_parts:
            system_prompt += "\n\n【上下文信息】\n" + "\n\n".join(context_parts)
        
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def clear_history(self):
        """清除历史上下文（保留系统和知识）"""
        self.blocks = [b for b in self.blocks if b.block_type != "history"]
    
    def estimate_tokens(self) -> int:
        """估算当前上下文token数"""
        total = 0
        for block in self.blocks:
            total += len(block.content) * 0.25
        return int(total)
    
    def summary(self) -> str:
        """生成状态摘要"""
        by_type = {}
        for block in self.blocks:
            by_type.setdefault(block.block_type, []).append(block.id)
        return f"上下文块统计: {', '.join(f'{k}:{len(v)}' for k,v in by_type.items())}"


def demo():
    """演示"""
    
    print("=" * 50)
    print("基础上下文管理示例")
    print("=" * 50)
    
    manager = BasicContextManager()
    
    # 设置系统
    manager.add_system("""你是一个Python编程助手。
当用户提出编程问题时，你应该：
1. 先解释概念和原理
2. 提供清晰的代码示例
3. 指出常见的错误和最佳实践""")
    
    # 添加知识上下文
    manager.add_knowledge(
        "列表推导式是Python的简洁语法，用于创建列表。基本格式: [表达式 for 项 in 可迭代对象]",
        source="Python官方文档"
    )
    manager.add_knowledge(
        "字典推导式类似: {键:值 for 项 in 可迭代对象}",
        source="Python官方文档"
    )
    
    # 模拟对话历史
    manager.add_history("user", "什么是列表推导式？")
    manager.add_history("assistant", "列表推导式是Python创建列表的简洁方式。例如: [x*2 for x in range(5)] 会生成 [0,2,4,6,8]")
    manager.add_history("user", "那字典推导式呢？")
    
    # 用户新问题
    user_question = "给我一个实际的例子"
    
    # 构建Prompt
    messages = manager.build_prompt(user_question)
    
    print(f"\n当前上下文状态: {manager.summary()}")
    print(f"估算Token: {manager.estimate_tokens()}")
    
    print("\n" + "-" * 40)
    print("生成的System Prompt:")
    print("-" * 40)
    print(messages[0]["content"])
    
    print("\n" + "-" * 40)
    print("用户输入:")
    print("-" * 40)
    print(messages[1]["content"])
    
    # 注意：需要API密钥才能实际调用
    # from config import LLMConfig
    # from utils.llm_client import LLMClient
    # config = LLMConfig(provider="openai", model="gpt-4o-mini")
    # client = LLMClient(config)
    # response = client.chat(messages)
    # print(f"\n回复: {response}")


if __name__ == "__main__":
    demo()
