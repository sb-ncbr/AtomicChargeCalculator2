from pydantic import BaseModel


class TokenResponse(BaseModel):
    """JWT Token response."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str
    id_token: str
