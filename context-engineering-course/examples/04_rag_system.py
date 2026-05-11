"""
examples/04_rag_system.py
完整RAG系统实现
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import hashlib


# ==================== 核心组件 ====================

@dataclass
class Document:
    """文档"""
    id: str
    content: str
    metadata: Dict = field(default_factory=dict)
    
    @classmethod
    def from_text(cls, text: str, metadata: Dict = None):
        doc_id = hashlib.md5(text.encode()).hexdigest()[:8]
        return cls(id=doc_id, content=text, metadata=metadata or {})


class SimpleChunker:
    """文档分块器"""
    
    @staticmethod
    def chunk(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks


class SimpleEmbedder:
    """
    简化嵌入器
    
    实际生产环境应使用:
    - OpenAI text-embedding-3-small
    - BGE (BAAI General Embedding)
    - Sentence-Transformers
    """
    
    def __init__(self, dim: int = 128):
        self.dim = dim
    
    def embed(self, text: str) -> List[float]:
        """生成文本嵌入向量（简化实现）"""
        h = hashlib.md5(text.encode()).digest()
        vec = []
        for i in range(self.dim):
            byte_val = h[i % len(h)]
            vec.append((byte_val + i * 17) % 100 / 100.0)
        norm = sum(x*x for x in vec) ** 0.5
        return [x/norm for x in vec] if norm > 0 else vec


class VectorStore:
    """简单向量存储"""
    
    def __init__(self):
        self.chunks: Dict[str, Dict] = {}
    
    def add(self, chunk_id: str, content: str, embedding: List[float], metadata: Dict = None):
        self.chunks[chunk_id] = {
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {}
        }
    
    def search(self, query_emb: List[float], top_k: int = 5) -> List[Dict]:
        """余弦相似度搜索"""
        scores = []
        for cid, chunk in self.chunks.items():
            sim = sum(a*b for a,b in zip(query_emb, chunk["embedding"]))
            scores.append((sim, cid, chunk))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": cid,
                "content": chunk["content"],
                "score": sim,
                "metadata": chunk["metadata"]
            }
            for sim, cid, chunk in scores[:top_k]
        ]


# ==================== RAG系统 ====================

class RAGSystem:
    """
    检索增强生成系统
    
    完整流程:
    1. index_documents() - 文档索引
    2. query() - 问答
    """
    
    def __init__(self, config: LLMConfig):
        self.client = LLMClient(config)
        self.chunker = SimpleChunker()
        self.embedder = SimpleEmbedder()
        self.vector_store = VectorStore()
    
    def index_documents(self, documents: List[Document], chunk_size: int = 300):
        """索引文档"""
        for doc in documents:
            chunks = self.chunker.chunk(doc.content, chunk_size)
            for i, chunk_text in enumerate(chunks):
                chunk_id = f"{doc.id}_{i}"
                embedding = self.embedder.embed(chunk_text)
                self.vector_store.add(
                    chunk_id,
                    chunk_text,
                    embedding,
                    {"source": doc.metadata.get("source", "unknown")}
                )
        print(f"索引完成: {len(documents)} 文档, {len(self.vector_store.chunks)} 块")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """检索相关文档"""
        q_emb = self.embedder.embed(query)
        return self.vector_store.search(q_emb, top_k)
    
    def generate(self, question: str, contexts: List[Dict]) -> str:
        """基于检索结果生成回答"""
        context_parts = []
        for i, ctx in enumerate(contexts, 1):
            context_parts.append(
                f"【文档{i}】来源:{ctx['metadata'].get('source','未知')}\n"
                f"内容: {ctx['content']}"
            )
        context = "\n\n".join(context_parts)
        
        prompt = f"""基于以下参考资料回答问题：

【参考资料】
{context}

【问题】
{question}

【回答要求】
1. 优先使用参考资料
2. 标注来源
3. 如需补充说明请注明"""

        return self.client.chat([{"role": "user", "content": prompt}])
    
    def query(self, question: str, top_k: int = 3) -> Dict:
        """完整的RAG问答流程"""
        # 1. 检索
        results = self.retrieve(question, top_k)
        
        if not results:
            return {
                "question": question,
                "answer": "未找到相关内容",
                "sources": []
            }
        
        # 2. 生成
        answer = self.generate(question, results)
        
        # 3. 返回结果
        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "content": r["content"][:100] + "..." if len(r["content"]) > 100 else r["content"],
                    "source": r["metadata"].get("source", "未知"),
                    "score": round(r["score"], 3)
                }
                for r in results
            ]
        }


# ==================== 演示 ====================

def demo():
    """演示"""
    
    # 准备文档
    docs = [
        Document.from_text(
            "Python是一种高级编程语言，由Guido van Rossum于1991年创建。"
            "它以简洁易读的语法著称，支持多种编程范式，包括面向对象、函数式和过程式编程。"
            "Python拥有丰富的标准库和第三方包生态系统。",
            {"source": "Python简介.txt"}
        ),
        Document.from_text(
            "FastAPI是现代Python Web框架，用于构建API。"
            "它基于Pydantic和Starlette，支持异步编程，性能接近NodeJS和Go。"
            "FastAPI自动生成OpenAPI文档，可以在/docs路径访问。"
            "它还具有自动数据验证和序列化功能。",
            {"source": "FastAPI指南.txt"}
        ),
        Document.from_text(
            "关系型数据库如PostgreSQL使用SQL语言，支持事务和复杂查询。"
            "它们遵循ACID原则：原子性、一致性、隔离性、持久性。"
            "非关系型数据库如MongoDB使用文档存储模型，适合灵活的数据结构和大数据场景。",
            {"source": "数据库基础.txt"}
        ),
        Document.from_text(
            "Docker是一个开源容器化平台，可以打包应用及其依赖，实现一致的运行环境。"
            "Dockerfile用于定义镜像构建步骤，docker-compose用于定义多容器应用。"
            "常见的Docker命令包括：docker build, docker run, docker ps等。",
            {"source": "Docker指南.txt"}
        ),
    ]
    
    # 初始化RAG
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    rag = RAGSystem(config)
    
    # 索引文档
    print("=" * 50)
    print("RAG 系统演示")
    print("=" * 50)
    rag.index_documents(docs)
    
    # 问答
    questions = [
        "Python语言有什么特点？",
        "FastAPI适合做什么？",
        "Docker能用来做什么？"
    ]
    
    for q in questions:
        print(f"\n问题: {q}")
        print("-" * 40)
        result = rag.query(q)
        print(f"回答:\n{result['answer']}")
        print(f"\n来源:")
        for src in result['sources']:
            print(f"  - [{src['source']}] 相关度:{src['score']}")
    
    # 注意：需要设置 OPENAI_API_KEY 环境变量才能实际调用API
    # export OPENAI_API_KEY='your-key'


if __name__ == "__main__":
    demo()
