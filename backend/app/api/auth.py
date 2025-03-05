from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import TokenResponse
from app.core.exceptions.schemas import ErrorResponseModel
from app.core.exceptions.schemas import ErrorResponseModel
from app.utils.unit_of_work import IUnitOfWork, UnitOfWork


router = APIRouter(prefix="/api/auth", tags=["Auth"])


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


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
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.register(user_data)


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
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.login(form_data, response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    refresh_token = request.cookies.get("refresh_token")
    return await user_service.refresh_token(refresh_token)
