"""pytest tests for pyrestfileparser
These tests cover:
1. Basic parsing of two well‑formed requests.
2. Handling of non‑JSON bodies with non‑JSON content‑type.
3. Raising a ValueError when the body is invalid JSON but the header claims application/json.
4. Correct stripping of full‑line comments in every legal position.
5. Acceptance of both # and // comment styles.
"""

import json
import textwrap

import pytest

from pyrestfileparser.parser import parse_rest_file, HTTPRequest

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _dedent(s: str) -> str:
    """Remove leading indentation and margin pipes used in multi‑line strings."""
    return textwrap.dedent(s).replace("│", "").lstrip("\n")


# ──────────────────────────────────────────────────────────────────────────────
# Happy‑path parsing
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
    assert r0.headers["Content-Type"] == "application/json"
    assert r0.headers["Authorization"] == "Bearer abc123"
    assert json.loads(r0.body) == {"key": "value"}

    r1: HTTPRequest = reqs[1]
    assert r1.method == "POST"
    assert r1.url == "https://api.example.com/submit"
    assert r1.http_version == "HTTP/1.1"
    assert r1.headers["Content-Type"] == "application/json"
    assert json.loads(r1.body) == {"message": "Hello, world!"}


# ──────────────────────────────────────────────────────────────────────────────
# Non‑JSON body with non‑JSON content type
# ──────────────────────────────────────────────────────────────────────────────


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
    assert r.headers["Content-Type"] == "text/plain"
    assert r.body == "Hello world!"


# ──────────────────────────────────────────────────────────────────────────────
# Invalid JSON body should raise
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
# Comment handling tests
# ──────────────────────────────────────────────────────────────────────────────
def test_comment_lines_are_ignored():
    sample = _dedent(
        """
        │### leading delimiter comment
        │# leading comment before request line
        │PATCH https://api.example.com/foo HTTP/1.1
        │# comment between request line and headers
        │Content-Type: text/plain
        │// comment inside header section
        │# comment between headers and body
        │
        │# inside body – should not be stripped
        │name=Ada
        │age=42
        │# comment after body
        │###
        │// comment before second request
        │GET https://api.example.com/bar
        │Accept: application/json
        │
        │### trailing delimiter
        """
    )
    reqs = parse_rest_file(sample)
    assert len(reqs) == 2

    r0, r1 = reqs
    assert r0.method == "PATCH"
    assert r1.method == "GET"
    assert "inside body" in r0.body


def test_comment_styles_hash_and_slash():
    sample = _dedent(
        """
        │# hash comment
        │// double‑slash comment
        │PATCH https://api.example.com/baz
        │X-Foo: bar
        │
        │###
        """
    )

    reqs = parse_rest_file(sample)
    assert len(reqs) == 1
    r = reqs[0]
    assert r.method == "PATCH"
    assert r.headers["X-Foo"] == "bar"

def test_mixed_case_methods_are_normalised():
    sample = "patch https://api.example.com/foo\n\n"
    req = parse_rest_file(sample)[0]
    assert req.method == "PATCH"