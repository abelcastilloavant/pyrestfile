# pyrestfileparser

*Parse VS Code REST‑Client **`.rest`** files into plain Python objects you can feed to any HTTP client — perfect for load‑testing, fixtures, and scripting.*

---

## Why?

The VS Code REST‑Client extension is fantastic for ad‑hoc API calls, but its request files aren’t machine‑readable out of the box. **pyrestfileparser** lets you keep those same files in your repository and programmatically use them or validate them within Python.

## Features

- ✅  Parse multiple requests per file (separated by `###`).
- ✅  Preserve method, URL, headers, and body exactly as written.
- ✅  Ignore full‑line comments (`#` or `//`) in the same places VS Code does.
- ✅  Validate JSON bodies when `Content‑Type: application/json` is set.
- ✅  Zero runtime dependencies beyond **pyparsing**.

---

## Installation

```bash
# library only
pip install pyrestfileparser

# with dev / test tooling (pytest, coverage, pre‑commit)
pip install ".[dev]"
```

---

## Quick‑start

```python
from pyrestfileparser import parse_rest_file

with open("api.rest") as f:
    requests = parse_rest_file(f.read())

for req in requests:
    print(req.method, req.url)
```

`HTTPRequest` instances expose:

| attribute      | type             | example                                |
| -------------- | ---------------- | -------------------------------------- |
| `method`       | `str`            | `"POST"`                               |
| `url`          | `str`            | `"https://api.example.com/v1/users"`   |
| `http_version` | `str`            | `"HTTP/1.1"` (optional)                |
| `headers`      | `dict[str, str]` | `{"Content-Type": "application/json"}` |
| `body`         | `str` or None    | `"raw body text"`                      |

---

### Using with **Locust**

```python
# locustfile.py
import random
from locust import HttpUser, task, between
from pyrestfileparser import parse_rest_file

REQUESTS = parse_rest_file(open("api.rest").read())

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def random_call(self):
        r = random.choice(REQUESTS)
        self.client.request(
            method=r.method,
            url=r.url,
            headers=r.headers,
            data=r.body,
        )
```

Run with `locust -f locustfile.py`.

---

## Development & Testing

```bash
# create virtual env of your choice, then
pip install -e ".[dev]"
pre-commit install          # lint on every commit
pytest -q                   # run unit tests
```

### CI

A ready‑made GitHub Actions workflow (`.github/workflows/unit_tests_and_code_checks.yaml`) runs pre‑commit and pytest on every push.

---

## Roadmap

- Variable substitution (`@token = …`, `{{token}}`).
- File includes (`@file=./payload.json`).
- JavaScript test scripts (low priority).
- CLI (`pyrest run api.rest`).

PRs welcome!

---

## License

MIT © 2025 Abel Castillo

