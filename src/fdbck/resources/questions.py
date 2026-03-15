"""Questions resource for the fdbck SDK."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator, Optional

from .._types import (
    CreateQuestionParams,
    ListQuestionsParams,
    ListResponsesParams,
    ListWebhooksParams,
    PaginatedList,
    Question,
    QuestionResultsResponse,
    WebhookDelivery,
)

if TYPE_CHECKING:
    from .._client import AsyncFdbck, Fdbck


def _build_create_body(params: CreateQuestionParams) -> dict[str, Any]:
    """Validate and build the request body for question creation."""
    has_expires_in = "expires_in" in params
    has_expires_at = "expires_at" in params

    if has_expires_in and has_expires_at:
        raise ValueError("Provide either expires_in or expires_at, not both")
    if not has_expires_in and not has_expires_at:
        raise ValueError("Either expires_in or expires_at is required")

    body: dict[str, Any] = dict(params)

    if has_expires_in:
        seconds = body.pop("expires_in")
        dt = datetime.now(timezone.utc).replace(microsecond=0)
        from datetime import timedelta

        expires = dt + timedelta(seconds=seconds)
        body["expires_at"] = expires.isoformat().replace("+00:00", "Z")

    return body


def _build_query(params: dict[str, Any]) -> dict[str, str]:
    """Convert typed params to string query dict."""
    query: dict[str, str] = {}
    for key, value in params.items():
        if value is not None:
            query[key] = str(value)
    return query


class QuestionsResource:
    """Sync questions resource."""

    def __init__(self, client: Fdbck) -> None:
        self._client = client

    def create(self, params: CreateQuestionParams) -> Question:
        """Create a new question."""
        body = _build_create_body(params)
        return self._client._request("POST", "/v1/questions", json=body)

    def get(self, question_id: str) -> Question:
        """Get a question by ID."""
        return self._client._request("GET", f"/v1/questions/{question_id}")

    def list(self, params: Optional[ListQuestionsParams] = None) -> PaginatedList:
        """List questions with pagination."""
        query = _build_query(dict(params)) if params else None
        return self._client._request("GET", "/v1/questions", params=query)

    def list_all(
        self, params: Optional[ListQuestionsParams] = None
    ) -> Iterator[Question]:
        """Auto-paginate through all questions."""
        opts: dict[str, Any] = dict(params) if params else {}
        opts.pop("cursor", None)
        cursor: Optional[str] = None

        while True:
            if cursor is not None:
                opts["cursor"] = cursor
            page = self.list(opts)  # type: ignore[arg-type]
            yield from page["data"]
            pagination = page["pagination"]
            if not pagination["has_more"]:
                break
            cursor = pagination["next_cursor"]

    def results(
        self,
        question_id: str,
        params: Optional[ListResponsesParams] = None,
    ) -> QuestionResultsResponse:
        """Get responses for a question with aggregated results."""
        query = _build_query(dict(params)) if params else None
        return self._client._request(
            "GET", f"/v1/questions/{question_id}/responses", params=query
        )

    def cancel(self, question_id: str) -> Question:
        """Cancel (delete) a question."""
        return self._client._request("DELETE", f"/v1/questions/{question_id}")

    def webhooks(
        self,
        question_id: str,
        params: Optional[ListWebhooksParams] = None,
    ) -> PaginatedList:
        """Get webhook delivery logs for a question."""
        query = _build_query(dict(params)) if params else None
        return self._client._request(
            "GET", f"/v1/questions/{question_id}/webhooks", params=query
        )


class AsyncQuestionsResource:
    """Async questions resource."""

    def __init__(self, client: AsyncFdbck) -> None:
        self._client = client

    async def create(self, params: CreateQuestionParams) -> Question:
        """Create a new question."""
        body = _build_create_body(params)
        return await self._client._request("POST", "/v1/questions", json=body)

    async def get(self, question_id: str) -> Question:
        """Get a question by ID."""
        return await self._client._request("GET", f"/v1/questions/{question_id}")

    async def list(self, params: Optional[ListQuestionsParams] = None) -> PaginatedList:
        """List questions with pagination."""
        query = _build_query(dict(params)) if params else None
        return await self._client._request("GET", "/v1/questions", params=query)

    async def list_all(
        self, params: Optional[ListQuestionsParams] = None
    ) -> AsyncIterator[Question]:
        """Auto-paginate through all questions."""
        opts: dict[str, Any] = dict(params) if params else {}
        opts.pop("cursor", None)
        cursor: Optional[str] = None

        while True:
            if cursor is not None:
                opts["cursor"] = cursor
            page = await self.list(opts)  # type: ignore[arg-type]
            for item in page["data"]:
                yield item
            pagination = page["pagination"]
            if not pagination["has_more"]:
                break
            cursor = pagination["next_cursor"]

    async def results(
        self,
        question_id: str,
        params: Optional[ListResponsesParams] = None,
    ) -> QuestionResultsResponse:
        """Get responses for a question with aggregated results."""
        query = _build_query(dict(params)) if params else None
        return await self._client._request(
            "GET", f"/v1/questions/{question_id}/responses", params=query
        )

    async def cancel(self, question_id: str) -> Question:
        """Cancel (delete) a question."""
        return await self._client._request("DELETE", f"/v1/questions/{question_id}")

    async def webhooks(
        self,
        question_id: str,
        params: Optional[ListWebhooksParams] = None,
    ) -> PaginatedList:
        """Get webhook delivery logs for a question."""
        query = _build_query(dict(params)) if params else None
        return await self._client._request(
            "GET", f"/v1/questions/{question_id}/webhooks", params=query
        )
