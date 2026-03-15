"""Tests for the tokens resource."""

from __future__ import annotations

import json

import httpx
import respx

from fdbck import Fdbck

API_KEY = "sk_fdbck_test_key_123"
BASE = "https://api.fdbck.sh"

TOKEN_RESPONSE = {
    "token": "V1StGXR8_Z5jdHi6",
    "respond_url": "https://fdbck.sh/f/V1StGXR8_Z5jdHi6",
    "expires_at": "2025-01-01T01:00:00Z",
}


class TestCreate:
    def test_create_with_respondent(self):
        with respx.mock:
            route = respx.post(f"{BASE}/v1/questions/q_123/token").mock(
                return_value=httpx.Response(200, json=TOKEN_RESPONSE)
            )
            with Fdbck(API_KEY) as client:
                result = client.tokens.create("q_123", {"respondent": "user_42"})
                assert result["token"] == "V1StGXR8_Z5jdHi6"
                assert result["respond_url"] == "https://fdbck.sh/f/V1StGXR8_Z5jdHi6"
                sent = json.loads(route.calls[0].request.content)
                assert sent["respondent"] == "user_42"

    def test_create_without_params(self):
        with respx.mock:
            respx.post(f"{BASE}/v1/questions/q_123/token").mock(
                return_value=httpx.Response(200, json=TOKEN_RESPONSE)
            )
            with Fdbck(API_KEY) as client:
                result = client.tokens.create("q_123")
                assert result["token"] == "V1StGXR8_Z5jdHi6"

    def test_create_with_metadata(self):
        with respx.mock:
            route = respx.post(f"{BASE}/v1/questions/q_123/token").mock(
                return_value=httpx.Response(200, json=TOKEN_RESPONSE)
            )
            with Fdbck(API_KEY) as client:
                client.tokens.create(
                    "q_123",
                    {"respondent": "user_42", "metadata": {"source": "email"}},
                )
                sent = json.loads(route.calls[0].request.content)
                assert sent["metadata"] == {"source": "email"}
