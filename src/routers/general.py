from fastapi import APIRouter
from src.utils.fastapi_models import APIInfo


router = APIRouter(tags=["General"])


@router.get("/", response_model=APIInfo)
async def api_info():
    """APIの基本情報を取得します。"""
    return APIInfo()
