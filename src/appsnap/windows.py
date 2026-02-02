"""Window enumeration and finding utilities for Windows."""

import ctypes
from typing import Dict, List, Optional

import win32gui
from fuzzywuzzy import process

# DPI awareness setup (from Windows-MCP pattern)
PROCESS_PER_MONITOR_DPI_AWARE = 2


def setup_dpi_awareness() -> None:
    """
    Set up DPI awareness for accurate window coordinate retrieval.

    Uses Per-Monitor DPI Awareness (v2) if available, falls back to basic DPI awareness.
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
    except Exception:
        # Fallback for older Windows versions
        ctypes.windll.user32.SetProcessDPIAware()


def find_all_windows() -> List[Dict[str, any]]:
    """
    Enumerate all visible windows with titles.

    Returns:
        List of window dictionaries containing:
            - handle: Window handle (HWND)
            - title: Window title text
            - bbox: Bounding box tuple (left, top, right, bottom)
    """
    windows = []

    def callback(hwnd, _):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Only include windows with titles
                try:
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    # Filter out windows with invalid dimensions
                    if right > left and bottom > top:
                        windows.append(
                            {
                                "handle": hwnd,
                                "title": title,
                                "bbox": (left, top, right, bottom),
                            }
                        )
                except Exception:
                    # Skip windows that can't be queried
                    pass

    win32gui.EnumWindows(callback, None)
    return windows


def find_window(window_name: str, threshold: int = 70) -> Optional[Dict[str, any]]:
    """
    Find a window by fuzzy name matching.

    Args:
        window_name: Window title to search for (partial matches supported)
        threshold: Fuzzy match threshold 0-100 (default 70).
                  Higher = stricter matching, lower = more lenient.

    Returns:
        Window dictionary with handle, title, and bbox, or None if not found.

    Example:
        >>> window = find_window("Visual Studio")
        >>> if window:
        ...     print(f"Found: {window['title']}")
        ...     print(f"Bbox: {window['bbox']}")
    """
    windows = find_all_windows()
    if not windows:
        return None

    # Create mapping of titles to window data
    window_titles = {w["title"]: w for w in windows}

    # Fuzzy match against all window titles
    match = process.extractOne(
        window_name, list(window_titles.keys()), score_cutoff=threshold
    )

    if match:
        matched_title = match[0]
        return window_titles[matched_title]

    return None


def get_window_list_formatted() -> List[str]:
    """
    Get a sorted list of all window titles for display.

    Returns:
        Sorted list of window title strings.
    """
    windows = find_all_windows()
    return sorted([w["title"] for w in windows])


# Initialize DPI awareness when module is imported
setup_dpi_awareness()
