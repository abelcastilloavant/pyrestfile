import textwrap
from pyrestfileparser.parser import parse_rest_file


def _dedent(s: str) -> str:
    """Remove leading indentation and margin pipes used in multi‑line strings."""
    return textwrap.dedent(s).replace("│", "").lstrip("\n")


# ──────────────────────────────────────────────────────────────────────────────
# Comment handling tests
# ──────────────────────────────────────────────────────────────────────────────
def failing_test_comment_lines_are_ignored():
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
    assert r0.headers["Content-Type"] == "text/plain"
    assert "comment after body" in r0.body
    assert "comment between headers and body" not in r0.body
    assert "inside body" in r0.body

    assert r1.method == "GET"
