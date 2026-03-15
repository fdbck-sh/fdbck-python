"""Tests for the questions resource."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx
import pytest
import respx

from fdbck import Fdbck

API_KEY = "sk_fdbck_test_key_123"
BASE = "https://api.fdbck.sh"


def make_question(**overrides):
    """Return a question response dict with defaults."""
    base = {
        "id": "q_123",
        "question": "How was it?",
        "type": "yes_no",
        "options": ["Yes", "No"],
        "status": "collecting",
        "expires_at": "2025-12-01T00:00:00Z",
        "max_responses": None,
        "metadata": None,
        "theme_color": "#FF6B35",
        "theme_mode": "dark",
        "hide_branding": False,
        "welcome_message": None,
        "thank_you_message": None,
        "total_responses": 0,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


class TestCreate:
    def test_create_with_expires_in(self):
        with respx.mock:
            route = respx.post(f"{BASE}/v1/questions").mock(
                return_value=httpx.Response(200, json=make_question())
            )
            with Fdbck(API_KEY) as client:
                result = client.questions.create({
                    "question": "How was it?",
                    "type": "yes_no",
                    "expires_in": 86400,
                })
                assert result["id"] == "q_123"
                sent = json.loads(route.calls[0].request.content)
                assert "expires_at" in sent
                assert "expires_in" not in sent

    def test_create_with_expires_at(self):
        with respx.mock:
            respx.post(f"{BASE}/v1/questions").mock(
                return_value=httpx.Response(200, json=make_question())
            )
            with Fdbck(API_KEY) as client:
                result = client.questions.create({
                    "question": "How was it?",
                    "type": "yes_no",
                    "expires_at": "2025-12-01T00:00:00Z",
                })
                assert result["id"] == "q_123"

    def test_create_both_expires_raises(self):
        with Fdbck(API_KEY) as client:
            with pytest.raises(ValueError, match="not both"):
                client.questions.create({
                    "question": "Q",
                    "type": "yes_no",
                    "expires_in": 100,
                    "expires_at": "2025-12-01T00:00:00Z",
                })

    def test_create_no_expires_raises(self):
        with Fdbck(API_KEY) as client:
            with pytest.raises(ValueError, match="required"):
                client.questions.create({
                    "question": "Q",
                    "type": "yes_no",
                })

    def test_create_rating(self):
        q = make_question(
            type="rating",
            options=None,
            rating_config={"min": 1, "max": 5, "min_label": "Bad", "max_label": "Great"},
        )
        with respx.mock:
            respx.post(f"{BASE}/v1/questions").mock(
                return_value=httpx.Response(200, json=q)
            )
            with Fdbck(API_KEY) as client:
                result = client.questions.create({
                    "question": "Rate us",
                    "type": "rating",
                    "rating_config": {"min": 1, "max": 5},
                    "expires_in": 3600,
                })
                assert result["type"] == "rating"


class TestGet:
    def test_get(self):
        with respx.mock:
            respx.get(f"{BASE}/v1/questions/q_123").mock(
                return_value=httpx.Response(200, json=make_question())
            )
            with Fdbck(API_KEY) as client:
                result = client.questions.get("q_123")
                assert result["id"] == "q_123"


class TestList:
    def test_list(self):
        with respx.mock:
            respx.get(f"{BASE}/v1/questions").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "data": [make_question()],
                        "pagination": {"next_cursor": None, "has_more": False},
                    },
                )
            )
            with Fdbck(API_KEY) as client:
                page = client.questions.list()
                assert len(page["data"]) == 1
                assert page["pagination"]["has_more"] is False

    def test_list_with_params(self):
        with respx.mock:
            route = respx.get(f"{BASE}/v1/questions").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "data": [],
                        "pagination": {"next_cursor": None, "has_more": False},
                    },
                )
            )
            with Fdbck(API_KEY) as client:
                client.questions.list({"status": "collecting", "limit": 10})
                url = str(route.calls[0].request.url)
                assert "status=collecting" in url
                assert "limit=10" in url


class TestListAll:
    def test_list_all_pagination(self):
        q1 = make_question(id="q_1")
        q2 = make_question(id="q_2")
        q3 = make_question(id="q_3")
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    200,
                    json={
                        "data": [q1, q2],
                        "pagination": {"next_cursor": "cur_abc", "has_more": True},
                    },
                )
            return httpx.Response(
                200,
                json={
                    "data": [q3],
                    "pagination": {"next_cursor": None, "has_more": False},
                },
            )

        with respx.mock:
            respx.get(f"{BASE}/v1/questions").mock(side_effect=handler)
            with Fdbck(API_KEY) as client:
                ids = [q["id"] for q in client.questions.list_all()]
                assert ids == ["q_1", "q_2", "q_3"]
                assert call_count == 2


class TestResults:
    def test_results(self):
        with respx.mock:
            respx.get(f"{BASE}/v1/questions/q_123/responses").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "question_id": "q_123",
                        "type": "yes_no",
                        "status": "collecting",
                        "total_responses": 5,
                        "results": {"Yes": 3, "No": 2},
                        "data": [
                            {
                                "id": "r_1",
                                "question_id": "q_123",
                                "value": "Yes",
                                "respondent": "user_1",
                                "created_at": "2025-01-01T00:00:00Z",
                            }
                        ],
                        "pagination": {"next_cursor": None, "has_more": False},
                    },
                )
            )
            with Fdbck(API_KEY) as client:
                results = client.questions.results("q_123")
                assert results["total_responses"] == 5
                assert len(results["data"]) == 1


class TestCancel:
    def test_cancel(self):
        with respx.mock:
            respx.delete(f"{BASE}/v1/questions/q_123").mock(
                return_value=httpx.Response(
                    200, json=make_question(status="cancelled")
                )
            )
            with Fdbck(API_KEY) as client:
                result = client.questions.cancel("q_123")
                assert result["status"] == "cancelled"


class TestWebhooks:
    def test_webhooks(self):
        with respx.mock:
            respx.get(f"{BASE}/v1/questions/q_123/webhooks").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "data": [
                            {
                                "id": "wh_1",
                                "event": "question.response_received",
                                "success": True,
                                "status_code": 200,
                                "attempts": 1,
                                "error": None,
                                "created_at": "2025-01-01T00:00:00Z",
                                "next_retry_at": None,
                            }
                        ],
                        "pagination": {"next_cursor": None, "has_more": False},
                    },
                )
            )
            with Fdbck(API_KEY) as client:
                page = client.questions.webhooks("q_123")
                assert len(page["data"]) == 1
                assert page["data"][0]["event"] == "question.response_received"
