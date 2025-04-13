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

DELIMITER_LINE_PATTERN = r"#{3,}"
COMMENT_LINE_PATTERN = r"\s*(#|//).*"
NON_WHITESPACE_CHARS_PATTERN = r"\S+"

SUPRESSED_NEWLINE = LineEnd().suppress()
DELIMITER = LineStart() + Regex(DELIMITER_LINE_PATTERN) + SUPRESSED_NEWLINE
COMMENT_LINE = Suppress(LineStart() + Regex(COMMENT_LINE_PATTERN) + (LineEnd() | StringEnd()))


def request_line_definition():
    """Defines the request line: an optional method, a URL, and an optional HTTP version."""
    method = Word(alphas, min=1).setResultsName("method").setParseAction(lambda t: t[0].upper())
    url = Regex(NON_WHITESPACE_CHARS_PATTERN).setResultsName("url")
    http_version = Combine(Literal("HTTP/") + Word("0123456789.")).setResultsName("http_version")
    return Optional(method + White()) + url + Optional(White() + http_version) + (LineEnd() | StringEnd())


def headers_definition():
    """Defines headers as zero or more header lines."""
    header_name = Word(alphanums + "-")
    header = Group(LineStart() + header_name("name") + Suppress(":") + restOfLine("value") + (LineEnd() | StringEnd()))
    header_or_comment = header | COMMENT_LINE
    return PPDict(ZeroOrMore(header_or_comment))


def body_definition():
    """Defines the body as all text until the next delimiter or end-of-file."""
    # We need to handle the case where there is no delimiter
    # at the end of the body because it's the last request
    # block in the file.
    return SkipTo(DELIMITER | StringEnd(), include=False).setResultsName("body")


def request_block_definition():
    """Defines a complete request block (request line, headers, body, and an optional trailing delimiter)."""
    req_line = request_line_definition()
    hdrs = headers_definition()
    bdy = body_definition()
    return Group(
        ZeroOrMore(COMMENT_LINE | SUPRESSED_NEWLINE)
        + req_line("request_line")
        + ZeroOrMore(COMMENT_LINE)
        + Optional(hdrs("headers"))
        + SUPRESSED_NEWLINE
        + Optional(bdy)
        + Optional(DELIMITER)
    )("request")


REST_PARSER = OneOrMore(request_block_definition()) + StringEnd()
