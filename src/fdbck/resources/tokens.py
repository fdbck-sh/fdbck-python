"""Tokens resource for the fdbck SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .._types import CreateTokenParams, TokenResult

if TYPE_CHECKING:
    from .._client import AsyncFdbck, Fdbck


class TokensResource:
    """Sync tokens resource."""

    def __init__(self, client: Fdbck) -> None:
        self._client = client

    def create(
        self,
        question_id: str,
        params: Optional[CreateTokenParams] = None,
    ) -> TokenResult:
        """Create a respondent token for a question."""
        body = dict(params) if params else {}
        return self._client._request(
            "POST", f"/v1/questions/{question_id}/token", json=body
        )


class AsyncTokensResource:
    """Async tokens resource."""

    def __init__(self, client: AsyncFdbck) -> None:
        self._client = client

    async def create(
        self,
        question_id: str,
        params: Optional[CreateTokenParams] = None,
    ) -> TokenResult:
        """Create a respondent token for a question."""
        body = dict(params) if params else {}
        return await self._client._request(
            "POST", f"/v1/questions/{question_id}/token", json=body
        )
