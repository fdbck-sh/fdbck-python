# fdbck

[![PyPI](https://img.shields.io/pypi/v/fdbck)](https://pypi.org/project/fdbck/)

Official Python SDK for [fdbck](https://fdbck.sh) — a simple API to programmatically collect and structure feedback from your users.

Full type annotations included (PEP 561).

```python
from fdbck import Fdbck

client = Fdbck("sk_fdbck_...")

question = client.questions.create({
    "question": "How was your first purchase?",
    "type": "rating",
    "rating_config": {"min": 1, "max": 5},
    "expires_in": 172800,
})

token = client.tokens.create(question["id"], {
    "respondent": "user_8f2a",
})

# Send this URL to your user — they answer on fdbck's hosted page
print(token["respond_url"])

# Later, read the results
results = client.questions.results(question["id"])
print(results["data"])  # [{"respondent": "user_8f2a", "value": 5, ...}]
```

## Install

```sh
pip install fdbck
```

Requires Python 3.9 or later. Single dependency: `httpx`.

## Get your API key

Sign up at [dashboard.fdbck.sh](https://dashboard.fdbck.sh) and grab your API key from the **API Keys** page. Keys start with `sk_fdbck_`.

## Quick start

The typical workflow is: **create a question**, **generate a token** for each respondent, **collect their answer**, and **read the results**.

Respondents can answer via fdbck's hosted response page, or directly from your app using a UI SDK ([React](https://github.com/fdbck-sh), [Flutter](https://github.com/fdbck-sh)).

### 1. Create a question

```python
question = client.questions.create({
    "question": "How would you rate our onboarding?",
    "type": "rating",
    "rating_config": {
        "min": 1,
        "max": 5,
        "min_label": "Terrible",
        "max_label": "Loved it",
    },
    "expires_in": 86400,  # 24 hours
})
```

Four question types are available:

| Type | Description | Required fields | Response `value` |
|------|-------------|-----------------|------------------|
| `yes_no` | Yes or no (options default to `["Yes", "No"]`) | — | `"Yes"` or `"No"` |
| `single_choice` | Pick one option | `options` | `"Option A"` |
| `multiple_choice` | Pick one or more | `options` | `["Option A", "Option B"]` |
| `rating` | Numeric scale | `rating_config` | `4` |

### 2. Generate tokens

Each respondent gets a unique, single-use token that authorizes them to answer once.

```python
token = client.tokens.create(question["id"], {
    "respondent": "user_42",  # your internal user ID (optional)
})

# token["respond_url"] → https://fdbck.sh/f/V1StGXR8_Z5jdHi6
# token["expires_at"]  → ISO timestamp (1 hour from creation)
```

Send `token["respond_url"]` to your user however you like — email, in-app notification, SMS, etc. They open the link, answer on fdbck's hosted response page, and see a confirmation message.

You can also embed the question directly in your app using `fdbck-react` or `fdbck-flutter` — pass the `token["token"]` value to the UI component and it handles submission for you.

### 3. Read results

Poll for responses at any time — they're available as soon as respondents answer.

```python
results = client.questions.results(question["id"])

for response in results["data"]:
    print(response["respondent"], response["value"])
    # → "user_42", 5

# Results are paginated — follow the cursor for more
if results["pagination"]["has_more"]:
    next_page = client.questions.results(question["id"], {
        "cursor": results["pagination"]["next_cursor"],
    })
```

### 4. Or use webhooks

Get notified in real time instead of polling.

```python
question = client.questions.create({
    "question": "How was your experience?",
    "type": "yes_no",
    "expires_in": 86400,
    "webhook_url": "https://myapp.com/hooks/fdbck",
    "webhook_trigger": "each_response",  # or "expiry", "both"
})
```

Verify incoming webhooks with the signing secret:

```python
is_valid = client.verify_webhook(raw_body, signature, webhook_secret)
# signature = X-FDBCK-Signature header
# webhook_secret = question["webhook_secret"] from creation response
```

`verify_webhook` is also available as a standalone import if you don't need a client instance:

```python
from fdbck import verify_webhook
```

## API reference

### `Fdbck(api_key, *, base_url=..., timeout=...)`

| Option | Type | Default |
|--------|------|---------|
| `base_url` | `str` | `https://api.fdbck.sh` |
| `timeout` | `float` | `30.0` (seconds) |

Supports context manager usage:

```python
with Fdbck("sk_fdbck_...") as client:
    info = client.me()
```

### `AsyncFdbck(api_key, *, base_url=..., timeout=...)`

Same interface, async. Uses `httpx.AsyncClient` under the hood.

```python
from fdbck import AsyncFdbck

async with AsyncFdbck("sk_fdbck_...") as client:
    question = await client.questions.create({...})
```

### Questions

#### `client.questions.create(params)` → `Question`

Creates a new question.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | `str` | Yes | The question text (max 500 chars) |
| `type` | `QuestionType` | Yes | `yes_no`, `single_choice`, `multiple_choice`, or `rating` |
| `options` | `list[str]` | For choice types | 2–20 answer options |
| `rating_config` | `RatingConfig` | For `rating` | `{"min", "max", "min_label?", "max_label?"}` |
| `expires_in` or `expires_at` | `int` or `str` | Yes (exactly one) | Seconds from now, or ISO 8601 timestamp |
| `max_responses` | `int` | No | Auto-complete after N responses |
| `webhook_url` | `str` | No | HTTPS URL to receive events |
| `webhook_trigger` | `WebhookTrigger` | No | `each_response`, `expiry`, or `both` |
| `metadata` | `dict[str, str]` | No | Arbitrary key-value pairs |
| `theme_color` | `str` | No | Hex color for response page |
| `theme_mode` | `"light"` or `"dark"` | No | Response page theme |
| `hide_branding` | `bool` | No | Hide "Powered by fdbck" (paid plans) |

#### `client.questions.get(question_id)` → `Question`

Returns a single question by ID.

#### `client.questions.list(params?)` → `PaginatedList`

Returns a paginated list of questions.

```python
page = client.questions.list({"status": "collecting", "limit": 20})

print(page["data"])                       # list[Question]
print(page["pagination"]["has_more"])     # bool
print(page["pagination"]["next_cursor"])  # str | None
```

| Option | Type | Description |
|--------|------|-------------|
| `status` | `QuestionStatus` | Filter by `collecting`, `completed`, `expired`, or `cancelled` |
| `sort` | `str` | Sort by `created_at` or `updated_at` |
| `order` | `str` | Sort direction: `asc` or `desc` |
| `created_after` | `str` | ISO 8601 — only return questions created after this time |
| `created_before` | `str` | ISO 8601 — only return questions created before this time |
| `limit` | `int` | Items per page |
| `cursor` | `str` | Cursor from a previous page's `pagination["next_cursor"]` |

#### `client.questions.list_all(params?)` → `Iterator[Question]`

Auto-paginates through all questions. Same options as `list` except `cursor`.

```python
for question in client.questions.list_all({"status": "collecting"}):
    print(question["id"], question["question"])
```

Async version yields via `async for`.

#### `client.questions.results(question_id, params?)` → `QuestionResultsResponse`

Returns aggregated results and individual responses for a question.

```python
results = client.questions.results(question["id"], {"limit": 50})

print(results["total_responses"])  # 142
print(results["results"])          # {"average": 4.3, "distribution": {...}}
print(results["type"])             # "rating"
print(results["status"])           # "completed"

for response in results["data"]:
    print(response["respondent"])  # "user_42" or None
    print(response["value"])       # answer value
    print(response["created_at"])  # ISO timestamp
```

#### `client.questions.cancel(question_id)` → `Question`

Cancels a question and returns the cancelled question. It stops accepting responses immediately.

#### `client.questions.webhooks(question_id, params?)` → `PaginatedList`

Returns webhook delivery logs for a question. Same pagination options as `results`.

### Tokens

#### `client.tokens.create(question_id, params?)` → `TokenResult`

Generates a single-use respondent token.

```python
token = client.tokens.create(question["id"], {
    "respondent": "user_42",  # optional — your internal ID for this respondent
})

token["token"]        # the raw token string
token["respond_url"]  # full URL to the hosted response page
token["expires_at"]   # ISO timestamp (1 hour from creation)
```

### Account

```python
info = client.me()
# info["user"]         → {"id", "email", "name", "avatar_url"}
# info["organization"] → {"id", "name", "slug", "plan", "role", "responses_used", ...}
```

## Error handling

```python
from fdbck import FdbckApiError, FdbckNetworkError

try:
    client.questions.create({...})
except FdbckApiError as err:
    print(err.status)   # 401, 422, etc.
    print(err.code)     # "unauthorized", "validation_error", etc.
    print(err.args[0])  # Human-readable message
    print(err.details)  # {"fields": [...]} for validation errors
except FdbckNetworkError as err:
    print(err)          # Connection error, timeout, etc.
    print(err.__cause__)  # Original exception
```

## Requirements

- Python 3.9+
- An API key from [dashboard.fdbck.sh](https://dashboard.fdbck.sh)

## Links

- [Documentation](https://docs.fdbck.sh)
- [Dashboard](https://dashboard.fdbck.sh)
- [GitHub](https://github.com/fdbck-sh)

## License

MIT
