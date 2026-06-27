from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.logging import get_logger

router = APIRouter(prefix="/api/v1/reading-materials", tags=["reading-materials"])
logger = get_logger("ReadingMaterialsRouter")

_project_root = Path(__file__).resolve().parent.parent.parent.parent
_data_dir = _project_root / "data"
_materials_dir = _data_dir / "reading_materials"
_META_FILE = _materials_dir / "materials.json"
_MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024


def _load_items() -> list[dict[str, Any]]:
    if not _META_FILE.exists():
        return []
    try:
        data = json.loads(_META_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_items(items: list[dict[str, Any]]) -> None:
    _materials_dir.mkdir(parents=True, exist_ok=True)
    _META_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _find_item(material_id: str) -> dict[str, Any]:
    for item in _load_items():
        if item.get("id") == material_id:
            return item
    raise HTTPException(status_code=404, detail="阅读资料不存在")


@router.get("")
async def list_materials() -> list[dict[str, Any]]:
    items = _load_items()
    for item in items:
        path = _materials_dir / item["filename"]
        item["file_exists"] = path.exists()
        item["file_size_kb"] = round(path.stat().st_size / 1024) if path.exists() else 0
    return items


@router.post("/upload")
async def upload_material(
    name: str = Form(..., description="资料名称"),
    subject: str = Form(default="", description="可选科目"),
    file: UploadFile = File(..., description="阅读资料 PDF 文件"),
) -> dict[str, Any]:
    name = name.strip()
    subject = subject.strip().lower()
    if not name:
        raise HTTPException(status_code=400, detail="资料名称不能为空")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(content) > _MAX_PDF_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="PDF 文件不能超过 50MB，请压缩后再上传")

    _materials_dir.mkdir(parents=True, exist_ok=True)
    material_id = uuid.uuid4().hex
    filename = f"{material_id}.pdf"
    (_materials_dir / filename).write_bytes(content)

    item = {
        "id": material_id,
        "name": name,
        "subject": subject,
        "filename": filename,
        "original_filename": file.filename,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    items = _load_items()
    items.insert(0, item)
    _save_items(items)
    logger.info(f"[ReadingMaterials] 资料已保存: {filename} ({len(content) // 1024} KB)")
    return {"ok": True, "item": item, "message": "阅读资料上传成功"}


@router.get("/file/{material_id}")
async def view_material(material_id: str):
    item = _find_item(material_id)
    path = _materials_dir / item["filename"]
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF 文件不存在")
    filename = f"{item['name']}.pdf"
    filename_encoded = quote(filename, safe="")
    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename*=UTF-8''{filename_encoded}"},
    )


@router.patch("/{material_id}/name")
async def rename_material(material_id: str, name: str = Form(..., description="新的资料名称")) -> dict[str, Any]:
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="名称不能为空")
    items = _load_items()
    for item in items:
        if item.get("id") == material_id:
            item["name"] = name
            _save_items(items)
            return {"ok": True, "id": material_id, "name": name}
    raise HTTPException(status_code=404, detail="阅读资料不存在")


@router.delete("/{material_id}")
async def delete_material(material_id: str) -> dict[str, Any]:
    items = _load_items()
    kept = []
    deleted = None
    for item in items:
        if item.get("id") == material_id:
            deleted = item
        else:
            kept.append(item)
    if deleted is None:
        raise HTTPException(status_code=404, detail="阅读资料不存在")
    path = _materials_dir / deleted["filename"]
    if path.exists():
        path.unlink()
    _save_items(kept)
    return {"ok": True, "id": material_id}
