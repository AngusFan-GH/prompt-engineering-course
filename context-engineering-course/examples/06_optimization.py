"""
examples/06_optimization.py
上下文优化技巧示例
"""

import sys
sys.path.append("..")

from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class ContextBlock:
    """上下文块"""
    id: str
    content: str
    score: float = 1.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContextOptimizer:
    """
    上下文优化器
    
    优化策略:
    1. 去重 - 移除重复内容
    2. 压缩 - 精简冗余描述
    3. 排序 - 按相关性排序
    4. 截断 - 控制在token限制内
    """
    
    @staticmethod
    def deduplicate(contexts: List[ContextBlock], threshold: float = 0.85) -> List[ContextBlock]:
        """
        去重
        
        移除相似度超过阈值的内容
        """
        if not contexts:
            return []
        
        unique = [contexts[0]]
        
        for ctx in contexts[1:]:
            is_duplicate = False
            for unique_ctx in unique:
                if ContextOptimizer._calculate_similarity(
                    ctx.content,
                    unique_ctx.content
                ) > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(ctx)
        
        return unique
    
    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """计算文本相似度（Jaccard）"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    @staticmethod
    def compress(contexts: List[ContextBlock], max_length: int = 500) -> List[ContextBlock]:
        """
        压缩上下文
        
        在句子边界处截断
        """
        compressed = []
        
        for ctx in contexts:
            content = ctx.content
            
            if len(content) <= max_length:
                compressed.append(ctx)
            else:
                # 在句子边界截断
                truncated = content[:max_length]
                for sep in ["。", "！", "？", ". ", "!\n", "?\n"]:
                    last_sep = truncated.rfind(sep)
                    if last_sep > max_length * 0.7:
                        truncated = truncated[:last_sep + 1]
                        break
                
                compressed.append(ContextBlock(
                    id=ctx.id,
                    content=truncated + "...",
                    score=ctx.score,
                    metadata=ctx.metadata
                ))
        
        return compressed
    
    @staticmethod
    def prioritize(
        contexts: List[ContextBlock],
        max_count: int = 5,
        max_total_chars: int = 3000
    ) -> List[ContextBlock]:
        """
        按优先级截断
        
        1. 按相关性排序
        2. 优先保留高相关度内容
        3. 控制总长度
        """
        # 排序
        sorted_ctx = sorted(contexts, key=lambda x: x.score, reverse=True)
        
        result = []
        total_chars = 0
        
        for ctx in sorted_ctx:
            ctx_chars = len(ctx.content)
            
            if len(result) >= max_count or total_chars + ctx_chars > max_total_chars:
                break
            
            result.append(ctx)
            total_chars += ctx_chars
        
        return result
    
    @staticmethod
    def extract_key_info(contexts: List[ContextBlock]) -> str:
        """
        提取关键信息摘要
        
        从多个上下文块中提取核心信息
        """
        if not contexts:
            return ""
        
        key_points = []
        
        for ctx in contexts:
            # 简化：取每个块的前几个句子
            sentences = ctx.content.split("。")
            if sentences:
                key_points.append(sentences[0].strip() + "。")
        
        return " ".join(key_points[:3])


class TokenBudgetManager:
    """
    Token预算管理器
    
    确保Prompt不超过模型的上下文窗口限制
    """
    
    def __init__(self, max_tokens: int = 100000, reserved_output: int = 2000):
        self.max_tokens = max_tokens
        self.reserved_output = reserved_output
        self.available_for_input = max_tokens - reserved_output
    
    def estimate_tokens(self, text: str) -> int:
        """估算token数量"""
        chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other = len(text) - chinese
        return int(chinese * 1.5 + other * 0.25)
    
    def can_fit(self, parts: List[str]) -> bool:
        """检查是否能容纳"""
        total = sum(self.estimate_tokens(p) for p in parts)
        return total <= self.available_for_input
    
    def fit_with_budget(
        self,
        system: str,
        contexts: List[ContextBlock],
        user_query: str
    ) -> Dict[str, str]:
        """
        在Token预算内构建Prompt
        
        Returns:
            {"system": "...", "context": "...", "query": "..."}
        """
        system_tokens = self.estimate_tokens(system)
        query_tokens = self.estimate_tokens(user_query)
        
        # 预算分配
        system_budget = min(system_tokens, int(self.available_for_input * 0.1))
        query_budget = min(query_tokens, int(self.available_for_input * 0.2))
        context_budget = self.available_for_input - system_budget - query_budget
        
        # 裁剪各部分
        system_final = self._trim_to_tokens(system, system_budget)
        query_final = self._trim_to_tokens(user_query, query_budget)
        
        # 选择和裁剪上下文
        context_parts = []
        used_tokens = 0
        
        for ctx in sorted(contexts, key=lambda x: x.score, reverse=True):
            ctx_tokens = self.estimate_tokens(ctx.content)
            
            if used_tokens + ctx_tokens <= context_budget:
                context_parts.append(ctx.content)
                used_tokens += ctx_tokens
            else:
                # 尝试部分保留
                remaining = context_budget - used_tokens
                if remaining > 100:  # 至少保留100 tokens
                    partial = self._trim_to_tokens(ctx.content, remaining)
                    context_parts.append(partial)
                break
        
        return {
            "system": system_final,
            "context": "\n\n".join(context_parts),
            "query": query_final
        }
    
    def _trim_to_tokens(self, text: str, max_tokens: int) -> str:
        """将文本裁剪到指定token数"""
        current = self.estimate_tokens(text)
        
        if current <= max_tokens:
            return text
        
        # 二分查找合适的截断点
        left, right = 0, len(text)
        
        while left < right:
            mid = (left + right + 1) // 2
            if self.estimate_tokens(text[:mid]) <= max_tokens:
                left = mid
            else:
                right = mid - 1
        
        return text[:left]


def demo():
    """演示"""
    
    print("=" * 50)
    print("上下文优化技巧示例")
    print("=" * 50)
    
    optimizer = ContextOptimizer()
    
    # 准备测试数据
    contexts = [
        ContextBlock("1", "Python是一种高级编程语言，由Guido van Rossum于1991年创建。它以简洁易读的语法著称。"),
        ContextBlock("2", "Python是一种高级编程语言，广泛应用于Web开发、数据科学、AI等领域。"),
        ContextBlock("3", "JavaScript是由Brendan Eich于1995年创建的编程语言，主要用于Web前端开发。"),
        ContextBlock("4", "FastAPI是现代Python Web框架，用于构建API，支持异步编程，性能优秀。"),
    ]
    
    # 去重
    print("\n【去重前】")
    for ctx in contexts:
        print(f"  {ctx.id}: {ctx.content[:40]}...")
    
    unique = optimizer.deduplicate(contexts)
    
    print("\n【去重后】")
    for ctx in unique:
        print(f"  {ctx.id}: {ctx.content[:40]}...")
    
    # Token预算管理
    print("\n" + "-" * 40)
    print("【Token预算管理】")
    
    manager = TokenBudgetManager(max_tokens=1000, reserved_output=200)
    
    system = "你是一个专业的编程助手。" * 50
    query = "Python语言的特点是什么？" * 20
    
    result = manager.fit_with_budget(
        system,
        unique,
        query
    )
    
    print(f"系统指令: {manager.estimate_tokens(result['system'])} tokens")
    print(f"上下文: {manager.estimate_tokens(result['context'])} tokens")
    print(f"用户问题: {manager.estimate_tokens(result['query'])} tokens")
    print(f"总输入: {manager.estimate_tokens(result['system'] + result['context'] + result['query'])} tokens")


if __name__ == "__main__":
    demo()
