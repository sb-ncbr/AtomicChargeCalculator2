"""Auth routes."""

import urllib
import urllib.parse

import httpx
from api.v1.schemas.response import Response
from core.dependency_injection.container import Container
from db.models.user.user import User
from db.repositories.user_repository import UserRepository
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel
from services.oidc import OIDCService


class TokenResponse(BaseModel):
    """JWT Token response."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str
    id_token: str


auth_router = APIRouter(prefix="/auth", tags=["auth"], include_in_schema=False)


@auth_router.get("/login", tags=["login"])
@inject
async def login(oidc_service: OIDCService = Depends(Provide[Container.oidc_service])):
    """Initiate the OIDC authentication flow."""
    config = await oidc_service.get_oidc_config()
    auth_endpoint = config["authorization_endpoint"]
    params = {
        "response_type": "code",
        "client_id": oidc_service.client_id,
        "scope": "openid",
        "redirect_uri": oidc_service.redirect_uri,
    }
    query = urllib.parse.urlencode(params)

    return RedirectResponse(f"{auth_endpoint}?{query}")


@auth_router.get("/logout", tags=["logout"])
@inject
async def logout(
    request: Request, oidc_service: OIDCService = Depends(Provide[Container.oidc_service])
):
    """Log out the user."""
    config = await oidc_service.get_oidc_config()
    token = request.cookies.get("access_token")
    redirect_uri = "https://acc2-dev.biodata.ceitec.cz/"  # TODO get from config

    response = RedirectResponse(redirect_uri)

    if "end_session_endpoint" in config:
        end_session_endpoint = config["end_session_endpoint"]
        params = {
            "client_id": oidc_service.client_id,
            "post_logout_redirect_uri": redirect_uri,
        }

        if token:
            params["id_token_hint"] = token

        query = urllib.parse.urlencode(params)
        response = RedirectResponse(f"{end_session_endpoint}?{query}")

    response.delete_cookie("access_token", secure=True, httponly=True, path="/")

    return response


@auth_router.get("/callback", tags=["callback"])
@inject
async def auth_callback(
    code: str,
    oidc_service: OIDCService = Depends(Provide[Container.oidc_service]),
    user_repository: UserRepository = Depends(Provide[Container.user_repository]),
):
    """Handle the callback from the OIDC provider."""

    config = await oidc_service.get_oidc_config()
    token_endpoint = config["token_endpoint"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_endpoint,
            data={
                "grant_type": "authorization_code",
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=httpx.BasicAuth(
                username=oidc_service.client_id,
                password=oidc_service.client_secret,
            ),
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to get token: {response.text}",
            )

        tokens = TokenResponse(**response.json())

        payload = await oidc_service.verify_token(tokens.access_token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify token",
            )

        # create user if does not exist
        openid = payload["sub"]
        user = user_repository.get(openid)
        if user is None:
            user = User(openid=openid)
            user_repository.store(user)

        # set session cookie
        response = RedirectResponse(url="https://acc2-dev.biodata.ceitec.cz/")
        response.set_cookie("access_token", tokens.access_token, secure=True, httponly=True)

        return response


@auth_router.get("/verify", tags=["verify"])
async def verify(request: Request):
    """Verifies if user is logged in."""

    user = request.state.user
    return Response(data={"isAuthenticated": user is not None})
