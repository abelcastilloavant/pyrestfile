from pyrestfile.request_block_grammar import unpack_request_block
from pyrestfile.top_level_grammar import RequestBlock


def test_unpack_request_block_full():
    """
    Test a full request block including description, a complete request line, headers,
    and a JSON body.
    """
    block = RequestBlock(
        description="My Test Request",
        request_line="GET http://example.com/path HTTP/1.1",
        headers="Content-Type: application/json\nAuthorization: Bearer abc123",
        body='{"key": "value"}',
    )
    req = unpack_request_block(block)
    assert req.description == "My Test Request"
    assert req.method == "GET"
    assert req.url == "http://example.com/path"
    assert req.http_version == "HTTP/1.1"
    # In the unpacking, Content-Type is separated from other headers.
    assert req.content_type.lower() == "application/json"
    assert req.headers.get("Authorization") == "Bearer abc123"
    assert req.body == '{"key": "value"}'


def test_unpack_request_block_no_headers_no_body():
    """
    Test a block with no headers and no body.
    """
    block = RequestBlock(
        description="No Headers or Body",
        request_line="DELETE http://example.com/item/123 HTTP/1.1",
        headers="",
        body="",
    )
    req = unpack_request_block(block)
    assert req.description == "No Headers or Body"
    assert req.method == "DELETE"
    assert req.url == "http://example.com/item/123"
    assert req.http_version == "HTTP/1.1"
    # No headers should result in an empty dictionary.
    assert req.headers == {}
    assert req.content_type == ""
    # Body is empty so, in our implementation, it should be an empty string.
    assert req.body == ""


def test_unpack_request_block_with_extra_whitespace():
    """
    Test that extra whitespace is removed appropriately from the request line and headers.
    """
    block = RequestBlock(
        description="Whitespace Test",
        request_line="  PUT http://example.com/update HTTP/2.0  ",
        headers="  Content-Type:   text/plain  \n   X-Custom:   value   ",
        body="  Some body text  \n  with extra spaces  ",
    )
    req = unpack_request_block(block)
    assert req.description == "Whitespace Test"
    # The unpacking function should normalize spacing in the request line.
    assert req.method == "PUT"
    assert req.url == "http://example.com/update"
    assert req.http_version == "HTTP/2.0"
    # Header values should be trimmed.
    assert req.content_type.lower() == "text/plain"
    assert req.headers.get("X-Custom") == "value"
    # The body should be rendered as-is (after trimming exterior spaces).
    assert req.body == "Some body text  \n  with extra spaces"
