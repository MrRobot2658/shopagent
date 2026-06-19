"""Auth endpoints — login / logout / me (Redis-backed sessions)."""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import auth, config
from ..db.models import User
from ..db.session import get_session
from ..schemas import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_session)):
    user = await db.scalar(select(User).where(User.username == req.username))
    if not user or not auth.verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    profile = {"username": user.username, "role": user.role}
    token = await auth.create_session(profile)
    response.set_cookie(
        key=config.SESSION_COOKIE,
        value=token,
        max_age=config.SESSION_TTL,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return {"user": profile, "message": "登录成功"}


@router.post("/logout")
async def logout(response: Response, sa_session: str | None = Cookie(default=None)):
    await auth.destroy_session(sa_session)
    response.delete_cookie(config.SESSION_COOKIE, path="/")
    return {"message": "已登出"}


@router.get("/me")
async def me(user=Depends(auth.require_user)):
    return {"user": user}
