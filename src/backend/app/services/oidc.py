"""OIDC service module."""

import os

import httpx

from cachetools import TTLCache
from dotenv import load_dotenv

from jose import JWTError, jwt

from services.logging.base import LoggerBase

load_dotenv()


class OIDCService:
    """Service for handling OIDC operations."""

    def __init__(self, logger: LoggerBase):
        self.logger = logger

        self.config_cache = TTLCache(maxsize=1, ttl=3600)
        self.jwks_cache = TTLCache(maxsize=1, ttl=3600)

        self.base_url = os.environ.get("OIDC_BASE_URL", "")
        self.discovery_url = os.environ.get("OIDC_DISCOVERY_URL", "")
        self.redirect_url = os.environ.get("OIDC_REDIRECT_URL", "")
        self.client_id = os.environ.get("OIDC_CLIENT_ID", "")
        self.client_secret = os.environ.get("OIDC_CLIENT_SECRET", "")
        self.audience = os.environ.get("OIDC_REDIRECT_URL", "")

        self._ensure_env_set()

    async def get_oidc_config(self) -> dict:
        """Get the OIDC configuration from the discovery endpoint or cache, if available.

        Returns:
            dict: OIDC configuration.
        """

        if "config" not in self.config_cache:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.discovery_url)
                response.raise_for_status()
                self.config_cache["config"] = response.json()

        return self.config_cache.get("config", {})

    async def get_jwks(self) -> dict:
        """Get the JWKs from the discovery endpoint or cache, if available.

        Returns:
            dict: JWKs.
        """

        if "jwks" not in self.jwks_cache:
            config = await self.get_oidc_config()
            jwks_uri = config["jwks_uri"]

            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_uri)
                response.raise_for_status()
                self.jwks_cache["jwks"] = response.json()

        return self.jwks_cache.get("jwks", {})

    async def verify_token(self, token: str) -> dict | None:
        """Verify the token and return the claims.

        Args:
            token (str): The token to verify.

        Returns:
            dict | None: The claims of the token or None if the token is invalid.
        """
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                self.logger.warn("No 'kid' in token header.")
                return None

            jwks = await self.get_jwks()

            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    # https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-key-set-properties
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
                    }

            if not rsa_key:
                return None

            config = await self.get_oidc_config()

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=config["issuer"],
            )
            return payload
        except JWTError as e:
            self.logger.warn(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error verifying token: {str(e)}")
            return None

    def _ensure_env_set(self) -> None:
        if not self.base_url:
            raise EnvironmentError("OIDC_BASE_URL environment variable is not set")

        if not self.discovery_url:
            raise EnvironmentError("OIDC_DISCOVERY_URL environment variable is not set")

        if not self.redirect_url:
            raise EnvironmentError("OIDC_REDIRECT_URL environment variable is not set")

        if not self.client_id:
            raise EnvironmentError("OIDC_CLIENT_ID environment variable is not set")

        if not self.client_secret:
            raise EnvironmentError("OIDC_CLIENT_SECRET environment variable is not set")

        if not self.audience:
            raise EnvironmentError("OIDC_REDIRECT_URL environment variable is not set")
