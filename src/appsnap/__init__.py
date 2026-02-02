"""appsnap - Fast Windows screenshot tool for AI coding agents."""

__version__ = "0.1.0"
__author__ = "appsnap contributors"
__license__ = "MIT"

from appsnap.windows import find_all_windows, find_window
from appsnap.capture import capture_region

__all__ = [
    "find_all_windows",
    "find_window",
    "capture_region",
    "__version__",
]
