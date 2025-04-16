"""Top-level grammar for parsing REST files.

This module provides functions to parse REST files into structured request blocks,
including handling delimiters, headers, and bodies. It uses regular expressions to 
identify and extract relevant parts of the text.

The main function here is `parse_rest_file_text`, which takes a string input and 
returns a list of `RequestBlock` objects for further unpacking.
"""

import re
from dataclasses import dataclass

@dataclass
class RequestBlock:
    description: str
    request_line: str
    headers: str
    body: str

DELIMITER_LINE_MATCHER = re.compile(r'^\s*#{3,}.*$')
DELIMITER_LINE_PATTERN = r'(^\s*#{3,}.*(?:\n|$))'

def split_along_delimiters(text):
    parts = re.split(DELIMITER_LINE_PATTERN, text, flags=re.MULTILINE)

    unprocessed_blocks = []
    pending_delim = ""

    for part in parts:
        if re.match(DELIMITER_LINE_PATTERN, part):
            pending_delim = part.rstrip('\n')
        else:
            if part.strip():
                if pending_delim:
                    block = pending_delim + "\n" + part.lstrip("\n")
                else:
                    block = part
                unprocessed_blocks.append(block.strip())
            pending_delim = ""
    return unprocessed_blocks


def is_comment_line(line: str) -> bool:
    """
    Returns True if the line is a comment.
    A comment line starts with '//' or with '#' but not '###' (i.e. not a delimiter).
    """
    s = line.strip()
    return s.startswith("//") or (s.startswith("#") and not s.startswith("###"))


def parse_block(unprocessed_block: str) -> RequestBlock:
    """
    Parses a block of text that corresponds to one request block into a RequestBlock object.
    """
    lines = iter(unprocessed_block.splitlines())

    def next_nonempty(iterator, skip_comments=True):
        for l in iterator:
            stop_here = bool(l.strip())
            if skip_comments:
                stop_here = stop_here and not is_comment_line(l)
            if stop_here:
                return l.rstrip()
        return None

    first_line = next_nonempty(lines, skip_comments=True)
    if first_line is None:
        return RequestBlock(description="", request_line="", headers="", body="")

    description = None
    if DELIMITER_LINE_MATCHER.match(first_line):
        m = re.match(r'^\s*#{3,}\s*(.*)$', first_line)
        if m:
            description = m.group(1).strip()
        first_line = next_nonempty(lines, skip_comments=True)

    request_line = first_line

    header_lines = []
    for line in lines:
        cleaned_line = line.strip()
        keep_this_line = cleaned_line and not is_comment_line(cleaned_line)
        if keep_this_line:
            header_lines.append(line.rstrip())
        else:
            break
    headers = "\n".join(header_lines).strip() if header_lines else ""

    first_body_line = next_nonempty(lines, skip_comments=False)
    if first_body_line:
        body_lines = [first_body_line.rstrip()]
        for line in lines:
            body_lines.append(line.rstrip())
        body = "\n".join(body_lines).strip()
    else:
        body = ""
        
    return RequestBlock(
        description=description,
        request_line=request_line,
        headers=headers,
        body=body
    )


def parse_rest_file_text(text: str) -> list[RequestBlock]:
    """
    Parses the given text into a list of request blocks.
    Each block is represented as a dictionary with keys 'request_line', 'headers', and 'body'.
    """
    unprocessed_blocks = split_along_delimiters(text)
    request_blocks = [parse_block(block) for block in unprocessed_blocks if block.strip()]
    return request_blocks