from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter
from app.models.response import ScriptListResponse, ScriptItem, GalleryResponse, PhotoItem

router = APIRouter(prefix="/content", tags=["内容数据"])

# 模拟讲解脚本列表
MOCK_SCRIPTS = [
    ScriptItem(id=1, title="山东大学堂创办", era="1901", duration="2:30"),
    ScriptItem(id=2, title="齐鲁大学的百年兴衰", era="1917-1952", duration="3:15"),
    ScriptItem(id=3, title="老舍在山大的岁月", era="1930-1934", duration="2:45"),
    ScriptItem(id=4, title="侯宝璋与医学教育", era="1934-1949", duration="3:00"),
    ScriptItem(id=5, title="院系调整与山东医学院", era="1952", duration="2:20"),
    ScriptItem(id=6, title="趵突泉校区今昔", era="当代", duration="2:50"),
]

PHOTOS_ROOT = Path(__file__).resolve().parents[3] / "data" / "photos" / "Photos"

CATEGORY_LABELS = {
    "老照片彩色化": "彩色化",
    "老照片修复": "修复",
    "老照片拍摄原版": "原始影像",
    "动态化": "动态影像",
}


def infer_era(name: str) -> str:
    """从文件名提取资料中明确出现的年代；未标注时保留为“校史影像”。"""
    for year in ("1901", "1924", "1932", "1935", "1941", "1952", "2021"):
        if year in name:
            return f"{year}s"
    if "抗日战争" in name:
        return "抗战时期"
    if "齐鲁大学" in name:
        return "齐鲁大学时期"
    return "校史影像"


def build_gallery() -> list[PhotoItem]:
    if not PHOTOS_ROOT.is_dir():
        return []

    supported_extensions = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm"}
    media_files = sorted(
        (path for path in PHOTOS_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in supported_extensions),
        key=lambda path: (path.parent.name, path.name),
    )
    items: list[PhotoItem] = []
    for index, path in enumerate(media_files, start=1):
        relative_path = path.relative_to(PHOTOS_ROOT).as_posix()
        category = CATEGORY_LABELS.get(path.parent.name, path.parent.name)
        is_video = path.suffix.lower() in {".mp4", ".webm"}
        items.append(
            PhotoItem(
                id=index,
                title=path.stem,
                era=infer_era(path.stem),
                location="山东大学校史资料",
                image_url=f"/media/photos/{quote(relative_path, safe='/')}",
                category=category,
                media_type="video" if is_video else "image",
            )
        )
    return items


@router.get("/scripts", response_model=ScriptListResponse)
async def get_scripts():
    return ScriptListResponse(total=len(MOCK_SCRIPTS), items=MOCK_SCRIPTS)


@router.get("/gallery", response_model=GalleryResponse)
async def get_gallery():
    photos = build_gallery()
    return GalleryResponse(total=len(photos), items=photos)
