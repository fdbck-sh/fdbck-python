"""Tests for webhook verification."""

from __future__ import annotations

import hashlib
import hmac

from fdbck import verify_webhook

SECRET = "whsec_test_secret_123"
BODY = '{"event":"question.response_received","data":{"id":"r_1"}}'


def _sign(body: str, secret: str) -> str:
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


class TestVerifyWebhook:
    def test_valid_signature(self):
        sig = _sign(BODY, SECRET)
        assert verify_webhook(BODY, sig, SECRET) is True

    def test_invalid_signature(self):
        assert verify_webhook(BODY, "a" * 64, SECRET) is False

    def test_tampered_body(self):
        sig = _sign(BODY, SECRET)
        assert verify_webhook(BODY + "x", sig, SECRET) is False

    def test_wrong_secret(self):
        sig = _sign(BODY, SECRET)
        assert verify_webhook(BODY, sig, "wrong_secret") is False

    def test_wrong_length_signature(self):
        assert verify_webhook(BODY, "tooshort", SECRET) is False

    def test_empty_signature(self):
        assert verify_webhook(BODY, "", SECRET) is False
