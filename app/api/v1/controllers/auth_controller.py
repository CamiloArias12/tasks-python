from datetime import timedelta
from typing import Any
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import LoginRequest
from app.schemas.response import Envelope, Meta
from app.services.auth_service import AuthService


class AuthController:
    def __init__(self):
        self.service = AuthService()

    async def login(
        self,
        request: Request,
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_db),
    ) -> Any:
        user = await self.service.authenticate_user(db, login_data.username, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = Token(
            access_token=security.create_access_token(
                user.email, expires_delta=access_token_expires
            ),
            token_type="bearer"
        )
        
        return Envelope(
            data=token_data,
            meta=Meta(request_id=getattr(request.state, "request_id", None))
        )


