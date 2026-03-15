"""Error classes for the fdbck SDK."""

from __future__ import annotations

from typing import Any


class FdbckError(Exception):
    """Base error for all fdbck SDK errors."""


class FdbckApiError(FdbckError):
    """Error returned by the fdbck API."""

    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details

    def __repr__(self) -> str:
        return f"FdbckApiError(status={self.status}, code={self.code!r}, message={self.args[0]!r})"


class FdbckNetworkError(FdbckError):
    """Network-level error (connection failure, timeout, etc.)."""
