from pyrestfile.top_level_grammar import parse_rest_file_text


def test_empty_text():
    text = ""
    result = parse_rest_file_text(text)
    assert result == []


def test_single_block_without_delimiter_no_body():
    text = """POST http://example.com/api
Content-Length: 123
Content-Type: text/plain
"""
    result = parse_rest_file_text(text)
    assert len(result) == 1
    block = result[0]

    assert block.request_line == "POST http://example.com/api"
    assert block.headers == "Content-Length: 123\nContent-Type: text/plain"
    assert block.body == ""


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

    assert block.request_line == "GET http://example.com HTTP/1.1"
    assert block.headers == "Content-Type: application/json\nAccept: */*"
    assert block.body == '{"key": "value"}'


def test_multiple_blocks():
    """
    The sample text simulates a REST file with three request blocks.
    Block 1: No leading delimiter. It contains a GET request with headers and a JSON body.
    Block 2: Has a delimiter line that includes extra text. It contains a POST request with headers and a form-encoded body.
    Block 3: Has a delimiter with extra text, and contains only a DELETE request (no headers or body).
    """
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

    block1 = result[0]
    assert block1.request_line == "GET http://example.com/resource HTTP/1.1"
    assert block1.headers == "Content-Type: application/json\nUser-Agent: TestClient"
    assert block1.body == '{\n  "query": "value"\n}'

    block2 = result[1]
    assert block2.request_line == "POST http://example.com/resource HTTP/1.1"
    assert block2.headers == "Content-Type: application/x-www-form-urlencoded"
    assert block2.body == "param1=foo&param2=bar"

    block3 = result[2]
    assert block3.request_line == "DELETE http://example.com/resource/123 HTTP/1.1"
    assert block3.headers == ""
    assert block3.body == ""


def test_block_no_headers_but_with_body():
    """
    Here, the request line is followed by one or more empty lines,
    after which group3 (the body) is present.
    """
    text = """GET http://example.com
     
Body starts here.
Second line of body.
"""
    result = parse_rest_file_text(text)
    assert len(result) == 1
    block = result[0]
    assert block.request_line == "GET http://example.com"
    assert block.headers == ""
    assert block.body == "Body starts here.\nSecond line of body."


def test_description_capture():
    sample_text = """### My REST request description
GET http://example.com/path HTTP/1.1
Content-Type: application/json

{"data": "sample"}
"""
    result = parse_rest_file_text(sample_text)
    assert len(result) == 1, "Expected a single request block"
    block = result[0]

    assert block.description == "My REST request description"
    assert block.request_line == "GET http://example.com/path HTTP/1.1"
    assert block.headers == "Content-Type: application/json"
    assert block.body == '{"data": "sample"}'
