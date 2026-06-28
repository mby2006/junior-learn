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

当前仓库没有项目级测试目录；`Glob` 搜索只发现虚拟环境内第三方包测试。新增测试前先确认项目希望采用的测试框架。

## 运行入口与访问地址

- 应用入口：`src/api/main.py`
- 启动脚本：`src/api/run_server.py`
- API 前缀：`/api/v1`
- 前端页面：`http://localhost:8001/ui`
- 健康检查：`http://localhost:8001/api/v1/health`
- OpenAPI：`http://localhost:8001/docs`

`src/api/run_server.py` 会切换到项目根目录，把根目录加入 `sys.path`，再用 Uvicorn 启动 `src.api.main:app`。默认端口从配置读取，常见为 `8001`。

## 架构概览

```text
web/index.html  →  /api/v1/*  →  FastAPI routers  →  Agents  →  Services  →  LLM / Embedding / data
```

- 前端是 `web/index.html` 单文件 SPA，使用 Alpine.js + Tailwind 本地资源，无构建步骤。
- 后端是 FastAPI，`src/api/main.py` 注册路由并挂载 `/ui` 静态前端。
- `src/api/routers/` 只处理 HTTP 请求、参数和响应。
- `src/agents/` 编排业务流程，例如作业批改、问答、记忆、出题。
- `src/services/` 封装 LLM、Embedding、RAG、EverMemOS、配置加载等底层能力。
- `data/` 保存运行时数据、上传文件、教材 PDF、向量索引等。

## 核心路由

`src/api/main.py` 当前注册：

- `/api/v1/homework/*`：作业图片 OCR、批改、知识点和试卷标签。
- `/api/v1/wrong-book/*`：错题本 CRUD 和统计。
- `/api/v1/explain/*`：多轮题目解析，支持文本、图片和教材检索增强。
- `/api/v1/settings/*`：用户偏好。
- `/api/v1/profile/*`：学情画像和长期记忆。
- `/api/v1/history/*`：批改记录和答疑记录。
- textbook router：教材 PDF 上传、索引、预览、删除、重命名。
- reading-materials router：阅读资料上传和管理。
- `/api/v1/health`：健康检查。

## 作业批改流程

作业批改主路径是：

```text
OcrAgent → GradeAgent → KnowPointAgent → ExamTagAgent
```

批改完成后会写入：

- `WrongBookService`：本地错题数据。
- `EverMemOSService`：可选的学情长期记忆上传。

修改作业批改响应结构时，要同步检查 `web/index.html` 的调用和展示逻辑。

## 知识库与教材

教材上传、状态、预览、删除、重命名由 textbook router 负责。问答页会通过教材索引做检索增强。

需要保持同步的科目映射：

- `src/agents/explain/kb_manager.py`
- `src/api/routers/textbook.py`
- `src/agents/explain/explain_agent.py` 中存在独立旧科目名映射，改科目时也要检查。

阅读资料只用于在线阅读，不参与 AI 检索。

## 前端结构

`web/index.html` 使用 Alpine 状态 `page` 控制页面：

- `dashboard`：首页
- `homework`：作业批改
- `inquire`：知识点查询
- `wrongbook`：错题本
- `kb`：知识库
- `history`：历史记录
- `profile`：我的
- `dino`：恐龙快跑

修改前端时注意：

- 无构建步骤，改 `web/index.html` 后刷新即可。
- CDN 已本地化到 `web/vendor/`，部署时必须一起上传。
- 移动端底部导航使用 safe-area 相关样式，新增固定底部输入区时要避让底部菜单。
- 带 `x-show` 的页面根容器不要写 `display: ... !important`，否则会覆盖 Alpine 的隐藏逻辑，导致其它页面内容串出来。
- 知识点查询页移动端是整页滚动，消息区不单独内部滚动。

## 恐龙快跑

恐龙游戏在 `web/dino/index.html`，由主 SPA 通过 iframe 嵌入。

主页面和 iframe 通过 `postMessage` 通信：

- 游戏结束：`dinoGameOver`
- 实时分数：`dinoScore`
- 父页面重启：`dinoRestart`

移动端画面高度同时受两处影响：

- `web/index.html` 中 iframe 容器高度。
- `web/dino/index.html` 中 Canvas 的 `CW`、`CH`、`GROUND_Y` 和 `resizeCanvas()`。

修改 Canvas 尺寸时要同步检查地面位置、障碍物位置和移动端显示比例。

## 配置

`.env.example` 提供示例。关键变量包括：

```bash
BACKEND_PORT=8001

LLM_BINDING=openai
LLM_MODEL=gpt-4o
LLM_API_KEY=sk-xxx
LLM_HOST=https://api.openai.com/v1

EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_HOST=https://api.openai.com/v1
EMBEDDING_DIMENSION=3072
```

YAML 配置：

- `config/main.yaml`：系统级配置、科目、日志、RAG provider 等。
- `config/agents.yaml`：各 Agent 的 temperature、max_tokens 等。

LLM 使用 OpenAI 兼容接口，可通过 `.env` 切换 OpenAI、Gemini、Kimi 等。Embedding 也可单独配置。

## 部署与运行注意事项

- 优先使用 `python src/api/run_server.py` 启动本地服务。
- `requirements.txt` 已包含 `tenacity`，但仍需额外安装 `pydantic-settings`。
- 大 PDF 上传需要反向代理设置足够大的 `client_max_body_size`。
- `data/` 是运行时数据目录，部署或上传代码时避免覆盖服务器已有数据。
- 如果只改前端，优先只上传 `web/index.html`；涉及恐龙游戏时再上传 `web/dino/index.html`。

生产常用检查：

```bash
cd /opt/StudyBuddy-public-main
systemctl status studybuddy --no-pager
journalctl -u studybuddy -n 100 --no-pager
curl http://127.0.0.1:8001/api/v1/health
```

## 代码变更注意

- 修改路由返回结构时，同步检查 `web/index.html` 调用方。
- 修改教材科目、分册、名称时，同步检查上传下拉、教材管理和问答 Agent。
- 修改移动端布局时，同时验证底部导航、输入框、整页滚动和 `x-show` 页面隐藏是否正常。
- 修改 LLM/Embedding provider 时，优先检查 `src/services/llm/`、`src/services/embedding/` 和 `.env` 配置读取路径。
