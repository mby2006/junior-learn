"""
Generate Router — 智能出题
=========================

此路由提供 AI 智能出题功能：
  - 自定义模式：从知识库按知识点出题
  - 模拟试卷模式：仿写 PDF 真题风格
  - 仿真卷模式：从历史批改记录出题
  - WebSocket 流式推送生成进度

路由
-----
WS   /api/v1/generate/ws               — WebSocket 连接，流式生成进度
POST /api/v1/generate/custom          — 自定义模式出题
POST /api/v1/generate/mimic-pdf       — 从 PDF 仿写出题
POST /api/v1/generate/mimic-history   — 从历史批改生成仿真卷
GET  /api/v1/generate/history         — 获取出题历史
GET  /api/v1/generate/history/{id}    — 获取某次出题详情
DELETE /api/v1/generate/history/{id}  — 删除出题记录
GET  /api/v1/generate/history-questions — 获取历史批改题目列表（用于仿真卷）
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

# ── Project root ──────────────────────────────────────────────────────────────
_project_root = Path(__file__).resolve().parent.parent.parent.parent
import sys
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.agents.question.coordinator import AgentCoordinator
from src.logging import get_logger
from src.logging.handlers.websocket import LogInterceptor
from src.services.question_bank.service import QuestionBankService

logger = get_logger("GenerateRouter")

router = APIRouter()

# ── 单例（懒加载）──────────────────────────────────────────────────────────────
_question_bank: Optional[QuestionBankService] = None

def get_question_bank() -> QuestionBankService:
    global _question_bank
    if _question_bank is None:
        _question_bank = QuestionBankService(_project_root / "data")
    return _question_bank

# ── 数据存储：出题历史 ───────────────────────────────────────────────────────────
_generation_history_path = _project_root / "data" / "generation_history.json"

def _load_generation_history() -> dict[str, Any]:
    """加载出题历史。"""
    if not _generation_history_path.exists():
        return {"version": 1, "records": []}
    try:
        return json.loads(_generation_history_path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "records": []}

def _save_generation_record(record: dict[str, Any]) -> None:
    """保存出题记录。"""
    data = _load_generation_history()
    data["records"].insert(0, record)  # 新记录插在前面
    _generation_history_path.parent.mkdir(parents=True, exist_ok=True)
    _generation_history_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def _delete_generation_record(record_id: str) -> bool:
    """删除出题记录。"""
    data = _load_generation_history()
    original_len = len(data["records"])
    data["records"] = [r for r in data["records"] if r.get("id") != record_id]
    if len(data["records"]) == original_len:
        return False
    _generation_history_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return True

# ── 请求体定义 ───────────────────────────────────────────────────────────────────

class GenerateCustomRequest(BaseModel):
    """自定义出题请求。"""
    knowledge_point: str = Field(
        description="知识点，例如'一元二次方程'"
    )
    subject: Literal[
        "math", "physics", "chemistry",
        "english", "biology", "history", "chinese",
        "politics", "geography"
    ] = Field(
        default="math",
        description="科目"
    )
    num_questions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="出题数量，1-20"
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="难度：简单/中等/困难"
    )
    question_type: Literal["choice", "fill_blank", "calculation", "proof", "written"] = Field(
        default="choice",
        description="题目类型"
    )
    kb_name: Optional[str] = Field(
        default=None,
        description="知识库名称（教材上传后的ID）"
    )

class GenerateMimicPdfRequest(BaseModel):
    """从 PDF 仿写出题请求。"""
    pdf_id: str = Field(description="PDF 教材 ID")
    num_questions: int = Field(
        default=10,
        ge=1,
        le=30,
        description="出题数量"
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="难度"
    )

class GenerateMimicHistoryRequest(BaseModel):
    """从历史批改生成仿真卷请求。"""
    question_ids: list[str] = Field(
        description="选择的历史题目 ID 列表"
    )
    num_questions: int = Field(
        default=10,
        ge=1,
        le=30,
        description="出题数量"
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="难度"
    )

class HistoryQuestionListResponse(BaseModel):
    """历史题目列表响应（用于仿真卷选择）。"""
    questions: list[dict[str, Any]]
    total: int

# ── HTTP 端点 ─────────────────────────────────────────────────────────────────────

@router.get("/history", summary="获取出题历史")
async def get_generation_history(
    limit: int = 20,
    offset: int = 0,
):
    """获取出题历史列表，按时间倒序排列。"""
    data = _load_generation_history()
    records = data.get("records", [])
    total = len(records)
    paged = records[offset:offset + limit]
    return {
        "success": True,
        "total": total,
        "records": paged,
    }

@router.get("/history/{generation_id}", summary="获取出题详情")
async def get_generation_detail(generation_id: str):
    """获取某次出题的完整详情（包含所有题目）。"""
    data = _load_generation_history()
    for record in data.get("records", []):
        if record.get("id") == generation_id:
            return {"success": True, "record": record}
    raise HTTPException(status_code=404, detail="记录不存在")

@router.delete("/history/{generation_id}", summary="删除出题记录")
async def delete_generation_record(generation_id: str):
    """删除出题记录。"""
    success = _delete_generation_record(generation_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"success": True}

@router.get("/history-questions", summary="获取历史批改题目列表")
async def get_history_questions(
    subject: Optional[str] = None,
    limit: int = 50,
):
    """
    获取历史批改中的题目列表，用于"从历史批改生成仿真卷"功能。
    返回每个题目的基本信息供用户选择。
    """
    bank = get_question_bank()
    # 从 question_bank 中获取所有题目
    all_questions: list[dict] = []
    # 遍历每个科目题库
    data_dir = _project_root / "data" / "question_bank"
    if data_dir.exists():
        for json_file in data_dir.glob("*.json"):
            if subject and json_file.stem != subject:
                continue
            try:
                content = json_file.read_text(encoding="utf-8")
                bank_data = json.loads(content)
                for key, entry in bank_data.get("entries", {}).items():
                    all_questions.append({
                        "id": key,
                        "question_text": entry.get("question_text", ""),
                        "subject": entry.get("subject", json_file.stem),
                        "question_type": entry.get("question_type", "unknown"),
                        "created_at": entry.get("created_at", ""),
                        "hit_count": entry.get("hit_count", 0),
                    })
            except Exception as e:
                logger.warning(f"Failed to read {json_file}: {e}")
                continue
    # 按点击降序，截断到 limit
    all_questions.sort(key=lambda q: q.get("hit_count", 0), reverse=True)
    if subject:
        all_questions = [q for q in all_questions if q["subject"] == subject]
    result = all_questions[:limit]
    return {
        "success": True,
        "questions": result,
        "total": len(all_questions),
    }

# ── WebSocket 端点 ───────────────────────────────────────────────────────────────

@router.websocket("/ws")
async def websocket_generate(websocket: WebSocket):
    """
    WebSocket 连接用于智能出题，流式推送生成进度。

    工作流：
    1. 前端连接后，发送生成参数（mode + 参数）
    2. 后端协调器通过 WebSocket 逐步推送进度和结果
    3. 生成完成后保存到历史，前端可以展示题目卡片
    """
    await websocket.accept()
    logger.info("WebSocket generate connection accepted")

    try:
        # 1. 接收生成参数
        init_message = await websocket.receive_text()
        init_data = json.loads(init_message)
        mode = init_data.get("mode")  # "custom" | "mimic-pdf" | "mimic-history"

        # 2. 准备输出目录
        output_dir = _project_root / "data" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 3. 创建协调器
        kb_name = init_data.get("kb_name")
        coordinator = AgentCoordinator(
            kb_name=kb_name,
            output_dir=str(output_dir),
            language="zh",
        )

        # 4. 设置 WebSocket 回调
        async def ws_update(update_type: str, data: dict[str, Any]):
            await websocket.send_json({"type": update_type, **data})

        coordinator.set_ws_callback(ws_update)

        # 5. 用 LogInterceptor 捕获日志并通过 WebSocket 发送
        queue: asyncio.Queue[str] = asyncio.Queue()

        with LogInterceptor(queue) as interceptor:
            # 根据模式调用不同生成方法
            if mode == "custom":
                # 自定义模式
                requirement = {
                    "knowledge_point": init_data.get("knowledge_point", ""),
                    "difficulty": init_data.get("difficulty", "medium"),
                    "question_type": init_data.get("question_type", "choice"),
                    "subject": init_data.get("subject", "math"),
                }
                num_questions = init_data.get("num_questions", 5)
                result = await coordinator.generate_questions_custom(
                    requirement=requirement,
                    num_questions=num_questions,
                )
            elif mode == "mimic-pdf":
                # TODO: PDF 仿写模式（后续实现，需要提取 PDF 中的题目作为参考）
                # 目前占位，框架已就绪
                await ws_update("error", {"message": "PDF 仿写模式尚未实现"})
                return
            elif mode == "mimic-history":
                # 从历史批改生成 - 每个选中题目作为参考生成新题
                question_ids = init_data.get("question_ids", [])
                if not question_ids:
                    await ws_update("error", {"message": "未选择任何题目"})
                    return

                requirement_base = {
                    "difficulty": init_data.get("difficulty", "medium"),
                    "subject": init_data.get("subject", "math"),
                }

                # 批量生成
                result = {
                    "success": True,
                    "requested": len(question_ids),
                    "completed": 0,
                    "failed": 0,
                    "results": [],
                }

                for qid in question_ids:
                    # 从 question_bank 获取原题
                    bank = get_question_bank()
                    # 需要从对应科目文件中找到这个题
                    # 先尝试从所有题库搜索
                    found = False
                    original_question: Optional[dict] = None
                    data_dir = _project_root / "data" / "question_bank"
                    if data_dir.exists():
                        for json_file in data_dir.glob("*.json"):
                            try:
                                bank_data = json.loads(json_file.read_text(encoding="utf-8"))
                                if qid in bank_data.get("entries", {}):
                                    original_question = bank_data["entries"][qid]
                                    found = True
                                    break
                            except Exception:
                                continue
                    if not found or not original_question:
                        result["failed"] += 1
                        continue

                    # 用原题作为参考生成新题
                    requirement = requirement_base.copy()
                    requirement["reference_question"] = {
                        "question_text": original_question["question_text"],
                        "question_type": original_question["question_type"],
                        "correct_answer": original_question["correct_answer"],
                    }
                    requirement["knowledge_point"] = (
                        f"{original_question['subject']} {original_question['question_text'][:30]}"
                    )

                    single_result = await coordinator.generate_question(requirement=requirement)
                    if single_result.get("success"):
                        result["completed"] += 1
                        result["results"].append({
                            "question_id": f"q_{result['completed']}",
                            "focus": {"focus": f"仿写自历史题目 {qid}"},
                            "question": single_result["question"],
                            "validation": single_result["validation"],
                        })
                    else:
                        result["failed"] += 1

                result["success"] = result["completed"] > 0
            else:
                await ws_update("error", {"message": f"未知模式: {mode}"})
                return

            # 生成完成，保存到历史
            if result.get("success"):
                # 生成记录 ID
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                record_id = f"gen_{timestamp}"

                # 构建保存记录
                record = {
                    "id": record_id,
                    "mode": mode,
                    "created_at": datetime.now().isoformat(),
                    "params": init_data,
                    "summary": {
                        "requested": result.get("requested", 0),
                        "completed": result.get("completed", 0),
                        "failed": result.get("failed", 0),
                    },
                    "questions": [
                        {
                            "question_id": r.get("question_id"),
                            "focus": r.get("focus", {}),
                            "question": r.get("question"),
                            "validation": r.get("validation"),
                        }
                        for r in result.get("results", [])
                    ],
                }
                _save_generation_record(record)
                logger.info(f"Generation saved to history: {record_id}")

                # 发送完成消息（包含完整结果给前端渲染）
                await ws_update("complete", {
                    "generation_id": record_id,
                    "summary": record["summary"],
                    "questions": record["questions"],
                })
            else:
                error_msg = result.get("error", "Generation failed")
                await ws_update("error", {"message": error_msg})

    except WebSocketDisconnect:
        logger.info("WebSocket generate disconnected")
    except Exception as e:
        logger.error(f"WebSocket generate error: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
