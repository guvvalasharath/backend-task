from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.db.base import get_db
from app.db.models import User
from app.auth import hash_password, verify_password, create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    exists = await db.scalar(sa.select(User).where(User.email == email))
    if exists:
        raise HTTPException(400, "Email already registered")
    total_users = await db.scalar(sa.select(sa.func.count(User.id)))
    role = "admin" if total_users == 0 else "member"
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role
    )
    db.add(user)
    await db.commit()
    return {
        "message": "User created",
        "user_id": user.id,
        "role": role
    }


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    user = await db.scalar(sa.select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")

    return user
