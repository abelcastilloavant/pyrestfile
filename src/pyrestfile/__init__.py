from importlib.metadata import version, PackageNotFoundError

from pyrestfile.parser import parse_rest_file
from pyrestfile.request_block_grammar import HTTPRequest

try:
    __version__ = version(__package__ or "pyrestfileparser")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "parse_rest_file",
    "HTTPRequest",
]
