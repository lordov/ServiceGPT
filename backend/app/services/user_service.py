from fastapi import HTTPException, Response
from fastapi.exceptions import ResponseValidationError
from fastapi.security import OAuth2PasswordRequestForm

from app.core.exceptions.exceptions import UserAlreadyExists
from app.schemas.user import UserCreate
from app.core.security.pwdcrypt import password_hasher, verify_password
from app.utils.unit_of_work import IUnitOfWork
from app.core.security.auth import create_access_token, create_refresh_token, refresh_jwt
from app.core.my_logging import logger


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def register(self, user_data: UserCreate):
        """Регистрация нового пользователя."""
        async with self.uow:
            user = await self.uow.user.get_by_email(user_data.email)
            if user:
                logger.warning(
                    f"Попытка регистрации уже существующего email: {user_data.email}")
                raise HTTPException(
                    status_code=400, detail="Email already registered")
            try:
                hashed_password = password_hasher(user_data.password)
                new_user = await self.uow.user.create(user_data, hashed_password)
                await self.uow.commit()
                return new_user
            except ResponseValidationError as rve:
                logger.error(f"Ошибка валидации при регистрации: {rve}")
                raise rve
            except UserAlreadyExists as uae:
                logger.error(f"Пользователь уже существует: {uae}")
                raise uae
            except Exception as e:
                logger.error(f"Ошибка регистрации пользователя: {e}")
                raise HTTPException(
                    status_code=500, detail="Registration failed")

    async def login(self, form_data: OAuth2PasswordRequestForm, response: Response):
        """Вход в систему и выдача токенов"""
        async with self.uow:
            user = await self.uow.user.get_by_email(form_data.username)
            if not user or not await verify_password(form_data.password, user.hashed_password):
                logger.warning(f"Неверные учетные данные для: {form_data.username}")
                raise HTTPException(
                    status_code=401, detail="Invalid credentials")

            access_token = await create_access_token({"sub": user.email})
            refresh_token = await create_refresh_token(data={"sub": user.email})

            # ✅ Сохраняем refresh токен в HttpOnly Cookie
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                expires=60 * 60 * 24 * 7  # 7 дней
            )

            return {
                "access_token": access_token,
                "token_type": "bearer"
            }

    async def refresh_token(self, refresh_token: str):
        """Обновляет access-токен."""
        try:
            return await refresh_jwt(refresh_token)
        except Exception as e:
            logger.error(f"Ошибка обновления токена: {e}")
            raise HTTPException(status_code=401, detail="Token refresh failed")