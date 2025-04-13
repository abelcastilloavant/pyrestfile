import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pyrestfileparser.parsing_grammar import REST_PARSER
from pyrestfileparser.vars import collect_var_values, Renderer, strip_var_declarations


@dataclass
class HTTPRequest:
    """Dataclass representing a parsed HTTP request."""

    method: str
    url: str
    http_version: str
    headers: Dict[str, str] = field(default_factory=dict)
    content_type: Optional[str] = None
    body: Optional[str] = None


def process_block(block, renderer: Renderer) -> HTTPRequest:
    """
    Convert a parsed request block into an HTTPRequest instance.
    Checks that if a body is present, the Content-Type header includes 'application/json'
    and that the body is valid JSON.
    """
    method = block.get("method", "GET")
    url = renderer.render(block["url"])
    http_version = block.get("http_version", "")

    headers = {}
    if "headers" in block:
        for _, result in block["headers"].items():
            key = result.get("name", "").strip()
            value = result.get("value", "").strip()
            if key and value:
                headers[key] = renderer.render(value)

    body = block.get("body", "").strip()
    if body:
        body = renderer.render(body)
    content_type = headers.get("Content-Type", "")

    if body and "application/json" in content_type.lower():
        try:
            json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Content-Type is {content_type} but body is invalid json: {e}")

    return HTTPRequest(
        method=method, url=url, http_version=http_version, headers=headers, content_type=content_type, body=body
    )


def parse_rest_file(text: str, env: dict[str, str] = {}) -> List[HTTPRequest]:
    """
    Parse the input .rest file text and return a list of HTTPRequest objects.
    """
    inline_vars = collect_var_values(text)
    merged_vars = {**(env or {}), **inline_vars}
    renderer = Renderer(merged_vars)

    cleaned_text = strip_var_declarations(text)
    parsed = REST_PARSER.parseString(cleaned_text, parseAll=True)
    return [process_block(block, renderer) for block in parsed]
