# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Prompt Engineering course with Python examples demonstrating various LLM prompting techniques. The examples directory contains both **Python scripts** and **Jupyter Notebooks** for interactive learning.

## Architecture

### Core Components

**config.py** (parent directory)
- `LLMConfig` dataclass with provider, model, api_key, base_url, temperature, max_tokens fields
- Supports four providers: `openai`, `anthropic`, `ollama`, `minimax`
- Default: `provider="minimax"`, `model="MiniMax-M2.7"`

**utils/llm_client.py** (parent directory)
- `LLMClient` class provides unified interface for all LLM providers
- `chat(messages, temperature, **kwargs)` returns string response
- Automatically loads API keys from environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MINIMAX_API_KEY`)
- Minimax uses OpenAI-compatible API at `https://api.minimaxi.com/v1`
- Includes `estimate_tokens()` helper for token counting

## File Structure

### Jupyter Notebook (Recommended for Teaching)

**`prompt_engineering_complete.ipynb`** - 综合性教学 Notebook，包含所有章节：

| 章节 | 主题 | 内容 |
|------|-------|------|
| 第一章 | 基础对话 | 简单 LLM 调用、多轮对话、提示词模板 |
| 第二章 | 角色设定 | System Prompt、代码审查专家、数学老师、面试官 |
| 第三章 | Few-Shot 学习 | 文本分类、信息提取、SQL 生成 |
| 第四章 | 思维链 (CoT) | 零样本 CoT、数学应用题、逻辑推理 |
| 第五章 | ReAct 模式 | 推理 + 行动、工具调用、ReActAgent 类 |
| 第六章 | 高级技巧 | Self-Consistency、Tree of Thoughts、Prompt Chaining |
| 第七章 | RAG 系统 | Document 类、SimpleRAG 类、知识库问答 |
| 第八章 | 教学案例 | 代码审查、算法可视化、Bug 诊断、出题助手 |

### Python Scripts

对应的 `.py` 文件也存在（如 `01_basic_chat.py`），可用于命令行运行。

## Running Examples

### Jupyter Notebook (Recommended)

```bash
# Start Jupyter
cd examples
jupyter notebook

# Open prompt_engineering_complete.ipynb
```

API Key 已在 Notebook 第一个单元格中预设。

### Python Scripts

```bash
# Set Minimax API key
export MINIMAX_API_KEY='your-key'

# Run from examples directory
python3 01_basic_chat.py
python3 02_role_prompting.py
# etc.
```

## Key Patterns

### Message Format
All examples use standard message format:
```python
messages = [
    {"role": "system", "content": "..."},  # optional
    {"role": "user", "content": "..."}
]
response = client.chat(messages)
```

### Temperature Guidelines
- Code generation/factual: 0.0-0.3
- General tasks: 0.5-0.7
- Creative writing: 0.7-1.0

### Import Pattern
All example files use:
```python
import sys
sys.path.append("..")
from config import LLMConfig
from utils.llm_client import LLMClient
```

## Common Tasks

**Run a single example:** `python3 01_basic_chat.py`

**Test with Minimax (default):**
```python
config = LLMConfig(provider="minimax", model="MiniMax-M2.7")
```

**Switch to other providers:**
```python
# OpenAI
config = LLMConfig(provider="openai", model="gpt-4o-mini")

# Anthropic
config = LLMConfig(provider="anthropic", model="claude-3-sonnet")

# Ollama (local)
config = LLMConfig(provider="ollama", model="llama3", base_url="http://localhost:11434")
```

## Dependencies

Required packages: `openai`, `jupyter`, `requests`

Install: `pip install openai jupyter requests`

## Notes

- All examples use Minimax API by default (OpenAI-compatible format)
- Examples are designed for educational purposes with Chinese prompts
- Jupyter Notebooks are recommended for teaching/learning
- `07_rag_qa_system.ipynb` implements keyword-based retrieval (not vector-based)
- `05_react.ipynb` has mock tools; real tool integration requires custom implementation
