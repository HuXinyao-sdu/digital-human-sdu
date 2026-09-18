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

# 模拟图库
MOCK_PHOTOS = [
    PhotoItem(id=1, title="山东大学堂校门", era="1900s", location="济南泺源书院", image_url=""),
    PhotoItem(id=2, title="齐鲁大学主楼", era="1920s", location="趵突泉校区", image_url=""),
    PhotoItem(id=3, title="老舍在山大任教", era="1930s", location="青岛校区", image_url=""),
    PhotoItem(id=4, title="侯宝璋在实验室", era="1930s", location="齐鲁大学医学院", image_url=""),
]


@router.get("/scripts", response_model=ScriptListResponse)
async def get_scripts():
    return ScriptListResponse(total=len(MOCK_SCRIPTS), items=MOCK_SCRIPTS)


@router.get("/gallery", response_model=GalleryResponse)
async def get_gallery():
    return GalleryResponse(total=len(MOCK_PHOTOS), items=MOCK_PHOTOS)
