# Unity MCP Server - Python Wrapper

This Python package provides a wrapper around the Unity MCP Server binary for easy installation via PyPI.

## Installation

### Using uvx (recommended)

```bash
uvx --from unity-mcp-server unity-mcp --transport stdio --port 8080
```

### Using pipx

```bash
pipx run unity-mcp-server --transport stdio --port 8080
```

### Using pip

```bash
pip install unity-mcp-server
unity-mcp --transport stdio --port 8080
```

## Usage

```bash
unity-mcp --transport stdio --port 8080
```

On first run, the wrapper will automatically download the appropriate binary for your platform from GitHub Releases.

## MCP Client Configuration

### Claude Desktop / Claude Code

```bash
claude mcp add ai-game-developer uvx --from unity-mcp-server unity-mcp --transport stdio
```

Or manually add to your MCP settings:

```json
{
  "mcpServers": {
    "ai-game-developer": {
      "command": "uvx",
      "args": [
        "--from",
        "unity-mcp-server",
        "unity-mcp",
        "--transport",
        "stdio",
        "--port",
        "8080"
      ]
    }
  }
}
```

### Other MCP Clients

Configure your MCP client to run:

```bash
uvx --from unity-mcp-server unity-mcp --transport stdio --port 8080
```

## How It Works

The wrapper:

1. **Platform Detection**: Detects your platform (Windows/Linux/macOS, x64/ARM64)
2. **Binary Download**: Downloads the binary from GitHub Releases if not cached
3. **Caching**: Stores the binary in `~/.cache/unity-mcp-server/{version}/`
4. **Execution**: Runs the binary with forwarded arguments

## Development

### Setup

```bash
cd Python
pip install -e .
```

### Local Testing

```bash
# Test the CLI
unity-mcp --version

# Test with stdio transport
unity-mcp --transport stdio --port 8080
```

### Building and Publishing

```bash
# Install build dependencies
pip install build twine

# Build the package
python -m build

# Upload to PyPI (requires credentials)
python -m twine upload dist/*
```

### Development Mode

Install in editable mode for development:

```bash
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Troubleshooting

### Binary download fails

- Check your internet connection
- Verify GitHub Releases is accessible
- Check firewall/proxy settings
- Clear cache: `rm -rf ~/.cache/unity-mcp-server/`

### Binary not found

The wrapper looks for the binary in:
- `~/.cache/unity-mcp-server/{version}/`

Clear the cache to force a re-download.

### Permission denied (Linux/macOS)

The wrapper automatically makes the binary executable. If you encounter permission issues:

```bash
chmod +x ~/.cache/unity-mcp-server/{version}/unity-mcp-server
```

## License

MIT - See [LICENSE](../LICENSE) for details.
