# rest_parser.py
import json
from dataclasses import dataclass, field
from typing import Dict, List
from pyrestfileparser.parsing_grammar import REST_PARSER

@dataclass
class HTTPRequest:
    """Dataclass representing a parsed HTTP request."""
    method: str
    url: str
    http_version: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""

def process_block(block) -> HTTPRequest:
    """
    Convert a parsed request block into an HTTPRequest instance.
    Checks that if a body is present, the Content-Type header includes 'application/json'
    and that the body is valid JSON.
    """
    method_val = block.get("method", "GET")
    url_val = block["url"]
    http_ver = block.get("http_version", "")
    
    # Build headers dictionary.
    headers_dict = {}
    if "headers" in block:
        for key, value in block["headers"].items():
            headers_dict[key] = value.strip()
    
    # Extract and strip the body.
    body_val = block.get("body", "").strip()
    
    # If a body is present, enforce that Content-Type includes 'application/json' and it is valid JSON.
    if body_val:
        ct = headers_dict.get("Content-Type", "")
        if "application/json" not in ct.lower():
            raise ValueError(f"Body provided but Content-Type is not application/json: {ct}")
        try:
            json.loads(body_val)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON body: {e}")
    
    return HTTPRequest(
        method=method_val,
        url=url_val,
        http_version=http_ver,
        headers=headers_dict,
        body=body_val
    )

def parse_rest_file(text: str) -> List[HTTPRequest]:
    """
    Parse the input .rest file text and return a list of HTTPRequest objects.
    """
    parsed = REST_PARSER.parseString(text, parseAll=True)
    return [process_block(block) for block in parsed]
