"""Webhook signature verification."""

from __future__ import annotations

import hashlib
import hmac


def verify_webhook(raw_body: str, signature: str, secret: str) -> bool:
    """Verify an incoming webhook signature from fdbck.

    Args:
        raw_body: The raw JSON string body of the webhook request.
        signature: The value of the ``X-FDBCK-Signature`` header.
        secret: The webhook secret from question creation.

    Returns:
        ``True`` if the signature is valid.
    """
    expected = hmac.new(
        secret.encode("utf-8"),
        raw_body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if len(expected) != len(signature):
        return False

    return hmac.compare_digest(expected, signature)
