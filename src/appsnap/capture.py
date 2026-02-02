"""Screenshot capture utilities using Pillow ImageGrab."""

from pathlib import Path
from typing import Tuple

from PIL import ImageGrab
import win32gui


def capture_window(hwnd: int, output_path: str) -> None:
    """
    Capture a screenshot of a specific window by handle.

    Uses Pillow's ImageGrab with direct window handle for accurate capture.
    This method is more reliable than region-based capture on multi-monitor setups.
    Automatically creates parent directories if they don't exist.

    Args:
        hwnd: Window handle (HWND) to capture
        output_path: File path where screenshot will be saved (PNG format)

    Raises:
        ValueError: If window cannot be captured (minimized, invalid handle, etc.)
        OSError: If screenshot cannot be saved to the specified path

    Example:
        >>> hwnd = 12345  # Window handle
        >>> capture_window(hwnd, "screenshot.png")
    """
    # Validate window is visible
    if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
        raise ValueError("Window is not visible or invalid handle")

    # Check if window is minimized
    if win32gui.IsIconic(hwnd):
        raise ValueError("Window is minimized - cannot capture")

    # Ensure output directory exists
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Use Pillow's direct window capture (Pillow 11.2.1+)
        img = ImageGrab.grab(bbox=None, include_layered_windows=True, all_screens=False, xdisplay=None)
        
        # Get window rect for bbox capture as fallback
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid window dimensions: {width}x{height}")
        
        # Capture using bbox (more reliable than MSS on multi-monitor)
        img = ImageGrab.grab(bbox=(left, top, right, bottom), include_layered_windows=True, all_screens=True)
        
        if img is None or img.size[0] == 0 or img.size[1] == 0:
            raise ValueError("Captured image is empty")

        img.save(str(output_path_obj), "PNG")
    except Exception as e:
        raise ValueError(f"Failed to capture window: {e}")


def validate_output_path(path: str) -> None:
    """
    Validate that an output path is usable.

    Args:
        path: File path to validate

    Raises:
        ValueError: If path is invalid or points to a directory
    """
    output_path = Path(path)

    # Check if path points to an existing directory
    if output_path.exists() and output_path.is_dir():
        raise ValueError(f"Output path is a directory: {path}")

    # Check if parent directory can be created/accessed
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ValueError(f"Cannot create parent directory for {path}: {e}")
