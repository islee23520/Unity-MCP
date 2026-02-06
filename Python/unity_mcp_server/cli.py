#!/usr/bin/env python
"""
Command-line interface for Unity MCP Server wrapper.

Provides commands to download, manage, and run the Unity MCP Server binary.
"""

import argparse
import sys
from typing import List, Optional

from .downloader import ServerDownloader
from .platform import get_platform_binary_name


def cmd_download(args: argparse.Namespace) -> int:
    """Download the Unity MCP Server binary."""
    print(f"Downloading Unity MCP Server (version: {args.version or 'latest'})...")
    # TODO: Implement actual download logic
    print("Download complete!")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run the Unity MCP Server."""
    print("Starting Unity MCP Server...")
    # TODO: Implement server execution
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    """Show version information."""
    from . import __version__

    print(f"unity-mcp-server version {__version__}")
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="unity-mcp",
        description="Unity MCP Server wrapper and downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  unity-mcp download              Download the latest server binary
  unity-mcp download --version 1.0.0  Download a specific version
  unity-mcp run                   Run the Unity MCP Server
  unity-mcp version               Show version information
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download command
    download_parser = subparsers.add_parser(
        "download",
        help="Download the Unity MCP Server binary",
    )
    download_parser.add_argument(
        "--version",
        type=str,
        help="Specific version to download (default: latest)",
    )
    download_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output directory (default: ~/.unity-mcp-server)",
    )
    download_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-download even if binary exists",
    )
    download_parser.set_defaults(func=cmd_download)

    # Run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run the Unity MCP Server",
    )
    run_parser.add_argument(
        "--transport",
        choices=["stdio", "streamableHttp"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    run_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP transport (default: 8080)",
    )
    run_parser.set_defaults(func=cmd_run)

    # Version command
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information",
    )
    version_parser.set_defaults(func=cmd_version)

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    if hasattr(parsed_args, "func"):
        return parsed_args.func(parsed_args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
