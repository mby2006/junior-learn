# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt
pip install pydantic-settings

# 本地开发启动
python src/api/run_server.py

# 健康检查
curl http://localhost:8001/api/v1/health

# Docker 启动
docker compose up -d --build

# Docker 日志
docker compose logs -f studybuddy

# Docker 停止
docker compose down

# 语法检查单个 Python 文件
python -m py_compile src/api/run_server.py
```

## 架构概览

```text
web/index.html  →  /api/v1/*  →  FastAPI routers  →  Agents  →  Services  →  LLM / Embedding / data
```

- **前端**: `web/index.html` 单文件 SPA，使用 Alpine.js + Tailwind CSS，无构建步骤，改完直接刷新。CDN 已本地化到 `web/vendor/`。
- **后端**: FastAPI，`src/api/main.py` 注册路由，`src/api/routers/` 只处理 HTTP 请求、参数校验和响应。
- **Agents**: `src/agents/` 编排业务流程：
  - `question/`: 智能出题（`AgentCoordinator` → `RetrieveAgent` → `GenerateAgent` → `RelevanceAnalyzer`）
  - `homework/`: 作业批改 OcrAgent → GradeAgent → KnowPointAgent → ExamTagAgent
  - `explain/`: 多轮题目解析，支持教材 RAG 检索增强
  - `memory/`: 学情画像和长期记忆
- **Services**: `src/services/` 封装底层能力：
  - `llm/`: LLM 客户端，支持多 provider（OpenAI/Anthropic/Gemini 等）
  - `embedding/`: Embedding 客户端
  - `rag/`: RAG 流水线
  - `question_bank/`: 本地题库缓存服务（历次批改缓存）
  - `evermemos/`: EverMemOS 长期记忆云服务对接
  - `config/`: 统一配置加载
- **配置**:
  - `.env`: 环境变量（LLM API Key/Host/Model）
  - `config/main.yaml`: 系统级配置、科目、日志
  - `config/agents.yaml`: 各 Agent 的 temperature/max_tokens 参数
- **数据存储**: `data/` 保存运行时数据：
  - `question_bank/`: 题库缓存 JSON（每科一个文件）
  - `generated/`: 智能出题输出
  - `generation_history.json`: 出题历史记录
  - `homework_images/`: 作业批改上传图片
  - `user/`: 用户个人数据（学情、偏好等）
  - `textbooks/`: 上传教材 PDF 和向量索引

## 核心路由

| 路由 | 前缀 | 功能 |
|------|------|------|
| homework | `/api/v1/homework` | 作业图片 OCR、批改、知识点标注 |
| wrong-book | `/api/v1/wrong-book` | 错题本 CRUD 和统计 |
| explain | `/api/v1/explain` | 多轮题目解析，支持文本/图片 |
| generate | `/api/v1/generate` | 智能出题 - WebSocket 流式生成 + 历史记录 |
| textbook | `/api/v1/textbook` | 教材 PDF 上传、索引、预览 |  |
| profile | `/api/v1/profile` | 学情画像和长期记忆 |
| settings | `/api/v1/settings` | 用户偏好设置 |
| history | `/api/v1/history` | 批改记录和答疑历史 |
| health | `/api/v1/health` | 健康检查 |

## 前端结构

`web/index.html` 使用 Alpine 状态 `page` 控制页面切换：
- `dashboard`: 首页
- `homework`: 作业批改
- `inquire`: 知识点查询/问答
- `wrongbook`: 错题本
- `kb`: 知识库（教材管理）
- `generate`: 智能出题（新增）
- `history`: 历史记录
- `profile`: 我的
- `dino`: 恐龙快跑小游戏

## 代码变更注意事项

1. **修改路由返回结构** → 同步检查 `web/index.html` 调用方
2. **修改教材科目/分册** → 同步检查 `src/agents/explain/kb_manager.py` + `src/api/routers/textbook.py` + `src/agents/explain/explain_agent.py`
3. **修改移动端布局** → 同时验证底部导航避让、输入框、页面隐藏逻辑
4. **修改 LLM/Embedding provider** → 优先检查 `src/services/llm/` 和 `src/services/embedding/`
5. **出题功能** → 后端保存历史到 `data/generation_history.json`，前端直接加载渲染

## 访问地址

- 前端: `http://localhost:8001/ui`
- 健康检查: `http://localhost:8001/api/v1/health`
- OpenAPI: `http://localhost:8001/docs`
