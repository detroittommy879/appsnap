"""Main CLI entry point for appsnap."""

import argparse
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import NoReturn, Optional

from appsnap import __version__
from appsnap.capture import capture_region, validate_output_path
from appsnap.windows import find_window, get_window_list_formatted


def list_windows() -> None:
    """List all capturable windows and exit."""
    windows = get_window_list_formatted()

    if not windows:
        print("No windows found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(windows)} window(s):\n")
    for title in windows:
        print(f"  • {title}")

    sys.exit(0)


def generate_temp_path() -> str:
    """
    Generate a timestamped filename in the system temp directory.

    Returns:
        Full path to temp file like: /tmp/appsnap_YYYYMMDD_HHMMSS.png
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"appsnap_{timestamp}.png"
    temp_dir = Path(tempfile.gettempdir()) / "appsnap"
    temp_dir.mkdir(exist_ok=True)
    return str(temp_dir / filename)


def capture_window(
    window_name: str, output_path: Optional[str], threshold: int, json_output: bool
) -> None:
    """
    Capture a window screenshot and output the result.

    Args:
        window_name: Window title to search for
        output_path: Custom output path, or None for temp directory
        threshold: Fuzzy matching threshold (0-100)
        json_output: Whether to output JSON format
    """
    # Find the window
    window = find_window(window_name, threshold=threshold)

    if not window:
        print(
            f'Error: No window found matching "{window_name}" (threshold: {threshold})',
            file=sys.stderr,
        )
        print("\nTip: Use 'appsnap --list' to see all available windows", file=sys.stderr)
        print("     Or try lowering the threshold with '--threshold 60'", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if output_path is None:
        output_path = generate_temp_path()
    else:
        # Validate custom path
        try:
            validate_output_path(output_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Capture the screenshot
    try:
        capture_region(window["bbox"], output_path)
    except ValueError as e:
        print(f"Error capturing screenshot: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output results
    if json_output:
        result = {
            "path": str(Path(output_path).resolve()),
            "window": window["title"],
            "bbox": list(window["bbox"]),
        }
        print(json.dumps(result, indent=2))
    else:
        print(str(Path(output_path).resolve()))
        if output_path.startswith(tempfile.gettempdir()):
            print(f"Window: {window['title']}", file=sys.stderr)
            print(f"Note: Temp files may be auto-deleted by the system", file=sys.stderr)


def main() -> NoReturn:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="appsnap",
        description="Fast Windows screenshot tool for AI coding agents",
        epilog='Example: appsnap "Visual Studio Code" --output screenshot.png',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "window_name",
        nargs="?",
        help="Window title to search for (supports fuzzy matching)",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all capturable windows and exit",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="Output file path (default: temp directory with timestamp)",
    )

    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=70,
        metavar="N",
        help="Fuzzy match threshold 0-100 (default: 70, lower = more lenient)",
    )

    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output result as JSON with path and metadata",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"appsnap {__version__}",
        help="Show version and exit",
    )

    args = parser.parse_args()

    # Handle --list flag
    if args.list:
        list_windows()

    # Validate arguments
    if not args.window_name:
        parser.print_help()
        sys.exit(1)

    # Validate threshold range
    if not 0 <= args.threshold <= 100:
        print("Error: Threshold must be between 0 and 100", file=sys.stderr)
        sys.exit(1)

    # Capture window screenshot
    capture_window(args.window_name, args.output, args.threshold, args.json)

    sys.exit(0)


if __name__ == "__main__":
    main()
