#!/usr/bin/env python
"""
Command-line interface for Unity MCP Server wrapper.

Provides commands to download, manage, and run the Unity MCP Server binary.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from . import __version__
from .downloader import download_binary, get_cached_binary


def execute_binary(
    binary_path: Path, args: Sequence[str], is_stdio_mode: bool = False
) -> int:
    """Execute the binary with given arguments."""
    if sys.platform != "win32":
        binary_path.chmod(0o755)

    process: Optional[subprocess.Popen] = None
    try:
        if is_stdio_mode:
            process = subprocess.Popen(
                [str(binary_path)] + list(args),
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                bufsize=0,
            )
        else:
            process = subprocess.Popen(
                [str(binary_path)] + list(args),
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

        return process.wait()

    except FileNotFoundError:
        print(f"Error: Binary not found at {binary_path}", file=sys.stderr)
        return 127
    except PermissionError:
        print(f"Error: Permission denied executing {binary_path}", file=sys.stderr)
        return 126
    except KeyboardInterrupt:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        return 130
    except Exception as e:
        print(f"Error executing binary: {e}", file=sys.stderr)
        return 1


def get_version_from_env_or_package() -> str:
    """Get server version from environment or package version."""
    env_version = os.environ.get("UNITY_MCP_VERSION")
    if env_version:
        return env_version
    return __version__.lstrip("v")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="unity-mcp",
        description="Unity MCP Server - AI-powered bridge to Unity Editor/Runtime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  unity-mcp --transport stdio                    # Run with stdio transport
  unity-mcp --transport streamableHttp --port 8080  # Run HTTP server on port 8080
  unity-mcp --version                            # Show version
  unity-mcp download --version 0.42.0            # Download specific version

Environment Variables:
  UNITY_MCP_VERSION    Server version to use (default: package version)
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "streamableHttp"],
        default="stdio",
        help="Transport mode for MCP client communication (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP transport and plugin communication (default: 8080)",
    )
    parser.add_argument(
        "--plugin-timeout",
        type=int,
        default=10000,
        help="Plugin connection timeout in milliseconds (default: 10000)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )

    subparsers = parser.add_subparsers(dest="command", help="Additional commands")

    download_parser = subparsers.add_parser(
        "download",
        help="Download the Unity MCP Server binary",
    )
    download_parser.add_argument(
        "--version",
        dest="dl_version",
        type=str,
        help="Specific version to download (default: latest)",
    )
    download_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-download even if binary exists",
    )

    return parser


def cmd_download(args: argparse.Namespace) -> int:
    """Download the Unity MCP Server binary."""
    version = args.dl_version or get_version_from_env_or_package()

    print(f"Downloading Unity MCP Server (version: {version})...")

    try:
        binary_path = download_binary(version)
        print(f"Download complete: {binary_path}")
        return 0
    except Exception as e:
        print(f"Error downloading binary: {e}", file=sys.stderr)
        return 1


def cmd_run(args: argparse.Namespace, forwarded_args: List[str]) -> int:
    """Run the Unity MCP Server."""
    version = get_version_from_env_or_package()

    binary_path = get_cached_binary(version)

    if binary_path is None:
        print(f"Binary not found for version {version}. Downloading...")
        try:
            binary_path = download_binary(version)
        except Exception as e:
            print(f"Error downloading binary: {e}", file=sys.stderr)
            return 1

    print(f"Starting Unity MCP Server (version: {version})...")

    is_stdio_mode = args.transport == "stdio"

    binary_args: List[str] = []

    for i, arg in enumerate(forwarded_args):
        if arg.startswith("--transport="):
            transport_value = arg.split("=", 1)[1]
            binary_args.append(f"--client-transport={transport_value}")
        elif arg == "--transport":
            continue
        elif (
            arg in ("stdio", "streamableHttp")
            and i > 0
            and forwarded_args[i - 1] == "--transport"
        ):
            binary_args.append(f"--client-transport={arg}")
        elif arg.startswith("--port="):
            binary_args.append(arg)
        elif arg == "--port":
            continue
        elif arg.isdigit() and i > 0 and forwarded_args[i - 1] == "--port":
            binary_args.append(f"--port={arg}")
        elif arg.startswith("--plugin-timeout="):
            binary_args.append(arg)
        elif arg == "--plugin-timeout":
            continue
        elif arg.isdigit() and i > 0 and forwarded_args[i - 1] == "--plugin-timeout":
            binary_args.append(f"--plugin-timeout={arg}")

    if not any(a.startswith("--client-transport=") for a in binary_args):
        binary_args.append(f"--client-transport={args.transport}")
    if not any(a.startswith("--port=") for a in binary_args):
        binary_args.append(f"--port={args.port}")
    if not any(a.startswith("--plugin-timeout=") for a in binary_args):
        binary_args.append(f"--plugin-timeout={args.plugin_timeout}")

    return execute_binary(binary_path, binary_args, is_stdio_mode)


def show_version() -> int:
    """Show version information."""
    version = get_version_from_env_or_package()
    print(f"unity-mcp version {__version__}")
    print(f"Server version: {version}")
    return 0


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point."""
    if args is None:
        args = sys.argv[1:]

    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.version:
        return show_version()

    if parsed_args.command == "download":
        return cmd_download(parsed_args)

    return cmd_run(parsed_args, args)


if __name__ == "__main__":
    sys.exit(main())
