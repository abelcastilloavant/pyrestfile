import json
import textwrap
import pytest

from pyrestfile.parser import parse_rest_file, HTTPRequest

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _dedent(s: str) -> str:
    """Remove leading indentation and margin pipes used in multi‑line strings."""
    return textwrap.dedent(s).replace("│", "").lstrip("\n")


# ──────────────────────────────────────────────────────────────────────────────
# Happy‑path parsing tests
# ──────────────────────────────────────────────────────────────────────────────


def test_parse_two_valid_requests():
    sample = _dedent(
        """
        │GET https://api.example.com HTTP/1.1
        │Content-Type: application/json
        │Authorization: Bearer abc123
        │
        │{"key": "value"}
        │###
        │POST https://api.example.com/submit HTTP/1.1
        │Content-Type: application/json
        │
        │{"message": "Hello, world!"}
        """
    )
    reqs = parse_rest_file(sample)
    assert len(reqs) == 2

    r0: HTTPRequest = reqs[0]
    assert r0.method == "GET"
    assert r0.url == "https://api.example.com"
    assert r0.http_version == "HTTP/1.1"
    assert r0.content_type == "application/json"
    assert r0.headers["Authorization"] == "Bearer abc123"
    assert json.loads(r0.body) == {"key": "value"}

    r1: HTTPRequest = reqs[1]
    assert r1.method == "POST"
    assert r1.url == "https://api.example.com/submit"
    assert r1.http_version == "HTTP/1.1"
    assert r1.content_type == "application/json"
    assert json.loads(r1.body) == {"message": "Hello, world!"}


def test_plain_text_body_is_accepted():
    sample = _dedent(
        """
        │POST https://api.example.com/submit HTTP/1.1
        │Content-Type: text/plain
        │
        │Hello world!
        """
    )
    reqs = parse_rest_file(sample)
    assert len(reqs) == 1
    r: HTTPRequest = reqs[0]
    assert r.method == "POST"
    assert r.content_type == "text/plain"
    assert r.body == "Hello world!"


# ──────────────────────────────────────────────────────────────────────────────
# Error Handling for Invalid JSON
# ──────────────────────────────────────────────────────────────────────────────


def test_invalid_json_raises_value_error():
    sample = _dedent(
        """
        │POST https://api.example.com/submit HTTP/1.1
        │Content-Type: application/json
        │
        │{"message": "Hello, world!"  # missing closing brace
        """
    )
    with pytest.raises(ValueError):
        parse_rest_file(sample)


# ──────────────────────────────────────────────────────────────────────────────
# Comment filtering tests (outside of body)
# ──────────────────────────────────────────────────────────────────────────────


def test_comment_styles_hash_and_slash():
    sample = _dedent(
        """
        │# This is a hash comment that should be ignored
        │// This is a double-slash comment to be skipped as well
        │PATCH https://api.example.com/baz HTTP/1.1
        │X-Foo: bar
        """
    )
    reqs = parse_rest_file(sample)
    assert len(reqs) == 1
    r = reqs[0]
    assert r.method == "PATCH"
    assert r.headers["X-Foo"] == "bar"


def test_mixed_case_methods_are_normalised():
    sample = "patch https://api.example.com/foo HTTP/1.1\n\n"
    req = parse_rest_file(sample)[0]
    assert req.method == "PATCH"


# ──────────────────────────────────────────────────────────────────────────────
# Variable rendering in URL and headers
# ──────────────────────────────────────────────────────────────────────────────


def test_rendered_headers_and_url():
    text = _dedent(
        """
        │@token = abc123
        │GET https://{{host}}/v1/foo HTTP/1.1
        │Authorization: Bearer {{token}}
        │
        │
        """
    )
    parsed = parse_rest_file(text, env={"host": "api.example.com"})
    req = parsed[0]
    assert req.url == "https://api.example.com/v1/foo"
    assert req.headers["Authorization"] == "Bearer abc123"
