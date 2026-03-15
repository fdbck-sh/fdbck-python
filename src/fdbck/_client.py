"""Sync and async client classes for the fdbck SDK."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from ._errors import FdbckApiError, FdbckNetworkError
from ._version import VERSION
from ._webhook import verify_webhook as _verify_webhook
from .resources.questions import AsyncQuestionsResource, QuestionsResource
from .resources.tokens import AsyncTokensResource, TokensResource

DEFAULT_BASE_URL = "https://api.fdbck.sh"
DEFAULT_TIMEOUT = 30.0


class Fdbck:
    """Sync client for the fdbck API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key.startswith("sk_fdbck_"):
            raise ValueError('Invalid API key: must start with "sk_fdbck_"')

        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"fdbck-python/{VERSION}",
            },
        )
        self.questions = QuestionsResource(self)
        self.tokens = TokensResource(self)

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, str]] = None,
    ) -> Any:
        """Make an authenticated request to the fdbck API."""
        try:
            response = self._client.request(
                method, path, json=json, params=params
            )
        except httpx.HTTPError as exc:
            raise FdbckNetworkError(str(exc)) from exc

        if response.status_code == 204:
            return None

        try:
            data = response.json()
        except Exception:
            raise FdbckApiError(
                response.status_code, "parse_error", "Failed to parse response body"
            )

        if not response.is_success:
            err = data.get("error", {}) if isinstance(data, dict) else {}
            raise FdbckApiError(
                response.status_code,
                err.get("code", "unknown_error"),
                err.get("message", f"Request failed with status {response.status_code}"),
                err.get("details"),
            )

        return data

    def me(self) -> dict[str, Any]:
        """Get current account info."""
        return self._request("GET", "/v1/me")

    def verify_webhook(self, raw_body: str, signature: str, secret: str) -> bool:
        """Verify a webhook signature."""
        return _verify_webhook(raw_body, signature, secret)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> Fdbck:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncFdbck:
    """Async client for the fdbck API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key.startswith("sk_fdbck_"):
            raise ValueError('Invalid API key: must start with "sk_fdbck_"')

        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"fdbck-python/{VERSION}",
            },
        )
        self.questions = AsyncQuestionsResource(self)
        self.tokens = AsyncTokensResource(self)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, str]] = None,
    ) -> Any:
        """Make an authenticated request to the fdbck API."""
        try:
            response = await self._client.request(
                method, path, json=json, params=params
            )
        except httpx.HTTPError as exc:
            raise FdbckNetworkError(str(exc)) from exc

        if response.status_code == 204:
            return None

        try:
            data = response.json()
        except Exception:
            raise FdbckApiError(
                response.status_code, "parse_error", "Failed to parse response body"
            )

        if not response.is_success:
            err = data.get("error", {}) if isinstance(data, dict) else {}
            raise FdbckApiError(
                response.status_code,
                err.get("code", "unknown_error"),
                err.get("message", f"Request failed with status {response.status_code}"),
                err.get("details"),
            )

        return data

    async def me(self) -> dict[str, Any]:
        """Get current account info."""
        return await self._request("GET", "/v1/me")

    def verify_webhook(self, raw_body: str, signature: str, secret: str) -> bool:
        """Verify a webhook signature."""
        return _verify_webhook(raw_body, signature, secret)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncFdbck:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
