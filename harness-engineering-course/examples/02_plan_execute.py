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
