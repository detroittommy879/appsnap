# Publishing Guide for appsnap

## Table of Contents

1. [Local Installation Testing](#local-installation-testing)
2. [Publishing to PyPI with GitHub Actions](#publishing-to-pypi-with-github-actions)
3. [Manual PyPI Publishing](#manual-pypi-publishing)
4. [AI Agent Skills Integration](#ai-agent-skills-integration)

---

## Local Installation Testing

### Test with `uv tool install` (from local directory)

```bash
# Install from local directory
cd c:\2nd\Main\Git-Projects-downloaded\Windows-MCP-00\appsnap
uv tool install .

# Now `appsnap` should work from anywhere!
cd c:\
appsnap --list
appsnap "Chrome" --output test.png
```

### Test with `pipx install` (from local directory)

```bash
# Install from local directory
cd c:\2nd\Main\Git-Projects-downloaded\Windows-MCP-00\appsnap
pipx install .

# Now accessible globally
cd c:\Users\YourUser
appsnap --help
```

### Test with GitHub (before PyPI)

Once pushed to GitHub, users can install directly:

```bash
# Install from GitHub repo
uv tool install git+https://github.com/yourusername/appsnap.git

# Or with pipx
pipx install git+https://github.com/yourusername/appsnap.git
```

### Uninstall for testing

```bash
# Remove with uv
uv tool uninstall appsnap

# Remove with pipx
pipx uninstall appsnap
```

---

## Publishing to PyPI with GitHub Actions

### Step 1: Set Up PyPI API Token

1. **Log in to PyPI**: https://pypi.org/
2. **Go to Account Settings** → **API tokens**
3. **Create a new token**:
   - Token name: `appsnap-github-actions`
   - Scope: Choose "Entire account" (or limit to project after first upload)
   - Copy the token (starts with `pypi-`)
4. **Save it immediately** - you won't see it again!

### Step 2: Add Token to GitHub

1. Go to your GitHub repo: `https://github.com/yourusername/appsnap`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `PYPI_API_TOKEN`
5. Value: Paste your PyPI token
6. Click **Add secret**

### Step 3: Create GitHub Actions Workflow

The workflow file is already created at `.github/workflows/publish.yml` (see below).

### Step 4: Publish a Release

**Option A: Using Git Tags (Recommended)**

```bash
# Make sure everything is committed
git status

# Create and push a version tag
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will automatically build and publish to PyPI!
```

**Option B: Using GitHub Releases UI**

1. Go to your repo on GitHub
2. Click **Releases** → **Create a new release**
3. Click **Choose a tag** → Type `v0.2.0` → **Create new tag**
4. Fill in release title: `v0.2.0 - Bulk capture feature`
5. Add release notes (optional)
6. Click **Publish release**
7. GitHub Actions will trigger automatically!

### Step 5: Verify Publication

1. **Check GitHub Actions**: Go to **Actions** tab, watch the workflow run
2. **Check PyPI**: Visit `https://pypi.org/project/appsnap/`
3. **Test Installation**:
   ```bash
   uv tool install appsnap
   appsnap --version
   ```

### Updating Versions

For subsequent releases:

1. Update version in `pyproject.toml` and `src/appsnap/__init__.py`
2. Commit the changes
3. Create a new tag:
   ```bash
   git tag v0.2.1
   git push origin v0.2.1
   ```
4. GitHub Actions publishes automatically!

---

## Manual PyPI Publishing

If you prefer manual control or GitHub Actions fails:

### Install Build Tools

```bash
uv pip install --upgrade build twine
```

### Build the Package

```bash
cd c:\2nd\Main\Git-Projects-downloaded\Windows-MCP-00\appsnap

# Clean old builds
Remove-Item -Recurse dist, build, *.egg-info -ErrorAction SilentlyContinue

# Build distribution packages
python -m build
```

This creates:

- `dist/appsnap-0.2.0-py3-none-any.whl` (wheel)
- `dist/appsnap-0.2.0.tar.gz` (source)

### Upload to Test PyPI (Optional)

Test your package first:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test install
uv tool install --index-url https://test.pypi.org/simple/ appsnap
```

### Upload to Real PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Enter your PyPI username and API token when prompted
# Username: __token__
# Password: pypi-...your-token...
```

### Verify

```bash
# Install from PyPI
uv tool install appsnap

# Test
appsnap --version
appsnap --list
```

---

## AI Agent Skills Integration

### General CLI Access (Works for All)

Once `appsnap` is installed globally (via `uv tool install` or `pipx install`), most AI agents can call it directly:

```python
import subprocess
import json

# Call appsnap from any directory
result = subprocess.run(
    ["appsnap", "Chrome", "--json"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
screenshot_path = data["path"]
```

### Claude Desktop (MCP Server)

For Claude Desktop, you can create a simple MCP server wrapper:

**Create `mcp-appsnap/server.py`:**

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import subprocess
import json

app = Server("appsnap")

@app.tool()
def capture_window(window_name: str, output_path: str = None) -> dict:
    """Capture a screenshot of a Windows application window."""
    cmd = ["appsnap", window_name, "--json"]
    if output_path:
        cmd.extend(["--output", output_path])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

@app.tool()
def list_windows() -> list[str]:
    """List all capturable windows."""
    result = subprocess.run(
        ["appsnap", "--list"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0], streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Add to Claude Desktop config:**

```json
{
  "mcpServers": {
    "appsnap": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\mcp-appsnap", "run", "server.py"]
    }
  }
}
```

### Windsurf / Cascade

Create a skill file:

**`appsnap.ts` or `appsnap.md`:**

```typescript
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function captureWindow(windowName: string): Promise<string> {
  const { stdout } = await execAsync(`appsnap "${windowName}" --json`);
  const result = JSON.parse(stdout);
  return result.path;
}

export async function listWindows(): Promise<string[]> {
  const { stdout } = await execAsync("appsnap --list");
  return stdout
    .trim()
    .split("\n")
    .filter((line) => line.startsWith("  •"))
    .map((line) => line.slice(4));
}
```

### Cline / Roo-Cline

Add to custom tools:

```json
{
  "name": "capture_window",
  "description": "Capture a screenshot of a Windows application window",
  "inputSchema": {
    "type": "object",
    "properties": {
      "window_name": {
        "type": "string",
        "description": "The window title to capture"
      }
    },
    "required": ["window_name"]
  },
  "command": "appsnap \"{{window_name}}\" --json"
}
```

### Gemini CLI / Qwen Code

These support MCP servers directly, same approach as Claude Desktop.

### Simple Script Approach (Universal)

Create a simple wrapper script that any agent can call:

**`capture.ps1`:**

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$WindowName
)

$result = appsnap $WindowName --json | ConvertFrom-Json
Write-Output $result.path
```

**`capture.py`:**

```python
#!/usr/bin/env python3
import sys
import subprocess
import json

def capture_window(window_name):
    result = subprocess.run(
        ["appsnap", window_name, "--json"],
        capture_output=True,
        text=True,
        check=True
    )
    data = json.loads(result.stdout)
    return data["path"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: capture.py <window_name>")
        sys.exit(1)

    path = capture_window(sys.argv[1])
    print(path)
```

---

## Troubleshooting

### "appsnap: command not found" after installation

**Windows (PowerShell):**

```powershell
# Check if uv tools bin is in PATH
$env:PATH -split ';' | Select-String "uv"

# Add uv tools to PATH (if needed)
$uvBin = "$env:USERPROFILE\.local\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$uvBin", "User")

# Restart terminal and try again
appsnap --version
```

**Linux/Mac:**

```bash
# Check PATH
echo $PATH | grep uv

# Add to PATH if needed (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc
appsnap --version
```

### Package not found on PyPI

- Wait 2-3 minutes after publishing for PyPI to index
- Check spelling: `uv tool install appsnap` (all lowercase)
- Verify on PyPI: https://pypi.org/project/appsnap/

### Import errors after installation

```bash
# Reinstall with dependencies
uv tool uninstall appsnap
uv tool install appsnap

# Or force reinstall
uv tool install --force appsnap
```

---

## Quick Reference

```bash
# Local testing
uv tool install .

# Install from GitHub
uv tool install git+https://github.com/yourusername/appsnap.git

# Install from PyPI (after publishing)
uv tool install appsnap

# Update
uv tool install --upgrade appsnap

# Uninstall
uv tool uninstall appsnap

# Publish new version
git tag v0.2.1
git push origin v0.2.1
```

---

**Ready to publish!** Start with Step 1 (PyPI token) and the automated GitHub Actions will handle everything else. 🚀
