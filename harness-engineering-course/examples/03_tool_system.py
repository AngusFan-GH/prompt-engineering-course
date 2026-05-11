"""
工具调用系统设计
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union, get_type_hints, get_origin, get_args
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
    
    print("\n=== 生成工具提示 ===")
    print(registry.get_tools_for_prompt()[:500])


if __name__ == "__main__":
    demo_tool_registry()
