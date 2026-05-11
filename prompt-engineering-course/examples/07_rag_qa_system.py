"""
examples/07_rag_qa_system.py
RAG (Retrieval-Augmented Generation) 问答系统示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json


@dataclass
class Document:
    """文档类"""
    content: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    """检索结果"""
    content: str
    score: float
    metadata: Dict


class SimpleRAG:
    """
    简化的RAG系统
    
    功能:
    1. 文档存储
    2. 关键词检索
    3. 基于检索结果生成答案
    """
    
    def __init__(self, config: LLMConfig):
        self.client = LLMClient(config)
        self.documents: List[Document] = []
        self.name = "SimpleRAG"
    
    def add_documents(self, docs: List[Document]):
        """添加文档到知识库"""
        self.documents.extend(docs)
        print(f"已添加 {len(docs)} 个文档，当前共 {len(self.documents)} 个文档")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievedChunk]:
        """
        简单检索（实际应用中应使用向量数据库）
        这里用TF-IDF风格的词频计算做演示
        """
        query_words = self._tokenize(query.lower())
        results = []
        
        for doc in self.documents:
            doc_words = self._tokenize(doc.content.lower())
            
            # 计算词频重叠
            intersection = query_words & doc_words
            if intersection:
                score = len(intersection) / max(len(query_words), 1)
                results.append(RetrievedChunk(
                    content=doc.content,
                    score=score,
                    metadata=doc.metadata
                ))
        
        # 排序返回top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def _tokenize(self, text: str) -> set:
        """简单分词"""
        # 去除标点，提取中英文词汇
        import re
        # 英文分词
        english_words = set(re.findall(r'[a-zA-Z]+', text.lower()))
        # 简单中文分词（按字符）
        chinese_chars = set(re.findall(r'[\u4e00-\u9fff]+', text.lower()))
        chinese_words = set()
        for chars in chinese_chars:
            # 简单的滑动窗口分词
            for i in range(len(chars)):
                for j in range(i+2, min(i+5, len(chars)+1)):
                    chinese_words.add(chars[i:j])
        
        return english_words | chinese_words
    
    def generate_answer(self, query: str, context_docs: List[RetrievedChunk]) -> str:
        """基于检索结果生成答案"""
        
        context = "\n\n".join([
            f"【文档{i+1}】{doc.content}\n来源: {doc.metadata.get('source', '未知')}"
            for i, doc in enumerate(context_docs)
        ])
        
        prompt = f"""基于以下参考资料回答问题。如果资料中没有相关信息，请明确说明。

【问题】{query}

【参考资料】
{context}

【回答要求】
1. 优先使用参考资料中的信息
2. 引用时标注来源
3. 如需补充知识库之外的信息，请标注"根据常识..."
4. 回答要准确、简洁、有条理

【回答】"""
        
        return self.client.chat([{"role": "user", "content": prompt}])
    
    def query(self, question: str, top_k: int = 3) -> str:
        """完整问答流程"""
        # 1. 检索相关文档
        docs = self.retrieve(question, top_k)
        
        if not docs:
            return "抱歉，知识库中没有找到相关信息。"
        
        # 2. 生成答案
        return self.generate_answer(question, docs)
    
    def batch_query(self, questions: List[str]) -> List[Dict]:
        """批量问答"""
        results = []
        for q in questions:
            answer = self.query(q)
            results.append({"question": q, "answer": answer})
        return results


class EnhancedRAG(SimpleRAG):
    """增强版RAG，支持更多功能"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.name = "EnhancedRAG"
    
    def hybrid_search(self, query: str, top_k: int = 3) -> List[RetrievedChunk]:
        """
        混合搜索：结合语义和关键词
        这里简化实现，实际应使用向量相似度
        """
        # 关键词匹配
        keyword_results = self.retrieve(query, top_k * 2)
        
        # 重排序：考虑文档质量和新鲜度
        for doc in keyword_results:
            # 模拟相关性调整
            source = doc.metadata.get("source", "")
            if "官方文档" in source:
                doc.score *= 1.2
        
        return sorted(keyword_results, key=lambda x: x.score, reverse=True)[:top_k]
    
    def query_with_citation(self, question: str, top_k: int = 3) -> Dict:
        """
        带引用的问答
        返回结构化结果
        """
        docs = self.retrieve(question, top_k)
        
        if not docs:
            return {
                "answer": "抱歉，知识库中没有找到相关信息。",
                "sources": []
            }
        
        answer = self.generate_answer(question, docs)
        
        return {
            "answer": answer,
            "sources": [
                {
                    "content": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content,
                    "source": doc.metadata.get("source", "未知"),
                    "relevance": round(doc.score, 3)
                }
                for doc in docs
            ]
        }


