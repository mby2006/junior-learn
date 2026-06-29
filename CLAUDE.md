# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 激活虚拟环境（Windows）
source venv/Scripts/activate

# 安装依赖
pip install -r requirements.txt
pip install pydantic-settings

# 本地开发启动（自动激活端口和热重载）
python src/api/run_server.py

# 健康检查
curl http://localhost:8001/api/v1/health

# 语法检查
python -m py_compile src/api/run_server.py

# Docker 部署
docker compose up -d --build

# 部署前检查
python -m py_compile src/api/run_server.py
python -m py_compile src/services/evermemos/client.py

# 列出需要上传的文件（git 变更）
git diff --name-only
```

## 服务器部署

```bash
# 项目路径（服务器）
cd /opt/StudyBuddy-public-main

# 激活虚拟环境
source venv/bin/activate

# 拉取最新代码或上传文件后重启
pkill -f "python.*run_server"
nohup python src/api/run_server.py > logs/server.log 2>&1 &

# 验证
curl http://localhost:8001/api/v1/health

# 查看实时日志
tail -f logs/server.log

# 通过 systemd 管理（生产推荐）
systemctl status studybuddy --no-pager
journalctl -u studybuddy -n 50 --no-pager
sudo systemctl restart studybuddy

# Docker 部署
docker compose up -d --build
docker compose logs -f studybuddy
docker compose down
```

## 架构概览

```
web/index.html  →  /api/v1/*  →  FastAPI routers  →  Agents  →  Services  →  LLM / Embedding / data
```

### 前端

`web/index.html` 单文件 SPA（~4700 行），使用 Alpine.js 3 + Tailwind CSS（CDN 已本地化到 `web/vendor/`），无构建步骤，修改后直接刷新即可。

**Alpine.js `this.` 规则（极易犯错）**：
- HTML 模板（`x-text`, `x-show`, `:class` 等属性值）：**不要用 `this.`**，直接写属性名 `page`, `prof.streak`
- JS 方法/getter 体（`app()` 返回对象内）：**必须用 `this.`**，`this.prof.streak`, `this.wbFilter()`
- 事件处理（`@click`, `@mouseover`）：方法调用无需 `this`，`@click="toggleTheme()"`
- 模板访问对象属性如 `gen.checked`：Alpine 不追踪 `Set` 对象，用普通对象 `{}` 代替

**页面结构**：通过 `page` 状态切换，所有页面 div 用 `x-show="page==='xxx'"` 控制显示。

| page | 功能 |
|------|------|
| dashboard | 首页仪表盘 |
| homework | 作业批改 |
| inquire | 知识点查询/问答 |
| wrongbook | 错题本（闪卡复习） |
| kb | 知识库（教材/阅读资料） |
| generate | 智能出题 |
| history | 历史记录 |
| profile | 我的/偏好设置 |
| dino | 恐龙快跑小游戏 |

**深色模式**：CSS 变量实现，`:root` 浅色 + `html.dark` 深色，通过 `toggleTheme()` 切换。使用 `var(--bg-card)` 等变量引用颜色。

### 后端

FastAPI 应用，入口 `src/api/main.py`，启动脚本 `src/api/run_server.py`（自动切换到项目根目录）。

**路由器职责**：只处理 HTTP 请求、参数校验和响应，不包含业务逻辑。

| 路由 | 前缀 | 说明 |
|------|------|------|
| homework | `/api/v1/homework` | OCR → 批改 → 知识点标注 → ExamTag |
| wrong-book | `/api/v1/wrong-book` | 错题本 CRUD |
| explain | `/api/v1/explain` | 多轮解析（文本+图片+RAG） |
| generate | `/api/v1/generate` | 智能出题（WebSocket 流式） |
| textbook | `/api/v1/textbook` | 教材 PDF 管理 |
| reading-materials | `/api/v1/reading-materials` | 阅读资料管理 |
| profile | `/api/v1/profile` | 学情画像 |
| settings | `/api/v1/settings` | UI 偏好设置 |
| history | `/api/v1/history` | 批改/答疑历史 |

### Agents

`src/agents/` 编排业务流程：

- **question/**：智能出题，`AgentCoordinator` → `RetrieveAgent`(RAG 检索) → `GenerateAgent`(LLM 生成) → `RelevanceAnalyzer`(相关性分析)
- **homework/**：作业批改流水线，`OCRAgent`(图片→题目) → `GradeAgent`(逐题批改) → `KnowPointAgent`(知识点标注) → `ExamTagAgent`(试卷特征)
- **explain/**：多轮解析，支持教材 RAG 检索增强
- **memory/**：学情画像、长期记忆

### Services

`src/services/` 封装底层能力：

- **llm/**：统一 LLM 调用，支持多 provider（OpenAI 兼容接口）
- **embedding/**：Embedding 客户端
- **rag/**：RAG 流水线（支持 lightrag 等多种实现）
- **question_bank/**：本地题库缓存
- **evermemos/**：EverMemOS 长期记忆云服务

## 部署注意事项

1. **只改前端** → 只需上传 `web/index.html`，无需重启后端
2. **改了后端代码** → 必须重启后端进程（见上）
3. **`data/` 目录** → 生产数据目录，上传代码时**不要覆盖**服务器已有数据
4. **`logs/` 目录** → 可能不存在，首次启动需 `mkdir -p logs`
5. **环境变量** → 服务器 `.env` 必须单独配置 API Key，不要上传本地 `.env`
6. **反向代理** → 大 PDF 上传需设置足够大的 `client_max_body_size`
7. **需要上传的完整文件列表**：

   ```
   后端变更 → src/*（对应修改的 .py 文件）
   前端变更 → web/index.html
   注意     → web/vendor/ 目录必须完整（CDN 本地化依赖）
   注意     → 不要上传 data/、.env、venv/、__pycache__/
   ```

## 配置

```bash
# .env - 环境变量
LLM_BINDING=openai                    # openai / azure_openai / gemini
LLM_MODEL=qwen3.7-plus                # 主模型
LLM_API_KEY=sk-xxx
LLM_HOST=https://dashscope.aliyuncs.com/compatible-mode/v1

EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-v3
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_HOST=https://dashscope.aliyuncs.com/compatible-mode/v1

# 可同时配置多 provider（如 DeepSeek）
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

BACKEND_PORT=8001
```

- `.env`：LLM/Embedding 配置（未提交到仓库）
- `config/main.yaml`：系统级配置、科目映射
- `config/agents.yaml`：各 Agent 的 temperature/max_tokens

## 数据存储（data/）

`data/` 为运行时数据目录，部署时避免覆盖：

- `question_bank/`：题库缓存 JSON
- `generation_history.json`：出题历史
- `homework_images/`：批改上传图片
- `user/`：用户偏好、学情数据
- `textbooks/`：教材 PDF + 向量索引
- `history/`：批改记录和答疑记录 JSON

## 代码变更注意事项

1. **修改 API 返回结构** → 必须同步检查 `web/index.html` 中对应 fetch 调用和渲染
2. **修改教材科目/分册** → 同步 3 处：`kb_manager.py` + `textbook.py` + `explain_agent.py`
3. **修改移动端布局** → 验证底部导航避让(`mob-scroll`)、`x-show` 页面隐藏、输入框弹起行为
4. **修改 LLM/Embedding** → 检查 `src/services/llm/` 和 `src/services/embedding/`
5. **前端 x-show 容器** → 不要加 `display: ... !important`，会覆盖 Alpine 隐藏逻辑
6. **`data/` 文件操作** → JSON 读写用 `asyncio.Lock` 防止并发写入损坏
7. **后台任务** → `asyncio.create_task` 需加 `task.add_done_callback()` 记录异常
8. **主题/颜色** → 使用 CSS 变量 `var(--bg-card)` 而非硬编码值，深色模式自动适配
