"""
ReAct Agent 实现

ReAct = Reasoning + Acting

核心循环:
1. Thought: 思考当前状态和下一步行动
2. Action: 执行工具调用
3. Observation: 观察结果
4. (重复直到任务完成)
"""

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
    llm_call: Callable  # LLM调用函数
    max_iterations: int = 10
    
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
