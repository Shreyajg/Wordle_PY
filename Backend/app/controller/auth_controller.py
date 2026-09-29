from fastapi import APIRouter, Depends, Response

from app.config.dependencies import get_jwt_service, get_user_service
from app.config.security_config import TOKEN_COOKIE, get_authenticated_user
from app.controller.schemas import AuthRequest, AuthResponse
from app.model.user import User
from app.service.jwt_service import JwtService
from app.service.user_service import UserService

router = APIRouter(prefix="/auth")

COOKIE_MAX_AGE = 60 * 60


def _set_token_cookie(response: Response, token: str, max_age: int) -> None:
    response.set_cookie(
        key=TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=False,
        path="/",
        max_age=max_age,
        samesite="lax",
    )


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(token=None, username=user.username, role=user.role.value)


@router.get("/me", response_model=AuthResponse)
async def get_current_user(
    user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.find_by_username(user.username)
    return _auth_response(user)


@router.post("/register", response_model=AuthResponse)
async def register(
    request: AuthRequest,
    response: Response,
    user_service: UserService = Depends(get_user_service),
    jwt_service: JwtService = Depends(get_jwt_service),
):
    user = await user_service.register(request.username, request.password, request.confirm_password)
    _set_token_cookie(response, jwt_service.generate_token(user.username), COOKIE_MAX_AGE)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: AuthRequest,
    response: Response,
    user_service: UserService = Depends(get_user_service),
    jwt_service: JwtService = Depends(get_jwt_service),
):
    user = await user_service.login(request.username, request.password)
    _set_token_cookie(response, jwt_service.generate_token(user.username), COOKIE_MAX_AGE)
    return _auth_response(user)


@router.post("/logout", status_code=204, dependencies=[Depends(get_authenticated_user)])
async def logout():
    response = Response(status_code=204)
    _set_token_cookie(response, "", 0)
    return response
