from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import ResponseValidationError

from app.database import get_db
from app.services.user import get_user_by_email, create_user
from app.core.security.pwdcrypt import verify_password
from app.core.security.auth import create_access_token, create_refresh_token, get_current_user, refresh_jwt
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import TokenResponse
from app.core.exceptions.schemas import ErrorResponseModel
from app.core.exceptions.exceptions import UserAlreadyExists
from app.core.exceptions.schemas import ErrorResponseModel

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary='Registery',
    description='The endpoint register new user',
    responses={
        status.HTTP_201_CREATED: {"model": UserOut},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponseModel},
    }
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, user_data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        new_user = await create_user(db, user_data)
        return new_user
    except ResponseValidationError:
        raise ResponseValidationError
    except UserAlreadyExists as uae:
        raise uae
    except Exception as e:
        return {
            "message": "Registration failed",
            "error": str(e)
        }


@router.post(
        "/login",
        response_model=TokenResponse,
        summary='Login',
        description='The endpoint login user',
        responses={
            status.HTTP_200_OK: {"model": TokenResponse},
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseModel},
        }
        )
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not await verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = await create_access_token({"sub": user.email})
    refresh_token = await create_refresh_token(
        data={"sub": user.email},
    )
    # ✅ Сохраняем refresh токен в HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        expires=60 * 60 * 24 * 7  # 7 days
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    return await refresh_jwt(refresh_token, session)


@router.get("/users/me", response_model=UserOut)
async def read_users_me(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Получаем пользователя по email (email == current_user)
    # Здесь предполагается, что мы имеем функцию для поиска пользователя по email
    user = await get_user_by_email(db, current_user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.to_read_model()
