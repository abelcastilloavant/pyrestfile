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

# Suppress newline (CRLF)
CRLF = LineEnd().suppress()

DELIMITER = LineStart() + Regex(DELIMITER_LINE_PATTERN) + LineEnd().suppress()

# Comments in .rest files are lines starting with '#' or '//'.
COMMENT_LINE = Suppress(LineStart() + Regex(COMMENT_LINE_PATTERN) + LineEnd())


def request_line_definition():
    """Defines the request line: an optional method, a URL, and an optional HTTP version."""
    method = Word(alphas.upper(), min=1)("method")
    url = Regex(NON_WHITESPACE_CHARS_PATTERN).setResultsName("url")
    http_version = Combine(Literal("HTTP/") + Word("0123456789.")).setResultsName("http_version")
    return Optional(method + White()) + url + Optional(White() + http_version)

def headers_definition():
    """Defines headers as zero or more header lines."""
    header_name = Word(alphanums + "-")
    header = Group(header_name("name") + Suppress(":") + restOfLine("value") + CRLF)
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
        ZeroOrMore(COMMENT_LINE | CRLF)
        + req_line("request_line")
        + CRLF
        + Optional(hdrs("headers") + CRLF)
        + Optional(bdy)
        # If we don't consume the delimiter after the body,
        # it will cause parsing issues for the next block.
        + Optional(DELIMITER)
    )("request")



REST_PARSER = OneOrMore(request_block_definition()) + StringEnd()
