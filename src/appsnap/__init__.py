"""appsnap - Fast Windows screenshot tool for AI coding agents."""

__version__ = "0.1.2"
__author__ = "appsnap contributors"
__license__ = "MIT"

from appsnap.windows import find_all_windows, find_window
from appsnap.capture import capture_window as capture_window_screenshot

__all__ = [
    "find_all_windows",
    "find_window",
    "capture_window_screenshot",
    "__version__",
]
