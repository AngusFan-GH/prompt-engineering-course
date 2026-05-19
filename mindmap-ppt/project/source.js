export const sourceMarkdown = `
- AI Harness Engineering
  90分钟掌握 Agent 工程底座
  @image generated/harness-overview.svg
    - 课程定位
      从会问答到会执行
      @image generated/capability-ladder.svg
        - 授课对象
          大三学生与工程基础
          - 先修要求
            Python 和 LLM API
          - 课程时长
            两课时共九十分钟
        - 能力跃迁
          文本生成走向目标执行
          - LLM 层
            负责语言理解与生成
          - Tools 层
            让模型调用外部函数
          - Agent 层
            多步推理和状态管理
          - Multi-Agent 层
            多角色协作分工
        - 概念边界
          Harness 约束自主执行
          - 不是完全自主
            受工具权限和流程控制
          - 核心变化
            观察选择执行读取反馈
    - 执行循环
      Agent Loop 是共同骨架
      @image generated/agent-loop.svg
        - 构建提示
          注入环境技能和工具
        - 调用模型
          根据上下文决定动作
        - 解析响应
          文本返回或工具调用
          - 工具调用
            调度器执行后写回消息
          - 文本响应
            形成最终用户回答
        - 管理上下文
          接近上限先压缩历史
        - 工程挑战
          安全成本幻觉可观测
          - 工具安全
            权限分级和人工确认
          - 上下文窗口
            压缩摘要和滑动窗口
          - 工具幻觉
            Schema 约束和白名单
          - 行为追踪
            日志链路和步骤回放
    - 框架对比
      三种路径服务不同场景
      @image generated/framework-comparison.svg
        - Hermes Agent
          工具优先技能驱动
          - 适合场景
            运维自动化和全栈 Agent
          - 组织方式
            Toolset 与 SKILL.md
        - LangChain 系
          可组合编排最灵活
          - 核心能力
            LCEL 与 LangGraph
          - 记忆方式
            History 或 checkpoint
        - CrewAI
          角色协作和任务编排
          - 组织模型
            Agent Task Crew Flow
          - 适合场景
            多 Agent 协作流程
    - 核心组件
      Tools Skills Memory 协同
      @image generated/components-memory.svg
        - Tools
          定义能做什么
          - Schema
            名称描述参数约束
          - Handler
            执行真实外部操作
          - Registry
            绑定描述和函数
        - Skills
          定义如何做得更好
          - 触发条件
            明确何时加载技能
          - 步骤指南
            指导工具组合顺序
          - 验证清单
            防止常见执行失误
        - Memory
          保存状态与长期知识
          - 工作记忆
            当前上下文窗口
          - 短期记忆
            本轮任务状态
          - 长期记忆
            用户偏好和知识
        - 协作关系
          策略执行记忆闭环
          - Skills 决策
            选择工具和流程
          - Tools 执行
            产生可验证结果
          - Memory 补充
            维持跨轮一致性
    - 实训安排
      用练习巩固工程判断
        - 第一课时
          概念辨析与框架选型
          - 判断 Agent
            区分单次调用和长期任务
          - 选型分析
            代码仓库分析与 PR 评论
        - 第二课时
          工具技能记忆设计
          - 工具定义
            写 Schema 并实现 Handler
          - 技能设计
            为代码审查写 SKILL.md
          - 记忆方案
            区分会话内和跨会话
        - 实践原则
          先约束再让模型行动
          - 工具原则
            单一职责和结构化返回
          - 技能原则
            有触发条件和反模式
          - 记忆原则
            分层存储并保护隐私
`;
