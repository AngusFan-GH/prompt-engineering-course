"""
适合教学的场景化案例

包含三个完整案例:
1. 智能客服Agent
2. 数据处理Pipeline Agent
3. 研究助手Agent
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import json
import asyncio
import re


# ==================== 案例一：智能客服Agent ====================

class Intent(Enum):
    """用户意图枚举"""
    GREETING = "greeting"
    PRODUCT_QUERY = "product_query"
    ORDER_STATUS = "order_status"
    RETURN_REQUEST = "return_request"
    GENERAL_QUESTION = "general_question"
    GOODBYE = "goodbye"


@dataclass
class ConversationContext:
    """对话上下文"""
    user_id: str = ""
    session_id: str = ""
    current_intent: Optional[Intent] = None
    mentioned_products: List[str] = field(default_factory=list)
    mentioned_order_id: str = ""
    sentiment: str = "neutral"
    turn_count: int = 0
    collected_info: Dict[str, Any] = field(default_factory=dict)


class SmartCustomerService:
    """
    智能客服Agent
    
    功能：
    - 意图识别
    - 多轮对话
    - 订单查询
    - 退换货处理
    - 情感分析
    """
    
    def __init__(self):
        self.tools = self._register_tools()
        self.context = ConversationContext()
    
    def _register_tools(self) -> Dict[str, Callable]:
        """注册工具"""
        return {
            "search_product": self._search_product,
            "get_order_status": self._get_order_status,
            "initiate_return": self._initiate_return,
            "get_return_policy": self._get_return_policy,
            "transfer_to_human": self._transfer_to_human,
            "analyze_sentiment": self._analyze_sentiment,
        }
    
    def _search_product(self, query: str, category: str = None) -> Dict:
        """搜索商品"""
        products = [
            {"id": "P001", "name": "iPhone 15 Pro", "price": 7999, "stock": 100},
            {"id": "P002", "name": "MacBook Pro 14", "price": 15999, "stock": 50},
            {"id": "P003", "name": "AirPods Pro", "price": 1899, "stock": 200},
        ]
        results = [p for p in products if query.lower() in p["name"].lower()]
        return {"count": len(results), "products": results}
    
    def _get_order_status(self, order_id: str) -> Dict:
        """查询订单状态"""
        orders = {
            "ORD001": {"status": "shipped", "eta": "2024-01-15", "tracking": "SF123456"},
            "ORD002": {"status": "processing", "eta": None, "tracking": None},
            "ORD003": {"status": "delivered", "eta": "2024-01-10", "tracking": "SF789012"},
        }
        if order_id in orders:
            return {"order_id": order_id, **orders[order_id]}
        return {"error": f"Order {order_id} not found"}
    
    def _initiate_return(self, order_id: str, reason: str) -> Dict:
        """发起退换货"""
        return {
            "return_id": f"RET{order_id}",
            "status": "approved",
            "instructions": "请将商品寄至: 北京市朝阳区xxx，收件人: 售后部",
            "refund_amount": "预计3-5个工作日退款"
        }
    
    def _get_return_policy(self) -> str:
        """获取退换货政策"""
        return """
