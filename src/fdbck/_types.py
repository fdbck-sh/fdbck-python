"""Type definitions for the fdbck SDK."""

from __future__ import annotations

from typing import Any, List, Literal, Optional, Union

from typing import TypedDict

QuestionType = Literal["yes_no", "single_choice", "multiple_choice", "rating"]
QuestionStatus = Literal["collecting", "completed", "expired", "cancelled"]
WebhookTrigger = Literal["expiry", "each_response", "both"]

WebhookEvent = Literal[
    "question.response_received",
    "question.completed",
    "question.expired",
    "question.cancelled",
]

ErrorCode = Literal[
    "unauthorized",
    "invalid_token",
    "forbidden",
    "plan_restricted",
    "plan_limit_reached",
    "not_found",
    "already_responded",
    "already_closed",
    "question_expired",
    "validation_error",
    "rate_limit_exceeded",
    "internal_error",
    "bad_request",
    "conflict",
    "gone",
    "not_collecting",
    "parse_error",
    "unknown_error",
]


class RatingConfig(TypedDict, total=False):
    """Rating scale configuration."""

    min: int
    max: int
    min_label: str
    max_label: str


class CreateQuestionParams(TypedDict, total=False):
    """Parameters for creating a question."""

    question: str
    type: QuestionType
    options: List[str]
    rating_config: RatingConfig
    expires_in: int
    expires_at: str
    max_responses: int
    webhook_url: str
    webhook_trigger: WebhookTrigger
    metadata: dict[str, str]
    theme_color: str
    theme_mode: Literal["light", "dark"]
    hide_branding: bool
    welcome_message: str
    thank_you_message: str


class Question(TypedDict, total=False):
    """A question resource."""

    id: str
    question: str
    type: QuestionType
    options: Optional[List[str]]
    rating_config: RatingConfig
    status: QuestionStatus
    expires_at: str
    max_responses: Optional[int]
    webhook_url: str
    webhook_trigger: WebhookTrigger
    webhook_secret: str
    metadata: Optional[dict[str, str]]
    theme_color: str
    theme_mode: str
    hide_branding: bool
    welcome_message: Optional[str]
    thank_you_message: Optional[str]
    total_responses: int
    created_at: str
    updated_at: str


class Pagination(TypedDict):
    """Pagination metadata."""

    next_cursor: Optional[str]
    has_more: bool


class PaginatedList(TypedDict):
    """Paginated list envelope."""

    data: List[Any]
    pagination: Pagination


class ResponseItem(TypedDict):
    """A single response item."""

    id: str
    question_id: str
    value: Any
    respondent: Optional[str]
    created_at: str


class QuestionResultsResponse(TypedDict, total=False):
    """Aggregated results with paginated individual responses."""

    question_id: str
    type: str
    status: str
    total_responses: int
    results: dict[str, Any]
    data: List[ResponseItem]
    pagination: Pagination


class WebhookDelivery(TypedDict, total=False):
    """A webhook delivery log entry."""

    id: str
    event: WebhookEvent
    success: bool
    status_code: Optional[int]
    attempts: int
    error: Optional[str]
    created_at: str
    next_retry_at: Optional[str]


class CreateTokenParams(TypedDict, total=False):
    """Parameters for creating a respondent token."""

    respondent: str
    metadata: dict[str, str]


class TokenResult(TypedDict):
    """Token creation result."""

    token: str
    respond_url: str
    expires_at: str


class AccountUser(TypedDict):
    """User info from GET /v1/me."""

    id: str
    email: str
    name: Optional[str]
    avatar_url: Optional[str]


class AccountOrganization(TypedDict, total=False):
    """Organization info from GET /v1/me."""

    id: str
    name: str
    slug: str
    plan: str
    role: Optional[str]
    responses_used: int
    responses_limit: Optional[int]
    period_starts_at: str
    period_ends_at: Optional[str]
    consecutive_overage_months: int
    has_billing: bool


class AccountInfo(TypedDict):
    """Account info from GET /v1/me."""

    user: Optional[AccountUser]
    organization: Optional[AccountOrganization]


class ListQuestionsParams(TypedDict, total=False):
    """Parameters for listing questions."""

    cursor: str
    limit: int
    status: QuestionStatus
    sort: Literal["created_at", "updated_at"]
    order: Literal["asc", "desc"]
    created_after: str
    created_before: str


class ListResponsesParams(TypedDict, total=False):
    """Parameters for listing responses."""

    cursor: str
    limit: int


class ListWebhooksParams(TypedDict, total=False):
    """Parameters for listing webhook deliveries."""

    cursor: str
    limit: int
