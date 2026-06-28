# StudyBuddy 新增功能规划文档

> 文档版本：v1.0 · 日期：2026-06-27  
> 范围：基于现有功能（作业批改 / 答疑 / 出题 / 错题本 / 学情记忆 / 知识库 RAG）的新增功能规划  
> 技术栈：FastAPI + Alpine.js + Tailwind CSS（单文件 SPA）+ LLM 多供应商 + RAG 向量检索

---

## 目录

1. [功能总览与优先级矩阵](#一功能总览与优先级矩阵)
2. [第一类：学习效率工具](#二第一类学习效率工具)
   - 2.1 番茄专注钟
   - 2.2 学习计划表
   - 2.3 考试倒计时
3. [第二类：知识管理系统](#三第二类知识管理系统)
   - 3.1 知识图谱可视化
   - 3.2 Markdown 笔记本
   - 3.3 AI 思维导图生成
4. [第三类：AI 能力增强](#四第三类ai-能力增强)
   - 4.1 智能复习计划（艾宾浩斯遗忘曲线）
   - 4.2 AI 作文批改
   - 4.3 英语口语练习
5. [第四类：游戏化激励系统](#五第四类游戏化激励系统)
   - 5.1 成就徽章墙
   - 5.2 成长树
   - 5.3 每日打卡热力图
6. [第五类：实用学科工具](#六第五类实用学科工具)
   - 5.1 智能单词本
   - 5.2 公式速查手册
   - 5.3 古诗文背诵默写
7. [第六类：多模态与外部集成](#七第六类多模态与外部集成)
   - 7.1 语音朗读 TTS
   - 7.2 手写公式识别
   - 7.3 视频讲解推荐
8. [数据库变更汇总](#八数据库变更汇总)
9. [API 路由变更汇总](#九api-路由变更汇总)
10. [前端页面变更汇总](#十前端页面变更汇总)
11. [实施路线图](#十一实施路线图)

---

## 一、功能总览与优先级矩阵

### 优先级说明

| 标记 | 含义 | 建议时间 |
|------|------|----------|
| P0 | 与现有功能联动最强，投入产出比最高 | 立即启动 |
| P1 | 体验提升明显，技术难度适中 | 第二批 |
| P2 | 锦上添花，有空再做 | 第三批 |

### 功能优先级总表

| # | 功能名 | 类别 | 优先级 | 推荐度 | 主要联动模块 | 技术难度 |
|---|--------|------|--------|--------|-------------|----------|
| 1 | 智能复习计划 | AI 增强 | P0 | ★★★★★ | 错题本 | 中 |
| 2 | AI 作文批改 | AI 增强 | P0 | ★★★★ | LLM 服务 | 低 |
| 3 | 智能单词本 | 实用工具 | P0 | ★★★★ | 答疑/错题 | 低 |
| 4 | 手写公式识别 | 多模态 | P1 | ★★★★ | 答疑 | 中 |
| 5 | 知识图谱可视化 | 知识管理 | P1 | ★★★★ | 错题/答疑 | 高 |
| 6 | 番茄专注钟 | 学习效率 | P1 | ★★★ | Dashboard | 低 |
| 7 | 学习计划表 | 学习效率 | P1 | ★★★ | Dashboard | 低 |
| 8 | Markdown 笔记本 | 知识管理 | P1 | ★★★ | 答疑 | 中 |
| 9 | 古诗文背诵默写 | 实用工具 | P1 | ★★★ | 无 | 中 |
| 10 | 成就徽章墙 | 激励系统 | P1 | ★★★ | 全局 | 中 |
| 11 | AI 思维导图 | 知识管理 | P2 | ★★★ | 知识库 RAG | 中 |
| 12 | 视频讲解推荐 | 多模态 | P2 | ★★★ | 错题 | 低 |
| 13 | 英语口语练习 | AI 增强 | P2 | ★★★ | 无 | 高 |
| 14 | 考试倒计时 | 学习效率 | P2 | ★★ | Dashboard | 低 |
| 15 | 成长树 | 激励系统 | P2 | ★★ | Dashboard | 低 |
| 16 | 每日打卡热力图 | 激励系统 | P2 | ★★ | 全局 | 低 |
| 17 | 公式速查手册 | 实用工具 | P2 | ★★ | 无 | 低 |
| 18 | 语音朗读 TTS | 多模态 | P2 | ★★ | 全局 | 低 |

---

## 二、第一类：学习效率工具

### 2.1 番茄专注钟

**功能描述**

在侧边栏增加一个番茄钟入口，点击进入全屏专注模式。25 分钟专注计时 + 5 分钟休息提醒，支持自定义时长。每次专注会话自动记录科目和学习时长，数据汇入 Dashboard 周报。

**用户故事**

- 作为学生，我想在写作业前启动番茄钟，帮我保持专注
- 作为学生，我想看到本周累计专注时长，了解自己的学习投入
- 作为学生，我想在专注时屏蔽其他页面入口，减少干扰

**前端设计**

```
新增页面：pomodoro
├── 顶部：大号圆形倒计时（SVG 环形进度条）
├── 中部：科目选择器（复用现有科目列表）+ 模式切换（25min / 50min / 自定义）
├── 底部：本周专注统计（累计时长 / 完成次数 / 各科目占比饼图）
└── 专注中：全屏遮罩 + 白噪音开关 + "放弃专注"按钮
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/pomodoro/start` | 开始专注会话，参数：`{subject, duration_min}` |
| PUT | `/api/pomodoro/{session_id}/complete` | 标记会话完成 |
| DELETE | `/api/pomodoro/{session_id}` | 放弃会话 |
| GET | `/api/pomodoro/stats` | 获取周/月统计，返回 `{total_min, sessions, by_subject}` |

**数据存储**

```python
# src/api/routers/pomodoro.py
# 数据文件：data/user/pomodoro_sessions.json（复用现有 JSON 文件存储模式）

{
  "sessions": [
    {
      "id": "uuid",
      "subject": "数学",
      "started_at": "2026-06-27T19:00:00",
      "completed_at": "2026-06-27T19:25:00",
      "duration_min": 25,
      "status": "completed"  # completed / abandoned
    }
  ]
}
```

**加分项**

- 白噪音背景音（雨声/咖啡馆/图书馆，用免费 CDN 音频）
- 专注完成时弹出随机鼓励语（从预设列表抽取）
- 连续完成 4 个番茄钟后自动进入长休息（15 分钟）

---

### 2.2 学习计划表

**功能描述**

用户可以创建周计划（如"周一 19:00-20:00 数学"），每日首页 Dashboard 展示今日任务清单。完成任务后打勾，系统自动统计完成率。支持 AI 根据错题分布自动建议学习计划。

**用户故事**

- 作为学生，我想制定每周学习计划，合理分配各科目时间
- 作为学生，我想在首页看到今日待办，完成后打勾
- 作为学生，我想让 AI 根据我的错题分布建议下周重点学什么

**前端设计**

```
新增页面：plan
├── 左侧：周视图日历（7 列 x 时间段行），点击空白格创建任务
├── 右侧：任务详情面板（科目 / 时间段 / 备注 / 关联知识点）
├── 顶部：本周完成率进度条 + "AI 建议" 按钮
└── Dashboard 集成：今日任务清单卡片（前 3 条 + "查看全部"链接）
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/plan/week` | 获取本周计划 |
| POST | `/api/plan/task` | 创建任务 |
| PUT | `/api/plan/task/{id}` | 更新任务（标记完成/修改时间） |
| DELETE | `/api/plan/task/{id}` | 删除任务 |
| GET | `/api/plan/today` | 获取今日任务清单 |
| POST | `/api/plan/ai-suggest` | AI 根据错题分布生成建议计划 |

**数据存储**

```python
# data/user/study_plan.json
{
  "tasks": [
    {
      "id": "uuid",
      "subject": "数学",
      "weekday": 1,          # 0=周日, 1=周一
      "start_time": "19:00",
      "end_time": "20:00",
      "title": "复习一元二次方程",
      "knowledge_points": ["一元二次方程", "韦达定理"],
      "completed": false,
      "created_at": "2026-06-27T10:00:00"
    }
  ]
}
```

**AI 建议逻辑**

```
1. 从错题本统计各科目错误次数 Top 5 知识点
2. 从答疑历史统计高频提问知识点
3. 组合生成 prompt → LLM 输出 JSON 格式的周计划建议
4. 前端展示建议列表，用户可一键采纳
```

---

### 2.3 考试倒计时

**功能描述**

用户设置考试日期和科目（如期中考试、期末考试），首页 Dashboard 顶部展示大字倒计时。关联该科目的复习进度条，考前 7 天自动提醒生成冲刺计划。

**用户故事**

- 作为学生，我想在首页看到距离期末考试还有几天
- 作为学生，我想看到各科目复习进度，知道哪些还没复习完
- 作为学生，我想在考前一周收到提醒，自动生成冲刺计划

**前端设计**

```
Dashboard 顶部新增组件：exam-countdown
├── 大号倒计时数字（如 "距离期末考试还有 14 天"）
├── 多考试切换 Tab（期中 / 期末 / 模拟考）
├── 各科目复习进度条（未开始 / 进行中 / 已完成）
└── 考前 7 天：闪烁提醒 + "生成冲刺计划" 按钮
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/exam/list` | 获取所有考试 |
| POST | `/api/exam` | 添加考试 |
| PUT | `/api/exam/{id}` | 更新考试信息 |
| DELETE | `/api/exam/{id}` | 删除考试 |
| PUT | `/api/exam/{id}/progress` | 更新科目复习进度 |

**数据存储**

```python
# data/user/exams.json
{
  "exams": [
    {
      "id": "uuid",
      "name": "期末考试",
      "date": "2026-07-10",
      "subjects": [
        {"subject": "数学", "progress": 0.6},
        {"subject": "语文", "progress": 0.3}
      ]
    }
  ]
}
```

---

## 三、第二类：知识管理系统

### 3.1 知识图谱可视化

**功能描述**

从错题和答疑历史中自动提取知识点，按科目构建知识点关联图。节点大小表示出题频率，颜色表示掌握程度（红色=薄弱、黄色=一般、绿色=熟练）。点击节点可查看相关错题和答疑记录。

**用户故事**

- 作为学生，我想一眼看到哪个知识点最薄弱（红色节点最大）
- 作为学生，我想点击知识点节点，查看相关错题列表
- 作为学生，我想对比上次的知识图谱，看到自己的进步

**前端设计**

```
新增页面：knowledge-graph
├── 顶部：科目选择器 + 时间范围（近 30 天 / 全部）
├── 主区域：ECharts 力导向图（force graph）
│   ├── 节点：圆圈，大小=出题频率，颜色=掌握程度
│   ├── 连线：知识点之间的关联（同章节/同题目共现）
│   └── 交互：点击节点 → 右侧滑出详情面板（相关错题 / 答疑记录 / 讲解链接）
├── 右侧：图例 + 统计摘要（薄弱知识点 N 个 / 熟练 N 个）
└── 底部：时间轴滑块，拖动查看历史快照对比
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/knowledge/graph?subject=&days=` | 获取知识图谱数据 |
| GET | `/api/knowledge/graph/history` | 获取历史快照列表 |
| GET | `/api/knowledge/node/{kp_id}/details` | 获取知识点详情（相关错题/答疑） |

**图谱构建逻辑**

```python
# src/services/knowledge_graph.py

def build_graph(subject: str, days: int = 30) -> dict:
    """
    1. 从错题本提取该科目所有错题的知识点标签
    2. 从答疑历史提取该科目的提问知识点
    3. 统计每个知识点出现次数 → 节点大小
    4. 统计每个知识点的正确率 → 节点颜色
       - 正确率 < 40% → 红色 (c-coral-600)
       - 40% ~ 70% → 黄色 (c-amber-400)
       - > 70% → 绿色 (c-teal-600)
    5. 同一题目中出现的知识点之间建立连线
    6. 返回 {nodes: [...], links: [...]}
    """
```

**技术要点**

- 后端使用 `collections.Counter` 统计知识点频次
- 前端使用 ECharts `graph` 图表类型，`layout: 'force'`
- 图谱数据缓存到 `data/user/knowledge_graph_cache.json`，每日更新

---

### 3.2 Markdown 笔记本

**功能描述**

按科目/章节创建笔记，支持 Markdown 编辑和 LaTeX 公式渲染（MathJax）。支持从答疑对话一键保存为笔记，笔记间可双向链接。全文搜索功能。

**用户故事**

- 作为学生，我想在答疑后把重要知识点保存为笔记
- 作为学生，我想按科目和章节整理笔记，方便复习时查找
- 作为学生，我想在笔记中插入数学公式，理科笔记更清晰

**前端设计**

```
新增页面：notes
├── 左侧栏：笔记目录树（科目 > 章节 > 笔记），支持拖拽排序
├── 中间：Markdown 编辑器（分屏预览）
│   ├── 工具栏：加粗/斜体/标题/列表/公式/代码块/图片
│   ├── 编辑区：textarea + 行号
│   └── 预览区：marked.js 渲染 + MathJax 公式
├── 右侧：笔记信息面板（创建时间 / 修改时间 / 标签 / 双向链接）
└── 顶部：全文搜索框
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/notes` | 获取笔记列表（支持按科目/章节过滤） |
| POST | `/api/notes` | 创建笔记 |
| PUT | `/api/notes/{id}` | 更新笔记内容 |
| DELETE | `/api/notes/{id}` | 删除笔记 |
| GET | `/api/notes/search?q=` | 全文搜索 |
| POST | `/api/notes/from-chat` | 从答疑对话保存为笔记 |

**数据存储**

```python
# data/user/notes.json
{
  "notes": [
    {
      "id": "uuid",
      "title": "一元二次方程的解法",
      "subject": "数学",
      "chapter": "第三章",
      "content": "## 公式法\n\n$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$\n\n...",
      "tags": ["公式法", "配方法", "因式分解"],
      "links": ["note_id_2", "note_id_3"],   # 双向链接
      "source": "manual",                      # manual / from_chat
      "source_chat_id": null,
      "created_at": "2026-06-27T10:00:00",
      "updated_at": "2026-06-27T10:30:00"
    }
  ]
}
```

**前端依赖**

```html
<!-- 在 index.html 中引入 -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

---

### 3.3 AI 思维导图生成

**功能描述**

用户输入一个主题（如"光合作用"），AI 自动生成知识结构思维导图。支持从知识库 RAG 结果增强生成，生成后可编辑（拖拽调整、添加/删除子节点），可导出为图片。

**用户故事**

- 作为学生，我想输入一个知识点主题，AI 帮我生成完整的思维导图
- 作为学生，我想在导图上手动添加节点，补充自己的理解
- 作为学生，我想把思维导图导出为图片，打印贴在书桌前

**前端设计**

```
新增页面：mindmap
├── 顶部：主题输入框 + "生成" 按钮 + "RAG 增强" 开关
├── 主区域：思维导图画布（markmap 或自定义 SVG 树）
│   ├── 根节点居中，子节点向外辐射
│   ├── 双击节点：编辑文字
│   ├── 右键节点：添加子节点 / 删除 / 标记重点
│   └── 拖拽：调整节点位置
└── 底部：导出按钮（PNG / SVG / Markdown 大纲）
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/mindmap/generate` | AI 生成思维导图，参数：`{topic, use_rag, subject}` |
| GET | `/api/mindmap/list` | 获取已保存的思维导图列表 |
| POST | `/api/mindmap` | 保存思维导图 |
| PUT | `/api/mindmap/{id}` | 更新思维导图 |
| DELETE | `/api/mindmap/{id}` | 删除思维导图 |

**AI 生成逻辑**

```python
# src/agents/mindmap/generator.py

async def generate_mindmap(topic: str, use_rag: bool, subject: str) -> dict:
    """
    1. 如果 use_rag=True，先用 topic 检索知识库获取相关教材内容
    2. 构造 prompt：
       "请为主题「{topic}」生成知识结构思维导图，
        按 JSON 格式输出：{title, children: [{title, children: [...]}]}
        最多 3 层深度，每个节点最多 5 个子节点。"
    3. 调用 LLM → 解析 JSON → 返回前端
    4. 前端使用 markmap 渲染
    """
```

**前端依赖**

```html
<script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.16/markmap-autoloader.min.js"></script>
```

---

## 四、第三类：AI 能力增强

### 4.1 智能复习计划（艾宾浩斯遗忘曲线）⭐ P0 重点推荐

**功能描述**

基于错题本数据（知识点 + 错误次数 + 上次复习时间），使用艾宾浩斯遗忘曲线计算每个知识点的复习优先级。每天自动生成"今日复习清单"，复习后通过小测验验证掌握程度并更新掌握度。

**核心算法**

```
遗忘曲线公式：R = e^(-t/S)
  R = 记忆保留率 (0~1)
  t = 距上次复习的天数
  S = 记忆强度 (初始=1, 每次正确复习 *1.6, 错误 *0.8)

复习优先级 = (1 - R) * 错误次数权重 * 知识点重要性
  → 优先级越高，越需要今天复习
```

**用户故事**

- 作为学生，我想每天打开 App 就看到"今天该复习什么"，不用自己想
- 作为学生，我想通过翻卡模式复习错题，正面题目反面答案
- 作为学生，我想看到每个知识点的掌握度曲线，知道哪些已经巩固了

**前端设计**

```
新增页面：review
├── 今日复习清单（卡片列表）
│   ├── 每张卡片：知识点名称 + 错误次数 + 上次复习时间 + 预计遗忘率
│   └── 点击"开始复习" → 进入翻卡模式
├── 翻卡模式（全屏）
│   ├── 正面：题目 + 知识点标签
│   ├── 点击翻转 → 反面：答案 + 解析 + 相关讲解链接
│   ├── 底部：自评按钮（记得 / 模糊 / 忘了）
│   └── 自评结果更新记忆强度 S
├── 掌握度曲线（折线图）：各知识点的 R 值随时间变化
└── 复习统计：今日已复习 N 个 / 待复习 M 个 / 连续复习 N 天
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/review/today` | 获取今日复习清单 |
| POST | `/api/review/session` | 开始复习会话 |
| POST | `/api/review/session/{id}/result` | 提交复习结果（记得/模糊/忘了） |
| GET | `/api/review/stats` | 复习统计（连续天数 / 累计复习 / 掌握度分布） |
| GET | `/api/review/mastery-curve?kp_id=` | 单个知识点掌握度曲线 |

**数据存储**

```python
# data/user/review_memory.json
{
  "knowledge_points": {
    "一元二次方程": {
      "error_count": 3,
      "last_reviewed": "2026-06-25",
      "memory_strength": 2.56,     # S 值
      "review_history": [
        {"date": "2026-06-20", "result": "forgot", "s_before": 1.0, "s_after": 0.8},
        {"date": "2026-06-22", "result": "vague", "s_before": 0.8, "s_after": 1.28},
        {"date": "2026-06-25", "result": "remembered", "s_before": 1.28, "s_after": 2.56}
      ]
    },
    "光合作用": { ... }
  },
  "sessions": [
    {
      "id": "uuid",
      "date": "2026-06-27",
      "items": ["一元二次方程", "光合作用"],
      "completed": 2,
      "results": [...]
    }
  ]
}
```

**与现有错题本的联动**

```
错题本新增/删除错题 → 自动更新 review_memory.json 中对应知识点的 error_count
  → error_count 增加 → 复习优先级提高 → 更容易出现在今日清单中

复习完成且连续 3 次"记得" → 该知识点标记为"已掌握"
  → 从复习队列中移除（但仍保留在错题本中作为记录）
```

**定时任务**

```python
# 每日凌晨 2:00 计算当日复习清单
# src/services/review_scheduler.py

@scheduler.scheduled_job("cron", hour=2)
async def generate_daily_review():
    """
    遍历所有知识点，计算 R = e^(-t/S)
    筛选 R < 0.5 的知识点进入今日清单
    按 (1-R) * error_count 排序
    """
```

---

### 4.2 AI 作文批改

**功能描述**

用户输入或粘贴中/英文作文，AI 从立意、结构、语言、卷面四个维度打分（各 25 分），逐段批注，给出修改版和范文对比。支持历年中考满分作文库对比。

**用户故事**

- 作为学生，我想写完作文后让 AI 帮我打分和批注
- 作为学生，我想看到 AI 给出的修改版，对比学习
- 作为学生，我想看到同主题的满分范文，学习借鉴

**前端设计**

```
新增页面：essay
├── 左侧：作文输入区
│   ├── 体裁选择（记叙文 / 议论文 / 说明文 / 英语作文）
│   ├── 题目输入框
│   └── 正文 textarea（字数统计）
├── 右侧：批改结果区
│   ├── 总分大字显示（如 78/100）+ 四维度雷达图
│   ├── 逐段批注（原文 + 红色批注 + 修改建议）
│   ├── AI 修改版（全文重写）
│   └── 范文推荐（同主题/同体裁的中考满分作文）
└── 底部：历史批改记录列表
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/essay/grade` | 提交作文批改 |
| GET | `/api/essay/history` | 批改历史列表 |
| GET | `/api/essay/{id}` | 查看批改详情 |

**AI Prompt 设计**

```python
# src/agents/essay/grader.py

ESSAY_GRADE_PROMPT = """
你是一位资深的初中语文/英语老师，请批改以下{language}作文。

## 评分维度（每项 25 分，总分 100）
1. **立意**：主题是否明确、深刻、有新意
2. **结构**：层次是否清晰、过渡是否自然、首尾是否呼应
3. **语言**：用词是否准确、句式是否多样、是否有文采
4. **卷面**：字数是否达标、是否有错别字/语法错误

## 输出格式（严格 JSON）
{
  "scores": {"theme": 20, "structure": 18, "language": 22, "presentation": 23},
  "total": 83,
  "paragraphs": [
    {"original": "原文段落", "comments": "批注内容", "revised": "修改后段落"}
  ],
  "overall_comment": "总体评价",
  "revised_full": "AI 修改版全文",
  "highlights": ["好词好句1", "好词好句2"]
}

## 作文信息
- 体裁：{genre}
- 题目：{title}
- 正文：{content}
"""
```

**数据存储**

```python
# data/user/essay_records.json
{
  "records": [
    {
      "id": "uuid",
      "language": "chinese",     # chinese / english
      "genre": "记叙文",
      "title": "那一次，我长大了",
      "content": "原文...",
      "result": { ... },          # AI 返回的完整 JSON
      "created_at": "2026-06-27T15:00:00"
    }
  ]
}
```

---

### 4.3 英语口语练习

**功能描述**

系统出示句子或短文，用户通过浏览器麦克风朗读，Web Speech API 进行语音识别，将识别结果与原文对比，逐词评分并给出纠音建议。

**用户故事**

- 作为学生，我想练习英语朗读，获得发音评分
- 作为学生，我想知道哪个单词发音不准，获得纠正建议
- 作为学生，我想看到口语流利度曲线，跟踪进步

**前端设计**

```
新增页面：speaking
├── 顶部：难度选择（七年级 / 八年级 / 九年级）+ 体裁（单词 / 句子 / 短文）
├── 中间：语料展示区（高亮当前朗读位置）+ 录音波形动画
├── 下方：评分面板
│   ├── 总分（流利度 + 准确度 + 完整度）
│   ├── 逐词标注（绿色=正确 / 红色=错误 / 黄色=模糊）
│   └── 纠音建议（音标 + 正确发音示例）
└── 底部：历史练习记录 + 流利度趋势曲线
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/speaking/materials?level=&type=` | 获取朗读素材 |
| POST | `/api/speaking/evaluate` | 提交识别结果，后端计算评分 |
| GET | `/api/speaking/history` | 练习历史 |
| GET | `/api/speaking/stats` | 流利度趋势 |

**前端核心代码**

```javascript
// 语音识别（浏览器端完成）
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.continuous = true;
recognition.interimResults = true;

recognition.onresult = (event) => {
  // 逐词对比原文，计算相似度
  // 相似度 > 80% → 绿色
  // 50% ~ 80% → 黄色
  // < 50% → 红色
};
```

---

## 五、第四类：游戏化激励系统

### 5.1 成就徽章墙

**功能描述**

定义成就规则（如"连续打卡 7 天""累计批改 50 份作业""攻克 10 个薄弱知识点"），满足条件自动解锁徽章。徽章分普通/稀有/史诗三个等级，可分享。

**成就规则定义**

| 成就名 | 条件 | 等级 | 图标 |
|--------|------|------|------|
| 初次批改 | 完成第一次作业批改 | 普通 | 铅笔 |
| 勤奋学子 | 连续学习 7 天 | 普通 | 日历 |
| 错题猎手 | 累计收藏 50 道错题 | 普通 | 猎枪 |
| 坚持不懈 | 连续学习 30 天 | 稀有 | 盾牌 |
| 批改达人 | 累计批改 50 份作业 | 稀有 | 勋章 |
| 知识攻克者 | 掌握 10 个薄弱知识点 | 稀有 | 旗帜 |
| 学霸之路 | 累计学习 100 小时 | 史诗 | 皇冠 |
| 全科精通 | 所有科目均有批改记录 | 史诗 | 星辰 |
| 满分作文 | 作文批改获得 95+ 分 | 史诗 | 羽毛笔 |

**前端设计**

```
新增页面：achievements
├── 顶部：已解锁数 / 总数 + 完成度进度条
├── 徽章网格（3 列）
│   ├── 已解锁：彩色徽章 + 解锁日期 + 光效动画
│   ├── 未解锁：灰色徽章 + "???" + 条件提示
│   └── 点击：弹出详情卡片（成就描述 / 解锁条件 / 获得时间）
└── 最近解锁（横向滚动，最近 5 个）
```

**后端逻辑**

```python
# src/services/achievement_checker.py

# 成就检查在以下事件后触发：
# - 作业批改完成 → 检查"初次批改""批改达人"
# - 每日打卡 → 检查"勤奋学子""坚持不懈"
# - 错题入库 → 检查"错题猎手"
# - 复习完成 → 检查"知识攻克者"
# - 作文批改 → 检查"满分作文"

ACHIEVEMENT_RULES = [
    {"id": "first_grade", "name": "初次批改", "condition": lambda s: s["homework_count"] >= 1, "rarity": "common"},
    {"id": "streak_7", "name": "勤奋学子", "condition": lambda s: s["streak_days"] >= 7, "rarity": "common"},
    {"id": "streak_30", "name": "坚持不懈", "condition": lambda s: s["streak_days"] >= 30, "rarity": "rare"},
    # ...
]
```

---

### 5.2 成长树

**功能描述**

Dashboard 角落展示一棵成长树，每日学习时长 = 浇水，错题攻克 = 施肥。随累计学习量升级：种子 → 幼苗 → 小树 → 大树 → 开花 → 结果。不同科目可养不同花色的树。

**成长阶段**

| 阶段 | 累计学习时长 | 树的形态 |
|------|-------------|----------|
| 种子 | 0 ~ 2h | 一颗种子埋在土里 |
| 发芽 | 2 ~ 5h | 冒出两片小叶 |
| 幼苗 | 5 ~ 15h | 细茎几片叶子 |
| 小树 | 15 ~ 40h | 树干 + 树冠 |
| 大树 | 40 ~ 100h | 茂盛大树 |
| 开花 | 100 ~ 200h | 大树 + 花朵 |
| 结果 | 200h+ | 大树 + 果实 |

**前端设计**

```
Dashboard 右下角：成长树组件
├── SVG 绘制的树（根据阶段切换不同 SVG）
├── 当前阶段名 + 距下一阶段进度条
├── 今日浇水次数（专注钟/学习计划完成时自动浇水）
├── 悬浮提示："再学 3h 就能长出更多叶子！"
└── 点击树 → 弹出成长历史时间轴
```

**技术方案**

- 纯前端 SVG + CSS 动画，无需额外后端接口
- 读取现有 pomodoro + plan + homework 的完成数据计算累计学习时长
- SVG 树的各阶段提前设计好，通过 CSS `display` 切换

---

### 5.3 每日打卡热力图

**功能描述**

每天完成任意学习任务（批改作业/答疑/出题/复习）后自动打卡。连续天数计数，日历热力图展示（参考 GitHub contribution graph）。7 天 / 30 天 / 100 天里程碑提醒。

**前端设计**

```
新增页面：check-in（或 Dashboard 子组件）
├── 大号连续天数数字 + "今日已打卡" 对勾
├── 日历热力图（近 90 天）
│   ├── 颜色深浅 = 当日学习强度（0 任务 = 灰色，1-2 = 浅绿，3+ = 深绿）
│   ├── 鼠标悬浮：显示日期 + 完成任务数
│   └── 里程碑标注（7 天 / 30 天 / 100 天）
├── 里程碑成就列表（已达成 / 未达成）
└── 补卡机制：看一段广告或完成 3 道题可补前一天打卡
```

**数据来源**

```python
# 不需要新增存储，从现有数据计算：
# - homework 批改记录 → 有记录 = 当天活跃
# - explain 答疑记录 → 有记录 = 当天活跃
# - review 复习记录 → 有记录 = 当天活跃
# - pomodoro 专注记录 → 有记录 = 当天活跃
# 以上任意一个有记录即判定当天已打卡
```

---

## 六、第五类：实用学科工具

### 5.1 智能单词本

**功能描述**

在答疑/错题/阅读中遇到的生词可一键收藏到单词本，按艾宾浩斯间隔复习。支持三种测验模式：英译中、中译英、听写。支持导入/导出。

**用户故事**

- 作为学生，我想在答疑时遇到不认识的单词一键收藏
- 作为学生，我想每天用翻卡模式复习收藏的单词
- 作为学生，我想导出单词列表打印出来背

**前端设计**

```
新增页面：vocabulary
├── 标签页 1：单词列表
│   ├── 搜索框 + 科目/标签过滤
│   ├── 单词卡片列表（单词 / 音标 / 释义 / 例句 / 收藏时间 / 下次复习日期）
│   └── 批量操作（导出 CSV / 删除 / 移入已掌握）
├── 标签页 2：复习模式
│   ├── 翻卡界面（正面：单词，反面：音标+释义+例句）
│   ├── 自评按钮（认识 / 模糊 / 不认识）
│   └── 复习完成统计
├── 标签页 3：测验模式
│   ├── 英译中（给英文选中文）
│   ├── 中译英（给中文填英文）
│   └── 听写（播放发音，拼写单词）
└── 侧边栏：导入/导出按钮
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/vocabulary` | 单词列表（支持分页/筛选） |
| POST | `/api/vocabulary` | 添加单词 |
| PUT | `/api/vocabulary/{id}` | 更新单词信息 |
| DELETE | `/api/vocabulary/{id}` | 删除单词 |
| GET | `/api/vocabulary/review` | 获取今日待复习单词 |
| POST | `/api/vocabulary/review/result` | 提交复习结果 |
| GET | `/api/vocabulary/export` | 导出 CSV |
| POST | `/api/vocabulary/import` | 导入 CSV |

**数据存储**

```python
# data/user/vocabulary.json
{
  "words": [
    {
      "id": "uuid",
      "word": "photosynthesis",
      "phonetic": "/ˌfoʊtəˈsɪnθəsɪs/",
      "meaning": "光合作用",
      "example": "Plants use photosynthesis to convert sunlight into energy.",
      "subject": "生物",
      "source": "chat",             # chat / homework / manual
      "source_id": "explain_session_xxx",
      "memory_strength": 1.6,
      "last_reviewed": "2026-06-25",
      "next_review": "2026-06-28",  # 根据 S 值计算
      "status": "learning",         # learning / mastered
      "added_at": "2026-06-20T10:00:00"
    }
  ]
}
```

**与现有功能的联动**

```
答疑页面 → 选中文字 → 右键菜单"添加到单词本"
  → 调用 LLM 快速获取音标+释义+例句
  → 存入 vocabulary.json

错题页面 → 题目中的生词 → 点击单词 → 弹出"收藏到单词本"
```

---

### 5.2 公式速查手册

**功能描述**

按科目/章节分类整理初中常用公式，每个公式配适用场景说明和例题链接。支持搜索和收藏常用公式。考前速记模式随机展示公式卡片。

**前端设计**

```
新增页面：formulas
├── 左侧：科目/章节目录树
├── 右侧：公式卡片网格
│   ├── 公式名 + LaTeX 渲染的公式
│   ├── 适用场景说明
│   ├── 例题链接（跳转到出题页面，用该知识点出题）
│   └── 收藏星标
├── 顶部：搜索框 + "速记模式" 按钮
└── 速记模式：全屏翻卡（正面公式，背面说明+例题）
```

**数据来源**

```python
# data/formulas/math.json, physics.json, chemistry.json
{
  "chapters": [
    {
      "name": "一元二次方程",
      "formulas": [
        {
          "id": "f001",
          "name": "求根公式",
          "latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
          "description": "适用于所有一元二次方程 ax² + bx + c = 0 (a≠0)",
          "conditions": "判别式 Δ = b² - 4ac ≥ 0",
          "example_topic": "一元二次方程"
        }
      ]
    }
  ]
}
```

---

### 5.3 古诗文背诵默写

**功能描述**

选择必背篇目，进入填空默写模式（随机挖空关键字），AI 判断对错，标注易错字。背诵进度打卡，支持音频朗读跟背和诗词赏析卡片。

**用户故事**

- 作为学生，我想用填空默写模式练习古诗背诵
- 作为学生，我想知道哪些字容易写错，重点记忆
- 作为学生，我想听到标准朗读，跟着背诵

**前端设计**

```
新增页面：recitation
├── 标签页 1：篇目列表
│   ├── 按年级/朝代/类型（诗/词/文）分类
│   ├── 每篇：标题 + 作者 + 背诵进度 + "开始默写" 按钮
│   └── 搜索框
├── 标签页 2：默写模式（全屏）
│   ├── 原文展示（部分字挖空为输入框）
│   ├── 输入完成 → 点击"提交" → AI 判断对错
│   ├── 错误字标红 + 显示正确字 + 易错字提示
│   └── 默写完成 → 更新背诵进度
├── 标签页 3：赏析卡片
│   ├── 诗词全文 + 译文 + 赏析
│   └── 朗读按钮（TTS）
└── 侧边栏：背诵日历（已背诵篇目打勾）
```

**数据来源**

```python
# data/classical_poems/poems.json
{
  "poems": [
    {
      "id": "p001",
      "title": "静夜思",
      "author": "李白",
      "dynasty": "唐",
      "grade": 7,
      "type": "诗",
      "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
      "translation": "明亮的月光洒在床前的窗户纸上...",
      "analysis": "这首诗写的是在寂静的月夜思念家乡...",
      "error_prone_chars": ["疑", "霜", "举"]  # 易错字
    }
  ]
}
```

---

## 七、第六类：多模态与外部集成

### 7.1 语音朗读 TTS

**功能描述**

在题目/解析/知识点页面添加"朗读"按钮，调用浏览器 SpeechSynthesis API 朗读文本。支持语速调节、暂停/继续、中英文切换。

**前端设计**

```javascript
// 在所有内容展示区域添加朗读按钮
// 复用为全局组件：tts-button

class TTSButton {
  constructor(text) {
    this.utterance = new SpeechSynthesisUtterance(text);
    this.utterance.lang = /[\u4e00-\u9fa5]/.test(text) ? 'zh-CN' : 'en-US';
    this.utterance.rate = 1.0;  // 语速 0.5 ~ 2.0
  }

  play() { speechSynthesis.speak(this.utterance); }
  pause() { speechSynthesis.pause(); }
  resume() { speechSynthesis.resume(); }
  setRate(rate) { this.utterance.rate = rate; }
}
```

```
朗读按钮 UI：
├── 播放/暂停按钮（图标切换）
├── 语速滑块（0.5x ~ 2.0x）
├── 进度条（当前朗读位置高亮）
└── "睡前模式"：连续朗读多篇 + 定时停止
```

**技术要点**

- 纯前端实现，零后端成本
- 中文使用浏览器内置中文语音引擎
- 英文使用 en-US 语音引擎
- 自动检测文本语言（正则匹配中文字符）

---

### 7.2 手写公式识别

**功能描述**

拍照上传手写数学/物理公式，通过多模态 LLM（GPT-4o / Gemini）识别为 LaTeX，渲染为标准公式，可直接求解或请求 AI 讲解。

**用户故事**

- 作为学生，我想拍下手写公式让 AI 识别并求解
- 作为学生，我想把识别出的公式发给 AI 讲解解题步骤
- 作为学生，我想保存常用公式到公式手册

**前端设计**

```
在答疑页面增加"手写公式"入口：
├── 上传图片 / 拍照
├── 识别中 → loading 动画
├── 识别结果：
│   ├── LaTeX 渲染的公式（KaTeX）
│   ├── "求解" 按钮 → 发送给 AI 求解
│   ├── "讲解" 按钮 → 发送给 AI 讲解
│   └── "收藏" 按钮 → 存入公式手册
└── 识别历史列表
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/formula/recognize` | 上传图片，返回 LaTeX |
| POST | `/api/formula/solve` | 发送 LaTeX，AI 求解 |
| POST | `/api/formula/explain` | 发送 LaTeX，AI 讲解 |

**后端逻辑**

```python
# src/services/formula/recognizer.py

async def recognize_formula(image_base64: str) -> dict:
    """
    方案 A：调用多模态 LLM
    - 将图片作为 vision input 发送给 GPT-4o / Gemini
    - Prompt: "请将图片中的手写数学公式转换为 LaTeX 格式，只输出 LaTeX 代码。"
    
    方案 B：接入 MathPix API（精度更高但需付费）
    - POST https://api.mathpix.com/v3/text
    - 返回 LaTeX
    """
```

---

### 7.3 视频讲解推荐

**功能描述**

根据错题涉及的知识点，自动搜索 B 站教学视频，按相关度 + 播放量排序。可在页内嵌入播放或跳转，支持收藏和标记"已看完"。

**用户故事**

- 作为学生，我想在错题页面看到相关教学视频推荐
- 作为学生，我想在页内直接播放视频，不用跳转到 B 站
- 作为学生，我想标记已看完的视频，避免重复推荐

**前端设计**

```
错题详情页新增组件：video-recommendations
├── "相关教学视频" 标题
├── 视频卡片列表（最多 5 个）
│   ├── 缩略图 + 标题 + UP 主 + 播放量
│   ├── "播放" 按钮 → 弹出 iframe 播放器
│   ├── "收藏" 按钮
│   └── "已看完" 勾选
└── 已收藏视频列表（独立页面或侧边栏）
```

**后端 API**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/video/search?keyword=` | 搜索 B 站教学视频 |
| GET | `/api/video/recommend?kp=` | 根据知识点推荐视频 |
| POST | `/api/video/favorite` | 收藏视频 |
| PUT | `/api/video/{id}/watched` | 标记已看完 |

**后端逻辑**

```python
# src/services/video/bilibili.py

async def search_videos(keyword: str, limit: int = 5) -> list:
    """
    调用 B 站搜索 API（或使用爬虫）
    URL: https://api.bilibili.com/x/web-interface/search/type
    参数：keyword, search_type=video, order=click（按播放量排序）
    
    过滤规则：
    - 标题包含 keyword 或相关学科关键词
    - 时长 > 3 分钟（排除短视频）
    - 优先选择教育类 UP 主
    """
```

---

## 八、数据库变更汇总

所有新功能均复用现有 JSON 文件存储模式（`data/user/` 目录），无需引入新数据库。

| 文件路径 | 功能 | 说明 |
|----------|------|------|
| `data/user/pomodoro_sessions.json` | 番茄钟 | 专注会话记录 |
| `data/user/study_plan.json` | 学习计划表 | 周计划任务 |
| `data/user/exams.json` | 考试倒计时 | 考试日期和复习进度 |
| `data/user/notes.json` | 笔记本 | Markdown 笔记 |
| `data/user/mindmaps.json` | 思维导图 | 保存的思维导图 |
| `data/user/review_memory.json` | 智能复习计划 | 知识点记忆状态 |
| `data/user/essay_records.json` | 作文批改 | 作文和批改结果 |
| `data/user/speaking_records.json` | 口语练习 | 练习记录 |
| `data/user/achievements.json` | 成就系统 | 解锁记录 |
| `data/user/check_in.json` | 每日打卡 | 打卡记录 |
| `data/user/vocabulary.json` | 单词本 | 单词和复习状态 |
| `data/formulas/math.json` | 公式手册 | 数学公式 |
| `data/formulas/physics.json` | 公式手册 | 物理公式 |
| `data/formulas/chemistry.json` | 公式手册 | 化学公式 |
| `data/classical_poems/poems.json` | 古诗文 | 必背篇目数据库 |
| `data/user/video_favorites.json` | 视频收藏 | 收藏的 B 站视频 |
| `data/user/knowledge_graph_cache.json` | 知识图谱 | 图谱缓存（每日更新） |

---

## 九、API 路由变更汇总

新增路由文件均放在 `src/api/routers/` 目录下。

| 路由文件 | 前缀 | 功能 |
|----------|------|------|
| `pomodoro.py` | `/api/pomodoro` | 番茄钟 |
| `plan.py` | `/api/plan` | 学习计划表 |
| `exam.py` | `/api/exam` | 考试倒计时 |
| `notes.py` | `/api/notes` | 笔记本 |
| `mindmap.py` | `/api/mindmap` | 思维导图 |
| `review.py` | `/api/review` | 智能复习计划 |
| `essay.py` | `/api/essay` | 作文批改 |
| `speaking.py` | `/api/speaking` | 口语练习 |
| `achievement.py` | `/api/achievements` | 成就系统 |
| `vocabulary.py` | `/api/vocabulary` | 单词本 |
| `formula.py` | `/api/formula` | 公式识别 |
| `video.py` | `/api/video` | 视频推荐 |
| `knowledge_graph.py` | `/api/knowledge` | 知识图谱 |
| `recitation.py` | `/api/recitation` | 古诗文背诵 |

在 `src/api/routers/__init__.py` 中注册：

```python
from . import (
    pomodoro, plan, exam, notes, mindmap, review,
    essay, speaking, achievement, vocabulary, formula,
    video, knowledge_graph, recitation
)
```

---

## 十、前端页面变更汇总

在 `web/index.html` 的侧边栏导航中新增以下页面入口：

```javascript
// Alpine.js 导航配置新增
{ id: 'review',    label: '智能复习', icon: 'rotate' },
{ id: 'essay',     label: '作文批改', icon: 'pen' },
{ id: 'vocabulary',label: '单词本',   icon: 'book' },
{ id: 'pomodoro',  label: '专注钟',   icon: 'clock' },
{ id: 'plan',      label: '计划表',   icon: 'calendar' },
{ id: 'notes',     label: '笔记本',   icon: 'note' },
{ id: 'mindmap',   label: '思维导图', icon: 'tree' },
{ id: 'knowledge-graph', label: '知识图谱', icon: 'graph' },
{ id: 'achievements', label: '成就墙', icon: 'medal' },
{ id: 'speaking',  label: '口语练习', icon: 'mic' },
{ id: 'formulas',  label: '公式手册', icon: 'function' },
{ id: 'recitation',label: '古诗背诵', icon: 'scroll' },
```

Dashboard 新增组件：

| 组件 | 位置 | 关联功能 |
|------|------|----------|
| 考试倒计时 | 顶部横幅 | 考试倒计时 |
| 今日复习清单 | 主区域卡片 | 智能复习计划 |
| 今日任务清单 | 主区域卡片 | 学习计划表 |
| 成长树 | 右下角浮动 | 成长树 |
| 打卡热力图 | 侧边卡片 | 每日打卡 |
| 本周专注统计 | 侧边卡片 | 番茄专注钟 |

---

## 十一、实施路线图

### Phase 1：核心价值闭环（第 1-2 周）

> 目标：用最小投入补齐"学 → 练 → 改 → 复习"闭环中最薄弱的"复习"环节

| 序号 | 功能 | 工作量 | 说明 |
|------|------|--------|------|
| 1 | 智能复习计划 | 3-4 天 | P0，与错题本联动，遗忘曲线算法 |
| 2 | AI 作文批改 | 2-3 天 | P0，复用 LLM，设计 prompt 即可 |
| 3 | 智能单词本 | 2-3 天 | P0，基础 CRUD + 翻卡复习 |
| 4 | 每日打卡热力图 | 1 天 | P1，从现有数据计算，纯前端 |

### Phase 2：学习体验增强（第 3-4 周）

> 目标：提升学习效率和知识管理能力

| 序号 | 功能 | 工作量 | 说明 |
|------|------|--------|------|
| 5 | 番茄专注钟 | 2 天 | 前端为主，后端记录会话 |
| 6 | 学习计划表 | 2-3 天 | CRUD + Dashboard 集成 |
| 7 | 成就徽章墙 | 2-3 天 | 规则引擎 + 前端展示 |
| 8 | 语音朗读 TTS | 0.5 天 | 纯前端，半天搞定 |
| 9 | 考试倒计时 | 1 天 | 纯前端 + localStorage |

### Phase 3：知识管理深化（第 5-6 周）

> 目标：从"做题工具"升级为"知识管理平台"

| 序号 | 功能 | 工作量 | 说明 |
|------|------|--------|------|
| 10 | Markdown 笔记本 | 3-4 天 | 编辑器 + MathJax + 搜索 |
| 11 | 知识图谱可视化 | 3-4 天 | 后端图构建 + ECharts 渲染 |
| 12 | AI 思维导图 | 2-3 天 | LLM 生成 + markmap 渲染 |
| 13 | 古诗文背诵默写 | 2-3 天 | 语料库 + 填空交互 |

### Phase 4：高阶能力拓展（第 7-8 周）

> 目标：多模态和外部集成

| 序号 | 功能 | 工作量 | 说明 |
|------|------|--------|------|
| 14 | 手写公式识别 | 2-3 天 | 多模态 LLM 识别 |
| 15 | 视频讲解推荐 | 2 天 | B 站 API 搜索 |
| 16 | 公式速查手册 | 1-2 天 | 静态数据 + LaTeX 渲染 |
| 17 | 成长树 | 1-2 天 | SVG 动画 + 数据驱动 |
| 18 | 英语口语练习 | 3-4 天 | Web Speech API + 评分算法 |

### 路线图总览

```
Phase 1 (W1-W2)          Phase 2 (W3-W4)         Phase 3 (W5-W6)        Phase 4 (W7-W8)
┌─────────────────┐      ┌─────────────────┐     ┌─────────────────┐    ┌─────────────────┐
│ 智能复习计划  ★  │      │ 番茄专注钟       │     │ Markdown 笔记本  │    │ 手写公式识别     │
│ AI 作文批改      │      │ 学习计划表       │     │ 知识图谱可视化   │    │ 视频讲解推荐     │
│ 智能单词本       │      │ 成就徽章墙       │     │ AI 思维导图      │    │ 公式速查手册     │
│ 每日打卡热力图   │      │ 语音朗读 TTS     │     │ 古诗文背诵默写   │    │ 成长树           │
│                  │      │ 考试倒计时       │     │                  │    │ 英语口语练习     │
└─────────────────┘      └─────────────────┘     └─────────────────┘    └─────────────────┘
     P0 闭环                效率 + 激励              知识管理               高阶拓展
```

---

## 附录：技术决策说明

### 为什么继续用 JSON 文件而不是 SQLite？

1. 项目现有存储模式就是 JSON 文件（`data/user/` 目录），保持一致性
2. 单用户场景下 JSON 文件读写性能足够
3. 不引入新依赖，降低部署复杂度
4. 数据可读性好，方便调试和手动修改
5. 如果未来需要多用户或高并发，可统一迁移到 SQLite/PostgreSQL

### 为什么前端不拆分组件？

1. 现有架构是 Alpine.js + Tailwind 单文件 SPA，保持风格统一
2. 新增页面通过 Alpine.js `x-show` 控制显隐，无需路由库
3. 如果 `index.html` 超过 3000 行，可考虑拆分为多个 HTML 文件 + JS 模块

### LLM 调用成本控制

| 功能 | LLM 调用频率 | 预估 Token/次 | 成本控制策略 |
|------|-------------|-------------|-------------|
| 智能复习计划 | 每日 1 次 | 0（纯算法） | 无需 LLM |
| AI 作文批改 | 用户触发 | ~2000 | 限制每日 5 次 |
| AI 思维导图 | 用户触发 | ~1500 | 限制每日 10 次 |
| 手写公式识别 | 用户触发 | ~500 | 限制每日 20 次 |
| 学习计划 AI 建议 | 每周 1 次 | ~1000 | 免费额度内 |

---

> 文档结束。如有疑问或需要调整优先级，请直接修改本文档。
