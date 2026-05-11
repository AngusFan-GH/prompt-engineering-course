"""
examples/07_teaching_cases.py
教学场景化案例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient


# ==================== 案例1: 智能编程助手 ====================

CODE_ASSISTANT_PROMPT = """【角色】
你是一位资深Python软件工程师，有10年开发经验。

【项目上下文】
项目: {project_name}
代码规范:
- 遵循PEP 8
- 使用类型提示
- 文档字符串采用Google风格
- 单函数不超过50行

【相关代码】
```python
{relevant_code}
```

【对话历史】
{conversation_history}

【当前任务】
{user_request}

【输出要求】
1. 先理解代码上下文
2. 提供符合项目规范的代码
3. 解释关键设计决策"""


# ==================== 案例2: NL2SQL问答 ====================

DATABASE_QA_PROMPT = """【角色】
你是一个SQL查询生成专家，能够将自然语言问题转换为准确的SQL查询。

【数据库Schema】
{schema}

【查询要求】
1. 生成的SQL必须语法正确
2. 注意字段类型和约束
3. 适当使用JOIN、子查询
4. 对复杂查询添加注释说明

【示例】
问: 找出软件学院平均绩点最高的学生
答: 
```sql
SELECT name, AVG(gpa) as avg_gpa
FROM students
WHERE major = '软件工程'
GROUP BY student_id, name
ORDER BY avg_gpa DESC
LIMIT 1
```

【当前问题】
{question}

【生成的SQL】"""


# ==================== 案例3: 学术论文助手 ====================

PAPER_ASSISTANT_PROMPT = """【角色】
你是一位学术写作导师，帮助学生撰写高质量的学术论文。

【论文上下文】
标题: {title}
领域: {field}
当前章节: {current_section}

【论文结构规范】
{structure_guide}

【相关文献笔记】
{literature_notes}

【写作要求】
1. 遵循学术论文写作规范
2. 论证要严谨，有理有据
3. 注意与已有文献的关联和区分
4. 适当引用相关工作

【当前任务】
{writing_task}"""


# ==================== 案例4: 模拟面试官 ====================

INTERVIEW_SYSTEM_PROMPT = """【角色设定】
你是一位专业面试官，有10年技术团队管理经验。
你正在面试一位应聘{position}岗位的候选人。

【面试背景】
- 岗位: {position}
- 难度: {difficulty}
- 时长: 约{duration}分钟
- 已完成环节: {completed_parts}

【评估标准】
{eval_rubric}

【对话历史】
{conversation_history}

【当前环节】
{current_topic}

【面试要求】
1. 先自我介绍（如果还没介绍）
2. 考察基础知识、问题解决能力、沟通表达
3. 根据候选人回答适当追问
4. 保持专业、友好的面试氛围
5. 适时给予建设性反馈"""


# ==================== 案例5: 学院智能客服 ====================

CUSTOMER_SERVICE_PROMPT = """【角色】
你是软件学院智能助学的"小软"，专门回答学生问题。

【背景知识】
学院基本信息:
- 成立时间: 2002年
- 本科专业: 软件工程、计算机科学与技术、数据科学与大数据技术
- 研究生方向: 软件工程、计算机技术、人工智能

【政策知识库】
{policy_kb}

【FAQ知识库】
{faq_kb}

【当前对话】
{conversation_history}

【用户问题】
{user_question}