退换货政策:
1. 商品签收后7天内可申请退换货
2. 商品需保持完好，未经使用
3. 定制商品不支持退换货
4. 退款将在收到商品后3-5个工作日处理
"""
    
    def _transfer_to_human(self, reason: str) -> str:
        """转人工客服"""
        return "正在为您转接人工客服，请稍候..."
    
    def _analyze_sentiment(self, text: str) -> str:
        """简单情感分析"""
        negative_words = ["不满", "投诉", "差", "烂", "垃圾", "失望", "生气", "愤怒"]
        if any(word in text for word in negative_words):
            return "negative"
        return "neutral"
    
    def recognize_intent(self, user_input: str) -> Intent:
        """意图识别"""
        user_lower = user_input.lower()
        if any(g in user_lower for g in ["你好", "hi", "hello", "在吗"]):
            return Intent.GREETING
        if any(k in user_lower for k in ["商品", "产品", "有什么", "卖", "多少钱"]):
            return Intent.PRODUCT_QUERY
        if any(k in user_lower for k in ["订单", "快递", "发货", "到了没"]):
            return Intent.ORDER_STATUS
        if any(k in user_lower for k in ["退货", "退换", "退款", "售后"]):
            return Intent.RETURN_REQUEST
        if any(g in user_lower for g in ["谢谢", "再见", "bye"]):
            return Intent.GOODBYE
        return Intent.GENERAL_QUESTION
    
    def handle_greeting(self, user_input: str = None) -> str:
        greetings = [
            "您好！我是智能客服小助手，很高兴为您服务。请问有什么可以帮您？",
            "Hello！欢迎来到我们的客服中心，我可以帮您查询商品、订单，或处理退换货问题。"
        ]
        return greetings[self.context.turn_count % len(greetings)]
    
    def handle_product_query(self, user_input: str) -> str:
        query = user_input.replace("商品", "").replace("产品", "").replace("有没有", "").strip()
        if not query:
            return "请问您想查询什么商品？"
        result = self._search_product(query)
        if result["count"] == 0:
            return f"抱歉，没有找到与'{query}'相关的商品，请尝试其他关键词。"
        response = f"为您找到 {result['count']} 件商品:\n"
        for p in result["products"][:3]:
            stock_status = "有货" if p["stock"] > 0 else "缺货"
            response += f"\n📦 {p['name']}\n   价格: ¥{p['price']} | 库存: {stock_status}\n"
        return response
    
    def handle_order_status(self, user_input: str) -> str:
        order_match = re.search(r'ORD\d+', user_input)
        if order_match:
            order_id = order_match.group()
            result = self._get_order_status(order_id)
            if "error" in result:
                return result["error"]
            status_map = {"processing": "处理中", "shipped": "已发货", "delivered": "已送达"}
            status_text = status_map.get(result["status"], result["status"])
            response = f"📦 订单 {order_id} 状态: {status_text}\n"
            if result.get("tracking"):
                response += f"快递单号: {result['tracking']}\n"
            if result.get("eta"):
                response += f"预计送达: {result['eta']}\n"
            return response
        return "请告诉我您的订单号，例如：ORD001"
    
    def handle_return_request(self, user_input: str) -> str:
        order_match = re.search(r'ORD\d+', user_input)
        if not order_match:
            return "请问您想退货的订单号是多少？"
        order_id = order_match.group()
        if "原因" not in user_input and "为什么" not in user_input:
            return f"好的，订单 {order_id} 要退货，请问是什么原因呢？"
        reasons = ["质量问题", "不想要了", "与描述不符", "发错了"]
        reason = next((r for r in reasons if r in user_input), "用户原因")
        result = self._initiate_return(order_id, reason)
        return f"""
✅ 退货申请已受理！

退货单号: {result['return_id']}
状态: {result['status']}

{result['instructions']}

