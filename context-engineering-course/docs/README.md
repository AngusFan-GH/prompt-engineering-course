# 上下文工程（Context Engineering）

## 课程概述

**上下文工程**是指对大语言模型（LLM）进行系统性管理、控制和优化的工程实践，其核心目标是确保模型在复杂任务中能够访问到正确、完整、适量的上下文信息。

本课程涵盖从基础概念到高级实践的完整知识体系，包括上下文管理策略、RAG检索增强生成技术、上下文注入优化以及真实教学场景案例。

---

## 目录

1. [核心概念定义](#1-核心概念定义)
2. [上下文管理的关键技术](#2-上下文管理的关键技术)
3. [RAG 检索增强生成技术](#3-rag-检索增强生成技术)
4. [上下文注入策略与优化](#4-上下文注入策略与优化)
5. [代码案例](#5-代码案例)
6. [教学场景案例](#6-教学场景案例)

---

## 1. 核心概念定义

### 1.1 什么是上下文工程？

**上下文工程（Context Engineering）** 是指对大语言模型进行系统性管理、控制和优化的工程实践，其核心目标是确保模型在复杂任务中能够访问到正确、完整、适量的上下文信息。

```
┌─────────────────────────────────────────────────────────────┐
│                    上下文工程示意图                           │
│                                                             │
│   用户输入 ──┬──→ 上下文管理器 ──→ LLM ──→ 响应输出         │
│              │         ↑                                    │
│              │         │                                    │
│   历史记录 ──┼──→  知识库/检索                              │
│              │         │                                    │
│   系统指令 ──┴──→  提示词模板                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 上下文工程 vs. 提示词工程

| 维度 | 提示词工程 (Prompt Engineering) | 上下文工程 (Context Engineering) |
|------|--------------------------------|--------------------------------|
| **关注点** | 单次交互的指令设计 | 多轮/复杂任务的信息管理 |
| **核心问题** | "怎么说才清楚？" | "模型需要知道什么？如何供给？" |
| **技术手段** | 角色设定、格式指令、示例 | 记忆系统、RAG、上下文窗口管理 |
| **典型场景** | 单次问答、简单任务 | 多轮对话、长文档分析、跨会话任务 |
| **时间跨度** | 毫秒级单次调用 | 秒到分钟级多轮交互 |

### 1.3 关键术语

| 术语 | 定义 |
|------|------|
| **上下文窗口（Context Window）** | 模型能接受的最大输入+输出 token 数 |
| **上下文Token** | 输入给模型的全部历史信息（对话历史、系统提示、用户输入等） |
| **上下文长度（Context Length）** | 模型能处理的最大 token 数 |
| **记忆（Memory）** | 在多轮对话中保存历史信息的技术 |
| **检索（Retrieval）** | 从外部知识源获取相关信息的过程 |
| **上下文压缩（Context Compression）** | 减少上下文长度的技术 |
| **注意力机制（Attention）** | 模型关注输入特定部分的能力 |

---

## 2. 上下文管理的关键技术

### 2.1 上下文窗口

#### 主流模型上下文窗口对比

| 模型 | 上下文窗口 |
|------|-----------|
| GPT-4o | 128K tokens |
| Claude 3.5 | 200K tokens |
| Gemini 1.5 | 1M tokens |
| Qwen2.5 | 128K tokens |

#### 核心问题

> **问题**：即使上下文窗口很大，上下文越长，推理成本越高，且模型对远距离信息的注意力会下降。

```
┌────────────────────────────────────────────────────────────┐
│                  上下文长度 vs 注意力衰减                    │
│                                                            │
│  注意力   │★★★★★★★★★★★★│★★★★★★│★★★│★               │
│  强度     │   近距离     │ 中距离  │远距离│ 更远            │
│                                                            │
│  Token位置│ ←─────────── 上下文窗口 ──────────→            │
│                                                            │
│  结论: 距离越远，模型关注度越低，信息可能丢失               │
└────────────────────────────────────────────────────────────┘
```

### 2.2 上下文管理的核心策略

```
┌─────────────────────────────────────────────────────┐
│                  上下文管理策略                       │
├─────────────┬─────────────┬─────────────┬────────────┤
│   记忆管理    │   窗口优化    │   知识注入    │  压缩与摘要  │
├─────────────┼─────────────┼─────────────┼────────────┤
│ • 对话历史   │ • 滚动窗口   │ • RAG检索    │ • 文本摘要   │
│ • 关键信息   │ • 重要性过滤  │ • 知识图谱   │ • Token控制  │
│ • 用户画像   │ • 语义压缩   │ • 工具返回   │ • 稀疏检索   │
└─────────────┴─────────────┴─────────────┴────────────┘
```

### 2.3 记忆系统的类型

#### 2.3.1 短期记忆（Short-term Memory）

仅保存当前会话的对话历史，适用于单次对话场景。

```python
class ShortTermMemory:
    """短期记忆：简单保存对话历史"""
    
    def __init__(self, max_history: int = 20):
        self.messages = []
        self.max_history = max_history  # 保留最近N轮
    
    def add(self, role: str, content: str):
        """添加消息"""
        self.messages.append({"role": role, "content": content})
    
    def get_context(self) -> list[dict]:
        """返回最近的对话历史"""
        return self.messages[-self.max_history:]
    
    def clear(self):
        """清空历史"""
        self.messages = []
```

#### 2.3.2 长期记忆（Long-term Memory）

跨会话持久化存储关键信息，使用向量数据库实现语义检索。

```python
class LongTermMemory:
    """长期记忆：基于向量数据库的持久化存储"""
    
    def __init__(self, embedding_model="text-embedding-3-small"):
        self.embeddings = []  # 实际生产应使用向量数据库
        self.memory_store = {}  # 原始内容存储
        self.embedding_model = embedding_model
    
    def add(self, key: str, content: str, metadata: dict = None):
        """添加记忆"""
        self.memory_store[key] = {
            "content": content,
            "metadata": metadata or {}
        }
    
    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """基于语义检索记忆"""
        # 实际生产应使用向量相似度搜索
        return list(self.memory_store.values())[:top_k]
    
    def search_by_keyword(self, keyword: str) -> list[dict]:
        """基于关键词搜索"""
        return [
            v for k, v in self.memory_store.items()
            if keyword.lower() in v["content"].lower()
        ]
```

#### 2.3.3 情景记忆（Episodic Memory）

记录和回忆特定经历/事件，模拟人类的情景记忆。

```python
from datetime import datetime
from typing import Optional

class EpisodicMemory:
    """情景记忆：记录事件序列"""
    
    def __init__(self):
        self.episodes = []
    
    def record(self, event_type: str, content: str, 
               entities: list[str] = None, 
               timestamp: datetime = None):
        """记录一个事件"""
        episode = {
            "type": event_type,
            "content": content,
            "entities": entities or [],
            "timestamp": timestamp or datetime.now(),
            "id": len(self.episodes)
        }
        self.episodes.append(episode)
    
    def recall(self, query: str = None, 
               entity: str = None,
               limit: int = 10) -> list[dict]:
        """回忆相关事件"""
        results = self.episodes
        
        if entity:
            results = [e for e in results if entity in e.get("entities", [])]
        
        # 按时间倒序返回最近的
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)[:limit]
```

#### 2.3.4 多层记忆系统架构

```python
class MemoryType(Enum):
    """记忆类型"""
    WORKING = "working"           # 工作记忆（当前对话）
    EPISODIC = "episodic"         # 情景记忆（过去事件）
    SEMANTIC = "semantic"         # 语义记忆（知识概念）
    PROCEDURAL = "procedural"     # 程序记忆（技能方法）

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
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Memory]:
        """检索相关记忆"""
        all_memories = (
            self.working_memory + 
            self.episodic_memory + 
            self.semantic_memory
        )
        
        # 基于关键词匹配 + 重要性权重计算
        query_words = set(query.lower().split())
        scored = []
        
        for mem in all_memories:
            mem_words = set(mem.content.lower().split())
            overlap = query_words & mem_words
            if overlap:
                score = len(overlap) * mem.importance * (1 + 0.1 * mem.access_count)
                scored.append((score, mem))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:top_k]]
    
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
```

### 2.4 滚动窗口策略

管理长对话时的上下文长度，确保token消耗可控。

```python
class SlidingWindowMemory:
    """滚动窗口记忆"""
    
    def __init__(self, max_tokens: int = 4000):
        self.messages = []
        self.max_tokens = max_tokens
    
    def count_tokens(self, messages: list[dict]) -> int:
        """简单估算token数（实际应使用tiktoken）"""
        return sum(len(m["content"]) // 4 for m in messages)
    
    def get_recent_messages(self, current_message: str) -> list[dict]:
        """获取在token限制内的最近消息"""
        result = []
        total_tokens = len(current_message) // 4  # 当前消息
        
        for msg in reversed(self.messages):
            msg_tokens = len(msg["content"]) // 4
            if total_tokens + msg_tokens <= self.max_tokens:
                result.insert(0, msg)
                total_tokens += msg_tokens
            else:
                break
        
        return result
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
```

### 2.5 上下文块管理

```python
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
    
    def build_prompt(self, user_input: str) -> List[Dict[str, str]]:
        """构建完整Prompt"""
        messages = []
        
        # System Prompt
        system_parts = []
        context_parts = []
        
        for block in self.blocks:
            if block.block_type == "system":
                system_parts.append(block.content)
            else:
                context_parts.append(block.content)
        
        system_prompt = "\n\n".join(system_parts)
        if context_parts:
            system_prompt += "\n\n【上下文信息】\n" + "\n\n".join(context_parts)
        
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_input})
        
        return messages
```

---

## 3. RAG 检索增强生成技术

### 3.1 RAG 核心原理

```
┌──────────────────────────────────────────────────────────┐
│                      RAG 工作流程                         │
│                                                          │
│  ┌──────────┐    检索     ┌──────────┐    生成    ┌─────┐│
│  │  用户问题  │ ────────▶ │  向量数据库 │ ────────▶ │ LLM ││
│  └──────────┘            └──────────┘            └─────┘│
│       │                       │                       │  │
│       │                       ▼                       │  │
│       │              ┌──────────────┐                 │  │
│       │              │  1. Query嵌入  │                 │  │
│       │              │  2. 向量相似度  │                 │  │
│       │              │  3. Top-K检索  │                 │  │
│       │              └──────────────┘                 │  │
│       │                       │                       │  │
│       ▼                       ▼                       ▼  │
│  ┌────────────────────────────────────────────┐         │
│  │     上下文: [检索结果] + 用户问题 + 指令      │         │
│  └────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────┘
```

**RAG 核心流程**：
1. **索引阶段**：将文档切分为块，生成嵌入向量，存储到向量数据库
2. **检索阶段**：将用户问题转换为向量，从数据库中检索最相似的Top-K块
3. **生成阶段**：将检索结果与问题组合成prompt，调用LLM生成回答

### 3.2 向量数据库选型

| 数据库 | 特点 | 适用场景 |
|--------|------|---------|
| **Chroma** | 轻量级、易用、本地 | 原型开发、小规模 |
| **Milvus** | 高性能、分布式 | 大规模生产环境 |
| **Qdrant** | Rust实现、高性能 | 生产环境 |
| **Pinecone** | 云服务、全托管 | 不想运维的场景 |
| **FAISS** | Facebook开源、GPU加速 | 需要本地部署 |

### 3.3 文档分块策略

合理的分块策略直接影响检索质量。

```python
from typing import Callable

class TextChunker:
    """文档分块器"""
    
    def __init__(self, 
                 chunk_size: int = 500,
                 overlap: int = 50,
                 split_by: str = "sentence"):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.split_by = split_by
    
    def split_by_sentence(self, text: str) -> list[str]:
        """按句子分割"""
        import re
        sentences = re.split(r'[。！？.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def split_by_paragraph(self, text: str) -> list[str]:
        """按段落分割"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def chunk(self, text: str) -> list[dict]:
        """生成重叠的文本块"""
        if self.split_by == "sentence":
            units = self.split_by_sentence(text)
        elif self.split_by == "paragraph":
            units = self.split_by_paragraph(text)
        else:
            units = [text]
        
        chunks = []
        start = 0
        
        while start < len(units):
            end = start
            current_chunk = []
            current_size = 0
            
            while end < len(units) and current_size < self.chunk_size:
                current_chunk.append(units[end])
                current_size += len(units[end])
                end += 1
            
            chunk_text = ''.join(current_chunk)
            chunks.append({
                "content": chunk_text,
                "start_idx": start,
                "end_idx": end
            })
            
            # 滑动窗口：移动start位置（减去重叠）
            start = end - self.overlap if self.overlap > 0 else end
        
        return chunks
```

**分块策略对比**：

| 策略 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 固定大小 | 简单可控 | 可能切断语义 | 通用场景 |
| 按段落 | 保持语义完整 | 块大小不一 | 结构化文档 |
| 按句子 | 最小语义单元 | 块太小，缺少上下文 | 精确检索 |
| 递归分割 | 智能边界 | 实现复杂 | 混合文档 |

### 3.4 Embedding 模型

```python
import hashlib
from typing import Optional

class SimpleEmbedder:
    """简化的Embedding封装（实际生产使用OpenAI/HuggingFace）"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.dimension = 1536
    
    def embed(self, text: str) -> list[float]:
        """生成文本向量"""
        # 实际应调用: openai.embeddings.create(input=text, model=self.model)
        import random
        random.seed(hash(text) % (2**32))
        return [random.uniform(-1, 1) for _ in range(self.dimension)]
    
    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot_product / (norm_a * norm_b + 1e-8)
```

**主流Embedding模型**：

| 模型 | 维度 | 特点 |
|------|------|------|
| text-embedding-3-small | 1536 | OpenAI最新模型，性价比高 |
| text-embedding-3-large | 3072 | OpenAI最高精度 |
| BGE-large | 1024 | 国产开源，支持中英 |
| sentence-transformers | 可配置 | HuggingFace通用模型 |

### 3.5 完整 RAG 实现

```python
import json
from typing import Optional

class RAGSystem:
    """完整的RAG问答系统"""
    
    def __init__(self, 
                 embedder: SimpleEmbedder,
                 chunker: TextChunker,
                 llm_client):
        self.embedder = embedder
        self.chunker = chunker
        self.llm = llm_client
        self.document_store = []  # 文档块存储
        self.vector_store = []     # 对应向量
    
    def ingest(self, document: str, metadata: dict = None):
        """摄入文档"""
        chunks = self.chunker.chunk(document)
        
        for i, chunk in enumerate(chunks):
            embedding = self.embedder.embed(chunk["content"])
            self.document_store.append({
                "content": chunk["content"],
                "metadata": {**(metadata or {}), "chunk_id": i}
            })
            self.vector_store.append(embedding)
    
    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """检索最相关的文档块"""
        query_embedding = self.embedder.embed(query)
        
        # 计算相似度并排序
        similarities = [
            (i, self.embedder.cosine_similarity(query_embedding, vec))
            for i, vec in enumerate(self.vector_store)
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k结果
        return [
            {**self.document_store[i], "similarity": sim}
            for i, sim in similarities[:top_k]
        ]
    
    def answer(self, question: str, system_prompt: str = None) -> str:
        """基于检索结果生成回答"""
        # 1. 检索相关文档
        relevant_docs = self.retrieve(question, top_k=3)
        
        # 2. 构建上下文
        context = "\n\n".join([
            f"[文档{i+1}] {doc['content']}"
            for i, doc in enumerate(relevant_docs)
        ])
        
        # 3. 构建prompt
        prompt = f"""基于以下参考资料回答用户问题。

参考资料：
{context}

用户问题：{question}

要求：
1. 仅基于给定资料回答
2. 如果资料不足以回答，说明信息不足
3. 回答要准确标注参考来源

回答："""
        
        # 4. 调用LLM
        return self.llm.chat(prompt)
```

---

## 4. 上下文注入策略与优化

### 4.1 上下文注入的三种模式

```
┌─────────────────────────────────────────────────────────────┐
│                    上下文注入模式对比                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│    模式       │    说明       │    优点       │      缺点       │
├──────────────┼──────────────┼──────────────┼────────────────┤
│ Full Context │ 全部上下文    │ 信息完整      │ 成本高、慢      │
│              │ 直接注入       │ 简单          │ 注意力分散      │
├──────────────┼──────────────┼──────────────┼────────────────┤
│  Dynamic     │ 动态选择      │ 精准、成本低  │ 实现复杂        │
│  Injection   │ 相关部分注入   │              │ 可能遗漏        │
├──────────────┼──────────────┼──────────────┼────────────────┤
│  Hierarchical│ 分层抽象注入  │ 可处理超长    │ 信息损失风险    │
│              │ 摘要→细节     │ 上下文        │ 实现复杂        │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

### 4.2 上下文注入器实现

```python
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
        """构建完整Prompt"""
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
```

### 4.3 上下文优先级排序

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable

class InformationPriority(Enum):
    CRITICAL = 1   # 必须知道（角色定义、核心规则）
    HIGH = 2       # 高度相关（当前任务相关）
    MEDIUM = 3     # 中等相关（背景信息）
    LOW = 4        # 低相关（历史对话）

@dataclass
class ContextItem:
    content: str
    priority: InformationPriority
    source: str  # "user_profile", "conversation", "knowledge_base"
    token_size: int

class PriorityBasedContextManager:
    """基于优先级的上下文管理器"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.context_items: list[ContextItem] = []
    
    def add(self, content: str, priority: InformationPriority, 
            source: str, token_size: int = None):
        self.context_items.append(ContextItem(
            content=content,
            priority=priority,
            source=source,
            token_size=token_size or len(content) // 4
        ))
    
    def build_context(self) -> str:
        """按优先级构建上下文，超出限制则截断低优先级内容"""
        # 按优先级排序
        sorted_items = sorted(self.context_items, key=lambda x: x.priority.value)
        
        context_parts = []
        total_tokens = 0
        
        for item in sorted_items:
            if total_tokens + item.token_size <= self.max_tokens:
                context_parts.append(item.content)
                total_tokens += item.token_size
            else:
                break  # 超出限制，不再添加
        
        return "\n".join(context_parts)
```

### 4.4 上下文压缩技术

```python
class ContextCompressor:
    """上下文压缩器"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def compress(self, text: str, target_tokens: int = 500) -> str:
        """将文本压缩到目标token数"""
        prompt = f"""将以下文本压缩到约{target_tokens}个token，保留核心信息。

原文：
{text}

压缩后的文本："""
        
        return self.llm.chat(prompt)
    
    def extract_key_points(self, text: str, max_points: int = 5) -> str:
        """提取关键点"""
        prompt = f"""从以下文本中提取最多{max_points}个关键点，用简洁的 bullet point 列出。

文本：
{text}

关键点："""
        
        return self.llm.chat(prompt)
    
    def compress_conversation(self, messages: list[dict], 
                              max_tokens: int = 2000) -> list[dict]:
        """压缩对话历史"""
        # 将对话转为摘要
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        summary = self.compress(conversation_text, target_tokens=max_tokens)
        
        return [
            {"role": "system", "content": f"对话摘要：\n{summary}"}
        ]
```

### 4.5 上下文优化器

```python
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
        去重：移除相似度超过阈值的内容
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
        """压缩上下文：在句子边界处截断"""
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
        """按优先级截断：优先保留高相关度内容"""
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
```

### 4.6 Token预算管理器

```python
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
                remaining = context_budget - used_tokens
                if remaining > 100:
                    partial = self._trim_to_tokens(ctx.content, remaining)
                    context_parts.append(partial)
                break
        
        return {
            "system": system_final,
            "context": "\n\n".join(context_parts),
            "query": query_final
        }
```

### 4.7 混合检索策略

```python
from typing import Optional

class HybridRetriever:
    """混合检索器：结合关键词+向量+知识图谱"""
    
    def __init__(self, vector_store, keyword_index, knowledge_graph=None):
        self.vector_store = vector_store
        self.keyword_index = keyword_index
        self.knowledge_graph = knowledge_graph  # 可选
    
    def retrieve(self, query: str, top_k: int = 5,
                 vector_weight: float = 0.7) -> list[dict]:
        """混合检索"""
        # 1. 向量检索
        vector_results = self.vector_store.search(query, top_k=top_k*2)
        
        # 2. 关键词检索
        keyword_results = self.keyword_index.search(query, top_k=top_k*2)
        
        # 3. 知识图谱检索（如果可用）
        kg_results = []
        if self.knowledge_graph:
            kg_results = self.knowledge_graph.search(query, top_k=top_k)
        
        # 4. RRF融合算法 (Reciprocal Rank Fusion)
        fused = self._rrf_fusion(
            [vector_results, keyword_results, kg_results],
            weights=[vector_weight, 1-vector_weight, 0.3]
        )
        
        return fused[:top_k]
    
    def _rrf_fusion(self, result_lists: list[list], 
                    weights: list[float], k: int = 60) -> list[dict]:
        """RRF融合算法"""
        scores = {}
        
        for results, weight in zip(result_lists, weights):
            for rank, result in enumerate(results):
                doc_id = result.get("id", id(result))
                # RRF公式: 1/(k+rank)
                score = weight * (1 / (k + rank))
                scores[doc_id] = scores.get(doc_id, 0) + score
        
        # 按分数排序
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # 返回完整文档
        all_docs = {}
        for results in result_lists:
            for r in results:
                doc_id = r.get("id", id(r))
                all_docs[doc_id] = r
        
        return [all_docs[doc_id] for doc_id in sorted_ids]
```

---

## 5. 代码案例

### 5.1 完整可运行的 RAG 问答系统

```python
"""
RAG问答系统完整示例
依赖：pip install openai chromadb
"""

import os
import json
from typing import Optional

# ============== 配置 ==============
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# ============== 简化版组件 ==============

class SimpleVectorStore:
    """简化版向量存储（生产环境请用Chroma/FAISS）"""
    
    def __init__(self):
        self.vectors = []
        self.documents = []
    
    def add(self, text: str, vector: list[float], metadata: dict = None):
        self.vectors.append(vector)
        self.documents.append({
            "text": text,
            "metadata": metadata or {}
        })
    
    def search(self, query_vector: list[float], top_k: int = 3) -> list[dict]:
        # 简化的余弦相似度
        def cosine_sim(a, b):
            dot = sum(x*y for x,y in zip(a,b))
            norm = (sum(x*x for x in a) * sum(x*x for x in b)) ** 0.5
            return dot / norm if norm else 0
        
        similarities = [
            (i, cosine_sim(query_vector, vec))
            for i, vec in enumerate(self.vectors)
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {**self.documents[i], "score": sim}
            for i, sim in similarities[:top_k]
        ]

class SimpleEmbedder:
    """OpenAI Embedding封装"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model
        self.dimension = 1536
    
    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

class SimpleLLM:
    """OpenAI LLM封装"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model
    
    def chat(self, prompt: str, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content

# ============== RAG系统 ==============

class RAGQA:
    """RAG问答系统"""
    
    def __init__(self):
        self.embedder = SimpleEmbedder()
        self.llm = SimpleLLM()
        self.vector_store = SimpleVectorStore()
        self.documents = []
    
    def ingest_documents(self, docs: list[dict]):
        """摄入文档"""
        for doc in docs:
            text = doc["content"]
            metadata = doc.get("metadata", {})
            
            # 生成embedding
            vector = self.embedder.embed(text)
            
            # 存储
            self.vector_store.add(text, vector, metadata)
            self.documents.append({"text": text, "metadata": metadata})
    
    def query(self, question: str, top_k: int = 3) -> dict:
        """问答"""
        # 1. 将问题转为向量
        query_vector = self.embedder.embed(question)
        
        # 2. 检索相似文档
        results = self.vector_store.search(query_vector, top_k=top_k)
        
        # 3. 构建上下文
        context = "\n\n".join([
            f"[参考文档{i+1}] {r['text']}"
            for i, r in enumerate(results)
        ])
        
        # 4. 构建prompt并生成回答
        full_prompt = f"""你是一个专业的问答助手。请基于以下参考资料回答用户问题。

参考资料：
{context}

用户问题：{question}

要求：
1. 仅基于给定资料回答
2. 如果资料不足，说明信息不足
3. 在回答中注明参考来源

回答："""
        
        answer = self.llm.chat(full_prompt)
        
        return {
            "question": question,
            "answer": answer,
            "sources": [
                {"text": r["text"], "metadata": r["metadata"], "score": r["score"]}
                for r in results
            ]
        }


# ============== 运行示例 ==============

if __name__ == "__main__":
    # 初始化RAG系统
    rag = RAGQA()
    
    # 准备知识库
    knowledge_base = [
        {"content": "软件工程是应用计算机科学、数学、管理学等原理，开发高质量软件的工程学科。", "metadata": {"topic": "软件工程定义"}},
        {"content": "瀑布模型是最经典的软件开发过程模型，将开发过程分为需求分析、设计、实现、测试、部署、维护等阶段。", "metadata": {"topic": "瀑布模型"}},
        {"content": "敏捷开发是一类以人为核心、迭代增量的开发方法，包括Scrum、XP极限编程等实践。", "metadata": {"topic": "敏捷开发"}},
    ]
    
    # 摄入文档
    rag.ingest_documents(knowledge_base)
    
    # 问答
    result = rag.query("什么是敏捷开发？")
    print(f"回答: {result['answer']}")
```

### 5.2 记忆增强对话系统

```python
"""
记忆增强的对话系统
支持短期记忆、长期记忆、实体记忆
"""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field
import json

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

class MemoryEnhancedConversation:
    """带记忆的对话系统"""
    
    def __init__(self, llm_client, max_short_memory: int = 10):
        self.llm = llm_client
        
        # 短期记忆：最近N轮对话
        self.short_term: list[Message] = []
        self.max_short_memory = max_short_memory
        
        # 长期记忆：关键信息持久化
        self.long_term: dict[str, dict] = {}
    
    def add_message(self, role: str, content: str):
        """添加消息到短期记忆"""
        self.short_term.append(Message(role, content))
        
        if len(self.short_term) > self.max_short_memory:
            self.short_term.pop(0)
    
    def get_short_memory(self) -> str:
        """获取短期记忆文本"""
        return "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in self.short_term
        ])
    
    def store_fact(self, key: str, value: str, metadata: dict = None):
        """存储事实到长期记忆"""
        self.long_term[key] = {
            "value": value,
            "metadata": metadata or {},
            "updated_at": datetime.now().isoformat()
        }
    
    def recall_fact(self, key: str) -> Optional[str]:
        """回忆特定事实"""
        entry = self.long_term.get(key)
        return entry["value"] if entry else None
    
    def remember_entity(self, entity: str, description: str):
        """记忆实体信息"""
        self.store_fact(f"entity:{entity}", description)
    
    def chat(self, user_input: str) -> str:
        """带记忆的对话"""
        self.add_message("user", user_input)
        
        # 收集上下文
        context_parts = []
        
        for key, entry in self.long_term.items():
            context_parts.append(f"[记忆] {key}: {entry['value']}")
        
        if self.short_term:
            context_parts.append(f"[最近对话]\n{self.get_short_memory()}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""你是一个有帮助的AI助手，具有良好的对话记忆能力。

当前上下文：
{context}

当前对话：
user: {user_input}

请基于上下文信息回答用户问题。"""
        
        response = self.llm.chat(prompt)
        self.add_message("assistant", response)
        
        return response
```

---

## 6. 教学场景案例

### 案例一：课程问答机器人

**场景**：为软件学院创建一个RAG驱动的课程问答机器人。

```python
class CourseQARobot:
    """课程问答机器人"""
    
    def __init__(self, course_materials: list[dict]):
        self.rag = RAGQA()
        self.rag.ingest_documents(course_materials)
        
        self.system_prompt = """你是一个软件学院的课程问答助手。你可以回答关于：
- 软件工程课程内容
- 编程作业相关问题
- 考试准备问题
- 技术概念解释

请用简洁清晰的语言回答，适合本科生理解。"""
    
    def answer(self, question: str) -> dict:
        result = self.rag.query(question)
        return result
```

**教学点**：
- RAG文档摄入与检索
- 上下文窗口管理
- 如何根据领域定制知识库

### 案例二：智能论文辅导助手

**场景**：帮助学生理解和分析学术论文。

```python
class PaperTutor:
    """论文辅导助手"""
    
    def __init__(self, paper_text: str):
        self.paper_text = paper_text
        self.summary = None
        self.key_concepts = {}
    
    def summarize(self, llm) -> str:
        """生成论文摘要"""
        prompt = f"""请为以下论文生成一个简洁的摘要（200字以内），包括：
1. 研究问题
2. 主要贡献
3. 核心方法

论文：
{self.paper_text[:5000]}..."""
        
        self.summary = llm.chat(prompt)
        return self.summary
    
    def answer_question(self, question: str, llm) -> str:
        """基于论文回答问题"""
        context = f"论文摘要：\n{self.summary or '未生成'}\n\n论文内容：\n{self.paper_text[:8000]}"
        
        prompt = f"""基于以下论文内容回答学生问题。

{context}

学生问题：{question}

要求：
1. 准确基于论文内容回答
2. 如果论文没有涉及这个问题，说明论文未涉及

回答："""
        
        return llm.chat(prompt)
```

**教学点**：
- 长上下文处理
- 文本摘要技术
- 教学对话设计

### 案例三：代码审查上下文助手

**场景**：在代码审查中，根据代码上下文提供智能建议。

```python
class CodeReviewContext:
    """代码审查上下文助手"""
    
    def __init__(self, codebase_summary: str = ""):
        self.codebase_summary = codebase_summary
        self.review_history = []
    
    def prepare_review_context(self, 
                                file_path: str,
                                file_content: str,
                                diff: str = None) -> str:
        """准备代码审查上下文"""
        
        context_parts = [
            f"【代码库概述】\n{self.codebase_summary}",
            f"【待审查文件】{file_path}\n\n{file_content}"
        ]
        
        if diff:
            context_parts.append(f"【代码变更】\n{diff}")
        
        if self.review_history:
            context_parts.append(
                f"【近期审查记录】\n" + 
                "\n".join(self.review_history[-3:])
            )
        
        return "\n\n".join(context_parts)
    
    def review_code(self, file_path: str, file_content: str, 
                    diff: str, llm) -> dict:
        """审查代码"""
        context = self.prepare_review_context(file_path, file_content, diff)
        
        prompt = f"""你是一个专业的代码审查助手。请审查以下代码变更。

{context}

请从以下维度进行审查：
1. **正确性**：逻辑是否正确，边界条件是否处理
2. **安全性**：是否有潜在的安全漏洞
3. **性能**：是否有性能问题
4. **可维护性**：代码是否清晰易读
5. **最佳实践**：是否符合该语言的编码规范

审查结果："""
        
        review_result = llm.chat(prompt)
        self.review_history.append(f"{file_path}: 审查完成")
        
        return {
            "file": file_path,
            "review": review_result
        }
```

**教学点**：
- 上下文注入策略
- 特定领域（代码审查）的prompt设计
- 对话历史的利用

### 案例四：NL2SQL问答系统

**场景**：将自然语言问题转换为SQL查询。

```python
DATABASE_QA_PROMPT = """【角色】
你是一个SQL查询生成专家，能够将自然语言问题转换为准确的SQL查询。

【数据库Schema】
{schema}

【查询要求】
1. 生成的SQL必须语法正确
2. 注意字段类型和约束
3. 适当使用JOIN、子查询
4. 对复杂查询添加注释说明

【示例】
问: 找出软件学院平均绩点最高的学生
答: 
```sql
SELECT name, AVG(gpa) as avg_gpa
FROM students
WHERE major = '软件工程'
GROUP BY student_id, name
ORDER BY avg_gpa DESC
LIMIT 1
```

【当前问题】
{question}

【生成的SQL】"""
```

### 案例五：学院智能客服

**场景**：软件学院智能助学助手"小软"。

```python
CUSTOMER_SERVICE_PROMPT = """【角色】
你是软件学院智能助学的"小软"，专门回答学生问题。

【背景知识】
学院基本信息:
- 成立时间: 2002年
- 本科专业: 软件工程、计算机科学与技术、数据科学与大数据技术
- 研究生方向: 软件工程、计算机技术、人工智能

【政策知识库】
{policy_kb}

【FAQ知识库】
{faq_kb}

【当前对话】
{conversation_history}

【用户问题】
{user_question}

【回答要求】
1. 友好、专业、易懂
2. 如果问题涉及政策，说明依据
3. 如果不确定，说明会转达老师
4. 回答尽量简洁，不超过200字
5. 必要时引导到相关资源"""
```

---

## 课程总结

### 核心知识体系

| 模块 | 核心要点 |
|------|---------|
| **核心概念** | 上下文工程≠提示词工程，上下文工程关注信息的系统化管理 |
| **上下文管理** | 短期/长期/情景记忆、滚动窗口、优先级排序 |
| **RAG技术** | 文档分块、向量检索、混合检索、上下文构建 |
| **优化策略** | 动态注入、分层抽象、压缩与摘要 |
| **代码案例** | RAG问答、记忆对话、代码审查助手 |

### 学习路径建议

```
1. 基础概念 → 2. 上下文管理 → 3. RAG技术 → 4. 注入优化 → 5. 实战项目
```

### 参考资源

- 课程源码：`/root/context-engineering-course/`
- 示例代码：`/root/context-engineering-course/examples/`
- 配置文件：`/root/context-engineering-course/config.py`
- LLM客户端：`/root/context-engineering-course/utils/llm_client.py`

---

*课程资源路径：`/root/context-engineering-course/`*
