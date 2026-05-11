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
        provider="minimax",
        model="MiniMax-M2.7",
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
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
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
    print("代码片段:")
    print(code_snippet)
    print(f"\n审查结果:\n{response}")


def multi_role_example():
    """多角色对话模拟"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    # 模拟辩论赛
    system_prompt = """你将扮演两位辩论者，进行一场关于"AI是否会取代程序员"的辩论。

辩手A（正方）：认为AI将大幅取代程序员工作
辩手B（反方）：认为AI是程序员的工具，不会取代

请以以下格式输出：
---
【正方A】：...（3-4句话）
【反方B】：...（3-4句话）
【正方A】：...（回应反驳）
【反方B】：...（回应反驳）
---
最终裁判（你）：总结双方观点，给出你认为更合理的结论"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "请开始辩论"}
    ]
    
    response = client.chat(messages)
    print("\n" + "=" * 50)
    print("多角色辩论示例")
    print("=" * 50)
    print(response)


if __name__ == "__main__":
    role_prompting_example()
    code_review_role_example()
    multi_role_example()
