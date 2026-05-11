"""
examples/05_context_injection.py
上下文注入策略示例
"""

import sys
sys.path.append("..")

from typing import List, Dict
from enum import Enum


class InjectionStrategy(Enum):
    """注入策略枚举"""
    DIRECT = "direct"              # 直接拼接
    LABELED = "labeled"            # 带标签分隔
    STRUCTURED = "structured"      # 结构化格式
    HYBRID = "hybrid"              # 混合模式


class ContextInjector:
    """
    上下文注入器
    
    提供多种注入策略，优化LLM对上下文的理解和利用
    """
    
    def __init__(self, strategy: InjectionStrategy = InjectionStrategy.STRUCTURED):
        self.strategy = strategy
    
    def build_prompt(
        self,
        system_instruction: str,
        context_blocks: List[Dict[str, str]],
        user_query: str
    ) -> List[Dict[str, str]]:
        """
        构建完整Prompt
        
        Args:
            system_instruction: 系统指令
            context_blocks: 上下文块列表 [{"content": "...", "source": "...", "score": 0.9}]
            user_query: 用户问题
        """
        if self.strategy == InjectionStrategy.DIRECT:
            return self._build_direct(system_instruction, context_blocks, user_query)
        elif self.strategy == InjectionStrategy.LABELED:
            return self._build_labeled(system_instruction, context_blocks, user_query)
        elif self.strategy == InjectionStrategy.STRUCTURED:
            return self._build_structured(system_instruction, context_blocks, user_query)
        else:
            return self._build_hybrid(system_instruction, context_blocks, user_query)
    
    def _build_direct(self, system: str, contexts: List[Dict], query: str) -> List[Dict]:
        """直接拼接"""
        context_text = "\n\n".join([ctx["content"] for ctx in contexts])
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": f"{context_text}\n\n问题: {query}"}
        ]
    
    def _build_labeled(self, system: str, contexts: List[Dict], query: str) -> List[Dict]:
        """带标签分隔"""
        parts = ["[参考资料]"]
        for i, ctx in enumerate(contexts, 1):
            parts.append(f"\n[文档{i}]\n{ctx['content']}")
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": "".join(parts) + f"\n\n基于以上资料回答: {query}"}
        ]
    
    def _build_structured(self, system: str, contexts: List[Dict], query: str) -> List[Dict]:
        """结构化模式 - 最佳实践"""
        parts = ["【参考资料】"]
        
        for i, ctx in enumerate(contexts, 1):
            source = ctx.get("source", "未知来源")
            score = ctx.get("score", 0)
            parts.append(f"\n【文档{i}】(来源: {source}, 相关度: {score:.2f})")
            parts.append(ctx["content"])
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": "".join(parts) + f"\n\n【问题】\n{query}"}
        ]
    
    def _build_hybrid(self, system: str, contexts: List[Dict], query: str) -> List[Dict]:
        """混合模式 - 按相关度分级注入"""
        high = [ctx for ctx in contexts if ctx.get("score", 0) > 0.7]
        low = [ctx for ctx in contexts if ctx.get("score", 0) <= 0.7]
        
        parts = []
        
        if high:
            parts.append("【高相关参考资料】")
            for ctx in high:
                parts.append(f"- {ctx['content']}")
        
        if low:
            parts.append("\n【其他可能相关的参考资料】")
            for ctx in low[:2]:
                parts.append(f"- {ctx['content'][:200]}...")
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": "\n".join(parts) + f"\n\n问题: {query}"}
        ]


def compare_strategies():
    """对比不同注入策略"""
    
    system = "你是一个知识问答助手。"
    contexts = [
        {
            "content": "Python是一种高级编程语言，由Guido van Rossum于1991年创建。",
            "source": "Python简介",
            "score": 0.95
        },
        {
            "content": "JavaScript是一种脚本语言，主要用于Web前端开发。",
            "source": "JS简介",
            "score": 0.3
        }
    ]
    query = "Python是谁创建的？"
    
    injector = ContextInjector()
    
    print("=" * 60)
    print("上下文注入策略对比")
    print("=" * 60)
    
    for strategy in InjectionStrategy:
        injector.strategy = strategy
        messages = injector.build_prompt(system, contexts, query)
        
        print(f"\n【{strategy.name}模式】")
        print("-" * 40)
        for msg in messages:
            print(f"[{msg['role']}]:")
            content = msg['content']
            # 截断显示
            if len(content) > 300:
                content = content[:300] + "..."
            print(content)
            print()


if __name__ == "__main__":
    compare_strategies()
