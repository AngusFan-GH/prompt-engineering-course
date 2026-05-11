"""
examples/05_react.py
ReAct (Reasoning + Acting) 模式示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient
from typing import Callable, Dict, Any


class ReActAgent:
    """ReAct模式Agent"""
    
    def __init__(self, config: LLMConfig):
        self.client = LLMClient(config)
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable):
        """注册工具"""
        self.tools[name] = func
    
    def _default_search(self, query: str) -> str:
        """模拟搜索工具"""
        return f"[搜索结果] 关于'{query}'的信息..."
    
    def _default_calculate(self, expression: str) -> str:
        """计算工具"""
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"计算错误: {e}"
    
    def _default_lookup(self, item: str) -> str:
        """查询工具"""
        database = {
            "Python": "一种高级编程语言，由Guido van Rossum创建",
            "LLM": "Large Language Model，大语言模型的缩写",
            "Prompt": "Prompt是给大语言模型的输入文本",
            "FastAPI": "一个现代、快速的Python Web框架",
            "SQL": "Structured Query Language，用于操作数据库"
        }
        return database.get(item, f"未找到关于'{item}'的信息")
    
    def run(self, task: str, max_iterations: int = 5) -> str:
        """
        执行ReAct循环
        
        Args:
            task: 任务描述
            max_iterations: 最大迭代次数
        
        Returns:
            最终答案
        """
        # 注册默认工具
        if not self.tools:
            self.register_tool("search", self._default_search)
            self.register_tool("calculate", self._default_calculate)
            self.register_tool("lookup", self._default_lookup)
        
        # 构建系统提示
        tool_descriptions = "\n".join([f"- {name}: {func.__doc__}" 
                                        for name, func in self.tools.items()])
        
        system_prompt = f"""你是一个推理和行动Agent。

可用工具:
{tool_descriptions}

输出格式 (每轮必须严格遵循):
Thought: <思考当前情况，决定下一步行动>
Action: <工具名> <工具参数>
Observation: <观察执行结果>

重复这个循环直到得到最终答案，然后输出:
Final Answer: <最终答案>"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"任务: {task}\n\n请开始推理和行动。"}
        ]
        
        context = ""
        
        for i in range(max_iterations):
            response = self.client.chat(messages, temperature=0)
            print(f"\n--- 迭代 {i+1} ---")
            print(response)
            
            # 检查是否得到最终答案
            if "Final Answer:" in response:
                final_answer = response.split("Final Answer:")[-1].strip()
                return final_answer
            
            # 解析Action并执行
            lines = response.split("\n")
            action_executed = False
            for line in lines:
                if line.startswith("Action:") and not action_executed:
                    action_part = line.replace("Action:", "").strip()
                    # 解析工具名和参数（可能带引号）
                    parts = action_part.split(maxsplit=1)
                    if len(parts) == 2:
                        tool_name, tool_arg = parts
                        tool_arg = tool_arg.strip('"\'')
                        
                        if tool_name in self.tools:
                            try:
                                result = self.tools[tool_name](tool_arg)
                                context += f"\nObservation: 执行 {tool_name}('{tool_arg}') 结果: {result}"
                                print(f"Observation: {result}")
                                action_executed = True
                            except Exception as e:
                                context += f"\nObservation: 工具执行错误: {e}"
            
            if not action_executed and "Observation:" not in response:
                # 没有找到有效的Action，尝试直接给出答案
                if i == max_iterations - 1:
                    return "无法完成任务，达到最大迭代次数"
            
            # 添加到对话历史
            messages.append({"role": "assistant", "content": response})
            if context:
                messages.append({"role": "user", "content": context})
        
        return "达到最大迭代次数，未能得到答案"


def react_example_direct():
    """直接使用ReAct风格Prompt"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7", temperature=0)
    client = LLMClient(config)
    
    react_prompt = """一个商店销售以下商品：
- iPhone 15: 原价7999元，促销价6999元
- AirPods Pro: 原价1999元，打8折
- iPad Air: 原价4799元，参加满1000减200活动

问题: 小明买了1部iPhone和2个AirPods，总价多少？

请按以下格式推理:

Thought: 分析需要计算的内容
Action: calculate <计算表达式>
Observation: <计算结果>
...重复直到得到答案
Final Answer: <最终总价>"""
    
    messages = [{"role": "user", "content": react_prompt}]
    response = client.chat(messages)
    
    print("=" * 50)
    print("ReAct 模式示例")
    print("=" * 50)
    print(response)


def react_agent_example():
    """使用ReAct Agent框架"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7", temperature=0)
    agent = ReActAgent(config)
    
    # 自定义工具
    def get_weather(city: str) -> str:
        """获取城市天气"""
        weather_db = {
            "北京": "晴，25°C",
            "上海": "多云，28°C",
            "深圳": "雷阵雨，30°C"
        }
        return weather_db.get(city, f"未找到{city}的天气信息")
    
    agent.register_tool("weather", get_weather)
    
    task = "北京和上海哪个城市更热？"
    print("\n" + "=" * 50)
    print("ReAct Agent 工具调用示例")
    print("=" * 50)
    result = agent.run(task, max_iterations=3)
    print(f"\n最终结果: {result}")


def multi_step_task_example():
    """多步骤任务示例"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7", temperature=0)
    agent = ReActAgent(config)
    
    # 添加更多工具
    def get_stock_price(symbol: str) -> str:
        """获取股票价格"""
        stocks = {
            "AAPL": "$178.50",
            "GOOGL": "$142.30",
            "MSFT": "$378.90"
        }
        return stocks.get(symbol, f"未找到{symbol}的股价")
    
    def calculate_investment(amount: str, price: str) -> str:
        """计算投资数量"""
        try:
            amt = float(amount.replace("$", ""))
            prc = float(price.replace("$", ""))
            shares = amt / prc
            return f"可以购买 {shares:.2f} 股"
        except:
            return "计算错误"
    
    agent.register_tool("stock_price", get_stock_price)
    agent.register_tool("calculate", calculate_investment)
    
    task = "如果我有1000美元，应该买多少股苹果(AAPL)股票？"
    
    print("\n" + "=" * 50)
    print("ReAct 多步骤任务示例")
    print("=" * 50)
    result = agent.run(task, max_iterations=5)
    print(f"\n最终结果: {result}")


if __name__ == "__main__":
    react_example_direct()
    react_agent_example()
    multi_step_task_example()
