"""Screenshot capture utilities using MSS."""

from pathlib import Path
from typing import Tuple

from mss import mss
from PIL import Image


def capture_region(bbox: Tuple[int, int, int, int], output_path: str) -> None:
    """
    Capture a screenshot of a specific screen region.

    Uses the MSS library for fast, efficient region-based capture.
    Automatically creates parent directories if they don't exist.

    Args:
        bbox: Bounding box tuple (left, top, right, bottom) in screen coordinates
        output_path: File path where screenshot will be saved (PNG format)

    Raises:
        ValueError: If window dimensions are invalid (width or height <= 0)
        OSError: If screenshot cannot be saved to the specified path

    Example:
        >>> bbox = (100, 100, 800, 600)
        >>> capture_region(bbox, "screenshot.png")
    """
    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top

    # Validate dimensions
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid window dimensions: {width}x{height}. "
            f"Window may be minimized or off-screen."
        )

    # Ensure output directory exists
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Define monitor region for MSS
    monitor = {"left": left, "top": top, "width": width, "height": height}

    # Capture and save
    with mss() as sct:
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(str(output_path_obj), "PNG")


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
