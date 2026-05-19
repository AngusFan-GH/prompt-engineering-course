# AI Harness Engineering 实训课程大纲

> **授课对象**：软件工程专业大三学生  
> **先修要求**：Python 编程基础、了解 LLM API 调用  
> **课程时长**：2 课时（90 分钟）  
> **课程目标**：理解 Agent/Harness 工程的核心概念，掌握 Tools、Skills、Memory 三大核心组件的设计与实现

---

## 第 1 课时：概念引入 —— 什么是 Harness Engineering（45 分钟）

### 学习目标

1. 能够解释 AI Agent 的定义与核心架构（感知-决策-行动循环）
2. 能够阐述 Harness Engineering 的概念及其在 AI 工程中的定位
3. 能够对比至少 2 种主流 Agent 框架的设计哲学差异

### 核心知识点

#### 知识点 1：从 LLM 到 Agent —— 能力跃迁

| 层级 | 能力 | 典型形态 |
|------|------|----------|
| LLM | 文本生成 | ChatGPT 问答 |
| LLM + Tools | 工具调用 | Function Calling |
| Agent | 目标驱动的多步推理 + 工具调用 + 状态管理 | AutoGPT, Hermes Agent |
| Multi-Agent | 协作/分工 | CrewAI, AutoGen |

关键转变：从“被动回答”到“目标驱动执行”。严格说，Agent 并不是完全自主的软件生命体，而是在 Harness 约束下反复进行“观察状态、选择动作、执行工具、读取反馈”的工程系统。

#### 知识点 2：什么是 Harness Engineering

**Harness（驾驭系统）** 是包裹在 LLM 核心推理能力之外的一整套工程基础设施，包括：

- **工具注册与调度**（Tool Registry & Dispatch）
- **技能/能力扩展**（Skills / Capabilities）
- **上下文与记忆管理**（Context & Memory）
- **会话生命周期管理**（Session Lifecycle）
- **安全与权限控制**（Safety & Permissions）

类比：LLM 是"大脑"，Harness 是"神经系统 + 四肢 + 感官"——没有 Harness，LLM 只能"想"不能"做"。

> **参考文章**：Lilian Weng, "LLM Powered Autonomous Agents"  
> https://lilianweng.github.io/posts/2023-06-23-agent/  
> 该文系统阐述了 Agent 的规划（Planning）、记忆（Memory）、工具使用（Tool Use）三大核心模块。

#### 知识点 3：三大主流框架对比

