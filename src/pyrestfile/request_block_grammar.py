import json
import re
from dataclasses import dataclass, field
from typing import Dict
from pyrestfile.top_level_grammar import RequestBlock


REQUEST_LINE_REGEX = r"^(?P<method>[a-zA-Z]+)\s+(?P<url>\S+)(?:\s+(?P<version>HTTP/\S+))?"
REQUEST_LINE_PATTERN = re.compile(REQUEST_LINE_REGEX)


@dataclass
class ParsedRequestLine:
    """Dataclass representing a parsed request line."""

    method: str
    url: str
    http_version: str = ""


@dataclass
class ParsedHeaders:
    """Dataclass representing parsed headers."""

    headers: Dict[str, str]
    content_type: str = ""


@dataclass
class HTTPRequest:
    """Dataclass representing a parsed HTTP request."""

    description: str
    method: str
    url: str
    http_version: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    content_type: str = ""
    body: str = ""


def unpack_request_line(request_line: str) -> ParsedRequestLine:
    """
    Unpacks the request line into its components: method, URL, and optional HTTP version.
    If a method is not present, defaults to GET.
    Example:
      "GET http://example.com/path HTTP/1.1" becomes
      {"method": "GET", "url": "http://example.com/path", "version": "HTTP/1.1"}
    """

    matched_values = REQUEST_LINE_PATTERN.match(request_line.strip())
    if not matched_values:
        return ParsedRequestLine(method="GET", url=request_line.strip(), http_version="")
    groups = matched_values.groupdict()
    method = groups.get("method", "GET").upper()
    url = groups.get("url", "").strip() if groups.get("url") else ""
    version = groups.get("version", "").strip() if groups.get("version") else ""
    return ParsedRequestLine(method=method, url=url, http_version=version)


def unpack_headers(headers: str) -> ParsedHeaders:
    """
    Unpacks header lines into a dictionary mapping header names to their values.
    Each header is expected to be formatted as "Header-Name: value".
    """
    header_dict = {}
    for line in headers.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            header_dict[key.strip()] = value.strip()
    if "Content-Type" in header_dict:
        content_type = header_dict.pop("Content-Type", "").strip()
    else:
        content_type = ""
    return ParsedHeaders(headers=header_dict, content_type=content_type)


def unpack_request_block(block: "RequestBlock") -> HTTPRequest:
    """
    Unpacks the RequestBlock into a ParsedRequest with a structured request line
    and headers. Uses unpack_request_line() and unpack_headers() internally.
    """
    parsed_request_line = unpack_request_line(block.request_line)
    parsed_headers = unpack_headers(block.headers)

    body = block.body.strip() if block.body else ""
    if parsed_headers.content_type and "application/json" in parsed_headers.content_type.lower():
        try:
            json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Content-Type is {parsed_headers.content_type} but body is invalid JSON: {e}")

    return HTTPRequest(
        description=block.description,
        method=parsed_request_line.method,
        url=parsed_request_line.url,
        http_version=parsed_request_line.http_version,
        headers=parsed_headers.headers,
        content_type=parsed_headers.content_type,
        body=body,
    )