def rag_demo():
    """RAG系统演示"""
    
    # 初始化
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    rag = SimpleRAG(config)
    
    # 准备知识库文档
    docs = [
        Document(
            content="Python是一种高级编程语言，由Guido van Rossum于1991年创建。特点是简洁易读的语法和强大的标准库支持。",
            metadata={"source": "python_basics.txt", "category": "语言基础"}
        ),
        Document(
            content="FastAPI是一个现代、快速的Python Web框架，用于构建API。基于Pydantic和Starlette，支持异步编程。性能接近NodeJS和Go。",
            metadata={"source": "fastapi_guide.txt", "category": "Web框架"}
        ),
        Document(
            content="Django是Python的全栈Web框架，包含ORM、管理后台、认证系统等。适合构建大型内容管理系统。",
            metadata={"source": "django_guide.txt", "category": "Web框架"}
        ),
        Document(
            content="关系型数据库如PostgreSQL使用SQL语言，支持事务和复杂查询。非关系型数据库如MongoDB使用文档存储模型。",
            metadata={"source": "database_intro.txt", "category": "数据库"}
        ),
        Document(
            content="Docker是一个开源容器化平台，可以打包应用及其依赖，实现一致的运行环境。Dockerfile用于定义镜像构建步骤。",
            metadata={"source": "docker_guide.txt", "category": "DevOps"}
        ),
        Document(
            content="Git是分布式版本控制系统，用于跟踪代码变更和协作开发。常用命令包括git add, git commit, git push等。",
            metadata={"source": "git_guide.txt", "category": "开发工具"}
        ),
    ]
    rag.add_documents(docs)
    
    # 问答示例
    questions = [
        "Python语言有什么特点？",
        "FastAPI和Django有什么区别？",
        "Docker能用来做什么？"
    ]
    
    print("\n" + "=" * 50)
    print("RAG 问答系统演示")
    print("=" * 50)
    
    for q in questions:
        print(f"\n问题: {q}")
        print("-" * 40)
        answer = rag.query(q)
        print(f"回答: {answer}\n")


def enhanced_rag_demo():
    """增强版RAG演示"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    rag = EnhancedRAG(config)
    
    docs = [
        Document(
            content="Python的数据类型包括：整数int、浮点数float、字符串str、布尔值bool、列表list、字典dict等。",
            metadata={"source": "Python官方文档", "category": "基础"}
        ),
        Document(
            content="FastAPI会自动为API生成OpenAPI文档，可在/docs路径访问。",
            metadata={"source": "FastAPI官方文档", "category": "框架"}
        ),
    ]
    rag.add_documents(docs)
    
    print("\n" + "=" * 50)
    print("增强版RAG - 带引用查询")
    print("=" * 50)
    
    result = rag.query_with_citation("Python有哪些数据类型？")
    print(f"\n回答:\n{result['answer']}")
    print("\n参考来源:")
    for src in result['sources']:
        print(f"  - [{src['source']}] 相关度:{src['relevance']}")


def build_knowledge_base_demo():
    """从文件构建知识库示例"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    rag = SimpleRAG(config)
    
    # 模拟从文件加载
    sample_docs = [
        {"content": "机器学习是人工智能的一个分支，研究如何让计算机从数据中学习。", "source": "ml_intro.txt"},
        {"content": "监督学习需要标注数据，无监督学习不需要标注。", "source": "ml_types.txt"},
        {"content": "神经网络模仿生物神经元工作原理，由多层节点组成。", "source": "nn_intro.txt"},
        {"content": "Transformer架构使用自注意力机制，是GPT等大模型的基础。", "source": "transformer.txt"},
    ]
    
    for doc_data in sample_docs:
        rag.add_documents([
            Document(content=doc_data["content"], metadata={"source": doc_data["source"]})
        ])
    
    # 知识库问答
    print("\n" + "=" * 50)
    print("知识库构建示例")
    print("=" * 50)
    
    questions = [
        "什么是机器学习？",
        "监督学习和无监督学习有什么区别？",
        "Transformer是什么？"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {rag.query(q)}")


if __name__ == "__main__":
    rag_demo()
    enhanced_rag_demo()
    build_knowledge_base_demo()