{result['refund_amount']}
"""
    
    def handle_general(self, user_input: str = "") -> str:
        responses = [
            "我理解您的问题。请问能否说得更具体一些？",
            "这个问题我不太确定，让我为您转接人工客服...",
        ]
        return responses[self.context.turn_count % len(responses)]
    
    def process(self, user_input: str) -> str:
        self.context.turn_count += 1
        self.context.sentiment = self._analyze_sentiment(user_input)
        intent = self.recognize_intent(user_input)
        self.context.current_intent = intent
        
        handlers = {
            Intent.GREETING: self.handle_greeting,
            Intent.PRODUCT_QUERY: self.handle_product_query,
            Intent.ORDER_STATUS: self.handle_order_status,
            Intent.RETURN_REQUEST: self.handle_return_request,
            Intent.GOODBYE: lambda: "感谢您的咨询，再见！有需要随时联系我。",
            Intent.GENERAL_QUESTION: self.handle_general,
        }
        
        handler = handlers.get(intent, self.handle_general)
        response = handler(user_input) if callable(handler) else handler
        
        if self.context.sentiment == "negative" and self.context.turn_count > 3:
            response += "\n\n抱歉给您带来不好的体验，是否需要我为您转接人工客服？"
        
        return response


# ==================== 案例二：数据处理Pipeline Agent ====================

class DataFormat(Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    UNKNOWN = "unknown"


@dataclass
class ProcessingStep:
    name: str
    description: str
    input_format: DataFormat
    output_format: DataFormat
    handler: Callable


class DataPipelineAgent:
    """数据处理Pipeline Agent"""
    
    def __init__(self):
        self.processors: Dict[str, ProcessingStep] = {}
        self._register_default_processors()
    
    def _register_default_processors(self):
        def validate_csv(data: List[Dict]) -> Dict:
            if not data:
                return {"valid": False, "error": "Empty data"}
            required_fields = set(data[0].keys())
            issues = []
            for i, row in enumerate(data[1:], start=2):
                missing = required_fields - set(row.keys())
                if missing:
                    issues.append(f"Row {i}: missing fields {missing}")
            return {"valid": len(issues) == 0, "total_rows": len(data), "issues": issues[:10]}
        
        def clean_data(data: List[Dict]) -> List[Dict]:
            cleaned = []
            for row in data:
                cleaned_row = {}
                for key, value in row.items():
                    if isinstance(value, str):
                        value = value.strip()
                    if value != "" and value is not None:
                        cleaned_row[key] = value
                if cleaned_row:
                    cleaned.append(cleaned_row)
            return cleaned
        
        def transform_to_json(data: List[Dict]) -> str:
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        def aggregate_data(data: List[Dict]) -> Dict:
            if not data:
                return {"count": 0}
            numeric_fields = {}
            for row in data:
                for key, value in row.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_fields:
                            numeric_fields[key] = []
                        numeric_fields[key].append(value)
            result = {"record_count": len(data)}
            for field, values in numeric_fields.items():
                result[f"{field}_sum"] = sum(values)
                result[f"{field}_avg"] = sum(values) / len(values)
                result[f"{field}_min"] = min(values)
                result[f"{field}_max"] = max(values)
            return result
        
        self.processors["validate"] = ProcessingStep("validate", "验证数据完整性和格式", DataFormat.CSV, DataFormat.CSV, validate_csv)
        self.processors["clean"] = ProcessingStep("clean", "清洗数据", DataFormat.CSV, DataFormat.CSV, clean_data)
        self.processors["to_json"] = ProcessingStep("to_json", "转换为JSON", DataFormat.CSV, DataFormat.JSON, transform_to_json)
        self.processors["aggregate"] = ProcessingStep("aggregate", "数据聚合", DataFormat.CSV, DataFormat.JSON, aggregate_data)
    
    def parse_csv(self, content: str) -> List[Dict]:
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return []
        headers = [h.strip() for h in lines[0].split(',')]
        data = []
        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            if len(values) == len(headers):
                row = dict(zip(headers, values))
                for k, v in row.items():
                    try:
                        row[k] = int(v)
                    except ValueError:
                        try:
                            row[k] = float(v)
                        except ValueError:
                            pass
                data.append(row)
        return data
    
    def generate_pipeline(self, request: str) -> List[str]:
        request_lower = request.lower()
        pipeline = ["validate"]
        if "清洗" in request or "clean" in request_lower:
            pipeline.append("clean")
        if "统计" in request or "分析" in request or "aggregate" in request_lower:
            pipeline.append("aggregate")
        if "json" in request_lower:
            pipeline.append("to_json")
        return pipeline if pipeline else ["validate", "clean"]
    
    async def execute_pipeline(self, data: Any, pipeline: List[str]) -> Dict[str, Any]:
        import time
        start_time = time.time()
        current_data = data
        results = {}
        stats = {}
        
        print(f"\n=== Pipeline: {' -> '.join(pipeline)} ===\n")
        
        for step_name in pipeline:
            if step_name not in self.processors:
                continue
            step = self.processors[step_name]
            print(f"[{step.name}] {step.description}...")
            try:
                output = step.handler(current_data)
                results[step_name] = output
                if isinstance(output, dict) and "total_rows" in output:
                    stats[f"{step_name}_rows"] = output["total_rows"]
                elif isinstance(output, list):
                    stats[f"{step_name}_rows"] = len(output)
                current_data = output
                print(f"[{step.name}] 完成")
            except Exception as e:
                print(f"[{step.name}] 错误: {e}")
                results[step_name] = {"error": str(e)}
        
        stats["process_time"] = f"{time.time() - start_time:.2f}s"
        return {"pipeline": pipeline, "results": results, "stats": stats, "final_data": current_data}


# ==================== 案例三：研究助手Agent ====================

@dataclass
class Literature:
    title: str
    authors: List[str]
    year: int
    venue: str = ""
    abstract: str = ""
    citations: int = 0
    url: str = ""
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "abstract": self.abstract[:200] + "..." if len(self.abstract) > 200 else self.abstract,
            "citations": self.citations,
            "keywords": self.keywords
        }


class ResearchAssistant:
    """研究助手Agent"""
    
    def __init__(self):
        self.tools = self._register_tools()
        self.literature_db: List[Literature] = []
        self.notes: Dict[str, str] = {}
        self._load_sample_literature()
    
    def _register_tools(self) -> Dict[str, Callable]:
        return {
            "search_papers": self._search_papers,
            "get_paper_details": self._get_paper_details,
            "take_notes": self._take_notes,
            "generate_outline": self._generate_outline,
        }
    
    def _load_sample_literature(self):
        self.literature_db = [
            Literature(
                title="Attention Is All You Need",
                authors=["Vaswani", "Shazeer", "Parmar"],
                year=2017,
                venue="NeurIPS",
                abstract="We propose a new network architecture, the Transformer, based solely on attention mechanisms.",
                citations=50000,
                keywords=["transformer", "attention", "NLP"]
            ),
            Literature(
                title="BERT: Pre-training of Deep Bidirectional Transformers",
                authors=["Devlin", "Chang", "Lee", "Toutanova"],
                year=2019,
                venue="NAACL",
                abstract="We introduce a new language representation model called BERT.",
                citations=40000,
                keywords=["BERT", "pre-training", "NLP"]
            ),
            Literature(
                title="ReAct: Synergizing Reasoning and Acting in Language Models",
                authors=["Yao", "Zhao", "Yu"],
                year=2023,
                venue="ICLR",
                abstract="We propose ReAct, a paradigm that allows LLMs to generate both reasoning traces and task-specific actions.",
                citations=5000,
                keywords=["ReAct", "reasoning", "action", "agent"]
            ),
        ]
    
    def _search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        query_lower = query.lower()
        query_words = set(query_lower.split())
        scored = []
        for lit in self.literature_db:
            score = 0
            lit_text = f"{lit.title} {lit.abstract} {' '.join(lit.keywords)}".lower()
            for word in query_words:
                if word in lit_text:
                    score += 1
            if lit.title.lower().__contains__(query_lower):
                score += 5
            if score > 0:
                scored.append((score, lit))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [lit.to_dict() for _, lit in scored[:max_results]]
    
    def _get_paper_details(self, title: str) -> Dict:
        for lit in self.literature_db:
            if title.lower() in lit.title.lower():
                return lit.to_dict()
        return {"error": "Paper not found"}
    
    def _take_notes(self, key: str, content: str) -> str:
        self.notes[key] = content
        return f"笔记已保存: {key}"
    
    def _generate_outline(self, topic: str, num_sections: int = 5) -> List[str]:
        return [
            f"1. {topic}概述",
            f"2. {topic}的核心概念",
            f"3. {topic}的主要方法",
            f"4. {topic}的应用场景",
            f"5. {topic}的未来发展方向",
            "6. 参考文献"
        ]
    
    async def research_task(self, task_description: str) -> Dict[str, Any]:
        print(f"\n{'='*60}")
        print(f"研究任务: {task_description}")
        print(f"{'='*60}\n")
        
        results = {"task": task_description, "steps": []}
        topic = task_description.replace("研究", "").replace("调查", "").strip()
        
        print(f"[步骤1] 搜索 '{topic}' 相关文献...")
        papers = self._search_papers(topic, max_results=5)
        results["papers"] = papers
        results["steps"].append({"step": "search", "papers_found": len(papers)})
        print(f"找到 {len(papers)} 篇相关文献\n")
        
        for i, paper in enumerate(papers[:3], 1):
            print(f"  {i}. {paper['title']} ({paper['year']})")
            print(f"     作者: {', '.join(paper['authors'][:3])}")
            print()
        
        print("[步骤2] 生成文献综述大纲...")
        outline = self._generate_outline(topic)
        results["outline"] = outline
        results["steps"].append({"step": "outline_generated"})
        
        print("\n生成的大纲:")
        for item in outline:
            print(f"  {item}")
        
        results["status"] = "completed"
        return results


# ==================== 演示函数 ====================

def demo_customer_service():
    """客服系统演示"""
    print("\n" + "="*60)
    print("案例一：智能客服Agent")
    print("="*60)
    
    cs = SmartCustomerService()
    dialogue = [
        "你好，我想买一部手机",
        "iPhone有货吗",
        "我的订单号是ORD001，现在到哪了",
        "我想退货，订单号ORD002",
        "质量有问题",
    ]
    
    for user_input in dialogue:
        print(f"\n👤 用户: {user_input}")
        response = cs.process(user_input)
        print(f"🤖 客服: {response}")


async def demo_data_pipeline():
    """数据处理Pipeline演示"""
    print("\n" + "="*60)
    print("案例二：数据处理Pipeline Agent")
    print("="*60)
    
    csv_data = """name,age,city,salary
张三,28,北京,15000
李四,35,上海,25000
王五,42,深圳,35000
赵六,31,广州,20000
,29,杭州,18000"""
    
    agent = DataPipelineAgent()
    data = agent.parse_csv(csv_data)
    print(f"\n原始数据: {len(data)} 条记录")
    
    result = await agent.execute_pipeline(data, ["validate", "clean", "aggregate"])
    print(f"\n统计: {result['stats']}")


async def demo_research_assistant():
    """研究助手演示"""
    print("\n" + "="*60)
    print("案例三：研究助手Agent")
    print("="*60)
    
    assistant = ResearchAssistant()
    result = await assistant.research_task("研究大语言模型Agent架构")
    print(f"\n完成状态: {result['status']}")


async def main():
    """运行所有演示"""
    print("\n" + "#"*60)
    print("# 驾驭工程 - 教学案例演示")
    print("#"*60)
    
    demo_customer_service()
    await demo_data_pipeline()
    await demo_research_assistant()
    
    print("\n" + "#"*60)
    print("# 所有案例演示完成!")
    print("#"*60)


if __name__ == "__main__":
    asyncio.run(main())
