"""
examples/08_teaching_cases.py
教学场景化案例
"""

import sys
sys.path.append("..")

from config import LLMConfig
from utils.llm_client import LLMClient


# ============================================================
# 案例1: 智能代码审查助手
# ============================================================

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


# ============================================================
# 案例2: SQL查询生成器
# ============================================================

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


# ============================================================
# 案例3: 算法可视化解释器
# ============================================================

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


# ============================================================
# 案例4: Bug诊断专家
# ============================================================

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


# ============================================================
# 案例5: 期末考试出题助手
# ============================================================

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


# ============================================================
# 案例6: 需求分析助手
# ============================================================

REQUIREMENT_ANALYSIS_PROMPT = """你是一位需求分析师。请分析以下用户需求，产出规范的需求文档。

【用户原始需求】
"我想做一个网上书店，能卖书，能让用户注册登录，能看到书的评论，还想有个购物车功能"

【输出格式】
## 需求分析文档

### 一、角色分析
- ...

### 二、功能模块
| 模块 | 功能点 | 优先级 | 备注 |

### 三、用户流程
### 四、数据模型
### 五、非功能性需求
### 六、待确认问题清单"""


# ============================================================
# 案例7: 代码重构建议
# ============================================================

CODE_REFACTOR_PROMPT = """你是一位代码重构专家。请分析以下代码并提供重构建议。

【原始代码】
```python
def process_data(data):
    result = []
    for i in data:
        if i['type'] == 'A':
            if i['value'] > 100:
                i['category'] = 'high'
            else:
                i['category'] = 'low'
        elif i['type'] == 'B':
            if i['value'] > 50:
                i['category'] = 'high'
            else:
                i['category'] = 'low'
        result.append(i)
    return result
```

【重构要求】
1. 提高代码可读性
2. 消除重复逻辑
3. 遵循 SOLID 原则

【输出格式】
### 重构后的代码
### 主要改进点
### 设计模式应用（如有）"""


# ============================================================
# 测试函数
# ============================================================

def test_code_review():
    """测试代码审查"""
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    print("=" * 50)
    print("案例1: 智能代码审查")
    print("=" * 50)
    
    response = client.chat([{"role": "user", "content": CODE_REVIEW_PROMPT}])
    print(response)


def test_nlp_to_sql():
    """测试NL2SQL"""
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    print("\n" + "=" * 50)
    print("案例2: 自然语言转SQL")
    print("=" * 50)
    
    response = client.chat([{"role": "user", "content": NLP_TO_SQL_PROMPT}])
    print(response)


def test_algorithm_visualizer():
    """测试算法可视化"""
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    print("\n" + "=" * 50)
    print("案例3: 算法可视化解释")
    print("=" * 50)
    
    response = client.chat([{"role": "user", "content": ALGORITHM_VISUALIZER_PROMPT}])
    print(response)


def test_bug_diagnosis():
    """测试Bug诊断"""
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    print("\n" + "=" * 50)
    print("案例4: Bug诊断专家")
    print("=" * 50)
    
    response = client.chat([{"role": "user", "content": BUG_DIAGNOSIS_PROMPT}])
    print(response)


def test_exam_generator():
    """测试出题系统"""
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    print("\n" + "=" * 50)
    print("案例5: 期末考试出题助手")
    print("=" * 50)
    
    response = client.chat([{"role": "user", "content": EXAM_GENERATOR_PROMPT}])
    print(response)


def test_requirement_analysis():
    """测试需求分析"""
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    print("\n" + "=" * 50)
    print("案例6: 需求分析助手")
    print("=" * 50)
    
    response = client.chat([{"role": "user", "content": REQUIREMENT_ANALYSIS_PROMPT}])
    print(response)


def test_code_refactor():
    """测试代码重构"""
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    print("\n" + "=" * 50)
    print("案例7: 代码重构建议")
    print("=" * 50)
    
    response = client.chat([{"role": "user", "content": CODE_REFACTOR_PROMPT}])
    print(response)


if __name__ == "__main__":
    # 注意：这些调用需要API密钥
    # test_code_review()
    # test_nlp_to_sql()
    # test_algorithm_visualizer()
    # test_bug_diagnosis()
    # test_exam_generator()
    # test_requirement_analysis()
    # test_code_refactor()
    
    print("=" * 50)
    print("教学案例演示")
    print("=" * 50)
    print("""
这些案例的Prompt已定义完毕。
要运行实际测试：
1. 设置环境变量: export OPENAI_API_KEY='your-key'
2. 取消上面函数调用的注释

所有案例都展示了不同的Prompt Engineering技巧，
可以让学生分析每个Prompt的设计思路。
""")