| 维度 | OpenClaw | Hermes Agent | LangChain / LangGraph |
|------|---------|-------------|----------------------|
| **设计哲学** | 个人 AI 助手、静态技能生态、多消息通道聚合 | 自驱式进化 Agent、自主创建技能、闭环学习 | 可组合链式编排、灵活模块化 |
| **工具调用** | Shell 命令白名单 + API 调用 + Skills 触发 | `registry.register()` + 40+ 内置工具集 + MCP 协议 | `@tool` 装饰器 / `StructuredTool` / 绑定工具 |
| **技能/扩展** | 5,400+ 社区 SKILL.md 技能（静态、人工编写） | SKILL.md + agentskills.io + **自主从经验生成新技能** | LCEL Runnable / LangGraph StateGraph / 自定义工作流 |
| **会话/记忆** | 静态文件式（`MEMORY.md` / `USER.md`，会话级注入） | Agent 自驱动持久化 + FTS5 跨会话检索 + Honcho 用户建模 | RunnableWithMessageHistory / LangGraph checkpoint |
| **进化能力** | 静态（无自主学习循环） | **有**（Agent 自主创建/改进技能、自我反思） | 无（依赖开发者编排） |
| **开源地址** | [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw) | [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | [github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) |
| **官方文档** | [openclaw.steephen.cc](https://openclaw.steephen.cc) | [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/docs/) | [python.langchain.com](https://python.langchain.com/) |

**设计哲学差异解读**：
- **OpenClaw**：奠定个人 AI 助手范式，5,400+ 社区技能覆盖广泛场景，SKILL.md 格式成为事实标准；但技能为静态、人工编写，无自主学习能力
- **Hermes Agent**：OpenClaw 的**进化版**——同属一个生态（`hermes claw migrate` 可直接导入 OpenClaw 的技能和记忆），核心突破是**自主创建技能**：Agent 在完成任务后主动将经验固化为新技能，无需人工干预
- **LangChain**：强调”可组合性”，通过 LCEL 实现链式编排，是*构建* Agent 的框架而非终端产品，灵活性最高但需要更多工程投入

> **背景补充**：OpenClaw 与 Hermes Agent 同源——Hermes Agent 团队明确提供了从 OpenClaw 一键迁移的工具 `hermes claw migrate`，可将 OpenClaw 的技能、记忆、消息配置完整导入。选择对比这两个框架，可以直观展示”静态技能系统”与”自进化 Agent”的差异。

#### 知识点 4：Agent Loop —— 核心执行循环

多数 Agent 框架的核心都围绕类似的执行循环展开：

```
┌─────────────────────────────────────┐
│           Agent Loop                │
│                                     │
│  1. 构建提示 (Build Prompt)         │
│     ↓                               │
│  2. 调用 LLM (LLM Inference)        │
│     ↓                               │
│  3. 解析响应 (Parse Response)        │
│     ├─ 文本响应 → 返回用户           │
│     └─ 工具调用 → 执行工具 → 回到 1  │
│                                     │
│  4. 上下文管理 (压缩/截断)           │
└─────────────────────────────────────┘
```

以 Hermes Agent 为例的核心循环逻辑（概念化描述，来源：`hermes-agent` 源码结构）：

```python
def run_conversation():
    # 1. 构建消息：系统提示注入环境信息 + 技能列表 + 工具 Schema
    messages = [build_system_message()]

    while iterations < max_iterations:
        # 当接近 token 上限时，先压缩历史消息，再调用模型
        if near_token_limit(messages):
            messages = compress_context(messages)

        # 2. 调用 LLM（可配置 providers：OpenAI / Anthropic / OpenRouter 等）
        response = llm.chat(messages, tools=tool_schemas)

        # 3. 解析响应
        if response.has_tool_calls:
            for tool_call in response.tool_calls:
                result = dispatch_tool(tool_call.name, tool_call.args)
                messages.append(tool_result_message(result))
            continue  # 继续循环
        else:
            # 4. 文本响应：Agent 可主动将重要信息 nudge 到长期记忆
            maybe_persist_memory(response.text)
            return response.text
```

**OpenClaw 的简化版 Agent Loop**（无自主学习循环，更易理解）：

```
用户消息 → OpenClaw Gateway → 注入 MEMORY.md / USER.md → LLM 推理
→ 如需工具 → 通过 Skills 系统调度（SKILL.md 中定义的工作流）
→ 返回结果
```

两者关键区别：Hermes 在每次回复后有机会**主动更新记忆**（`maybe_persist_memory`），OpenClaw 则依赖人工维护记忆文件。

#### 知识点 5：Harness 的工程挑战

| 挑战 | 描述 | 典型解决方案 |
|------|------|-------------|
| 工具安全 | LLM 可能调用危险工具 | 权限分级、check_fn 前置检查、人工确认 |
| 上下文窗口 | 长对话超出 token 限制 | 自动压缩、摘要、滑动窗口 |
| 幻觉问题 | LLM 编造不存在的工具 | Schema 约束、工具白名单 |
| 延迟与成本 | 多轮工具调用累积 | 并行调度、缓存、流式输出 |
| 可观测性 | 难以追踪 Agent 行为 | 日志链路、步骤回放、调试模式 |

### 实践练习建议

**练习 1：概念辨析（10 分钟，小组讨论）**

给定 3 个场景，判断是否需要 Agent，并说明理由：
- 场景 A：用户问"今天天津天气如何" → 单次工具调用即可
- 场景 B：用户要求"帮我监控某个 GitHub 仓库的 issue，每天总结新增的 bug" → 需要定时 Agent
- 场景 C：用户说"帮我写一封邮件" → 单次 LLM 生成即可

**练习 2：框架选型分析（10 分钟，书面）**

给定需求："构建一个能自动分析代码仓库、生成测试报告、并在 PR 中评论的 Agent"，请从 OpenClaw / Hermes Agent / LangChain 中选择最合适的框架，并写出理由。

---

## 第 2 课时：核心组件解析 —— Tools、Skills、Memory（45 分钟）

### 学习目标

1. 能够使用 Python 定义和注册一个自定义工具（Tool），并理解工具调用的完整流程
2. 能够解释 Skills 系统的设计原理，理解技能与工具的区别与联系
3. 能够设计一个简单的记忆管理方案，区分短期记忆与长期记忆的使用场景

### 核心知识点

#### 知识点 1：工具调用机制（Tool Calling）

**核心概念**：工具是 Agent 与外部世界交互的接口。每个工具由三部分组成：

1. **Schema 定义**：描述工具名称、功能、参数（遵循 OpenAI Function Calling 格式）
2. **Handler 实现**：实际执行逻辑的函数
3. **注册机制**：将 Schema 和 Handler 绑定，让 LLM 能"看到"并调用

**三大框架的工具定义对比**：

```python
# ========== OpenClaw 工具定义 ==========
# OpenClaw 通过 Skills 系统（SKILL.md）定义工具能力，
# 工具由 Shell 命令 / API 调用 / 脚本组成，通过 allowlist 控制权限
# 工具触发由 LLM 根据 SKILL.md 中的描述自主决定

# 工具安全：通过 command_allowlist.yaml 白名单限制可执行命令
# 示例白名单项：
# allowed_commands:
#   - shell: ["curl", "grep", "cat"]
#   - api: ["web_search", "send_message"]

# ========== Hermes Agent 工具定义 ==========
from tools.registry import registry

registry.register(
    name="web_search",                    # 工具名称
    toolset="web",                        # 所属工具集
    schema={                              # OpenAI 格式的函数 Schema
        "name": "web_search",
        "description": "搜索互联网获取信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"}
            },
            "required": ["query"]
        }
    },
    handler=lambda args, **kw: web_search(args.get("query", "")),
    check_fn=lambda: bool(os.getenv("SEARCH_API_KEY")),  # 条件注册
)

# ========== LangChain 工具定义 ==========
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """搜索互联网获取信息。Args: query: 搜索关键词"""
    return search_api(query)

# 或者使用 StructuredTool（更灵活）
from langchain_core.tools import StructuredTool

web_search_tool = StructuredTool.from_function(
    func=search_api,
    name="web_search",
    description="搜索互联网获取信息",
)
```

**工具调用的完整流程**：

```
用户输入 → LLM 推理 → 输出 tool_call: {name, args}
                           ↓
                    工具调度器匹配 name
                           ↓
                    解析 args，调用 handler
                           ↓
                    返回结果 → 追加到消息列表
                           ↓
                    LLM 继续推理 → 输出最终回答
```

#### 知识点 2：技能系统（Skills）

**核心问题**：工具解决“能做什么”，技能解决“在什么场景下按什么流程把工具用好”。

| 维度 | 工具（Tools） | 技能（Skills） |
|------|-------------|---------------|
| 粒度 | 单一操作（如搜索、读文件） | 工作流程（如"代码审查"、"调试"） |
| 知识 | 通常只包含参数和执行语义 | 包含触发条件、步骤指南、常见陷阱和验证清单 |
| 组合 | 互不依赖 | 可组合多个工具完成复杂任务 |
| 类比 | 锤子、螺丝刀 | 木工手册、装修指南 |

**OpenClaw 的 SKILL.md 示例**（静态技能，人工编写）：

```yaml
---
name: github-issue-monitor
description: Use when user asks to monitor GitHub repo issues or summarize bugs.
version: 1.0.0
---

# GitHub Issue Monitor

## Overview
Monitor a GitHub repository's issues and generate daily summaries.

## When to Use
- User asks to "monitor issues" or "track bugs" for a repo
- Don't use for: one-time searches

## Steps
1. **Fetch** — `gh issue list --repo <owner/repo> --state open`
2. **Filter** — filter by label (bug, feature, etc.)
3. **Summarize** — generate daily digest of new issues
4. **Alert** — send summary to configured channel

## Required Tools
- gh CLI (authenticated)
- curl (for API fallback)
```

**Hermes Agent 的 SKILL.md 示例**（自进化技能，支持自主生成）：

```yaml
---
name: systematic-debugging
description: Use when encountering bugs or errors. 4-phase root cause debugging approach.
version: 1.0.0
---

# Systematic Debugging

## Overview
4-phase approach: understand before fixing.

## When to Use
- Encounter a bug or error
- Don't use for: syntax errors with obvious fixes

## Steps
1. **Reproduce** — 确认可以稳定复现
2. **Isolate** — 缩小问题范围
3. **Hypothesize** — 形成根因假设
4. **Verify** — 验证修复有效

## Common Pitfalls
1. 不要一上来就改代码 — 先理解
2. 不要同时改多处 — 一次一个变量
```

**LangChain 的链式技能**（通过 LCEL 组合）：

```python
from langchain_core.runnables import RunnablePassthrough

# 将多个工具/步骤组合成一条链
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | output_parser
)
```

**Hermes Agent 的自主技能生成**（区别于 OpenClaw 的核心特性）：

```python
# Hermes Agent 可以在完成复杂任务后，自主将经验固化为新技能
# 这不是预先编写好的，而是 Agent 自己生成的 SKILL.md

# 示例：Agent 完成一次调试后，自主生成如下技能
"""
## Auto-Generated: python-unittest-debug
After debugging a Python unittest failure, save this skill.

## When to Use
- pytest/unittest failures in Python projects
- Don't use for: syntax errors

## Steps
1. Run: pytest <file> -v  (capture full output)
2. Parse: extract FAILED lines and traceback
3. Isolate: comment out passing tests to narrow scope
4. Verify: re-run with the specific test
"""

# LangChain 的链式技能（通过 LCEL 组合）：
from langchain_core.runnables import RunnablePassthrough

# 将多个工具/步骤组合成一条链
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | output_parser
)
```

#### 知识点 3：记忆管理（Memory）

**核心问题**：LLM API 调用本身无状态；Agent 需要由 Harness 显式维护消息历史、任务状态和持久化知识，才能具备跨轮次、跨任务的一致性。

```
┌────────────────────────────────────────────┐
│              记忆层次模型                    │
│                                            │
│  ┌──────────────┐   工作记忆（上下文窗口）   │
│  │  当前对话历史  │   ← 随对话动态更新        │
│  └──────────────┘                          │
│  ┌──────────────┐   短期记忆（会话内）       │
│  │  本轮任务状态  │   ← Scratchpad/变量       │
│  └──────────────┘                          │
│  ┌──────────────┐   长期记忆（跨会话）       │
│  │  用户偏好/知识 │   ← 持久化存储            │
│  └──────────────┘                          │
└────────────────────────────────────────────┘
```

**三大框架的记忆实现**：

| 框架 | 短期记忆 | 长期记忆 | 特殊能力 |
|------|---------|---------|---------|
| **OpenClaw** | 当前会话消息（Gateway 注入） | `MEMORY.md`（Agent 记忆）+ `USER.md`（用户画像） | 静态文件，会话开始时注入上下文；无自动压缩 |
| **Hermes Agent** | 当前消息列表 + 上下文压缩 | Agent 自驱动持久化 + FTS5 跨会话全文检索 + Honcho 用户建模 | **会话结束时 Agent 主动决定哪些信息值得保存** |
| **LangChain / LangGraph** | `RunnableWithMessageHistory` 或 LangGraph checkpoint | 向量库、数据库、摘要等外部持久化方案 | LangGraph 更适合生产级有状态 Agent；旧式 `ConversationBufferMemory` 不宜作为新项目首选 |

**OpenClaw 记忆文件示例**：

```markdown
# MEMORY.md
- 用户偏好中文回复
- 项目使用 pytest 框架
- 上次调试：API 路由问题在 v2 版本已修复
```

```markdown
# USER.md
- 姓名：张三
- 职业：软件工程师
- 偏好：简洁的技术解释，避免过度细节
```

**Hermes Agent 记忆工具使用示例**：

```python
# 保存持久记忆（跨会话保留）
memory(action="add", target="user", content="用户偏好中文回复")
memory(action="add", target="memory", content="项目使用 pytest 框架")

# 搜索历史会话
session_search(query="上次调试的问题")
```

**LangChain / LangGraph 记忆管理示例**：

```python
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 为每个会话 ID 维护独立的消息历史。生产环境通常换成 Redis、数据库、
# LangGraph checkpoint 或向量库，而不是只放在进程内存中。
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
)
```

#### 知识点 4：三大组件的协作关系

```
                    ┌─────────────┐
                    │   用户指令    │
                    └──────┬──────┘
                           ↓
                    ┌─────────────┐
                    │   Skills    │ ← 选择"怎么做"
                    │  (技能调度)  │    加载最佳实践
                    └──────┬──────┘
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Tool A  │ │  Tool B  │ │  Tool C  │ ← 工具执行
        │ (搜索)    │ │ (读文件)  │ │ (写代码)  │    "做什么"
        └─────┬────┘ └─────┬────┘ └─────┬────┘
              └────────────┼────────────┘
                           ↓
                    ┌─────────────┐
                    │   Memory    │ ← 保存/检索
                    │  (记忆管理)  │    "记住什么"
                    └──────┬──────┘
                           ↓
                    ┌─────────────┐
                    │   最终输出    │
                    └─────────────┘
```

**设计原则**：
- **Skills 决定策略**：选择哪些工具、以什么顺序、需要注意什么
- **Tools 执行操作**：具体的 I/O 操作，结果可验证
- **Memory 提供上下文**：避免重复询问，保持跨会话一致性

#### 知识点 5：工程实践要点

1. **工具设计原则**
   - 单一职责：每个工具只做一件事
   - 清晰描述：LLM 依赖 description 来决定是否调用
   - 参数最小化：只传必要参数，减少 LLM 出错概率
   - 返回结构化：JSON 格式输出，便于后续处理

2. **技能设计原则**
   - 触发条件明确："When to Use" 帮助 LLM 判断何时加载
   - 包含反模式："Common Pitfalls" 避免常见错误
   - 可验证：提供 "Verification Checklist"

3. **记忆设计原则**
   - 分层存储：区分临时状态与持久知识
   - 主动遗忘：过期信息应及时清理
   - 隐私安全：敏感信息不入记忆

### 实践练习建议

**练习 1：工具定义实战（15 分钟，编码）**

使用 OpenAI Function Calling 格式定义以下 3 个工具的 Schema：
- `calculate(expression: str) -> float`：计算数学表达式
- `get_weather(city: str, unit: str = "celsius") -> str`：获取天气
- `read_code(file_path: str, line_range: tuple = None) -> str`：读取代码文件

思考：如何让 description 足够清晰，使得 LLM 不会混淆 `calculate("2+3")` 和 `web_search("2+3的计算结果")`？

**练习 2：技能设计练习（10 分钟，书面）**

为以下场景设计一个 SKILL.md：
- 场景：你是一个"代码审查"技能
- 要求：包含触发条件、步骤指南、常见陷阱、验证清单

**练习 3：记忆方案设计（10 分钟，讨论）**

讨论以下场景中需要哪种记忆：
- 场景 A：Agent 在一次对话中需要记住之前 5 轮的内容 → 短期记忆
- 场景 B：Agent 需要记住用户的编程语言偏好 → 长期记忆
- 场景 C：Agent 需要记住上一次运行时的 bug 分析结果 → 长期记忆 + session_search

---

## 信息来源

### 官方文档

| 框架 | 资源 | URL |
|------|------|-----|
| OpenClaw | 官方文档 | https://openclaw.steephen.cc |
| OpenClaw | GitHub 仓库 | https://github.com/openclaw/openclaw |
| OpenClaw | 社区技能列表 | https://agentskills.io （与 Hermes 共享） |
| OpenClaw | 社区技能合集 | https://github.com/VoltAgent/awesome-openclaw-skills |
| Hermes Agent | 官方文档 | https://hermes-agent.nousresearch.com/docs/ |
| Hermes Agent | GitHub 仓库 | https://github.com/NousResearch/hermes-agent |
| Hermes Agent | 工具参考 | https://hermes-agent.nousresearch.com/docs/reference/tools-reference |
| Hermes Agent | 记忆系统 | https://hermes-agent.nousresearch.com/docs/user-guide/features/memory |
| Hermes Agent | 从 OpenClaw 迁移 | `hermes claw migrate` 命令 |
| LangChain | 官方文档 | https://python.langchain.com/ |
| LangChain | 工具调用文档 | https://python.langchain.com/docs/concepts/tools/ |
| LangChain | LangGraph 文档 | https://langchain-ai.github.io/langgraph/ |
| LangChain | GitHub 仓库 | https://github.com/langchain-ai/langchain |

### 补充技术文章

| 文章 | 作者 | URL | 核心要点 |
|------|------|-----|---------|
| LLM Powered Autonomous Agents | Lilian Weng | https://lilianweng.github.io/posts/2023-06-23-agent/ | 系统阐述 Agent 的规划、记忆、工具使用三大模块 |
| The Anatomy of an AI Agent | Chip Huyen | https://huyenchip.com/2025/01/16/agents.html | Agent 的工程架构与生产化挑战 |
| Tool Use and Function Calling | OpenAI Cookbook | https://cookbook.openai.com/articles/related_resources#function-calling | 工具调用的最佳实践 |

