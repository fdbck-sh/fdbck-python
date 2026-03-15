"""Tests for the fdbck client."""

from __future__ import annotations

import httpx
import pytest
import respx

from fdbck import AsyncFdbck, Fdbck, FdbckApiError, FdbckNetworkError

API_KEY = "sk_fdbck_test_key_123"
BASE = "https://api.fdbck.sh"


class TestConstructor:
    def test_valid_key(self):
        client = Fdbck(API_KEY)
        client.close()

    def test_invalid_key_prefix(self):
        with pytest.raises(ValueError, match="sk_fdbck_"):
            Fdbck("bad_key")

    def test_custom_base_url(self):
        client = Fdbck(API_KEY, base_url="https://custom.api.com/")
        assert client._client.base_url == httpx.URL("https://custom.api.com")
        client.close()

    def test_context_manager(self):
        with Fdbck(API_KEY) as client:
            assert client is not None


class TestAsyncConstructor:
    def test_invalid_key(self):
        with pytest.raises(ValueError, match="sk_fdbck_"):
            AsyncFdbck("nope")

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        async with AsyncFdbck(API_KEY) as client:
            assert client is not None


class TestRequest:
    def test_auth_header(self):
        with respx.mock:
            route = respx.get(f"{BASE}/v1/me").mock(
                return_value=httpx.Response(
                    200, json={"user": None, "organization": None}
                )
            )
            with Fdbck(API_KEY) as client:
                client.me()
                assert route.called
                request = route.calls[0].request
                assert request.headers["authorization"] == f"Bearer {API_KEY}"
                assert "fdbck-python/" in request.headers["user-agent"]

    def test_api_error(self):
        with respx.mock:
            respx.get(f"{BASE}/v1/me").mock(
                return_value=httpx.Response(
                    401,
                    json={"error": {"code": "unauthorized", "message": "Bad key"}},
                )
            )
            with Fdbck(API_KEY) as client:
                with pytest.raises(FdbckApiError) as exc_info:
                    client.me()
                assert exc_info.value.status == 401
                assert exc_info.value.code == "unauthorized"
                assert "Bad key" in str(exc_info.value)

    def test_api_error_with_details(self):
        with respx.mock:
            respx.post(f"{BASE}/v1/questions").mock(
                return_value=httpx.Response(
                    422,
                    json={
                        "error": {
                            "code": "validation_error",
                            "message": "Invalid fields",
                            "details": {"fields": ["question", "type"]},
                        }
                    },
                )
            )
            with Fdbck(API_KEY) as client:
                with pytest.raises(FdbckApiError) as exc_info:
                    client._request("POST", "/v1/questions", json={})
                assert exc_info.value.details == {"fields": ["question", "type"]}

    def test_network_error(self):
        with respx.mock:
            respx.get(f"{BASE}/v1/me").mock(
                side_effect=httpx.ConnectError("refused")
            )
            with Fdbck(API_KEY) as client:
                with pytest.raises(FdbckNetworkError):
                    client.me()

    def test_me(self):
        with respx.mock:
            respx.get(f"{BASE}/v1/me").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "user": {
                            "id": "u1",
                            "email": "a@b.com",
                            "name": "Alice",
                            "avatar_url": None,
                        },
                        "organization": {
                            "id": "org1",
                            "name": "Acme",
                            "slug": "acme",
                            "plan": "starter",
                            "role": "owner",
                            "responses_used": 42,
                            "responses_limit": 10000,
                            "period_starts_at": "2025-01-01T00:00:00Z",
                            "period_ends_at": None,
                            "consecutive_overage_months": 0,
                            "has_billing": True,
                        },
                    },
                )
            )
            with Fdbck(API_KEY) as client:
                info = client.me()
                assert info["user"]["email"] == "a@b.com"
                assert info["organization"]["plan"] == "starter"
