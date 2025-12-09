from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user

router = APIRouter(prefix="/users")

@router.get("/me")
async def me(user = Depends(get_current_user)):
    return user
