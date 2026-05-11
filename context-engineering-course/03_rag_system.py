"""
RAG系统实现 - 代码示例
========================

本模块展示完整的RAG（检索增强生成）系统实现：
1. 文档处理和分块
2. Embedding生成
3. 向量存储和检索
4. RAG流水线整合
"""

import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Callable


# ============================================================
# 1. 文档处理
# ============================================================

@dataclass
class Document:
    """文档对象"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    @classmethod
    def from_text(cls, text: str, metadata: Dict = None) -> "Document":
        """从文本创建文档"""
        doc_id = hashlib.md5(text.encode()).hexdigest()
        return cls(id=doc_id, content=text, metadata=metadata or {})


class TextChunker:
    """文本分块器"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, text: str, metadata: Dict = None) -> List[Document]:
        """分块主方法"""
        text = self._clean_text(text)
        paragraphs = self._split_paragraphs(text)
        
        chunks = []
        current = ""
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)
            
            if para_tokens > self.chunk_size:
                if current:
                    chunks.append(Document.from_text(current, metadata))
                    current = ""
                    current_tokens = 0
                
                chunks.extend(self._split_long_paragraph(para, metadata))
                continue
            
            if current_tokens + para_tokens > self.chunk_size:
                if current:
                    chunks.append(Document.from_text(current, metadata))
                
                current = self._get_overlap(current, para)
                current_tokens = self._estimate_tokens(current)
            
            current += para + "\n"
            current_tokens += para_tokens
        
        if current and self._estimate_tokens(current) >= self.min_chunk_size:
            chunks.append(Document.from_text(current.strip(), metadata))
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """按段落分割"""
        sentences = re.split(r'[。！？.!?\n]', text)
        paragraphs = []
        current = []
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            current.append(sent)
            if len(current) >= 4:
                paragraphs.append(' '.join(current))
                current = []
        
        if current:
            paragraphs.append(' '.join(current))
        
        return [p for p in paragraphs if p]
    
    def _split_long_paragraph(self, text: str, metadata: Dict) -> List[Document]:
        """分割长段落"""
        words = text.split()
        chunks = []
        current = []
        current_tokens = 0
        
        for word in words:
            word_tokens = self._estimate_tokens(word)
            
            if current_tokens + word_tokens > self.chunk_size:
                if current:
                    chunks.append(Document.from_text(' '.join(current), metadata))
                    overlap_words = current[-min(5, len(current)):]
                    current = overlap_words + [word]
                    current_tokens = sum(self._estimate_tokens(w) for w in current)
                else:
                    current = [word[:self.chunk_size * 4]]
                    current_tokens = self.chunk_size
            else:
                current.append(word)
                current_tokens += word_tokens
        
        if current:
            chunks.append(Document.from_text(' '.join(current), metadata))
        
        return chunks
    
    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
    
    def _get_overlap(self, text: str, new_text: str) -> str:
        """获取重叠文本"""
        overlap_chars = self.chunk_overlap * 4
        if len(text) <= overlap_chars:
            return text + " " + new_text
        return text[-overlap_chars:] + " " + new_text


# ============================================================
# 2. Embedding生成
# ============================================================

class Embedder(ABC):
    """Embedding生成器抽象类"""
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass
    
    def embed_single(self, text: str) -> List[float]:
        return self.embed([text])[0]


class TFIDFEmbedder(Embedder):
    """TF-IDF Embedder（演示用）"""
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.vocab: Dict[str, int] = {}
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        
        for text in texts:
            tokens = self._tokenize(text)
            tf = self._compute_tf(tokens)
            
            vector = [0.0] * self.dim
            for i, term in enumerate(tf.keys()):
                if term not in self.vocab:
                    self.vocab[term] = len(self.vocab) % self.dim
                vector[self.vocab[term]] = tf[term]
            
            # 归一化
            norm = sum(v * v for v in vector) ** 0.5
            if norm > 0:
                vector = [v / norm for v in vector]
            
            vectors.append(vector)
        
        return vectors
    
    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return text.split()
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        
        max_tf = max(tf.values()) if tf else 1
        return {k: v / max_tf for k, v in tf.items()}


# ============================================================
# 3. 向量存储
# ============================================================

class VectorStore(ABC):
    """向量存储抽象类"""
    
    @abstractmethod
    def add(self, documents: List[Document]) -> None:
        pass
    
    @abstractmethod
    def search(self, query: List[float], top_k: int) -> List[Tuple[Document, float]]:
        pass


