import pytest

# Import the API function from your module (adjust module name as needed)
from pyrestfileparser.new_parsing_grammar import parse_rest_file_text

# ---------------------------
# Test: Empty text
# ---------------------------
def test_empty_text():
    text = ""
    result = parse_rest_file_text(text)
    assert result == []


# ---------------------------
# Test: Single block without a delimiter and no explicit body
# ---------------------------
def test_single_block_without_delimiter_no_body():
    # In this case, there's no delimiter, and the block is only a request line with headers.
    text = """POST http://example.com/api
Content-Length: 123
Content-Type: text/plain
"""
    result = parse_rest_file_text(text)
    assert len(result) == 1
    block = result[0]
    # The first nonempty line is the request line.
    assert block["request_line"] == "POST http://example.com/api"
    # The subsequent nonempty lines become the headers.
    expected_headers = "Content-Length: 123\nContent-Type: text/plain"
    assert block["headers"] == expected_headers
    # Since there's no blank line, no body was provided; expect body to be None.
    assert block["body"] is None


# ---------------------------
# Test: Single block with an optional delimiter and a body
# ---------------------------
def test_single_block_with_delimiter_and_body():
    text = """### Optional delimiter line
GET http://example.com HTTP/1.1
Content-Type: application/json
Accept: */*

{"key": "value"}
"""
    result = parse_rest_file_text(text)
    assert len(result) == 1
    block = result[0]
    # The parser should skip the delimiter and use the next nonempty line as the request line.
    assert block["request_line"] == "GET http://example.com HTTP/1.1"
    expected_headers = "Content-Type: application/json\nAccept: */*"
    assert block["headers"] == expected_headers
    expected_body = '{"key": "value"}'
    assert block["body"] == expected_body

# ---------------------------
# Test: Multiple blocks using a REST-like file
# ---------------------------
def test_multiple_blocks():
    # The sample text simulates a REST file with three request blocks.
    # Block 1: No leading delimiter. It contains a GET request with headers and a JSON body.
    # Block 2: Has a delimiter line that includes extra text. It contains a POST request with headers and a form-encoded body.
    # Block 3: Has a delimiter with extra text, and contains only a DELETE request (no headers or body).
    text = """GET http://example.com/resource HTTP/1.1
Content-Type: application/json
User-Agent: TestClient

{
  "query": "value"
}
### POST Request to create resource
POST http://example.com/resource HTTP/1.1
Content-Type: application/x-www-form-urlencoded

param1=foo&param2=bar
### DELETE Request
DELETE http://example.com/resource/123 HTTP/1.1
"""
    result = parse_rest_file_text(text)
    assert len(result) == 3

    # Block 1: No leading delimiter.
    block1 = result[0]
    # Request line should be the GET request.
    assert block1["request_line"] == "GET http://example.com/resource HTTP/1.1"
    expected_headers1 = "Content-Type: application/json\nUser-Agent: TestClient"
    assert block1["headers"] == expected_headers1
    expected_body1 = '{\n  "query": "value"\n}'
    assert block1["body"] == expected_body1

    # Block 2: Preceded by a delimiter with extra text.
    block2 = result[1]
    assert block2["request_line"] == "POST http://example.com/resource HTTP/1.1"
    expected_headers2 = "Content-Type: application/x-www-form-urlencoded"
    assert block2["headers"] == expected_headers2
    expected_body2 = "param1=foo&param2=bar"
    assert block2["body"] == expected_body2

    # Block 3: Preceded by a delimiter with extra text.
    block3 = result[2]
    assert block3["request_line"] == "DELETE http://example.com/resource/123 HTTP/1.1"
    # No headers or body, so headers should be empty and body should be None.
    assert block3["headers"] == ""
    assert block3["body"] is None


# ---------------------------
# Test: Block with no headers but with a body
# ---------------------------
def test_block_no_headers_but_with_body():
    # Here, the request line is followed by one or more empty lines,
    # after which group3 (the body) is present.
    text = """GET http://example.com
     
Body starts here.
Second line of body.
"""
    result = parse_rest_file_text(text)
    assert len(result) == 1
    block = result[0]
    assert block["request_line"] == "GET http://example.com"
    # Expect no headers if no nonempty lines follow the request line until the blank line.
    assert block["headers"] == ""
    expected_body = "Body starts here.\nSecond line of body."
    assert block["body"] == expected_body
