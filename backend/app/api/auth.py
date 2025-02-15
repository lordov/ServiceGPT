from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import ResponseValidationError

from app.database import get_db
from app.services.user import get_user_by_email, create_user, verify_password
from app.auth import create_access_token
from app.schemas.user import UserCreate, UserOut
from app.core.exceptions.schemas import ErrorResponseModel
from app.core.exceptions.exceptions import UserAlreadyExists
from app.core.exceptions.schemas import ErrorResponseModel

router = APIRouter(prefix="/auth", tags=["Auth"])


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


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not await verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
