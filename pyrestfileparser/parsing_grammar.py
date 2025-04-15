from pyparsing import (
    FollowedBy,
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

DELIMITER_LINE_PATTERN = r"#{3,}"
COMMENT_LINE_PATTERN = r"(?:\s*#.*|\s*//.*)"
NON_WHITESPACE_CHARS_PATTERN = r"\S+"

DELIMITER = LineStart() + Regex(DELIMITER_LINE_PATTERN) + LineEnd()
COMMENT_LINE = LineStart() + Regex(COMMENT_LINE_PATTERN) + LineEnd()
EMPTY_LINE = Group(LineStart() + Optional(White(" \t")) + LineEnd())

def request_line_definition():
    """Defines the request line: an optional method, a URL, and an optional HTTP version."""
    method = Word(alphas, min=1).setResultsName("method")
    url = Regex(NON_WHITESPACE_CHARS_PATTERN).setResultsName("url")
    http_version = Combine(Literal("HTTP/") + Word("0123456789.")).setResultsName("http_version")
    return (LineStart() + Optional(method + White()) + url + Optional(White() + http_version) + LineEnd())("request_line")


def headers_definition():
    """Defines headers as zero or more header lines."""
    header_name = Word(alphanums + "-")
    header = Group(
        LineStart()
        + FollowedBy(Word(alphanums + "-") + ":")
        + header_name("name")
        + Literal(":")
        + restOfLine("value")
        + LineEnd()
    )
    header_or_comment = header | Group(COMMENT_LINE)
    headers_body = ZeroOrMore(header_or_comment)
    
    return PPDict(headers_body)("headers")


def body_definition():
    """Defines the body as all text until the next delimiter or end-of-file."""
    # We need to handle the case where there is no delimiter
    # at the end of the body because it's the last request
    # block in the file.
    return LineStart() + SkipTo(DELIMITER | StringEnd(), include=False).setResultsName("body")


def request_block_definition():
    """Defines a complete request block (request line, headers, body, and an optional trailing delimiter)."""
    req_line = request_line_definition()
    hdrs = headers_definition()
    bdy = body_definition()
    return Group(
        ZeroOrMore(COMMENT_LINE)
        + req_line
        + hdrs
        + Optional(bdy)
        + Optional(DELIMITER)
    )("request")


REST_PARSER = OneOrMore(request_block_definition()) + StringEnd()
