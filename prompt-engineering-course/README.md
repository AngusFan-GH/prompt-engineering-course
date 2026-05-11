# 提示词工程（Prompt Engineering）课程

> 面向软件学院本科生/研究生的技术教程

---

## 目录

1. [核心概念定义](#1-核心概念定义)
2. [关键技术要素](#2-关键技术要素)
3. [主流技巧和方法论](#3-主流技巧和方法论)
4. [实际代码案例](#4-实际代码案例)
5. [常见陷阱与最佳实践](#5-常见陷阱与最佳实践)
6. [教学场景化案例](#6-教学场景化案例)

---

## 1. 核心概念定义

### 1.1 什么是提示词工程

**提示词工程（Prompt Engineering）** 是指优化与 LLM（大语言模型）交互输入的技术和方法论，目的是获得更准确、更有用的输出。

```
┌─────────────────────────────────────────────────────────┐
│                      Prompt Engineering                   │
│  ┌─────────┐    ┌──────────────┐    ┌─────────┐         │
│  │  用户   │ -> │  Prompt设计  │ -> │  LLM    │         │
│  │  意图   │    │  + 优化策略  │    │  输出   │         │
│  └─────────┘    └──────────────┘    └─────────┘         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 关键术语

| 术语 | 英文 | 定义 |
|------|------|------|
| Prompt | 提示词 | 给LLM的输入文本 |
| Completion | 完成/回复 | LLM的输出文本 |
| Token | 令牌 | 文本处理的最小单位（约0.75个单词） |
| System Prompt | 系统提示 | 设定AI角色和行为的顶层指令 |
| Few-shot | 少样本学习 | 通过少量示例引导模型理解任务 |
| CoT | 思维链 | 引导模型展示推理过程 |
| Temperature | 温度参数 | 控制输出随机性（0=确定，1=创意） |
| Top-p | 核采样 | 控制输出多样性的采样策略 |

### 1.3 Token计算基础

```python
# 中英文token估算规则
def estimate_tokens(text: str) -> int:
    """简化的token估算"""
    # 英文: 约4字符=1 token
    # 中文: 约1.5-2字符=1 token
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.5 + other_chars * 0.25)
```

---

## 2. 关键技术要素

### 2.1 角色设定（Role Assignment）

设定AI扮演特定角色，利用角色特性获得更专业的回答。

```
┌─────────────────────────────────────────────────────────┐
│ System Prompt 示例:                                      │
│ "你是一位具有10年经验的Python后端工程师，专长于:          │
│  - FastAPI、Django开发                                   │
│  - 数据库设计与优化                                      │
│  - RESTful API架构                                       │
│ 请以专家身份回答以下技术问题。"                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 格式控制（Format Control）

明确指定期望的输出格式。

```
┌─────────────────────────────────────────────────────────┐
│ 格式控制示例:                                            │
│                                                          │
│ "请以JSON格式返回，字段包括:                              │
│  {                                                      │
│    'name': string,      // 产品名称                      │
│    'price': number,     // 价格(元)                      │
│    'features': string[] // 核心特性列表                   │
│  }"                                                    │
└─────────────────────────────────────────────────────────┘
```

### 2.3 链式思维（Chain of Thought, CoT）

引导模型展示推理过程，提高复杂问题的准确性。

```
┌─────────────────────────────────────────────────────────┐
│ 零样本CoT示例:                                           │
│                                                          │
│ 问题: "小明有5个苹果，小红给了他3个，然后小明吃了2个，    │
│        小明现在有多少个苹果？"                            │
│                                                          │
│ 要求: "请逐步思考(show your reasoning)，最后给出答案。"  │
└─────────────────────────────────────────────────────────┘
```

### 2.4 上下文窗口（Context Window）

现代LLM的上下文窗口限制与利用策略：

| 模型 | 上下文窗口 |
|------|-----------|
| GPT-4 | 128K tokens |
| Claude 3 | 200K tokens |
| Gemini 1.5 | 1M tokens |

```
利用策略:
1. 关键信息放开头/结尾（位置效应）
2. 冗余信息压缩精简
3. 重要指令重复（尤其是长文本场景）
```

---

## 3. 主流技巧和方法论

### 3.1 Few-Shot Learning（少样本学习）

通过K个示例让模型理解任务模式。

```python
# 示例：情感分析任务
few_shot_prompt = """
请判断以下评论的情感是正面还是负面。

示例1:
评论: "这家餐厅的服务太差了，等了1小时才上菜"
情感: 负面

示例2:
评论: "手机性能很强，拍照效果很满意"
情感: 正面

示例3:
评论: "还行吧，没有什么特别的感觉"
情感: 中性

请判断:
评论: "物流很快，但产品有划痕"
情感:"""
```

### 3.2 Chain of Thought (CoT) - 思维链

#### 3.2.1 零样本CoT（Zero-shot CoT）

```
在问题后添加: "请一步一步思考" 或 "Let me think step by step"
```

#### 3.2.2 完整示例（对比）

```
┌──────────────────────────────────────────────────────────┐
│ 基础Prompt:                                               │
│ "一个商店有87个苹果，卖出了33个，又进货50个，现在有多少？" │
│ 直接回答: 104                                            │
│ （可能错误）                                              │
├──────────────────────────────────────────────────────────┤
│ CoT Prompt:                                               │
│ "请逐步推理这个问题:                                      │
│  1. 原有: 87个                                           │
│  2. 卖出33个: 87 - 33 = 54个                              │
│  3. 又进货50个: 54 + 50 = 104个                           │
│ 最终答案: 104"                                           │
│ （正确）                                                  │
└──────────────────────────────────────────────────────────┘
```

### 3.3 ReAct (Reasoning + Acting)

结合推理与行动的框架，适用于需要外部工具的场景。

```
┌─────────────────────────────────────────────────────────┐
│ ReAct循环:                                                │
│  1. Thought (思考) -> 决定下一步行动                      │
│  2. Action (行动) -> 执行工具                             │
│  3. Observation (观察) -> 解读结果                       │
│  4. 重复直到得到最终答案                                  │
└─────────────────────────────────────────────────────────┘
```

### 3.4 Tree of Thoughts (ToT) - 思维树

探索多种解题路径，选择最优方案。

```
                    问题
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
      路径A         路径B         路径C
        ↓             ↓             ↓
     方案A1         方案B1        方案C1
        ↓             ↓             ↓
     方案A2         方案B2        方案C2
        ↓             ↓             ↓
     ✗放弃          ✓最优         ✗放弃
```

### 3.5 Prompt Chaining（提示链）

将复杂任务分解为多个子任务，按顺序执行。

```python
# 示例：文章处理流水线
pipeline = [
    {
        "task": "summarize",
        "prompt": "请总结以下文章的核心观点（不超过50字）..."
    },
    {
        "task": "extract_keywords", 
        "prompt": "基于摘要，提取5个关键词..."
    },
    {
        "task": "generate_tags",
        "prompt": "根据关键词，生成3个分类标签..."
    }
]
```

### 3.6 Self-Consistency（自洽性）

通过多次采样选择最一致的答案。

```python
# 投票机制示例
responses = []
for _ in range(5):
    response = call_llm(prompt + "请推理这个问题")
    responses.append(extract_answer(response))

# 统计最常见的答案
from collections import Counter
final_answer = Counter(responses).most_common(1)[0][0]
```

---

## 4. 实际代码案例

### 4.1 环境准备

```bash
pip install openai anthropic requests python-dotenv
```

### 4.2 基础调用框架

```python
"""
prompt_engineering/
├── examples/
│   ├── 01_basic_chat.py
│   ├── 02_role_prompting.py
│   ├── 03_few_shot.py
│   ├── 04_cot.py
│   ├── 05_react.py
│   └── 06_advanced_techniques.py
├── utils/
│   └── llm_client.py
└── config.py
"""

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import json

# config.py
@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "openai"  # openai, anthropic, ollama
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048

# utils/llm_client.py
class LLMClient:
    """统一LLM调用客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._load_api_key()
    
    def _load_api_key(self):
        """从环境变量加载API密钥"""
        if self.config.provider == "openai":
            self.config.api_key = os.getenv("OPENAI_API_KEY") or self.config.api_key
        elif self.config.provider == "anthropic":
            self.config.api_key = os.getenv("ANTHROPIC_API_KEY") or self.config.api_key
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: Optional[float] = None,
             **kwargs) -> str:
        """
        统一聊天接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            **kwargs: 其他参数
        
        Returns:
            str: 模型回复
        """
        if self.config.provider == "openai":
            return self._call_openai(messages, temperature, **kwargs)
        elif self.config.provider == "anthropic":
            return self._call_anthropic(messages, temperature, **kwargs)
        elif self.config.provider == "ollama":
            return self._call_ollama(messages, temperature, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")
    
    def _call_openai(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用OpenAI API"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装openai: pip install openai")
        
        client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        
        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用Anthropic API"""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("请安装anthropic: pip install anthropic")
        
        client = Anthropic(api_key=self.config.api_key)
        
        # 转换消息格式
        system = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered_messages.append(msg)
        
        response = client.messages.create(
            model=self.config.model,
            system=system,
            messages=filtered_messages,
            temperature=temperature or self.config.temperature,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        return response.content[0].text
    
    def _call_ollama(self, messages: List[Dict], temperature: Optional[float], **kwargs) -> str:
        """调用Ollama本地模型"""
        import requests
        
        url = (self.config.base_url or "http://localhost:11434") + "/api/chat"
        
        response = requests.post(url, json={
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "stream": False
        })
        response.raise_for_status()
        return response.json()["message"]["content"]
```

### 4.3 示例1：基础对话

```python
"""
examples/01_basic_chat.py
基础对话示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient


def basic_chat_example():
    """最基础的对话调用"""
    
    config = LLMConfig(
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    client = LLMClient(config)
    
    messages = [
        {"role": "user", "content": "你好，介绍一下Python的列表推导式"}
    ]
    
    response = client.chat(messages)
    print("=" * 50)
    print("基础对话示例")
    print("=" * 50)
    print(f"问题: {messages[0]['content']}")
    print(f"\n回答:\n{response}")


if __name__ == "__main__":
    basic_chat_example()
```

### 4.4 示例2：角色设定

```python
"""
examples/02_role_prompting.py
角色设定示例 - 模拟专业顾问
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient


def role_prompting_example():
    """使用角色设定获得更专业的回答"""
    
    config = LLMConfig(
        provider="openai", 
        model="gpt-4o-mini",
        temperature=0.5  # 较低温度获得更稳定的输出
    )
    
    client = LLMClient(config)
    
    # System Prompt: 设定专业角色
    system_prompt = """你是一位资深的Python后端工程师，具有10年开发经验。
专长领域:
- FastAPI、Django、Flask等Web框架
- PostgreSQL、MongoDB数据库设计与优化
- Redis缓存架构
- RESTful API设计与微服务架构
- Docker、Kubernetes容器化部署

回答要求:
1. 技术解释要准确，附带代码示例
2. 最佳实践要结合实际场景
3. 指出常见的坑和解决方案"""
    
    user_prompt = "我应该选择FastAPI还是Django来开发一个高并发的RESTful API服务？"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = client.chat(messages)
    
    print("=" * 50)
    print("角色设定示例 - Python后端专家")
    print("=" * 50)
    print(f"问题: {user_prompt}")
    print(f"\n回答:\n{response}")


def code_review_role_example():
    """代码审查角色"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    
    system_prompt = """你是一位严格的代码审查工程师。
审查重点:
1. 代码安全性（SQL注入、XSS等）
2. 性能问题（N+1查询、内存泄漏）
3. 代码可读性和可维护性
4. 错误处理是否完善

输出格式:
## 审查结果

### 问题列表
| 严重程度 | 位置 | 问题描述 | 建议修复 |

### 总体评分
/10

### 改进建议"""
    
    code_snippet = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()
'''
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请审查以下Python代码:\n{code_snippet}"}
    ]
    
    response = client.chat(messages)
    print("\n" + "=" * 50)
    print("代码审查示例")
    print("=" * 50)
    print(response)


if __name__ == "__main__":
    role_prompting_example()
    code_review_role_example()
```

### 4.5 示例3：Few-Shot Learning

```python
"""
examples/03_few_shot.py
Few-Shot学习示例 - 多示例引导
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient


def sentiment_analysis_few_shot():
    """情感分析 - Few-Shot示例"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0.3)
    client = LLMClient(config)
    
    # 构建Few-Shot prompt
    few_shot_prompt = """你是一个情感分析专家。请判断评论的情感是正面、负面还是中性。

示例格式:
评论: <评论内容>
情感: <正面/负面/中性>

【示例】

评论: "这家餐厅的牛排做得非常棒，服务员态度也很好，下次还会来！"
情感: 正面

评论: "等了2小时才上菜，菜品还凉了，太失望了"
情感: 负面

评论: "就是一个普通的快捷酒店，没有特别印象深刻的"
情感: 中性

评论: "瑜伽裤的弹性很好，穿着很舒服，但是颜色比图片暗一些"
情感: 中性

评论: "这个课程讲得很清楚，老师水平很高"
情感: 正面

【待分析】

评论: "键盘手感不错，但是用了三个月就出现了双击问题"
情感:"""
    
    messages = [{"role": "user", "content": few_shot_prompt}]
    response = client.chat(messages)
    
    print("=" * 50)
    print("Few-Shot情感分析示例")
    print("=" * 50)
    print(f"回答: {response}")


def entity_extraction_few_shot():
    """实体提取 - 结构化输出"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    
    system_prompt = """你是一个信息提取专家。根据用户提供的文本，提取结构化信息。

输出必须严格遵循以下JSON格式，不要添加任何其他内容:
{
    "person": {"name": "姓名", "age": 年龄},
    "company": {"name": "公司名", "position": "职位"},
    "skills": ["技能1", "技能2"]
}"""
    
    few_shot_examples = """
【示例1】
文本: "张伟是阿里巴巴的高级Java工程师，有8年开发经验，擅长微服务架构。"
输出: {"person": {"name": "张伟", "age": null}, "company": {"name": "阿里巴巴", "position": "高级Java工程师"}, "skills": ["Java", "微服务架构"]}

【示例2】
文本: "李娜，35岁，华为技术总监，精通云计算和容器技术。"
输出: {"person": {"name": "李娜", "age": 35}, "company": {"name": "华为", "position": "技术总监"}, "skills": ["云计算", "容器技术"]}

【待提取】
文本: "王鹏是腾讯的iOS开发工程师，12年经验，精通Swift和Flutter移动开发。"
输出:"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": few_shot_examples}
    ]
    
    response = client.chat(messages)
    print("\n" + "=" * 50)
    print("Few-Shot实体提取示例")
    print("=" * 50)
    print(f"回答: {response}")


if __name__ == "__main__":
    sentiment_analysis_few_shot()
    entity_extraction_few_shot()
```

### 4.6 示例4：Chain of Thought (CoT)

```python
"""
examples/04_cot.py
Chain of Thought 思维链示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient


def zero_shot_cot():
    """零样本CoT - 简单添加'请思考步骤'"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0)
    client = LLMClient(config)
    
    problem = """
问题: 一个水池有进水管和出水管。进水管每分钟注水15升，出水管每分钟排水8升。
      如果水池容量是500升，初始为空，同时打开进水管和出水管，需要多少分钟才能装满？
    """
    
    # 基础问题（可能直接给出错误答案）
    messages_basic = [
        {"role": "user", "content": f"{problem}\n请直接给出答案。"}
    ]
    
    # CoT问题（强制展示推理过程）
    messages_cot = [
        {"role": "user", "content": f"{problem}\n请一步一步思考，展示完整的推理过程。"}
    ]
    
    response_basic = client.chat(messages_basic)
    response_cot = client.chat(messages_cot)
    
    print("=" * 50)
    print("Zero-shot CoT 示例")
    print("=" * 50)
    print(f"【直接回答】\n{response_basic}")
    print(f"\n【CoT推理】\n{response_cot}")


def math_word_problem_cot():
    """数学应用题 - 完整CoT"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    
    problem = """
某电商平台在双十一进行促销：
- 原价商品打8折
- 优惠券：满200减50
- 购物节额外补贴：最终价格的10%

小明想买一个原价450元的背包，实际需要支付多少元？
"""
    
    cot_prompt = """请按照以下步骤逐步推理这个问题：

**步骤1: 计算折后价格**
**步骤2: 判断是否满足优惠券条件**
**步骤3: 计算优惠后的价格**
**步骤4: 计算购物节补贴金额**
**步骤5: 计算最终支付金额**

每个步骤都要写出计算公式和结果。"""
    
    messages = [
        {"role": "user", "content": problem + "\n" + cot_prompt}
    ]
    
    response = client.chat(messages)
    print("\n" + "=" * 50)
    print("数学应用题 CoT 详解")
    print("=" * 50)
    print(response)


def cot_with_self_verification():
    """CoT + 自我验证"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0)
    client = LLMClient(config)
    
    problem = """
判断以下论证是否正确：
"如果所有猫都喜欢鱼，小明是一只猫，所以小明喜欢吃鱼。"
"""
    
    verification_prompt = """请按以下步骤分析这个逻辑论证：

**步骤1: 识别前提和结论**
**步骤2: 检查前提是否为真**
**步骤3: 检查推理形式是否有效**
**步骤4: 得出结论**

**额外验证**: 尝试构造一个反例来检验论证的有效性。

格式：
论证结构: ...
有效性分析: ...
反例检验: ..."""
    
    messages = [
        {"role": "user", "content": problem + "\n" + verification_prompt}
    ]
    
    response = client.chat(messages)
    print("\n" + "=" * 50)
    print("CoT + 自我验证")
    print("=" * 50)
    print(response)


if __name__ == "__main__":
    zero_shot_cot()
    math_word_problem_cot()
    cot_with_self_verification()
```

### 4.7 示例5：ReAct模式

```python
"""
examples/05_react.py
ReAct (Reasoning + Acting) 模式示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient
import json


class ReActAgent:
    """ReAct模式Agent"""
    
    def __init__(self, config: LLMConfig):
        self.client = LLMClient(config)
        self.tools = {
            "search": self._search_tool,
            "calculate": self._calculate_tool,
            "look_up": self._lookup_tool
        }
    
    def _search_tool(self, query: str) -> str:
        """模拟搜索工具"""
        # 实际场景中可接入搜索引擎
        return f"[搜索结果] 关于'{query}'的信息: ..."
    
    def _calculate_tool(self, expression: str) -> str:
        """计算工具"""
        try:
            result = eval(expression)
            return str(result)
        except:
            return "计算错误"
    
    def _lookup_tool(self, item: str, key: str) -> str:
        """查询工具"""
        database = {
            "Python": "一种高级编程语言",
            "LLM": "Large Language Model，大语言模型",
            "Prompt": "人机交互的输入文本"
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
        context = ""
        
        system_prompt = f"""你是一个推理和行动Agent。

可用工具:
- search(query): 搜索信息
- calculate(expression): 数学计算
- look_up(item, key): 查询数据库

输出格式 (每轮必须严格遵循):
Thought: <思考当前情况，决定下一步>
Action: <工具名> <工具参数>
Observation: <观察执行结果>
... (多轮)
Final Answer: <最终答案>"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"任务: {task}\n\n请开始推理和行动。"}
        ]
        
        for i in range(max_iterations):
            response = self.client.chat(messages, temperature=0)
            
            # 检查是否得到最终答案
            if "Final Answer:" in response:
                final_answer = response.split("Final Answer:")[-1].strip()
                return final_answer
            
            # 解析Action并执行
            lines = response.split("\n")
            for line in lines:
                if line.startswith("Action:"):
                    action_part = line.replace("Action:", "").strip()
                    # 解析工具名和参数
                    parts = action_part.split(" ", 1)
                    if len(parts) == 2:
                        tool_name, tool_arg = parts
                        if tool_name in self.tools:
                            result = self.tools[tool_name](tool_arg)
                            context += f"\nObservation: {result}"
            
            # 添加到上下文
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": context})
        
        return "达到最大迭代次数，未能得到答案"


def react_example():
    """ReAct示例"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0)
    client = LLMClient(config)
    
    # 简单的ReAct对话演示
    react_prompt = """一个商店销售手机：
- iPhone原价8000元，促销价6800元
- Samsung原价6000元，打75折
- 小米原价4000元，参加满1000减200活动

问题: 如果小明买了1部iPhone和2部Samsung，总价是多少？
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
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0)
    agent = ReActAgent(config)
    
    task = "查找LLM的定义，然后计算10的平方根乘以5"
    result = agent.run(task)
    
    print("\n" + "=" * 50)
    print("ReAct Agent 执行")
    print("=" * 50)
    print(f"任务: {task}")
    print(f"结果: {result}")


if __name__ == "__main__":
    react_example()
    react_agent_example()
```

### 4.8 示例6：高级技巧组合

```python
"""
examples/06_advanced_techniques.py
高级技巧组合示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient
from collections import Counter


class AdvancedPrompting:
    """高级提示技巧"""
    
    def __init__(self, config: LLMConfig):
        self.client = LLMClient(config)
    
    def self_consistency(self, prompt: str, n_samples: int = 5) -> str:
        """
        Self-Consistency 自洽性
        通过多次采样选择最一致的答案
        """
        responses = []
        for _ in range(n_samples):
            response = self.client.chat(
                [{"role": "user", "content": prompt + "\n请推理并给出答案。"}],
                temperature=0.9
            )
            responses.append(response)
        
        # 简单投票：选择出现最多的答案模式
        # 实际场景中需要更复杂的答案解析
        print(f"采样了 {len(responses)} 次，得到 {len(set(responses))} 种不同回答")
        
        return responses[0]  # 简化处理
    
    def tree_of_thought(self, problem: str, options: list) -> str:
        """
        Tree of Thoughts 思维树
        探索多种解题路径
        """
        results = []
        
        for i, option in enumerate(options):
            prompt = f"""问题: {problem}

考虑方案 {i+1}: {option}

请详细分析:
1. 这个方案的优点
2. 这个方案的缺点  
3. 可能的风险

最终评价: ..."""
            
            response = self.client.chat([{"role": "user", "content": prompt}])
            results.append({"option": option, "analysis": response})
        
        # 综合评估
        synthesis_prompt = f"""请比较以下 {len(options)} 个方案，并推荐最佳选择:

{chr(10).join([f'方案{i+1}: {r["option"]}' for i, r in enumerate(results)])}

分析如下:
{chr(10).join([f'【方案{i+1} {r["option"]}】\n{r["analysis"]}' for i, r in enumerate(results)])}

综合推荐:"""
        
        final = self.client.chat([{"role": "user", "content": synthesis_prompt}])
        return final
    
    def prompt_chaining(self, task: str, chain: list) -> str:
        """
        Prompt Chaining 提示链
        将复杂任务分解为多个子任务
        """
        context = f"初始任务: {task}\n\n"
        
        for i, step in enumerate(chain):
            step_prompt = f"""【步骤 {i+1}: {step['task']}】

任务描述: {step['description']}
上下文: {context}

{step['prompt_template']}"""
            
            result = self.client.chat([{"role": "user", "content": step_prompt}])
            context += f"\n\n[步骤{i+1}结果]: {result}"
            print(f"✓ 步骤 {i+1} 完成: {step['task']}")
        
        return context


def advanced_techniques_demo():
    """高级技巧演示"""
    
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    advanced = AdvancedPrompting(config)
    
    print("=" * 50)
    print("Self-Consistency 示例")
    print("=" * 50)
    
    problem = """
推算一下：如果一个编程初学者每周花15小时学习，
需要多少周才能达到能找工作的水平？
假设'能找到工作'的标准是：
1. 掌握至少一门编程语言
2. 能独立完成小型项目
3. 理解基本的数据结构和算法
"""
    
    # self_consistency_result = advanced.self_consistency(problem, n_samples=3)
    # print(f"\n结果: {self_consistency_result}")
    print("(演示模式，跳过实际调用)")
    
    print("\n" + "=" * 50)
    print("Tree of Thoughts 示例")
    print("=" * 50)
    
    tech_problem = "创业公司应该选择什么技术栈来构建MVP？"
    options = [
        "使用微服务架构，便于后续扩展",
        "使用单体架构+模块化，快速交付",
        "使用Serverless，零运维成本"
    ]
    
    # tot_result = advanced.tree_of_thought(tech_problem, options)
    # print(f"\n{tot_result}")
    print("(演示模式，跳过实际调用)")
    
    print("\n" + "=" * 50)
    print("Prompt Chaining 示例")
    print("=" * 50)
    
    article_task = "分析并总结这篇技术文章"
    chain = [
        {
            "task": "关键词提取",
            "description": "从文章中提取核心关键词",
            "prompt_template": "请提取5-10个核心关键词，用逗号分隔。"
        },
        {
            "task": "摘要生成",
            "description": "基于关键词生成摘要",
            "prompt_template": "基于上述关键词，请用3句话总结文章核心内容。"
        },
        {
            "task": "要点分析",
            "description": "提取文章的主要观点",
            "prompt_template": "请列出文章的3-5个主要观点。"
        }
    ]
    
    # chain_result = advanced.prompt_chaining(article_task, chain)
    # print(f"\n{chain_result}")
    print("(演示模式，跳过实际调用)")


if __name__ == "__main__":
    advanced_techniques_demo()
```

### 4.9 示例7：完整项目 - 智能问答系统

```python
"""
examples/07_rag_qa_system.py
RAG (Retrieval-Augmented Generation) 问答系统示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient
from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class Document:
    """文档类"""
    content: str
    metadata: dict


@dataclass
class RetrievedChunk:
    """检索结果"""
    content: str
    score: float
    metadata: dict


class SimpleRAG:
    """简化的RAG系统"""
    
    def __init__(self, config: LLMConfig):
        self.client = LLMClient(config)
        self.documents: List[Document] = []
    
    def add_documents(self, docs: List[Document]):
        """添加文档"""
        self.documents.extend(docs)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievedChunk]:
        """
        简单检索（实际应用中应使用向量数据库）
        这里用关键词匹配做演示
        """
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents:
            # 简单的词频计算
            content_lower = doc.content.lower()
            doc_words = set(content_lower.split())
            intersection = query_words & doc_words
            score = len(intersection) / max(len(query_words), 1)
            
            if score > 0:
                results.append(RetrievedChunk(
                    content=doc.content,
                    score=score,
                    metadata=doc.metadata
                ))
        
        # 排序返回top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def generate_answer(self, query: str, context_docs: List[RetrievedChunk]) -> str:
        """基于检索结果生成答案"""
        
        context = "\n\n".join([
            f"【文档{i+1}】{doc.content}"
            for i, doc in enumerate(context_docs)
        ])
        
        prompt = f"""基于以下参考资料回答问题。如果资料中没有相关信息，请说明"资料中未涉及"。

【问题】{query}

【参考资料】
{context}

【回答要求】
1. 引用参考来源
2. 如需补充信息，请明确说明
3. 回答要准确、简洁"""
        
        return self.client.chat([{"role": "user", "content": prompt}])
    
    def query(self, question: str, top_k: int = 3) -> str:
        """完整问答流程"""
        # 1. 检索相关文档
        docs = self.retrieve(question, top_k)
        
        if not docs:
            return "抱歉，知识库中没有找到相关信息。"
        
        # 2. 生成答案
        return self.generate_answer(question, docs)


def rag_demo():
    """RAG系统演示"""
    
    # 初始化
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    rag = SimpleRAG(config)
    
    # 添加知识库文档
    docs = [
        Document(
            content="Python是一种高级编程语言，由Guido van Rossum于1991年创建。特点是简洁易读的语法和强大的库支持。",
            metadata={"source": "python_basics.txt"}
        ),
        Document(
            content="FastAPI是一个现代、快速的Python Web框架，用于构建API。它基于Pydantic和Starlette，支持异步编程。",
            metadata={"source": "fastapi_guide.txt"}
        ),
        Document(
            content="关系型数据库如PostgreSQL使用SQL语言，支持事务和复杂查询。非关系型数据库如MongoDB则使用文档存储。",
            metadata={"source": "database_intro.txt"}
        ),
        Document(
            content="Docker是一个容器化平台，可以打包应用及其依赖，实现一致的运行环境。Kubernetes是容器编排工具。",
            metadata={"source": "devops_tools.txt"}
        ),
    ]
    rag.add_documents(docs)
    
    # 问答示例
    questions = [
        "Python有什么特点？",
        "FastAPI和Django有什么区别？",
        "Docker和Kubernetes是什么关系？"
    ]
    
    print("=" * 50)
    print("RAG 问答系统演示")
    print("=" * 50)
    
    for q in questions:
        print(f"\n问题: {q}")
        print("-" * 40)
        answer = rag.query(q)
        print(f"回答: {answer}\n")


if __name__ == "__main__":
    rag_demo()
```

---

## 5. 常见陷阱与最佳实践

### 5.1 常见陷阱

#### 陷阱1：Prompt过长导致上下文丢失

```python
# ❌ 错误做法
bad_prompt = """
[插入10000字的背景材料]
[插入5000字的任务描述]
请回答: ...
"""

# ✅ 正确做法
good_prompt = """
关键背景（精简版）:
1. ...
2. ...
3. ...

核心任务: ...

重要约束: ...
"""
```

#### 陷阱2：指令冲突

```python
# ❌ 错误：指令相互矛盾
conflict_prompt = """
请简洁回答（不超过10字）。
同时请详细解释每个步骤。
"""

# ✅ 正确：明确优先级
clear_prompt = """
请简洁回答（不超过10字）。
如果需要补充解释，放在【可选说明】中。
"""
```

#### 陷阱3：假设模型知道未知信息

```python
# ❌ 错误
unclear_prompt = """
分析这个代码的性能问题
[代码]
"""

# ✅ 正确：提供足够上下文
clear_prompt = """
分析以下Python代码的性能问题：

环境: Python 3.9, 处理10万条数据
预期: 单次处理<1秒

代码:
[代码]

请指出具体瓶颈和优化建议。
"""
```

#### 陷阱4：忽略温度参数的影响

| 场景 | 推荐Temperature |
|------|----------------|
| 代码生成 | 0.0 - 0.3 |
| 事实问答 | 0.0 - 0.2 |
| 创意写作 | 0.7 - 1.0 |
| 翻译 | 0.3 - 0.5 |

### 5.2 最佳实践清单

```
┌─────────────────────────────────────────────────────────┐
│                   Prompt 最佳实践                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ✓ 结构清晰                                              │
│    - 使用分隔符（如###、---）区分不同部分                  │
│    - 重要指令放在开头或结尾                              │
│                                                          │
│  ✓ 具体明确                                              │
│    - 避免模糊词汇（"可能"、"也许"）                      │
│    - 指定输出格式和长度                                  │
│                                                          │
│  ✓ 示例驱动                                              │
│    - 复杂任务提供Few-shot示例                            │
│    - 示例要涵盖边界情况                                  │
│                                                          │
│  ✓ 逐步推理                                              │
│    - 复杂问题使用CoT                                      │
│    - 让模型展示思考过程                                  │
│                                                          │
│  ✓ 错误处理                                              │
│    - 指定如何处理不确定情况                              │
│    - 提供纠错机制                                        │
│                                                          │
│  ✓ 安全考虑                                              │
│    - 避免注入攻击                                        │
│    - 敏感信息脱敏                                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 5.3 调试技巧

```python
def debug_prompt(prompt: str, client: LLMClient):
    """调试Prompt的技巧"""
    
    # 1. 最小化测试：从最简单的版本开始
    print("Step 1: 测试最小化Prompt")
    
    # 2. 逐步添加元素
    additions = [
        "添加角色设定",
        "添加格式要求", 
        "添加Few-shot示例",
        "添加约束条件"
    ]
    
    for i, addition in enumerate(additions):
        print(f"\nStep {i+2}: 测试{addition}")
        # 测试代码...
    
    # 3. 检查Token消耗
    print(f"\nPrompt Token数: {len(prompt.split()) * 1.3}")
```

---

## 6. 教学场景化案例

### 案例1：智能代码审查助手

```python
"""
案例1: 智能代码审查助手
场景: 学生提交代码作业，系统自动审查
"""

CODE_REVIEW_PROMPT = """你是一位严格的代码审查专家。请审查以下学生代码。

【任务背景】
这是软件学院"数据结构"课程的作业，要求实现快速排序算法。

【评分标准】
1. 正确性 (40分): 算法是否正确实现
2. 效率 (30分): 时间/空间复杂度是否合理
3. 代码规范 (20分): 命名、注释、格式
4. 创新性 (10分): 是否有额外优化或改进

【待审查代码】
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [i for i in arr if i < pivot]
    mid = [i for i in arr if i == pivot]
    right = [i for i in arr if i > pivot]
    return quicksort(left) + mid + quicksort(right)
```

【输出格式】
## 审查结果

### 代码分析
...

### 问题列表
| 序号 | 位置 | 问题 | 建议 | 扣分 |

### 总分: X/100

### 改进建议
..."""
```

### 案例2：SQL查询生成器

```python
"""
案例2: 自然语言转SQL
场景: 学生用自然语言描述需求，系统生成SQL
"""

NLP_TO_SQL_PROMPT = """你是一个SQL查询生成器。

【数据库Schema】
Table: students
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 学号 |
| name | VARCHAR | 姓名 |
| age | INT | 年龄 |
| major | VARCHAR | 专业 |
| gpa | DECIMAL | 绩点 |
| enrollment_date | DATE | 入学日期 |

【任务】
将自然语言转换为SQL查询。

【示例】
输入: "找出软件学院平均绩点大于3.5的学生"
输出: 
```sql
SELECT name, gpa 
FROM students 
WHERE major = '软件工程' AND gpa > 3.5;
```

输入: "统计每个专业的学生人数和平均绩点"
输出:
```sql
SELECT major, COUNT(*) as student_count, AVG(gpa) as avg_gpa
FROM students
GROUP BY major;
```

【待转换】
输入: "找出年龄最小的5名学生，按入学日期排序"
输出:"""

# 测试
def test_nlp_to_sql():
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    
    messages = [{"role": "user", "content": NLP_TO_SQL_PROMPT}]
    response = client.chat(messages)
    print("=" * 50)
    print("NLP to SQL 示例")
    print("=" * 50)
    print(response)
```

### 案例3：算法可视化解释器

```python
"""
案例3: 算法可视化解释
场景: 学生学习排序算法，生成可视化描述
"""

ALGORITHM_VISUALIZER_PROMPT = """你是一个算法可视化教学助手。请解释以下排序算法的工作过程。

【任务】
解释"冒泡排序"如何对数组[5, 2, 8, 1, 9]进行排序。

【输出要求】
1. 分步展示每一轮的比较和交换
2. 用图示表示数组状态变化
3. 标注已排序部分
4. 说明时间复杂度

【格式示例】
```
第1轮:
  比较: 5 vs 2 -> 交换 [2, 5, 8, 1, 9]
  比较: 5 vs 8 -> 不交换 [2, 5, 8, 1, 9]
  ...
第1轮结束，最大值9就位 [?, ?, ?, ?, 9]
...
```"""
```

### 案例4：Bug诊断专家

```python
"""
案例4: Bug诊断与修复
场景: 学生遇到bug，AI辅助诊断
"""

BUG_DIAGNOSIS_PROMPT = """你是一位Python调试专家。

【问题描述】
学生在运行爬虫程序时遇到以下错误：
```
Traceback (most recent call last):
  File "scraper.py", line 42, in <module>
    data = parse_page(html)
  File "scraper.py", line 28, in parse_page
    items = soup.find_all('div', class_='item')
AttributeError: 'NoneType' object has no attribute 'find_all'
```

【代码片段】
```python
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='item')  # line 28
    return [parse_item(item) for item in items]
```

【可能原因】
请分析并列出3个最可能的原因，每个原因包含：
1. 原因说明
2. 如何验证
3. 解决方案"""
```

### 案例5：期末考试出题助手

```python
"""
案例5: 智能出题系统
场景: 教师输入知识点，自动生成考题
"""

EXAM_GENERATOR_PROMPT = """你是一位严谨的课程出题专家。请根据以下知识点生成考题。

【课程信息】
- 课程: 数据结构与算法
- 难度: 中等（期中考试水平）

【知识点】
1. 栈(LIFO)的基本概念和操作
2. 队列(FIFO)的基本概念和操作
3. 栈和队列的实现方式

【输出要求】
生成以下题型：

## 一、选择题 (3道)
每题有4个选项，仅1个正确答案

## 二、简答题 (2道)
考察概念理解

## 三、编程题 (1道)
要求学生用代码实现

【注意事项】
- 避免超纲内容
- 题目要有区分度
- 附上参考答案"""
```

---

## 附录：常用Prompt模板

### A. 通用任务模板

```python
TASK_TEMPLATE = """【角色】{role}

【任务】{task}

【背景信息】
{context}

【要求】
{requirements}

【输出格式】
{format}

【约束条件】
{constraints}"""
```

### B. 代码生成模板

```python
CODE_TEMPLATE = """【编程语言】{language}

【任务描述】{description}

【输入】{input}

【输出】{output}

【示例】
输入: {example_input}
输出: {example_output}

【要求】
1. 代码完整可运行
2. 添加适当注释
3. 考虑边界情况
4. 符合语言规范"""
```

### C. 翻译模板

```python
TRANSLATION_TEMPLATE = """请将以下{源语言}文本翻译为{目标语言}。

【翻译风格】
{style}

【原文】
{text}

【要求】
1. 准确传达原意
2. 符合目标语言习惯
3. 保持专业术语一致"""
```

---

## 练习题

### 练习1：优化Prompt
将以下Prompt优化为更清晰、更有效的版本：

```python
# 原始Prompt
"帮我看看这个代码有什么问题吗"

# 你的优化:
optimized_prompt = """
请审查以下Python代码的问题。

【代码】
[粘贴代码]

【期望行为】
[描述期望的行为]

【实际行为】
[描述实际的问题]
"""
```

### 练习2：设计Few-Shot Prompt
设计一个用于垃圾邮件分类的Few-Shot Prompt，包含3个正面示例和2个负面示例。

### 练习3：实现ReAct Agent
基于示例代码，实现一个能回答"今天天气怎么样？"的简单ReAct Agent。

---

## 参考资源

- OpenAI Prompt Engineering Guide: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic Claude Prompt Engineering: https://docs.anthropic.com/
- Lilian Weng's Blog - Prompt Engineering: https://lilianweng.github.io/
-微软Prompt Engineering Guide: https://learn.microsoft.com/prompt-engineering/

---

*课程版本: 1.0.0*
*最后更新: 2024年*
