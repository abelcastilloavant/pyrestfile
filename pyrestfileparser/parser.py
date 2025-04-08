# rest_parser.py
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pyrestfileparser.parsing_grammar import REST_PARSER


@dataclass
class HTTPRequest:
    """Dataclass representing a parsed HTTP request."""

    method: str
    url: str
    http_version: str
    headers: Dict[str, str] = field(default_factory=dict)
    content_type: Optional[str] = None
    body: Optional[str] = None


def process_block(block) -> HTTPRequest:
    """
    Convert a parsed request block into an HTTPRequest instance.
    Checks that if a body is present, the Content-Type header includes 'application/json'
    and that the body is valid JSON.
    """
    method = block.get("method", "GET")
    url = block["url"]
    http_version = block.get("http_version", "")

    headers = {}
    if "headers" in block:
        for key, value in block["headers"].items():
            headers[key] = value.strip()

    body = block.get("body", "").strip()
    content_type = headers.get("Content-Type", "")

    if body and "application/json" in content_type.lower():
        try:
            json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Content-Type is {content_type} but body is invalid json: {e}")

    return HTTPRequest(
        method=method, url=url, http_version=http_version, headers=headers, content_type=content_type, body=body
    )


def parse_rest_file(text: str) -> List[HTTPRequest]:
    """
    Parse the input .rest file text and return a list of HTTPRequest objects.
    """
    parsed = REST_PARSER.parseString(text, parseAll=True)
    return [process_block(block) for block in parsed]
