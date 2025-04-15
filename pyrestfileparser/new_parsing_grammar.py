import re

DELIMITER_LINE_MATCHER = re.compile(r'^\s*#{3,}.*$')
DELIMITER_LINE_PATTERN = r'(^\s*#{3,}.*(?:\n|$))'

def split_along_delimiters(text):
    parts = re.split(DELIMITER_LINE_PATTERN, text, flags=re.MULTILINE)

    blocks = []
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
                blocks.append(block.strip())
            pending_delim = ""
    return blocks


def is_empty(line: str) -> bool:
    """
    Checks if a line is empty or consists only of whitespace.
    """
    return not line.strip()


def parse_block(text: str) -> dict[str, str]:
    lines = text.splitlines()
    current_line = 0
    num_lines = len(lines)

    while current_line < num_lines and is_empty(lines[current_line]):
        current_line += 1
    if current_line < num_lines and DELIMITER_LINE_MATCHER.match(lines[current_line]):
        current_line += 1

    while current_line < num_lines and is_empty(lines[current_line]):
        current_line += 1

    if current_line >= num_lines:
        return {"request_line": "", "maybe_headers": "", "maybe_body": ""}

    request_line = lines[current_line].rstrip()
    current_line += 1

    maybe_header_lines = []
    while current_line < num_lines and not is_empty(lines[current_line]):
        maybe_header_lines.append(lines[current_line].rstrip())
        current_line += 1

    maybe_body_lines = []
    if current_line < num_lines and not lines[current_line].strip():
        while current_line < num_lines and is_empty(lines[current_line]):
            current_line += 1

        maybe_body_lines = [line.rstrip() for line in lines[current_line:]]

    if maybe_body_lines:
        parsed_header = "\n".join(maybe_header_lines).strip()
        parsed_body = "\n".join(maybe_body_lines).strip()
    else:
        parsed_header = "\n".join(maybe_header_lines).strip()
        parsed_body = None
    return {
        "request_line": request_line,
        "headers": parsed_header,
        "body": parsed_body,
    }


def parse_rest_file_text(text: str) -> list[dict[str, str]]:
    """
    Parses the given text into a list of request blocks.
    Each block is represented as a dictionary with keys 'request_line', 'headers', and 'body'.
    """
    blocks = split_along_delimiters(text)
    parsed_blocks = [parse_block(block) for block in blocks if block.strip()]
    return parsed_blocks