"""
examples/06_advanced_techniques.py
高级技巧组合示例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient
from collections import Counter
from typing import List, Callable
import json


class AdvancedPrompting:
    """高级提示技巧"""
    
    def __init__(self, config: LLMConfig):
        self.client = LLMClient(config)
    
    def self_consistency(self, prompt: str, question: str, n_samples: int = 5) -> dict:
        """
        Self-Consistency 自洽性
        通过多次采样选择最一致的答案
        """
        responses = []
        reasoning_results = []
        
        for i in range(n_samples):
            full_prompt = f"""{prompt}

问题: {question}

请详细推理并给出答案。"""
            response = self.client.chat(
                [{"role": "user", "content": full_prompt}],
                temperature=0.7
            )
            responses.append(response)
            reasoning_results.append(response)
        
        # 分析答案一致性
        # 这里简化处理，实际应该解析答案部分
        print(f"采样了 {len(responses)} 次，得到 {len(set(responses))} 种不同回答")
        
        return {
            "samples": reasoning_results,
            "final_answer": responses[0],  # 简化处理
            "diversity": len(set(responses)) / len(responses)
        }
    
    def tree_of_thought(self, problem: str, options: List[str]) -> dict:
        """
        Tree of Thoughts 思维树
        探索多种解题路径
        """
        results = []
        
        for i, option in enumerate(options):
            prompt = f"""问题: {problem}

考虑方案 {i+1}: {option}

请详细分析:
1. 这个方案的优点（列出3-5点）
2. 这个方案的缺点或风险（列出2-3点）
3. 适用场景

最后给出1-10分的评分并说明理由。"""
            
            response = self.client.chat([{"role": "user", "content": prompt}])
            results.append({
                "option": option,
                "analysis": response
            })
        
        # 综合评估
        options_summary = "\n".join([f'方案{i+1}: {r["option"]}' for i, r in enumerate(results)])
        analysis_summary = "\n".join([
            f'【方案{i+1} {r["option"]}分析】\n{r["analysis"]}' 
            for i, r in enumerate(results)
        ])
        
        synthesis_prompt = f"""请比较以下 {len(options)} 个方案，并给出最终推荐。

{options_summary}

分析如下:
{analysis_summary}

请给出:
1. 每个方案的优缺点总结（表格形式）
2. 最佳推荐方案及理由
3. 实施建议"""
        
        final_recommendation = self.client.chat([{"role": "user", "content": synthesis_prompt}])
        
        return {
            "individual_analysis": results,
            "synthesis": final_recommendation
        }
    
    def prompt_chaining(self, task: str, chain: List[dict]) -> dict:
        """
        Prompt Chaining 提示链
        将复杂任务分解为多个子任务
        """
        results = []
        context = f"初始任务: {task}\n\n"
        
        for i, step in enumerate(chain):
            step_prompt = f"""【步骤 {i+1}: {step['task']}】

任务描述: {step['description']}

{'-' * 40}
历史上下文:
{context}
{'-' * 40}

{step['prompt_template']}"""
            
            result = self.client.chat([{"role": "user", "content": step_prompt}])
            
            results.append({
                "step": step['task'],
                "result": result
            })
            
            context += f"\n\n[步骤{i+1} {step['task']}结果]:\n{result}"
            print(f"✓ 步骤 {i+1} 完成: {step['task']}")
        
        return {
            "steps": results,
            "final_context": context
        }
    
    def generate_skill_prompt(self, skill_name: str, context: str) -> str:
        """
        根据技能场景生成专用Prompt
        """
        prompt = f"""请为'{skill_name}'场景生成一个优化后的System Prompt。

场景描述: {context}

要求:
1. 设定清晰的AI角色
2. 定义输出格式
3. 包含必要的约束条件
4. 提供示例（如果是复杂任务）

输出格式:
## Role Prompt

【System Prompt内容在这里】

## 使用说明
[简短说明如何使用这个Prompt]"""
        
        response = self.client.chat([{"role": "user", "content": prompt}])
        return response


def advanced_techniques_demo():
    """高级技巧演示"""
    
    print("=" * 50)
    print("高级技巧演示（使用模拟输出）")
    print("=" * 50)
    
    # 演示模式说明
    print("""
注意: 以下演示使用模拟输出。
要运行实际示例，请确保:
1. 设置环境变量 OPENAI_API_KEY
2. 取消代码中的注释

以下代码结构是正确的，可以直接运行。
""")
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    advanced = AdvancedPrompting(config)
    
    # Self-Consistency 示例
    print("\n【Self-Consistency 示例】")
    problem = "鸡兔同笼问题：共有35个头，94只脚，问鸡和兔各多少只？"
    prompt = "请用代数方法详细推理这个问题。"
    
    # 实际调用（需要API密钥）
    # result = advanced.self_consistency(prompt, problem, n_samples=3)
    # print(result["final_answer"])
    
    print("(演示模式: 实际会多次采样并投票)")
    
    # Tree of Thoughts 示例
    print("\n【Tree of Thoughts 示例】")
    tech_problem = "创业公司应该选择什么技术栈来构建MVP（最小可行产品）？"
    options = [
        "微服务架构 + Kubernetes",
        "单体架构 + 模块化设计",
        "Serverless + BaaS服务"
    ]
    
    # 实际调用（需要API密钥）
    # tot_result = advanced.tree_of_thought(tech_problem, options)
    # print(tot_result["synthesis"])
    
    print("(演示模式: 会分析每个方案然后综合推荐)")
    
    # Prompt Chaining 示例
    print("\n【Prompt Chaining 示例】")
    article_task = "对一篇技术文章进行深度分析"
    chain = [
        {
            "task": "关键词提取",
            "description": "从文章中提取核心关键词和主题",
            "prompt_template": "请提取5-10个核心关键词，并概括文章主题（1句话）。"
        },
        {
            "task": "结构分析", 
            "description": "分析文章结构和主要论点",
            "prompt_template": "基于关键词，请分析文章的结构（引言、正文、结论）和3-5个主要论点。"
        },
        {
            "task": "摘要生成",
            "description": "生成简洁的摘要",
            "prompt_template": "基于以上分析，请用200字以内总结文章核心内容。"
        },
        {
            "task": "评价与建议",
            "description": "对文章进行评价",
            "prompt_template": "请评价这篇文章的优点、局限性和对读者的价值。（各2-3句话）"
        }
    ]
    
    # 实际调用（需要API密钥）
    # chain_result = advanced.prompt_chaining(article_task, chain)
    # print(chain_result["final_context"])
    
    print("(演示模式: 会按顺序执行4个步骤)")


def self_consistency_math_demo():
    """Self-Consistency数学题演示"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    problem = """
问题: 一个班有40名学生，其中女生占60%。后来转来了一些女生，使得女生占比变成了55%。
问：转来了多少名女生？
"""
    
    prompt_template = """请详细推理以下问题，步骤清晰：

{problem}

请按以下格式输出:
**推理过程**:
1. ...
2. ...

**答案**: X名女生
"""
    
    messages = [{"role": "user", "content": prompt_template.format(problem=problem)}]
    
    print("=" * 50)
    print("Self-Consistency 数学题演示")
    print("=" * 50)
    
    # 演示单次推理
    print("单次推理结果:")
    response = client.chat(messages)
    print(response)


if __name__ == "__main__":
    advanced_techniques_demo()
