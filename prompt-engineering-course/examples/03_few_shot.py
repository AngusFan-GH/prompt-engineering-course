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
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7", temperature=0.3)
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
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
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


def text_classification_few_shot():
    """文本分类 - 多分类Few-Shot"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7", temperature=0.2)
    client = LLMClient(config)
    
    few_shot_prompt = """请将新闻标题分类到以下类别之一：
- 科技 (tech)
- 体育 (sports)
- 娱乐 (entertainment)
- 财经 (finance)
- 国际 (international)

示例:

标题: "苹果发布新一代iPhone，搭载最新A18芯片"
分类: tech

标题: "中国队世界杯预选赛战胜韩国"
分类: sports

标题: "某明星新电影票房突破10亿"
分类: entertainment

标题: "央行宣布降准0.5个百分点"
分类: finance

标题: "欧盟峰会讨论气候变化议题"
分类: international

待分类:
标题: "特斯拉全自动驾驶获批在加州上路"
分类:"""
    
    messages = [{"role": "user", "content": few_shot_prompt}]
    response = client.chat(messages)
    
    print("\n" + "=" * 50)
    print("Few-Shot文本分类示例")
    print("=" * 50)
    print(response)


def sql_generation_few_shot():
    """Text-to-SQL - Few-Shot"""
    
    config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
    client = LLMClient(config)
    
    system_prompt = """你是SQL查询生成器。根据自然语言生成SQL查询。

【数据库Schema】
Table: orders
- id (INT, 主键)
- customer_name (VARCHAR)
- product (VARCHAR)
- quantity (INT)
- price (DECIMAL)
- order_date (DATE)
- status (VARCHAR) -- pending, completed, cancelled"""
    
    few_shot_prompt = """
【示例1】
问: 查出所有已完成的订单
SQL: SELECT * FROM orders WHERE status = 'completed';

【示例2】
问: 统计每个产品的销售总额
SQL: SELECT product, SUM(quantity * price) as total_sales FROM orders GROUP BY product;

【示例3】
问: 找出订单金额超过1000元的客户名单
SQL: SELECT DISTINCT customer_name FROM orders WHERE quantity * price > 1000;

【示例4】
问: 计算上个月每个产品的销量
SQL: SELECT product, SUM(quantity) as total_quantity FROM orders WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) GROUP BY product;

【待生成】
问: 找出订单数量最多的前5位客户
SQL:"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": few_shot_prompt}
    ]
    
    response = client.chat(messages)
    print("\n" + "=" * 50)
    print("Few-Shot Text-to-SQL 示例")
    print("=" * 50)
    print(response)


if __name__ == "__main__":
    sentiment_analysis_few_shot()
    entity_extraction_few_shot()
    text_classification_few_shot()
    sql_generation_few_shot()