class SimpleVectorStore(VectorStore):
    """简单内存向量存储"""
    
    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.documents: Dict[str, Document] = {}
        self.index: Dict[str, List[float]] = {}
    
    def add(self, documents: List[Document]) -> None:
        contents = [doc.content for doc in documents]
        embeddings = self.embedder.embed(contents)
        
        for doc, emb in zip(documents, embeddings):
            doc.embedding = emb
            self.documents[doc.id] = doc
            self.index[doc.id] = emb
    
    def search(self, query: List[float], top_k: int) -> List[Tuple[Document, float]]:
        scores = []
        
        for doc_id, vec in self.index.items():
            score = self._cosine(query, vec)
            scores.append((doc_id, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in scores[:top_k]:
            if doc_id in self.documents:
                results.append((self.documents[doc_id], score))
        
        return results
    
    def _cosine(self, a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))
    
    def count(self) -> int:
        return len(self.documents)


# ============================================================
# 4. RAG流水线
# ============================================================

class RAGPipeline:
    """
    RAG检索增强生成流水线
    """
    
    def __init__(
        self,
        chunker: TextChunker = None,
        embedder: Embedder = None,
        vector_store: VectorStore = None,
        llm_call: Callable = None
    ):
        self.chunker = chunker or TextChunker()
        self.embedder = embedder or TFIDFEmbedder()
        self.vector_store = vector_store or SimpleVectorStore(self.embedder)
        self.llm = llm_call or self._default_llm
    
    def _default_llm(self, prompt: str) -> str:
        return f"[模拟回复] 基于上下文: {prompt[:100]}..."
    
    def index_documents(self, texts: List[str], metadata_list: List[Dict] = None) -> int:
        """索引文档"""
        docs = []
        for i, text in enumerate(texts):
            meta = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
            docs.append(Document.from_text(text, meta))
        
        chunks = []
        for doc in docs:
            chunks.extend(self.chunker.chunk(doc.content, doc.metadata))
        
        self.vector_store.add(chunks)
        return len(chunks)
    
    def retrieve(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict]:
        """检索相关文档"""
        query_emb = self.embedder.embed_single(query)
        results = self.vector_store.search(query_emb, top_k)
        
        return [
            {
                "content": doc.content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
            if score >= threshold
        ]
    
    def generate(
        self,
        query: str,
        system_prompt: str = None,
        top_k: int = 5,
        return_context: bool = False
    ) -> Dict[str, Any]:
        """生成回答"""
        docs = self.retrieve(query, top_k)
        
        context_parts = []
        for i, doc in enumerate(docs):
            context_parts.append(f"[{i+1}] {doc['content']}")
            if doc.get("metadata"):
                context_parts.append(f"    来源: {doc['metadata'].get('source', '未知')}")
        
        context = "\n".join(context_parts)
        
        if system_prompt:
            prompt = f"{system_prompt}\n\n参考上下文：\n{context}\n\n问题：{query}\n\n回答："
        else:
            prompt = f"""基于以下参考上下文回答问题。

参考上下文：
{context}

问题：{query}

回答："""
        
        answer = self.llm(prompt)
        
        result = {"answer": answer, "sources": docs}
        
        if return_context:
            result["context"] = context
            result["retrieved_count"] = len(docs)
        
        return result


# ============================================================
# 演示代码
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("RAG系统演示")
    print("="*60)
    
    # 初始化RAG流水线
    rag = RAGPipeline()
    
    # 准备知识库
    knowledge_base = [
        {
            "text": """Python是一种高级编程语言，由Guido van Rossum于1991年创建。
            Python以其简洁易读的语法著称，广泛应用于Web开发、数据科学、AI等领域。""",
            "source": "Python简介"
        },
        {
            "text": """机器学习是人工智能的一个子集，通过算法让计算机从数据中学习。
            主要类型包括监督学习、无监督学习和强化学习。""",
            "source": "机器学习基础"
        },
        {
            "text": """深度学习使用多层神经网络进行学习，在图像识别、语音识别、
            自然语言处理等领域取得突破性进展。""",
            "source": "深度学习基础"
        },
        {
            "text": """RAG（检索增强生成）是一种结合检索和生成的AI技术，
            可以有效解决LLM的幻觉问题和知识过时问题。""",
            "source": "RAG技术"
        },
    ]
    
    # 索引文档
    texts = [item["text"] for item in knowledge_base]
    metas = [{"source": item["source"]} for item in knowledge_base]
    count = rag.index_documents(texts, metas)
    print(f"\n✓ 索引了 {count} 个文档块\n")
    
    # 检索示例
    print("="*60)
    print("检索演示")
    print("="*60)
    
    queries = [
        "什么是机器学习？",
        "深度学习和AI有什么关系？",
        "RAG技术有什么用？",
    ]
    
    for q in queries:
        print(f"\n查询: {q}")
        results = rag.retrieve(q, top_k=2)
        for i, r in enumerate(results, 1):
            print(f"  [{i}] Score: {r['score']:.4f}")
            print(f"      {r['content'][:60]}...")
    
    # 生成示例
    print("\n" + "="*60)
    print("生成演示")
    print("="*60)
    
    def mock_llm(prompt: str) -> str:
        if "Python" in prompt:
            return "Python是一种高级编程语言，由Guido van Rossum创建。它的语法简洁易读，广泛用于Web开发、数据科学和AI领域。"
        elif "机器学习" in prompt:
            return "机器学习是AI的一个分支，通过算法让计算机从数据中自动学习，无需明确编程。主要包括监督学习、无监督学习和强化学习。"
        elif "RAG" in prompt:
            return "RAG（检索增强生成）结合了检索系统和生成模型，可以利用外部知识库增强LLM的回复质量，有效减少幻觉问题。"
        return "根据上下文，这是一个技术相关的问题。"
    
    rag.llm = mock_llm
    
    for q in queries:
        result = rag.generate(q, return_context=True)
        print(f"\n问题: {q}")
        print(f"回答: {result['answer']}")
        print(f"检索到 {result['retrieved_count']} 个相关文档")