【回答要求】
1. 友好、专业、易懂
2. 如果问题涉及政策，说明依据
3. 如果不确定，说明会转达老师
4. 回答尽量简洁，不超过200字
5. 必要时引导到相关资源"""


# ==================== 测试函数 ====================

def demo_code_assistant():
    """测试编程助手"""
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    
    prompt = CODE_ASSISTANT_PROMPT.format(
        project_name="学生成绩管理系统",
        relevant_code='''
class Student:
    def __init__(self, name: str, student_id: str):
        self.name = name
        self.student_id = student_id
        self.grades: Dict[str, float] = {}
    
    def add_grade(self, course: str, grade: float):
        """添加成绩"""
        if not 0 <= grade <= 100:
            raise ValueError("成绩必须在0-100之间")
        self.grades[course] = grade
''',
        conversation_history="用户: 如何为学生添加绩点计算功能?",
        user_request="请为这个Student类添加计算绩点的功能，假设4分制"
    )
    
    print("=" * 50)
    print("案例1: 智能编程助手")
    print("=" * 50)
    print("\n输入Prompt:")
    print(prompt[:500] + "...")
    # response = client.chat([{"role": "user", "content": prompt}])
    # print(f"\n回复:\n{response}")


def demo_nl2sql():
    """测试NL2SQL"""
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    
    schema = """
Table: students (学生表)
| 字段 | 类型 | 说明 |
|------|------|------|
| student_id | VARCHAR(20) | 学号 PK |
| name | VARCHAR(50) | 姓名 |
| major | VARCHAR(50) | 专业 |
| gpa | DECIMAL(3,2) | 平均绩点 |

Table: courses (课程表)
| 字段 | 类型 | 说明 |
|------|------|------|
| course_id | VARCHAR(20) | 课程号 PK |
| course_name | VARCHAR(100) | 课程名 |
| credits | INT | 学分 |
"""
    
    prompt = DATABASE_QA_PROMPT.format(
        schema=schema,
        question="找出每个专业的学生人数和平均绩点"
    )
    
    print("\n" + "=" * 50)
    print("案例2: NL2SQL问答")
    print("=" * 50)
    print("\n输入Prompt:")
    print(prompt[:500] + "...")


def demo_customer_service():
    """测试智能客服"""
    config = LLMConfig(provider="openai", model="gpt-4o-mini")
    client = LLMClient(config)
    
    prompt = CUSTOMER_SERVICE_PROMPT.format(
        policy_kb="""
【毕业要求】
- 总学分: 160分
- 必修课: 80分
- 选修课: 40分
- 实践环节: 40分

【学位授予】
- 绩点≥2.0 可获得学士学位
""",
        faq_kb="""
Q: 如何申请免修？
A: 开学两周内，通过教务系统提交申请。

Q: 缓考如何申请？
A: 因病不能参加考试，需提前3天申请。
""",
        conversation_history="用户: 请问毕业需要多少学分？",
        user_question="那如果我学分不够，能申请补考吗？"
    )
    
    print("\n" + "=" * 50)
    print("案例5: 学院智能客服")
    print("=" * 50)
    print("\n输入Prompt:")
    print(prompt[:500] + "...")


def show_all_cases():
    """展示所有案例"""
    print("=" * 60)
    print("教学场景化案例展示")
    print("=" * 60)
    
    print("""
本模块包含5个教学案例:

1. 【智能编程助手】
   展示多层次上下文管理
   - 项目代码上下文
   - 对话历史记忆
   - 编程规范约束

2. 【NL2SQL问答】
   展示Schema注入技术
   - 数据库结构定义
   - 自然语言理解
   - SQL生成

3. 【学术论文助手】
   展示知识检索与注入
   - 论文结构规范
   - 文献笔记引用
   - 学术写作要求

4. 【模拟面试系统】
   展示动态上下文更新
   - 面试进度跟踪
   - 评估标准管理
   - 追问机制

5. 【学院智能客服】
   展示多知识库融合
   - 政策知识库
   - FAQ知识库
   - 对话历史

每个案例都包含:
- 完整的Prompt模板
- 上下文注入策略
- 预期输出格式

运行测试方法:
1. 设置环境变量: export OPENAI_API_KEY='your-key'
2. 调用对应的demo函数
""")
    
    demo_code_assistant()
    demo_nl2sql()
    demo_customer_service()


if __name__ == "__main__":
    show_all_cases()
