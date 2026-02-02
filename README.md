# 📸 appsnap

**Fast Windows screenshot tool for AI coding agents**

`appsnap` is a simple, fast CLI tool for capturing screenshots of Windows application windows. Perfect for AI agents that need to verify UI changes during development iterations.

## ✨ Features

- 🎯 **Window-specific capture** - Target apps by name with fuzzy matching
- 🚀 **Fast** - Screenshots in ~0.1-0.3 seconds
- 🤖 **Agent-friendly** - JSON output and stdout paths for easy parsing
- 📁 **Smart defaults** - Temp directory with auto-cleanup
- 🔍 **List windows** - See all capturable windows
- 🎨 **DPI-aware** - Handles high-DPI displays correctly

## 🚀 Quick Start

### Installation

```bash
# Install with uvx (recommended - when published to PyPI)
uvx appsnap

# Or install with uv tool
uv tool install appsnap

# Development mode (local testing)
git clone <repo>
cd appsnap
uv venv
uv pip install -e .
```

### Usage

**Option 1: After activating venv**

```bash
# Activate the virtual environment first
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Then use appsnap directly
appsnap --list
appsnap "Visual Studio Code"
```

**Option 2: Using uv run (no activation needed)**

```bash
# Run from within the appsnap directory
cd appsnap
uv run appsnap --list
uv run appsnap "Chrome" --output screenshot.png
```

**Common Commands:**

```bash
# List all capturable windows
appsnap --list

# Capture a window (saves to temp directory)
appsnap "Visual Studio Code"

# Capture with custom output path
appsnap "Chrome" --output screenshot.png

# JSON output for agents
appsnap "Notepad" --json
# {"path": "C:\\Temp\\appsnap\\appsnap_20260202_153045.png", "window": "Notepad", "bbox": [100, 200, 800, 600]}

# Adjust fuzzy matching threshold (0-100, default 70)
appsnap "VS" --threshold 60
```

## 🤖 AI Agent Integration

### Claude Desktop Skill

Add to your agent prompt or skill:

```
When you need to verify UI changes, use: appsnap "App Name" --json
Parse the JSON output to get the screenshot path and window metadata.
```

### Python Integration

```python
import subprocess
import json

result = subprocess.run(
    ["appsnap", "Chrome", "--json"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
screenshot_path = data["path"]
```

### PowerShell Integration

```powershell
$result = appsnap "VSCode" --json | ConvertFrom-Json
Write-Host "Screenshot: $($result.path)"
```

## 📖 CLI Options

```
positional arguments:
  window_name           Window title to search for (fuzzy matching)

options:
  -h, --help            Show this help message and exit
  -l, --list            List all capturable windows
  -o PATH, --output PATH
                        Output file path (default: temp directory)
  -t N, --threshold N   Fuzzy match threshold 0-100 (default: 70)
  -j, --json            Output JSON with path and metadata
```

## 🛠️ How It Works

1. **DPI Awareness** - Sets process DPI awareness for correct scaling on high-DPI displays
2. **Window Enumeration** - Uses Win32 API to enumerate all visible, non-minimized windows
3. **Fuzzy Matching** - Finds windows using `fuzzywuzzy` for flexible name matching
4. **Direct Window Capture** - Uses Win32 `PrintWindow` API to capture window content directly (works even when partially occluded)
5. **Output** - Saves to temp or custom location, prints path to stdout for easy agent parsing

## 🔧 Development

```bash
# Clone and install dev dependencies
git clone <repo>
cd appsnap
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run with local changes
uv run appsnap --list
```

## 🐛 Troubleshooting

### "No window found matching..."

- Use `appsnap --list` to see exact window titles
- Try lowering the threshold: `--threshold 60`
- Make sure the window is visible (not minimized)

### Screenshots are blank, wrong window, or multiple windows

**v0.1.1 Fix:** Switched to Win32 PrintWindow API for direct window content capture.

This method captures the actual window content, not screen regions, so it:

- Works correctly on multi-monitor setups
- Captures partially occluded windows
- Handles DPI scaling properly

If you still have issues:

- Ensure the window is not minimized (minimized windows cannot be captured)
- Some apps (especially GPU-accelerated ones) may not respond to PrintWindow correctly
- Try bringing the window to foreground if capture fails

### DPI/Scaling issues

The tool automatically handles DPI awareness. If you see incorrect sizing:

- Ensure Windows display scaling is consistent
- Check that the app respects DPI settings

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## Pillow](https://github.com/python-pillow/Pillow) - Screenshot capture and image processing

- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) - Fuzzy string matching
- [pywin32](https://github.com/mhammond/pywin32) - Windows API access

- [mss](https://github.com/BoboTiG/python-mss) - Fast screenshot capture
- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) - Fuzzy string matching
- [Pillow](https://github.com/python-pillow/Pillow) - Image processing

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

---

Made for AI agents, by developers 🤖❤️
