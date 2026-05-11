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
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7", temperature=0)
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
    
    print("=" * 50)
    print("Zero-shot CoT 示例")
    print("=" * 50)
    print("问题:", problem.strip())
    print()
    
    print("【直接回答】")
    response_basic = client.chat(messages_basic)
    print(response_basic)
    
    print("\n【CoT推理】")
    response_cot = client.chat(messages_cot)
    print(response_cot)


def math_word_problem_cot():
    """数学应用题 - 完整CoT"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
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


def logic_reasoning_cot():
    """逻辑推理 - CoT"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7", temperature=0)
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
    print("逻辑推理 CoT + 自我验证")
    print("=" * 50)
    print(response)


def debugging_cot():
    """Bug诊断 - CoT"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    problem = """
学生写的快速排序代码，运行结果不正确，请帮忙分析问题所在。

代码:
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    right = [x for x in arr[1:] if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)

# 测试
print(quicksort([3, 1, 4, 1, 5, 9, 2, 6]))
# 期望: [1, 1, 2, 3, 4, 5, 6, 9]
# 实际: [1, 2, 3, 4, 5, 6, 9, 1]  # 多了个1，缺了个9？
```
"""
    
    cot_prompt = """请按以下步骤分析这个快速排序的问题：

**步骤1: 理解快速排序原理**
**步骤2: 手动模拟代码执行** 
**步骤3: 追踪每一次递归调用**
**步骤4: 找出问题根源**
**步骤5: 提出修复方案

请详细写出每一步的分析过程。"""
    
    messages = [
        {"role": "user", "content": problem + "\n" + cot_prompt}
    ]
    
    response = client.chat(messages)
    print("\n" + "=" * 50)
    print("Bug诊断 - CoT推理")
    print("=" * 50)
    print(response)


if __name__ == "__main__":
    # 注意：这些调用会实际请求API
    # 如果没有API密钥或想跳过实际调用，可以注释掉
    zero_shot_cot()
    math_word_problem_cot()
    logic_reasoning_cot()
    debugging_cot()
