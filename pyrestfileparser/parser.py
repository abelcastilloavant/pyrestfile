from typing import List
from pyrestfileparser.top_level_grammar import parse_rest_file_text
from pyrestfileparser.http_request import HTTPRequest, unpack_request_block
from pyrestfileparser.vars import collect_var_values, Renderer, strip_var_declarations


def parse_rest_file(text: str, env: dict[str, str] = {}) -> List[HTTPRequest]:
    """
    Parse the input .rest file text and return a list of HTTPRequest objects.
    """
    inline_vars = collect_var_values(text)
    merged_vars = {**(env or {}), **inline_vars}
    renderer = Renderer(merged_vars)

    cleaned_text = strip_var_declarations(text)
    unprocessed_blocks = parse_rest_file_text(cleaned_text)
    requests = []
    for block in unprocessed_blocks:
        request_with_var_placeholders = unpack_request_block(block)
        request = renderer.render(request_with_var_placeholders)
        requests.append(request)

    return requests
