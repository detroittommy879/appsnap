"""Screenshot capture utilities using Win32 PrintWindow with fallback."""

import ctypes
from ctypes import windll
from pathlib import Path
import time

from PIL import Image, ImageGrab
import win32gui
import win32ui
import win32con


def capture_window(hwnd: int, output_path: str) -> None:
    """
    Capture a screenshot of a specific window by handle.

    Tries Win32 PrintWindow API first for direct window content capture.
    Falls back to screen region capture if PrintWindow fails (protected apps).

    Args:
        hwnd: Window handle (HWND) to capture
        output_path: File path where screenshot will be saved (PNG format)

    Raises:
        ValueError: If window cannot be captured
        OSError: If screenshot cannot be saved

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

    # Get window dimensions
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid window dimensions: {width}x{height}")

    # Ensure output directory exists
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Try PrintWindow first (works for most apps, even when partially occluded)
    try:
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        # PW_RENDERFULLCONTENT (0x00000002)
        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

        if result != 0:
            # PrintWindow succeeded
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            # Clean up
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            img.save(str(output_path_obj), "PNG")
            return

        # PrintWindow failed, clean up before fallback
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

    except Exception:
        pass  # Fall through to ImageGrab fallback

    # Fallback: Use PIL ImageGrab for screen region capture
    # This works for protected windows but requires them to be visible
    try:
        # Try to bring window to foreground for better capture
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.05)  # Brief pause for window to come to front
        except:
            pass  # Some windows don't allow foreground activation

        # Capture the screen region where the window is located
        img = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)

        if img is None or img.size[0] == 0 or img.size[1] == 0:
            raise ValueError("Captured image is empty")

        img.save(str(output_path_obj), "PNG")
        return

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
