# parser_grammar.py
from pyparsing import (
    Word,
    alphas,
    alphanums,
    Optional,
    Combine,
    Literal,
    White,
    restOfLine,
    LineEnd,
    OneOrMore,
    Group,
    Dict as PPDict,
    Regex,
    StringEnd,
    Suppress,
    SkipTo,
    LineStart,
    ZeroOrMore,
)

# Suppress newline (CRLF)
CRLF = LineEnd().suppress()

# Define a delimiter: a line starting with at least three '#' characters.
DELIMITER = LineStart() + Regex(r"#{3,}") + LineEnd().suppress()


def request_line_definition():
    """Defines the request line: an optional method, a URL, and an optional HTTP version."""
    method = Word(alphas.upper(), min=1)("method")
    url = Regex(r"\S+").setResultsName("url")
    http_version = Combine(Literal("HTTP/") + Word("0123456789.")).setResultsName("http_version")
    return Optional(method + White()) + url + Optional(White() + http_version)


def headers_definition():
    """Defines headers as zero or more header lines."""
    header_name = Word(alphanums + "-")
    header = Group(header_name("name") + Suppress(":") + restOfLine("value") + CRLF)
    return PPDict(ZeroOrMore(header))


def body_definition():
    """Defines the body as all text until the next delimiter or end-of-file."""
    # Use StringEnd() as an alternative so that if no delimiter is found, the body goes to the end.
    return SkipTo(DELIMITER | StringEnd(), include=False).setResultsName("body")


def request_block_definition():
    """Defines a complete request block (request line, headers, body, and an optional trailing delimiter)."""
    req_line = request_line_definition()
    hdrs = headers_definition()
    bdy = body_definition()
    return Group(
        req_line("request_line")
        + CRLF
        + Optional(hdrs("headers"))
        + Optional(CRLF)
        + Optional(bdy)
        + Optional(DELIMITER)  # Consume the delimiter if present.
    )("request")


# The complete parser: one or more request blocks until end-of-file.
REST_PARSER = OneOrMore(request_block_definition()) + StringEnd()
