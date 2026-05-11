# 驾驭工程（Harness Engineering）课程

> 面向软件学院本科生/研究生的技术教程

---

## 目录

1. [核心概念定义](#1-核心概念定义)
2. [AI Harness架构与实现](#2-ai-agent架构与实现)
3. [多步骤任务编排与工具调用](#3-多步骤任务编排与工具调用)
4. [输出质量控制与验证](#4-输出质量控制与验证)
5. [实际代码案例](#5-实际代码案例)
6. [适合教学的场景化案例](#6-适合教学的场景化案例)

---

## 1. 核心概念定义

### 1.1 什么是驾驭工程

**驾驭工程（Harness Engineering）** 是指围绕大语言模型或 AI Agent 构建“可控执行外壳”的系统性工程方法。它不只关注 Agent 本身的推理能力，还关注任务编排、工具路由、状态管理、权限与护栏、评估、可观测性和人工接管，使 AI 系统能够在真实业务环境中稳定、可审计、可回滚地完成复杂任务。

```
┌─────────────────────────────────────────────────────────────────┐
│                        驾驭工程框架                              │
│                                                                 │
│   ┌─────────┐     ┌──────────────┐     ┌─────────────┐          │
│   │  用户   │ ──> │  Agent Core  │ ──> │   执行器    │          │
│   │  目标   │     │  + 规划器    │     │  + 工具     │          │
│   └─────────┘     │  + 记忆      │     │  + 验证     │          │
│                   │  + 推理      │     └─────────────┘          │
│                   └──────────────┘                              │
│                          │                                      │
│                          ▼                                      │
│                   ┌──────────────┐                             │
│                   │   反馈循环    │                             │
│                   │  自我反思改进 │                             │
│                   └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Harness Engineering vs Agent Engineering

| 维度 | Agent Engineering | Harness Engineering |
|------|-------------------|---------------------|
| 核心对象 | 自主 Agent 的推理、计划和行动 | 包裹模型/Agent 的执行外壳与控制面 |
| 重点问题 | Agent 能不能完成任务 | Agent 如何被约束、评估、追踪和安全运行 |
| 关键模块 | Planner、Memory、Tools、Executor | Orchestrator、Policy、Tool Router、Guardrails、Evals、Tracing |
| 典型产物 | ReAct Agent、Plan-and-Execute Agent | 可审计的 AI 工作流、工具调用沙箱、评估集、人工审批链 |
| 教学目标 | 理解 Agent 行为模式 | 学会把 Agent 放进可靠工程系统中运行 |

### 1.2 AI Harness 的核心要素

| 要素 | 描述 | 作用 |
|------|------|------|
| **规划器 (Planner)** | 将复杂任务分解为可执行的子任务 | 任务分解、优先级排序 |
| **记忆 (Memory)** | 存储历史交互、知识和中间状态 | 持续学习、上下文保持 |
| **工具 (Tools)** | 调用外部API、函数或服务的能力 | 扩展能力边界 |
| **推理引擎 (Reasoning)** | ReAct、CoT 等推理模式 | 逻辑推理、决策 |
| **执行器 (Executor)** | 协调任务执行、处理异常 | 任务调度、流程控制 |
| **验证器 (Validator)** | 检验输出质量、确保符合预期 | 质量保证 |

### 1.3 Harness vs 传统程序

```
传统程序:
用户输入 → 固定规则 → 确定性输出

AI Agent:
用户目标 → 理解意图 → 规划步骤 → 工具执行 → 观察结果 → 反思调整 → 输出
```

### 1.4 关键术语表

| 术语 | 英文 | 定义 |
|------|------|------|
| Agent | Artificial Intelligence Agent | 能够自主决策和执行任务的AI系统 |
| ReAct | Reasoning + Acting | 结合推理和动作的Agent模式 |
| Plan-and-Execute | 计划-执行 | 先规划后执行的Agent架构 |
| Tool Calling | 工具调用 | Agent调用外部函数/API的能力 |
| 自我反思 | Self-Reflection | Agent审视和改进自身输出的能力 |
| 任务图 | Task Graph | 表示任务间依赖关系的有向无环图 |

---

## 2. AI Harness架构与实现

### 2.1 ReAct 模式（Reasoning + Acting）

ReAct 是一种让Agent交替进行**推理**和**行动**的模式，使模型能够显式地进行逐步推理，同时通过行动与外部环境交互。

```
┌─────────────────────────────────────────────────────────────┐
│                      ReAct 循环                              │
│                                                             │
│  ┌─────────┐                                                │
│  │  观察   │ ◄───────────────────────────────────────┐      │
│  │(Obs)   │                                            │      │
│  └────┬────┘                                            │      │
│       ▼                                                 │      │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐            │      │
│  │  思考   │ ──> │  行动   │ ──> │  观察   │            │      │
│  │(Think)  │     │(Action) │     │(Observe)│            │      │
│  └─────────┘     └────┬────┘     └─────────┘            │      │
│                      │                                  │      │
│                      └──────────────────────────────────┘      │
│                           (继续循环直到完成)                    │
└─────────────────────────────────────────────────────────────┘
```

**ReAct 的关键优势：**
- 推理过程透明可见
- 能够处理多步骤复杂任务
- 可以根据观察结果调整后续行动

### 2.2 Plan-and-Execute 模式

Plan-and-Execute（计划-执行）模式将任务处理分为两个阶段：
1. **规划阶段**：分析任务，生成完整的执行计划
2. **执行阶段**：按照计划逐步执行，可动态调整

```
┌─────────────────────────────────────────────────────────────┐
│                   Plan-and-Execute 架构                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    规划阶段                            │  │
│  │   用户目标 → 任务分解 → 依赖分析 → 生成执行计划        │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    执行阶段                            │  │
│  │   for each step in plan:                             │  │
│  │       执行步骤 → 验证结果 → 动态调整 → 继续/回退      │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

### 2.3 Harness 架构对比

| 模式 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| **ReAct** | 动态环境、交互式任务 | 灵活、可自适应 | 计算开销大、循环次数不固定 |
| **Plan-and-Execute** | 复杂但可预测的任务 | 计划可控、易于调试 | 缺乏灵活性、计划可能过时 |
| **混合模式** | 复杂综合任务 | 结合两者优点 | 实现复杂度高 |

---

## 3. 多步骤任务编排与工具调用

### 3.1 任务编排的核心概念

**任务图（Task Graph）**：用有向无环图（DAG）表示任务间的依赖关系。

```python
"""
任务图示例
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Callable, Any
from enum import Enum
from collections import defaultdict
import asyncio


class TaskStatus(Enum):
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    SKIPPED = "skipped"      # 跳过


@dataclass
class Task:
    """任务单元"""
    id: str
    name: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    result: Any = None
    error: Optional[str] = None
    action: Optional[Callable] = None  # 执行函数
    
    def can_execute(self, completed_tasks: Set[str]) -> bool:
        """检查依赖是否都已完成"""
        return all(dep_id in completed_tasks for dep_id in self.dependencies)


class TaskGraph:
    """
    任务编排图
    
    支持:
    - 任务依赖管理
    - 并行/串行执行
    - 执行结果传递
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.execution_order: List[str] = []
    
    def add_task(self, task: Task):
        """添加任务"""
        self.tasks[task.id] = task
    
    def add_edge(self, from_task_id: str, to_task_id: str):
        """添加依赖边: from_task -> to_task (to_task依赖from_task)"""
        if from_task_id in self.tasks and to_task_id in self.tasks:
            self.tasks[to_task_id].dependencies.append(from_task_id)
    
    def topological_sort(self) -> List[str]:
        """拓扑排序，确定执行顺序"""
        # Kahn算法
        in_degree = defaultdict(int)
        for task in self.tasks.values():
            for dep in task.dependencies:
                in_degree[task.id] += 1
        
        # 从入度为0的开始
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            task_id = queue.pop(0)
            result.append(task_id)
            
            # 减少依赖该任务的其他任务的入度
            for other_task in self.tasks.values():
                if task_id in other_task.dependencies:
                    in_degree[other_task.id] -= 1
                    if in_degree[other_task.id] == 0:
                        queue.append(other_task.id)
        
        self.execution_order = result
        return result
    
    async def execute(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行任务图
        
        Args:
            context: 在任务间传递的上下文数据
            
        Returns:
            所有任务的结果字典
        """
        if context is None:
            context = {}
        
        execution_order = self.topological_sort()
        completed = set()
        results = {}
        
        for task_id in execution_order:
            task = self.tasks[task_id]
            
            # 检查依赖
            if not task.can_execute(completed):
                task.status = TaskStatus.SKIPPED
                continue
            
            # 执行任务
            task.status = TaskStatus.RUNNING
            try:
                if task.action:
                    # 支持异步和同步函数
                    if asyncio.iscoroutinefunction(task.action):
                        result = await task.action(context, results)
                    else:
                        result = task.action(context, results)
                    task.result = result
                    results[task_id] = result
                    context[task_id] = result  # 结果传递给后续任务
                task.status = TaskStatus.COMPLETED
                completed.add(task_id)
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                # 可以选择继续执行或停止
                print(f"Task {task_id} failed: {e}")
        
        return results


# 使用示例
def demo_task_graph():
    """任务图演示"""
    
    # 创建任务
    async def fetch_user(context, results):
        print("获取用户信息...")
        return {"user_id": 123, "name": "张三"}
    
    async def fetch_orders(context, results):
        print("获取订单列表...")
        return [{"order_id": 1, "amount": 100}, {"order_id": 2, "amount": 200}]
    
    async def calculate_stats(context, results):
        orders = results.get("fetch_orders", [])
        total = sum(o["amount"] for o in orders)
        return {"total_amount": total, "order_count": len(orders)}
    
    async def generate_report(context, results):
        user = results.get("fetch_user", {})
        stats = results.get("calculate_stats", {})
        return f"报告: {user.get('name')} 共有 {stats.get('order_count')} 个订单，总金额 {stats.get('total_amount')}"
    
    # 构建任务图
    graph = TaskGraph()
    graph.add_task(Task(id="fetch_user", name="获取用户", action=fetch_user))
    graph.add_task(Task(id="fetch_orders", name="获取订单", action=fetch_orders))
    graph.add_task(Task(id="calculate_stats", name="统计", action=calculate_stats))
    graph.add_task(Task(id="generate_report", name="生成报告", action=generate_report))
    
    # 设置依赖关系
    graph.add_edge("fetch_user", "generate_report")
    graph.add_edge("fetch_orders", "calculate_stats")
    graph.add_edge("calculate_stats", "generate_report")
    
    # 执行
    results = asyncio.run(graph.execute())
    print("\n最终报告:", results.get("generate_report"))


if __name__ == "__main__":
    demo_task_graph()
```

### 3.2 工具调用系统设计

```python
"""
工具调用系统设计
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, get_type_hints, get_origin, get_args
from enum import Enum
import json
import inspect
from datetime import datetime


class ToolResult:
    """工具执行结果"""
    
    def __init__(self, success: bool, result: Any = None, error: str = None):
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Tool:
    """
    工具定义
    
    工具是Agent与外部世界交互的桥梁。
    每个工具都有:
    - 名称和描述
    - 参数模式 (JSON Schema)
    - 执行函数
    """
    name: str
    description: str
    parameters: Dict[str, Any]  # 参数模式
    func: Callable
    category: str = "general"  # 工具分类
    
    def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        try:
            # 参数验证（简化版）
            for param_name, param_info in self.parameters.get("properties", {}).items():
                if param_info.get("required", False) and param_name not in kwargs:
                    return ToolResult(False, error=f"Missing required parameter: {param_name}")
            
            result = self.func(**kwargs)
            return ToolResult(True, result=result)
        except Exception as e:
            return ToolResult(False, error=str(e))
    
    @staticmethod
    def from_function(func: Callable, name: str = None, description: str = None) -> "Tool":
        """
        从Python函数创建工具
        
        自动从函数签名提取参数信息
        """
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or ""
        
        # 从类型注解提取参数模式
        hints = get_type_hints(func)
        sig = inspect.signature(func)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['context', 'results']:  # 跳过内部参数
                continue
            
            param_type = hints.get(param_name, Any)
            json_type = _python_type_to_json(param_type)
            
            properties[param_name] = {
                "type": json_type,
                "description": f"Parameter: {param_name}"
            }
            
            if param.default is inspect.Parameter.empty:
                required.append(param_name)
        
        return Tool(
            name=tool_name,
            description=tool_desc,
            parameters={
                "type": "object",
                "properties": properties,
                "required": required
            },
            func=func
        )


def _python_type_to_json(py_type) -> str:
    """Python类型转JSON Schema类型"""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }
    
    origin = get_origin(py_type)
    if origin is Union:
        args = get_args(py_type)
        return _python_type_to_json(args[0])  # 取第一个非None类型
    
    return type_map.get(py_type, "string")


class ToolRegistry:
    """
    工具注册表
    
    管理所有可用工具，支持:
    - 工具注册/注销
    - 按名称/分类查询
    - 批量执行
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """注册工具"""
        self._tools[tool.name] = tool
        print(f"Registered tool: {tool.name}")
    
    def register_from_function(self, func: Callable, name: str = None, description: str = None):
        """从函数注册工具"""
        tool = Tool.from_function(func, name, description)
        self.register(tool)
    
    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self._tools.get(name)
    
    def list_tools(self, category: str = None) -> List[Tool]:
        """列出工具"""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools
    
    def get_tools_for_prompt(self) -> str:
        """生成工具描述，用于Prompt注入"""
        tool_descs = []
        for tool in self._tools.values():
            params_str = json.dumps(tool.parameters, indent=2, ensure_ascii=False)
            tool_descs.append(f"""
## {tool.name}

描述: {tool.description}

参数模式:
```json
{params_str}
```""")
        return "\n".join(tool_descs)


# ==================== 示例工具 ====================

# 计算器工具
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        # 安全评估（实际应使用安全的表达式求值器）
        allowed_chars = set("0123456789+-*/.() ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return str(result)
        return "Error: Invalid characters"
    except Exception as e:
        return f"Error: {e}"


# 搜索工具（模拟）
def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """搜索网络信息"""
    # 简化实现，返回模拟数据
    return [
        {"title": f"Result for {query} #1", "url": "http://example.com/1", "snippet": "这是搜索结果1"},
        {"title": f"Result for {query} #2", "url": "http://example.com/2", "snippet": "这是搜索结果2"},
    ][:max_results]


# 文件操作工具
def read_file(path: str, max_lines: int = 100) -> str:
    """读取文件内容"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [f.readline() for _ in range(max_lines)]
            content = ''.join(lines)
            if len(content) > 3000:
                return content[:3000] + "...(truncated)"
            return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error: {e}"


def write_file(path: str, content: str) -> str:
    """写入文件"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error: {e}"


# 工具注册演示
def demo_tool_registry():
    """工具注册演示"""
    registry = ToolRegistry()
    
    # 注册工具
    registry.register_from_function(calculator, "calculator", "执行数学计算")
    registry.register_from_function(web_search, "web_search", "搜索网络信息")
    registry.register_from_function(read_file, "read_file", "读取文件内容")
    registry.register_from_function(write_file, "write_file", "写入文件内容")
    
    # 列出工具
    print("\n=== 可用工具 ===")
    for tool in registry.list_tools():
        print(f"- {tool.name}: {tool.description}")
    
    # 执行工具
    print("\n=== 执行计算器 ===")
    result = registry.get("calculator").execute(expression="2 + 3 * 4")
    print(f"Result: {result.to_dict()}")
    
    print("\n=== 执行搜索 ===")
    result = registry.get("web_search").execute(query="Python教程")
    print(f"Result: {result.to_dict()}")


if __name__ == "__main__":
    demo_tool_registry()
```

---

## 4. 输出质量控制与验证

### 4.1 输出质量控制框架

```python
"""
输出质量控制与验证系统
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from datetime import datetime
import re
import json


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class ValidationResult:
    """验证结果"""
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        return self.status in [ValidationStatus.PASSED, ValidationStatus.WARNING]


class OutputValidator:
    """
    输出验证器基类
    
    各种验证规则:
    - 格式验证 (JSON/列表/字数限制)
    - 内容验证 (关键词/正则)
    - 语义验证 (使用LLM判断)
    - 业务规则验证
    """
    
    def validate(self, output: Any) -> ValidationResult:
        raise NotImplementedError


class JSONFormatValidator(OutputValidator):
    """JSON格式验证器"""
    
    def __init__(self, required_keys: List[str] = None):
        self.required_keys = required_keys or []
    
    def validate(self, output: Any) -> ValidationResult:
        if isinstance(output, str):
            try:
                data = json.loads(output)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    ValidationStatus.FAILED,
                    f"Invalid JSON format: {e}",
                    {"error": str(e)}
                )
        elif isinstance(output, dict):
            data = output
        else:
            return ValidationResult(
                ValidationStatus.FAILED,
                f"Expected dict or JSON string, got {type(output)}"
            )
        
        # 检查必需键
        missing_keys = [k for k in self.required_keys if k not in data]
        if missing_keys:
            return ValidationResult(
                ValidationStatus.FAILED,
                f"Missing required keys: {missing_keys}",
                {"missing_keys": missing_keys}
            )
        
        return ValidationResult(ValidationStatus.PASSED, "Valid JSON with all required keys")


class LengthValidator(OutputValidator):
    """长度验证器"""
    
    def __init__(self, min_length: int = None, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, output: Any) -> ValidationResult:
        text = str(output) if not isinstance(output, str) else output
        length = len(text)
        
        issues = []
        if self.min_length and length < self.min_length:
            issues.append(f"Too short: {length} < {self.min_length}")
        if self.max_length and length > self.max_length:
            issues.append(f"Too long: {length} > {self.max_length}")
        
        if issues:
            return ValidationResult(
                ValidationStatus.FAILED,
                "; ".join(issues),
                {"length": length}
            )
        
        return ValidationResult(
            ValidationStatus.PASSED,
            f"Length OK: {length}",
            {"length": length}
        )


class KeywordValidator(OutputValidator):
    """关键词验证器"""
    
    def __init__(self, required_keywords: List[str] = None, 
                 forbidden_keywords: List[str] = None,
                 case_sensitive: bool = False):
        self.required_keywords = required_keywords or []
        self.forbidden_keywords = forbidden_keywords or []
        self.case_sensitive = case_sensitive
    
    def validate(self, output: Any) -> ValidationResult:
        text = str(output)
        if not self.case_sensitive:
            text = text.lower()
        
        # 检查必需关键词
        missing = []
        for kw in self.required_keywords:
            check_kw = kw if self.case_sensitive else kw.lower()
            if check_kw not in text:
                missing.append(kw)
        
        # 检查禁用关键词
        found_forbidden = []
        for kw in self.forbidden_keywords:
            check_kw = kw if self.case_sensitive else kw.lower()
            if check_kw in text:
                found_forbidden.append(kw)
        
        issues = []
        if missing:
            issues.append(f"Missing keywords: {missing}")
        if found_forbidden:
            issues.append(f"Contains forbidden keywords: {found_forbidden}")
        
        if issues:
            return ValidationResult(
                ValidationStatus.FAILED,
                "; ".join(issues)
            )
        
        return ValidationResult(ValidationStatus.PASSED, "All keyword checks passed")


class RegexValidator(OutputValidator):
    """正则表达式验证器"""
    
    def __init__(self, pattern: str, error_message: str = "Pattern not matched"):
        self.pattern = re.compile(pattern)
        self.error_message = error_message
    
    def validate(self, output: Any) -> ValidationResult:
        text = str(output)
        match = self.pattern.search(text)
        
        if not match:
            return ValidationResult(
                ValidationStatus.FAILED,
                self.error_message,
                {"pattern": self.pattern.pattern}
            )
        
        return ValidationResult(
            ValidationStatus.PASSED,
            f"Pattern matched: {match.group()}",
            {"match": match.group()}
        )


class ValidationChain:
    """
    验证链
    
    组合多个验证器，短路或全部执行
    """
    
    def __init__(self, mode: str = "all"):
        """
        Args:
            mode: "all" 执行所有验证器
                  "any" 遇到第一个失败就停止
        """
        self.validators: List[OutputValidator] = []
        self.mode = mode
    
    def add(self, validator: OutputValidator) -> "ValidationChain":
        self.validators.append(validator)
        return self
    
    def validate(self, output: Any) -> List[ValidationResult]:
        results = []
        
        for validator in self.validators:
            result = validator.validate(output)
            results.append(result)
            
            if self.mode == "any" and not result.is_valid():
                break
        
        return results
    
    def validate_and_report(self, output: Any) -> bool:
        """验证并报告结果"""
        results = self.validate(output)
        
        print("\n=== 验证报告 ===")
        all_passed = True
        for result in results:
            status_icon = "✓" if result.is_valid() else "✗"
            print(f"{status_icon} [{result.status.value}] {result.message}")
            if not result.is_valid():
                all_passed = False
        
        return all_passed


# LLM辅助验证器
class LLMAssistedValidator(OutputValidator):
    """
    LLM辅助验证器
    
    使用LLM来判断输出是否符合要求
    适用于难以用规则验证的语义质量检查
    """
    
    def __init__(self, llm_client: Callable, criteria: str):
        """
        Args:
            llm_client: LLM调用函数
            criteria: 验证标准描述
        """
        self.llm_client = llm_client
        self.criteria = criteria
    
    def validate(self, output: Any) -> ValidationResult:
        prompt = f"""你是一个输出质量审核员。

验证内容:
{output}

验证标准:
{self.criteria}

请判断输出是否符合标准，只回答"通过"或"不通过"，并简述原因。
"""
        
        try:
            response = self.llm_client(prompt)
            
            if "通过" in response and "不通过" not in response:
                return ValidationResult(
                    ValidationStatus.PASSED,
                    "LLM validation passed",
                    {"llm_response": response}
                )
            else:
                return ValidationResult(
                    ValidationStatus.FAILED,
                    "LLM validation failed",
                    {"llm_response": response}
                )
        except Exception as e:
            return ValidationResult(
                ValidationStatus.WARNING,
                f"LLM validation error: {e}"
            )


# 验证器演示
def demo_validators():
    """验证器演示"""
    
    print("=== 验证器演示 ===\n")
    
    # 测试数据
    good_output = '{"name": "张三", "age": 25, "city": "北京"}'
    bad_output = '{"name": "张三"}'  # 缺少必需字段
    short_output = "Hi"
    
    # 创建验证链
    chain = ValidationChain(mode="all")
    chain.add(JSONFormatValidator(required_keys=["name", "age", "city"]))
    chain.add(LengthValidator(min_length=10, max_length=500))
    chain.add(KeywordValidator(
        required_keywords=["北京"],
        forbidden_keywords=["错误", "失败"]
    ))
    
    print("1. 测试有效输出:")
    chain.validate_and_report(good_output)
    
    print("\n2. 测试无效JSON:")
    chain.validate_and_report(bad_output)
    
    print("\n3. 测试过短内容:")
    chain.validate_and_report(short_output)


if __name__ == "__main__":
    demo_validators()
```

---

## 5. 实际代码案例

### 5.1 基础ReAct Agent实现

```python
"""
ReAct Agent 实现

ReAct = Reasoning + Acting

核心循环:
1. Thought: 思考当前状态和下一步行动
2. Action: 执行工具调用
3. Observation: 观察结果
4. (重复直到任务完成)
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum


class AgentAction(Enum):
    """Agent行动类型"""
    THINK = "think"
    ACTION = "action"
    OBSERVE = "observe"
    RESPOND = "respond"
    FINISH = "finish"


@dataclass
class Step:
    """Agent执行步骤"""
    step_number: int
    action: AgentAction
    thought: str = ""
    tool_name: str = ""
    tool_input: Dict[str, Any] = field(default_factory=dict)
    observation: Any = None
    result: Any = None


@dataclass
class ReActAgent:
    """
    ReAct Agent
    
    使用ReAct模式的AI Agent实现
    """
    name: str
    system_prompt: str
    tools: Dict[str, Callable]  # 工具注册表
    max_iterations: int = 10
    llm_call: Callable  # LLM调用函数
    
    def __post_init__(self):
        self.steps: List[Step] = []
        self.conversation_history: List[Dict] = []
    
    def build_system_prompt(self) -> str:
        """构建系统提示"""
        tools_desc = "\n".join([
            f"- **{name}**: {func.__doc__ or 'No description'}"
            for name, func in self.tools.items()
        ])
        
        return f"""你是 {self.name}，一个使用ReAct模式的AI助手。

你可以通过以下工具与世界交互:

{tools_desc}

ReAct模式工作流程:
1. THINK: 分析当前情况，思考下一步行动
2. ACTION: 选择并执行合适的工具
3. OBSERVE: 观察工具执行结果
4. 重复直到任务完成

每次回复请使用以下JSON格式:
{{
    "action": "think/action/observe/respond/finish",
    "thought": "你的思考过程",
    "tool": "工具名称(如果是action类型)",
    "tool_input": {{"参数名": "参数值"}},
    "response": "直接回复用户的内容(如果是respond类型)"
}}
"""
    
    def add_to_history(self, role: str, content: str):
        """添加对话历史"""
        self.conversation_history.append({"role": role, "content": content})
    
    def format_history(self) -> str:
        """格式化对话历史"""
        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.conversation_history[-10:]  # 最近10轮
        ])
    
    def parse_response(self, response_text: str) -> Dict:
        """解析LLM响应"""
        try:
            # 尝试提取JSON
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end]
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end]
            
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # 如果解析失败，尝试纯文本
            return {
                "action": "respond",
                "thought": response_text,
                "response": response_text
            }
    
    def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """执行工具"""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            tool = self.tools[tool_name]
            return tool(**tool_input)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    async def run(self, user_input: str) -> Dict[str, Any]:
        """
        运行Agent处理用户输入
        
        Returns:
            包含最终响应和执行历史的字典
        """
        self.steps = []
        self.add_to_history("user", user_input)
        
        step_num = 0
        final_response = ""
        
        while step_num < self.max_iterations:
            step_num += 1
            
            # 构建当前上下文
            context = f"""
系统提示:
{self.build_system_prompt()}

对话历史:
{self.format_history()}
"""
            # 调用LLM
            llm_response = await self.llm_call(context + f"\n\n用户: {user_input}\n请按照ReAct模式思考并输出JSON:")
            
            self.add_to_history("assistant", llm_response)
            
            # 解析响应
            parsed = self.parse_response(llm_response)
            
            action_type = parsed.get("action", "think")
            thought = parsed.get("thought", "")
            
            step = Step(
                step_number=step_num,
                action=AgentAction(action_type),
                thought=thought,
                tool_name=parsed.get("tool", ""),
                tool_input=parsed.get("tool_input", {})
            )
            
            if action_type == "action":
                # 执行工具
                result = self.execute_tool(step.tool_name, step.tool_input)
                step.observation = result
                step.result = result
                
                # 将结果加入对话历史
                self.add_to_history("system", f"[Tool: {step.tool_name}] Result: {result}")
                
            elif action_type == "respond":
                final_response = parsed.get("response", thought)
                step.result = final_response
                break
                
            elif action_type == "finish":
                final_response = parsed.get("response", "任务完成")
                step.result = final_response
                break
            
            self.steps.append(step)
        
        return {
            "response": final_response,
            "steps": [
                {
                    "step": s.step_number,
                    "action": s.action.value,
                    "thought": s.thought,
                    "tool": s.tool_name,
                    "tool_input": s.tool_input,
                    "observation": s.observation,
                    "result": s.result
                }
                for s in self.steps
            ],
            "iterations": step_num
        }


# ==================== 简单LLM模拟 ====================

def mock_llm_call(prompt: str) -> str:
    """
    模拟LLM调用
    
    实际使用时替换为真实API调用
    """
    # 简单的关键词匹配模拟
    if "计算" in prompt or "calculator" in prompt.lower():
        return json.dumps({
            "action": "action",
            "thought": "用户需要计算，我应该使用计算器工具",
            "tool": "calculator",
            "tool_input": {"expression": "2 + 3 * 4"}
        })
    elif "搜索" in prompt or "search" in prompt.lower():
        return json.dumps({
            "action": "action",
            "thought": "用户需要搜索信息，我将使用搜索工具",
            "tool": "web_search",
            "tool_input": {"query": "人工智能教程"}
        })
    elif "天气" in prompt:
        return json.dumps({
            "action": "action",
            "thought": "用户询问天气，使用天气工具",
            "tool": "get_weather",
            "tool_input": {"city": "北京"}
        })
    else:
        return json.dumps({
            "action": "respond",
            "thought": "这是一个通用问题，我直接回答",
            "response": "我理解你的问题，让我为你解答..."
        })


# 同步包装器用于演示
def run_react_demo():
    """ReAct Agent演示"""
    import asyncio
    
    # 定义工具
    def calculator(expression: str) -> str:
        """计算数学表达式"""
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"
    
    def web_search(query: str) -> str:
        """搜索网络"""
        return f"找到了关于'{query}'的10个搜索结果"
    
    def get_weather(city: str) -> str:
        """查询天气"""
        return f"{city}今天晴天，温度25-30度"
    
    # 创建Agent
    agent = ReActAgent(
        name="助手",
        system_prompt="你是一个智能助手",
        tools={
            "calculator": calculator,
            "web_search": web_search,
            "get_weather": get_weather
        },
        llm_call=mock_llm_call
    )
    
    # 运行
    async def main():
        result = await agent.run("帮我计算一下 2+3*4 等于多少")
        print("=== ReAct执行结果 ===")
        print(f"最终响应: {result['response']}")
        print(f"\n执行步骤 ({result['iterations']} 次迭代):")
        for step in result['steps']:
            print(f"\n步骤 {step['step']}: {step['action']}")
            print(f"  思考: {step['thought']}")
            if step['tool']:
                print(f"  工具: {step['tool']}")
                print(f"  输入: {step['tool_input']}")
                print(f"  观察: {step['observation']}")
    
    asyncio.run(main())


if __name__ == "__main__":
    run_react_demo()
```

### 5.2 Plan-and-Execute Agent实现

```python
"""
Plan-and-Execute Agent 实现

Plan-and-Execute 模式:
1. 先规划: 将任务分解为步骤序列
2. 后执行: 按计划执行每一步
3. 可动态调整: 根据执行结果调整后续计划
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import json


class PlanStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REVISED = "revised"


@dataclass
class PlanStep:
    """计划步骤"""
    id: int
    description: str
    tool_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: PlanStatus = PlanStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    depends_on: List[int] = field(default_factory=list)  # 依赖的前置步骤ID


@dataclass
class ExecutionPlan:
    """执行计划"""
    goal: str
    steps: List[PlanStep]
    status: PlanStatus = PlanStatus.PENDING
    
    def get_ready_steps(self) -> List[PlanStep]:
        """获取可以执行的步骤（依赖都已完成）"""
        completed_ids = {s.id for s in self.steps if s.status == PlanStatus.COMPLETED}
        ready = []
        for step in self.steps:
            if step.status == PlanStatus.PENDING:
                if all(dep in completed_ids for dep in step.depends_on):
                    ready.append(step)
        return ready


@dataclass
class PlanAndExecuteAgent:
    """
    Plan-and-Execute Agent
    
    核心思想:
    - Planner: 负责分析任务并生成计划
    - Executor: 负责按计划执行
    - 两者可以独立使用LLM或规则
    """
    
    name: str
    tools: Dict[str, Callable]
    planner_llm: Callable  # 规划器LLM
    executor_llm: Callable  # 执行器LLM
    max_replan: int = 2  # 最大重新规划次数
    
    def __post_init__(self):
        self.current_plan: Optional[ExecutionPlan] = None
        self.execution_history: List[Dict] = []
    
    async def plan(self, task: str) -> ExecutionPlan:
        """
        规划阶段
        
        调用Planner LLM将任务分解为可执行步骤
        """
        prompt = f"""你是一个任务规划专家。将用户的任务分解为具体的执行步骤。

任务: {task}

请以JSON格式输出计划:
{{
    "goal": "任务目标描述",
    "steps": [
        {{
            "id": 1,
            "description": "步骤描述",
            "tool": "工具名称",
            "parameters": {{"参数": "值"}},
            "depends_on": []
        }}
    ]
}}

可用工具: {list(self.tools.keys())}

注意:
- 每个步骤必须指定使用的工具
- 考虑步骤间的依赖关系
- 步骤应该足够小以便执行和验证
"""
        
        response = await self.planner_llm(prompt)
        
        try:
            if isinstance(response, str):
                data = json.loads(response)
            else:
                data = response
            
            steps = [
                PlanStep(
                    id=s["id"],
                    description=s["description"],
                    tool_name=s.get("tool", ""),
                    parameters=s.get("parameters", {}),
                    depends_on=s.get("depends_on", [])
                )
                for s in data.get("steps", [])
            ]
            
            return ExecutionPlan(goal=data.get("goal", task), steps=steps)
        except Exception as e:
            print(f"规划解析错误: {e}")
            # 返回简单计划
            return ExecutionPlan(
                goal=task,
                steps=[PlanStep(id=1, description=task, tool_name="direct_response")]
            )
    
    async def execute_step(self, step: PlanStep, context: Dict) -> Any:
        """执行单个步骤"""
        if step.tool_name not in self.tools:
            return {"error": f"Unknown tool: {step.tool_name}"}
        
        tool = self.tools[step.tool_name]
        
        # 填充上下文中的变量
        params = step.parameters.copy()
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$"):
                # 引用上下文中的值
                var_name = value[1:]
                params[key] = context.get(var_name, value)
        
        try:
            if asyncio.iscoroutinefunction(tool):
                return await tool(**params)
            else:
                return tool(**params)
        except Exception as e:
            return {"error": str(e)}
    
    async def execute(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        执行阶段
        
        按计划执行步骤，支持动态调整
        """
        plan.status = PlanStatus.IN_PROGRESS
        context = {"goal": plan.goal}
        results = {}
        
        print(f"\n开始执行计划: {plan.goal}")
        print(f"共 {len(plan.steps)} 个步骤\n")
        
        completed_count = 0
        
        while completed_count < len(plan.steps):
            # 获取可执行的步骤
            ready_steps = plan.get_ready_steps()
            
            if not ready_steps:
                # 检查是否有失败的步骤
                failed = [s for s in plan.steps if s.status == PlanStatus.FAILED]
                if failed:
                    print("有步骤失败，尝试重新规划...")
                    break
                await asyncio.sleep(0.1)  # 避免死循环
                continue
            
            # 并行执行独立的步骤
            tasks = []
            for step in ready_steps:
                step.status = PlanStatus.IN_PROGRESS
                print(f"[步骤 {step.id}] 开始: {step.description}")
                tasks.append(self.execute_step(step, context))
            
            # 等待所有任务完成
            step_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for step, result in zip(ready_steps, step_results):
                if isinstance(result, Exception):
                    step.status = PlanStatus.FAILED
                    step.error = str(result)
                    print(f"[步骤 {step.id}] 失败: {result}")
                elif isinstance(result, dict) and "error" in result:
                    step.status = PlanStatus.FAILED
                    step.error = result["error"]
                    print(f"[步骤 {step.id}] 失败: {result['error']}")
                else:
                    step.status = PlanStatus.COMPLETED
                    step.result = result
                    results[step.id] = result
                    context[f"step_{step.id}_result"] = result
                    print(f"[步骤 {step.id}] 完成")
                
                completed_count += 1
        
        # 判断是否完成
        all_completed = all(s.status == PlanStatus.COMPLETED for s in plan.steps)
        plan.status = PlanStatus.COMPLETED if all_completed else PlanStatus.FAILED
        
        return {
            "success": all_completed,
            "plan": plan,
            "results": results,
            "context": context
        }
    
    async def run(self, task: str) -> Dict[str, Any]:
        """
        完整的Plan-and-Execute流程
        """
        # 1. 规划
        plan = await self.plan(task)
        self.current_plan = plan
        
        # 2. 执行
        result = await self.execute(plan)
        
        # 3. 如果失败，尝试重新规划
        replan_count = 0
        while not result["success"] and replan_count < self.max_replan:
            replan_count += 1
            print(f"\n=== 重新规划 (第 {replan_count} 次) ===")
            
            # 基于之前的执行上下文生成新计划
            new_task = f"{task}\n\n之前的尝试失败了。请重新规划，考虑避免之前的错误。"
            plan = await self.plan(new_task)
            self.current_plan = plan
            result = await self.execute(plan)
        
        return result


# ==================== 演示 ====================

async def mock_llm(prompt: str) -> str:
    """模拟LLM"""
    if "计划" in prompt or "plan" in prompt.lower():
        return json.dumps({
            "goal": "分析某公司股票并给出投资建议",
            "steps": [
                {"id": 1, "description": "获取公司基本信息", "tool": "get_company_info", "parameters": {"symbol": "AAPL"}, "depends_on": []},
                {"id": 2, "description": "获取最新股票价格", "tool": "get_stock_price", "parameters": {"symbol": "AAPL"}, "depends_on": []},
                {"id": 3, "description": "获取财务数据", "tool": "get_financial_data", "parameters": {"symbol": "AAPL"}, "depends_on": [1]},
                {"id": 4, "description": "分析数据并生成报告", "tool": "generate_report", "parameters": {"company": "$step_1_result", "price": "$step_2_result", "financials": "$step_3_result"}, "depends_on": [2, 3]}
            ]
        })
    return "{}"


def get_company_info(symbol: str) -> dict:
    """获取公司信息"""
    return {"name": "Apple Inc.", "sector": "Technology", "employees": 164000}


def get_stock_price(symbol: str) -> dict:
    """获取股价"""
    return {"symbol": symbol, "price": 178.50, "change": 2.3}


def get_financial_data(symbol: str) -> dict:
    """获取财务数据"""
    return {"revenue": 394.3, "net_income": 99.8, "eps": 6.13}


def generate_report(company: dict, price: dict, financials: dict) -> str:
    """生成分析报告"""
    return f"""
# {company.get('name', 'Unknown')} 分析报告

## 基本信息
- 行业: {company.get('sector', 'N/A')}
- 员工数: {company.get('employees', 0):,}

## 股价信息
- 当前价格: ${price.get('price', 0):.2f}
- 涨跌: {price.get('change', 0):+.2f}%

## 财务数据
- 营收: ${financials.get('revenue', 0):.1f}B
- 净利润: ${financials.get('net_income', 0):.1f}B
- 每股收益: ${financials.get('eps', 0):.2f}

## 投资建议
基于以上数据，建议关注。
"""


async def demo_plan_execute():
    """Plan-and-Execute演示"""
    
    agent = PlanAndExecuteAgent(
        name="股票分析师",
        tools={
            "get_company_info": get_company_info,
            "get_stock_price": get_stock_price,
            "get_financial_data": get_financial_data,
            "generate_report": generate_report
        },
        planner_llm=mock_llm,
        executor_llm=mock_llm
    )
    
    result = await agent.run("分析苹果公司的股票")
    
    print("\n" + "="*50)
    print("执行完成!")
    print(f"成功: {result['success']}")
    print(f"\n最终报告:\n{result['results'].get(4, 'N/A')}")


if __name__ == "__main__":
    asyncio.run(demo_plan_execute())
```

---

## 6. 适合教学的场景化案例

### 6.1 案例一：智能客服Agent

**场景**：构建一个电商智能客服，能够回答商品查询、订单状态、退换货等问题。

```python
"""
案例一：智能客服Agent

场景：
- 用户咨询商品信息
- 查询订单状态
- 处理退换货请求
- 情绪识别与安抚

这个案例展示了：
1. 多工具协调
2. 对话状态管理
3. 条件分支处理
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import json


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
    sentiment: str = "neutral"  # positive, neutral, negative
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
        # 模拟数据库
        products = [
            {"id": "P001", "name": "iPhone 15 Pro", "price": 7999, "stock": 100},
            {"id": "P002", "name": "MacBook Pro 14", "price": 15999, "stock": 50},
            {"id": "P003", "name": "AirPods Pro", "price": 1899, "stock": 200},
        ]
        
        results = [p for p in products if query.lower() in p["name"].lower()]
        if category:
            results = [p for p in results if p.get("category") == category]
        
        return {"count": len(results), "products": results}
    
    def _get_order_status(self, order_id: str) -> Dict:
        """查询订单状态"""
        # 模拟订单数据
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
    
    def handle_greeting(self) -> str:
        """处理问候"""
        greetings = [
            "您好！我是智能客服小助手，很高兴为您服务。请问有什么可以帮您？",
            "Hello！欢迎来到我们的客服中心，我可以帮您查询商品、订单，或处理退换货问题。"
        ]
        return greetings[self.context.turn_count % len(greetings)]
    
    def handle_product_query(self, user_input: str) -> str:
        """处理商品查询"""
        # 提取商品关键词
        query = user_input.replace("商品", "").replace("产品", "").replace("有没有", "").strip()
        
        if not query:
            return "请问您想查询什么商品？"
        
        result = self._search_product(query)
        
        if result["count"] == 0:
            return f"抱歉，没有找到与'{query}'相关的商品，请尝试其他关键词。"
        
        response = f"为您找到 {result['count']} 件商品:\n"
        for p in result["products"][:3]:  # 最多显示3个
            stock_status = "有货" if p["stock"] > 0 else "缺货"
            response += f"\n📦 {p['name']}\n   价格: ¥{p['price']} | 库存: {stock_status}\n"
        
        return response
    
    def handle_order_status(self, user_input: str) -> str:
        """处理订单查询"""
        # 简化：直接使用用户输入中的订单号
        import re
        order_match = re.search(r'ORD\d+', user_input)
        
        if order_match:
            order_id = order_match.group()
            result = self._get_order_status(order_id)
            
            if "error" in result:
                return result["error"]
            
            status_map = {
                "processing": "处理中",
                "shipped": "已发货",
                "delivered": "已送达"
            }
            
            status_text = status_map.get(result["status"], result["status"])
            response = f"📦 订单 {order_id} 状态: {status_text}\n"
            
            if result.get("tracking"):
                response += f"快递单号: {result['tracking']}\n"
            if result.get("eta"):
                response += f"预计送达: {result['eta']}\n"
            
            return response
        
        return "请告诉我您的订单号，例如：ORD001"
    
    def handle_return_request(self, user_input: str) -> str:
        """处理退换货请求"""
        # 检查是否提供了订单号
        import re
        order_match = re.search(r'ORD\d+', user_input)
        
        if not order_match:
            return "请问您想退货的订单号是多少？"
        
        order_id = order_match.group()
        
        # 检查是否说明了原因
        if "原因" not in user_input and "为什么" not in user_input:
            return f"好的，订单 {order_id} 要退货，请问是什么原因呢？"
        
        # 提取原因（简化）
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
    
    def handle_general(self, user_input: str) -> str:
        """处理一般问题"""
        responses = [
            "我理解您的问题。请问能否说得更具体一些？",
            "这个问题我不太确定，让我为您转接人工客服...",
            "您可以尝试这样操作：1. 2. 3."
        ]
        return responses[self.context.turn_count % len(responses)]
    
    def process(self, user_input: str) -> str:
        """
        处理用户输入
        
        这是一个简化的同步版本，用于教学演示。
        实际生产环境应使用异步处理和更复杂的NLU。
        """
        self.context.turn_count += 1
        
        # 情感分析
        self.context.sentiment = self._analyze_sentiment(user_input)
        
        # 意图识别
        intent = self.recognize_intent(user_input)
        self.context.current_intent = intent
        
        # 根据意图处理
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
        
        # 如果用户情绪负面，考虑转人工
        if self.context.sentiment == "negative" and self.context.turn_count > 3:
            response += "\n\n抱歉给您带来不好的体验，是否需要我为您转接人工客服？"
        
        return response


def demo_customer_service():
    """客服系统演示"""
    
    print("=== 智能客服演示 ===\n")
    
    cs = SmartCustomerService()
    
    # 模拟对话
    dialogue = [
        "你好，我想买一部手机",
        "iPhone有货吗",
        "我的订单号是ORD001，现在到哪了",
        "我想退货，订单号ORD002",
        "质量有问题",
    ]
    
    for user_input in dialogue:
        print(f"👤 用户: {user_input}")
        response = cs.process(user_input)
        print(f"🤖 客服: {response}\n")


if __name__ == "__main__":
    demo_customer_service()
```

### 6.2 案例二：数据处理Pipeline Agent

**场景**：构建一个自动化数据处理Agent，能够接收数据处理请求、协调多个数据处理步骤、生成报告。

```python
"""
案例二：数据处理Pipeline Agent

场景：
- 接收数据处理请求
- 自动规划处理流程
- 执行数据清洗、转换、分析
- 生成处理报告

这个案例展示了：
1. Plan-and-Execute模式
2. 多步骤数据处理
3. 结果验证与报告生成
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from enum import Enum
import json
import re


class DataFormat(Enum):
    """数据格式"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    UNKNOWN = "unknown"


@dataclass
class DataSource:
    """数据源"""
    name: str
    path: str
    format: DataFormat = DataFormat.UNKNOWN
    size: int = 0
    row_count: int = 0


@dataclass
class ProcessingStep:
    """处理步骤"""
    name: str
    description: str
    input_format: DataFormat
    output_format: DataFormat
    handler: Callable


class DataPipelineAgent:
    """
    数据处理Pipeline Agent
    
    功能：
    - 自动识别数据格式
    - 规划处理流程
    - 执行数据处理
    - 生成处理报告
    """
    
    def __init__(self):
        self.processors: Dict[str, ProcessingStep] = {}
        self._register_default_processors()
    
    def _register_default_processors(self):
        """注册默认处理器"""
        
        def validate_csv(data: List[Dict]) -> Dict:
            """验证CSV数据"""
            if not data:
                return {"valid": False, "error": "Empty data"}
            
            required_fields = set(data[0].keys())
            issues = []
            
            for i, row in enumerate(data[1:], start=2):
                missing = required_fields - set(row.keys())
                if missing:
                    issues.append(f"Row {i}: missing fields {missing}")
                
                for key, value in row.items():
                    if value == "" or value is None:
                        issues.append(f"Row {i}: empty value in {key}")
            
            return {
                "valid": len(issues) == 0,
                "total_rows": len(data),
                "issues": issues[:10]  # 最多返回10个问题
            }
        
        def clean_data(data: List[Dict]) -> List[Dict]:
            """清洗数据"""
            cleaned = []
            for row in data:
                cleaned_row = {}
                for key, value in row.items():
                    # 去除首尾空白
                    if isinstance(value, str):
                        value = value.strip()
                    # 跳过空值
                    if value != "" and value is not None:
                        cleaned_row[key] = value
                if cleaned_row:
                    cleaned.append(cleaned_row)
            return cleaned
        
        def transform_to_json(data: List[Dict]) -> str:
            """转换为JSON"""
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        def aggregate_data(data: List[Dict]) -> Dict:
            """数据聚合"""
            if not data:
                return {"count": 0}
            
            # 简单的数值字段聚合
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
        
        def generate_report(data: List[Dict], stats: Dict) -> str:
            """生成报告"""
            report = f"""
# 数据处理报告

## 基本信息
- 记录数: {stats.get('record_count', len(data))}
- 处理时间: {stats.get('process_time', 'N/A')}

## 字段统计
"""
            for key, value in stats.items():
                if key != 'record_count' and key != 'process_time':
                    report += f"- {key}: {value}\n"
            
            report += f"""
## 数据样本 (前3条)
"""
            for i, row in enumerate(data[:3], 1):
                report += f"\n### 记录 {i}\n"
                for key, value in row.items():
                    report += f"- {key}: {value}\n"
            
            return report
        
        # 注册处理器
        self.processors["validate"] = ProcessingStep(
            name="validate",
            description="验证数据完整性和格式",
            input_format=DataFormat.CSV,
            output_format=DataFormat.CSV,
            handler=validate_csv
        )
        
        self.processors["clean"] = ProcessingStep(
            name="clean",
            description="清洗数据（去除空值、空白）",
            input_format=DataFormat.CSV,
            output_format=DataFormat.CSV,
            handler=clean_data
        )
        
        self.processors["to_json"] = ProcessingStep(
            name="to_json",
            description="转换为JSON格式",
            input_format=DataFormat.CSV,
            output_format=DataFormat.JSON,
            handler=transform_to_json
        )
        
        self.processors["aggregate"] = ProcessingStep(
            name="aggregate",
            description="数据聚合统计",
            input_format=DataFormat.CSV,
            output_format=DataFormat.JSON,
            handler=aggregate_data
        )
        
        self.processors["report"] = ProcessingStep(
            name="report",
            description="生成处理报告",
            input_format=DataFormat.CSV,
            output_format=DataFormat.JSON,
            handler=lambda data: (data, {})  # 特殊处理
        )
    
    def detect_format(self, file_path: str) -> DataFormat:
        """检测数据格式"""
        if file_path.endswith('.csv'):
            return DataFormat.CSV
        elif file_path.endswith('.json'):
            return DataFormat.JSON
        elif file_path.endswith(('.xls', '.xlsx')):
            return DataFormat.EXCEL
        return DataFormat.UNKNOWN
    
    def parse_csv(self, content: str) -> List[Dict]:
        """解析CSV内容"""
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = [h.strip() for h in lines[0].split(',')]
        data = []
        
        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            if len(values) == len(headers):
                row = dict(zip(headers, values))
                # 类型转换
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
        """
        根据请求生成处理管道
        
        简化实现：基于关键词匹配
        实际应用应使用LLM进行意图分析和流程规划
        """
        request_lower = request.lower()
        pipeline = []
        
        # 基础流程
        pipeline.append("validate")
        
        if "清洗" in request or "clean" in request_lower:
            pipeline.append("clean")
        
        if "统计" in request or "分析" in request or "aggregate" in request_lower:
            pipeline.append("aggregate")
        
        if "json" in request_lower:
            pipeline.append("to_json")
        
        if "报告" in request or "report" in request_lower:
            pipeline.append("report")
        
        return pipeline if pipeline else ["validate", "clean"]
    
    async def execute_pipeline(self, data: Any, pipeline: List[str]) -> Dict[str, Any]:
        """执行处理管道"""
        import time
        start_time = time.time()
        
        current_data = data
        results = {}
        stats = {}
        
        print(f"\n=== 开始执行管道: {' -> '.join(pipeline)} ===\n")
        
        for step_name in pipeline:
            if step_name not in self.processors:
                print(f"[警告] 未知步骤: {step_name}")
                continue
            
            step = self.processors[step_name]
            print(f"[{step.name}] {step.description}...")
            
            try:
                if step_name == "report":
                    # 报告生成需要数据和统计
                    output = step.handler(current_data, stats)
                    results[step_name] = output
                else:
                    output = step.handler(current_data)
                    results[step_name] = output
                    
                    # 收集统计信息
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
        
        return {
            "pipeline": pipeline,
            "results": results,
            "stats": stats,
            "final_data": current_data
        }


async def demo_data_pipeline():
    """数据处理Pipeline演示"""
    
    print("=" * 60)
    print("案例二：数据处理Pipeline Agent")
    print("=" * 60)
    
    # 模拟数据
    csv_data = """name,age,city,salary
张三,28,北京,15000
李四,35,上海,25000
王五,  42 ,深圳, 35000
赵六,31,广州,20000
,29,杭州,18000"""
    
    # 创建Agent
    agent = DataPipelineAgent()
    
    # 解析数据
    data = agent.parse_csv(csv_data)
    print(f"\n原始数据: {len(data)} 条记录")
    
    # 生成并执行管道
    requests = [
        "验证并清洗数据，然后生成报告",
        "分析数据并进行统计汇总",
    ]
    
    for request in requests:
        print(f"\n{'='*50}")
        print(f"请求: {request}")
        
        pipeline = agent.generate_pipeline(request)
        result = await agent.execute_pipeline(data, pipeline)
        
        print(f"\n统计: {result['stats']}")
        
        if "report" in result['results']:
            report = result['results']['report']
            if isinstance(report, str):
                print(f"\n报告预览:\n{report[:500]}...")


if __name__ == "__main__":
    asyncio.run(demo_data_pipeline())
```

### 6.3 案例三：研究助手Agent

**场景**：构建一个研究助手，能够搜索文献、整理资料、生成文献综述。

```python
"""
案例三：研究助手Agent

场景：
- 搜索学术文献
- 整理和管理资料
- 生成文献综述
- 回答研究问题

这个案例展示了：
1. 工具调用与协调
2. 外部知识检索
3. 内容生成与组织
4. 结构化输出
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import json
from datetime import datetime


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchTask:
    """研究任务"""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    results: Any = None
    error: Optional[str] = None


@dataclass
class Literature:
    """文献"""
    title: str
    authors: List[str]
    year: int
    venue: str = ""  # 发表场所
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
    """
    研究助手Agent
    
    功能：
    - 文献搜索
    - 资料整理
    - 文献综述生成
    - 研究问题回答
    """
    
    def __init__(self):
        self.tools = self._register_tools()
        self.literature_db: List[Literature] = []
        self.notes: Dict[str, str] = {}  # 笔记存储
        self._load_sample_literature()
    
    def _register_tools(self) -> Dict[str, Callable]:
        """注册工具"""
        return {
            "search_papers": self._search_papers,
            "get_paper_details": self._get_paper_details,
            "take_notes": self._take_notes,
            "list_notes": self._list_notes,
            "generate_outline": self._generate_outline,
            "write_section": self._write_section,
        }
    
    def _load_sample_literature(self):
        """加载示例文献库"""
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
                title="GPT-3: Language Models are Few-Shot Learners",
                authors=["Brown", "Mann", "Ryder"],
                year=2020,
                venue="NeurIPS",
                abstract="We demonstrate that scaling up language models greatly improves task-agnostic performance.",
                citations=30000,
                keywords=["GPT-3", "few-shot", "language model"]
            ),
            Literature(
                title="Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
                authors=["Wei", "Wang", "Schuurmans"],
                year=2022,
                venue="NeurIPS",
                abstract="We explore how generating a chain of thought can improve reasoning abilities.",
                citations=8000,
                keywords=["chain-of-thought", "reasoning", "prompting"]
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
        """搜索文献"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored = []
        for lit in self.literature_db:
            # 计算相关性得分
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
        
        results = [lit.to_dict() for _, lit in scored[:max_results]]
        return results
    
    def _get_paper_details(self, title: str) -> Dict:
        """获取文献详情"""
        for lit in self.literature_db:
            if title.lower() in lit.title.lower():
                return lit.to_dict()
        return {"error": "Paper not found"}
    
    def _take_notes(self, key: str, content: str) -> str:
        """记笔记"""
        self.notes[key] = content
        return f"笔记已保存: {key}"
    
    def _list_notes(self) -> List[str]:
        """列出笔记"""
        return list(self.notes.keys())
    
    def _generate_outline(self, topic: str, num_sections: int = 5) -> List[str]:
        """生成大纲"""
        # 简化实现
        return [
            f"1. {topic}概述",
            f"2. {topic}的核心概念",
            f"3. {topic}的主要方法",
            f"4. {topic}的应用场景",
            f"5. {topic}的未来发展方向",
            f"6. 参考文献"
        ]
    
    def _write_section(self, section_title: str, context: Dict = None) -> str:
        """写章节内容（模拟）"""
        return f"""
## {section_title}

这部分内容将详细讨论{section_title}相关的主题。
（实际实现中，这里会调用LLM生成完整内容）

### 3.1 背景介绍
介绍{section_title}的研究背景和意义。

### 3.2 主要方法
详细描述主要的方法和技术。

### 3.3 案例分析
通过具体案例说明应用。
"""
    
    async def research_task(self, task_description: str) -> Dict[str, Any]:
        """
        执行研究任务
        
        这是一个综合性的研究任务流程
        """
        print(f"\n{'='*60}")
        print(f"开始研究任务: {task_description}")
        print(f"{'='*60}\n")
        
        results = {
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "steps": []
        }
        
        # 步骤1: 理解任务
        print("[步骤1] 理解研究任务...")
        topic = task_description.replace("研究", "").replace("调查", "").strip()
        results["steps"].append({"step": "understanding", "status": "completed"})
        
        # 步骤2: 搜索相关文献
        print(f"[步骤2] 搜索 '{topic}' 相关文献...")
        papers = self._search_papers(topic, max_results=5)
        results["papers"] = papers
        results["steps"].append({"step": "search", "papers_found": len(papers)})
        print(f"找到 {len(papers)} 篇相关文献\n")
        
        for i, paper in enumerate(papers[:3], 1):
            print(f"  {i}. {paper['title']} ({paper['year']})")
            print(f"     作者: {', '.join(paper['authors'][:3])}")
            print(f"     引用: {paper['citations']:,}")
            print()
        
        # 步骤3: 整理笔记
        print("[步骤3] 整理研究笔记...")
        note_key = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        note_content = f"""
研究主题: {topic}
相关文献数: {len(papers)}
关键文献: {papers[0]['title'] if papers else 'N/A'}

主要发现:
- [待补充]
- [待补充]

研究空白:
- [待补充]
"""
        self._take_notes(note_key, note_content)
        results["steps"].append({"step": "notes_taken", "note_key": note_key})
        
        # 步骤4: 生成大纲
        print("[步骤4] 生成文献综述大纲...")
        outline = self._generate_outline(topic)
        results["outline"] = outline
        results["steps"].append({"step": "outline_generated"})
        
        print("\n生成的文献综述大纲:")
        for item in outline:
            print(f"  {item}")
        
        # 步骤5: 生成综述内容（部分）
        print("\n[步骤5] 生成综述内容（样例）...")
        section = self._write_section(f"{topic}研究综述", {"papers": papers})
        results["section_content"] = section
        results["steps"].append({"step": "content_generated"})
        
        results["status"] = "completed"
        
        return results


# ==================== 演示 ====================

async def demo_research_assistant():
    """研究助手演示"""
    
    assistant = ResearchAssistant()
    
    # 执行研究任务
    result = await assistant.research_task("研究大语言模型Agent架构")
    
    print("\n" + "="*60)
    print("研究任务完成!")
    print("="*60)
    print(f"\n找到文献: {len(result.get('papers', []))}")
    print(f"生成大纲: {len(result.get('outline', []))} 个章节")


if __name__ == "__main__":
    asyncio.run(demo_research_assistant())
```

---

## 附录：课程代码运行指南

### 环境准备

```bash
# 创建虚拟环境
python -m venv harness-env
source harness-env/bin/activate  # Linux/Mac
# harness-env\Scripts\activate  # Windows

# 安装依赖
pip install openai tiktoken asyncio
```

### 代码文件结构

```
harness-engineering-course/
├── README.md              # 课程文档
├── examples/
│   ├── 01_react_agent.py       # ReAct Agent实现
│   ├── 02_plan_execute.py      # Plan-and-Execute实现
│   ├── 03_tool_system.py       # 工具调用系统
│   ├── 04_validation.py        # 输出验证系统
│   ├── 05_teaching_cases.py    # 教学案例
│   ├── 06_harness_runtime.py   # Harness运行时、护栏、追踪与评估
│   └── harness_engineering_complete.ipynb # 完整课堂演示Notebook
└── utils/
    ├── llm_client.py      # LLM客户端
    └── __init__.py
```

### 运行示例

```bash
# 运行ReAct Agent演示
python examples/01_react_agent.py

# 运行Plan-and-Execute演示
python examples/02_plan_execute.py

# 运行教学案例
python examples/05_teaching_cases.py

# 运行Harness运行时演示
python examples/06_harness_runtime.py

# 打开完整Notebook演示
jupyter notebook examples/harness_engineering_complete.ipynb
```

---

**课程结束**

掌握以上内容后，学生将能够：
1. 理解 AI Harness 的核心概念和架构模式
2. 实现 ReAct 和 Plan-and-Execute 等 Agent 模式
3. 设计和使用工具调用系统
4. 实现输出质量控制、护栏、评估和追踪
5. 构建可控、可审计、可回滚的 AI Harness 应用
