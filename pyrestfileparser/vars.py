import re
import time
import uuid

from pyrestfileparser.http_request import HTTPRequest


OPTIONAL_WHITESPACE = r"\s*"
LINE_START = r"^" + OPTIONAL_WHITESPACE
VAR_NAME_GROUP = r"@(\w+)"
PADDED_EQ_SIGN = OPTIONAL_WHITESPACE + r"=" + OPTIONAL_WHITESPACE
VALUE_GROUP = r"(.+)$"
VAR_DECLARATION_REGEX = LINE_START + VAR_NAME_GROUP + PADDED_EQ_SIGN + VALUE_GROUP
VAR_DECLARATION_PATTERN = re.compile(VAR_DECLARATION_REGEX, re.M)

DOUBLE_LEFT_BRACE = r"{{"
VAR_REFERENCE_GROUP = r"([\w.-]+)"
DOUBLE_RIGHT_BRACE = r"}}"
VAR_REFERENCE_REGEX = (
    DOUBLE_LEFT_BRACE + OPTIONAL_WHITESPACE + VAR_REFERENCE_GROUP + OPTIONAL_WHITESPACE + DOUBLE_RIGHT_BRACE
)
VAR_REFERENCE_PATTERN = re.compile(VAR_REFERENCE_REGEX)


BUILTINS = {
    "$timestamp": lambda: str(int(time.time())),
    "$uuid": lambda: str(uuid.uuid4()),
}


def collect_var_values(text: str) -> dict[str, str]:
    """Collects variable declarations from the given text."""
    vars_: dict[str, str] = {}
    for match in VAR_DECLARATION_PATTERN.finditer(text):
        name = match.group(1).strip()
        value = match.group(2).strip()
        vars_[name] = value
    return vars_


def strip_var_declarations(text: str) -> str:
    """Strips variable declarations from the given text."""
    lines = text.splitlines()
    return "\n".join(line for line in lines if not VAR_DECLARATION_PATTERN.match(line))


class Renderer:
    """Renders variables and builtins in template string."""

    def __init__(self, variables: dict[str, str]):
        self.variables = variables

    def render(self, request: HTTPRequest) -> HTTPRequest:
        """Render the HTTPRequest object by replacing variables and builtins in its attributes."""
        if request.method:
            request.method = self._render_string(request.method)
        if request.url:
            request.url = self._render_string(request.url)
        if request.body:
            request.body = self._render_string(request.body)
        if request.headers:
            for key, value in request.headers.items():
                request.headers[key] = self._render_string(value)
        return request

    def _render_string(self, template: str) -> str:
        return VAR_REFERENCE_PATTERN.sub(self._substitute, template)

    def _substitute(self, match):
        key = match.group(1)
        if key in BUILTINS:
            return BUILTINS[key]()
        default_value = match.group(0)
        return self.variables.get(key, default_value)
