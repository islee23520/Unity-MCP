"""
Platform detection utilities for Unity MCP Server.

Handles detecting the current platform and selecting the appropriate
binary to download.
"""

import platform
import sys
from typing import Optional


def get_platform() -> str:
    """
    Detect current platform and return identifier.

    Returns:
        Platform string (e.g., "win-x64", "osx-arm64", "linux-x64")

    Supported platforms (from build-all.sh):
        - win-x64, win-x86, win-arm64
        - osx-x64, osx-arm64
        - linux-x64, linux-arm64
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map system names to GitHub release asset format
    platform_map = {
        "windows": "win",
        "linux": "linux",
        "darwin": "osx",
    }

    # Map machine architectures to standardized format
    # From build-all.sh: x64, x86, arm64 are the supported architectures
    arch_map = {
        # x64 architectures
        "amd64": "x64",
        "x86_64": "x64",
        # x86 architectures
        "i386": "x86",
        "i686": "x86",
        "x86": "x86",
        # ARM64 architectures
        "arm64": "arm64",
        "aarch64": "arm64",
    }

    plat = platform_map.get(system, system)
    arch = arch_map.get(machine, "x64")  # Default to x64 for unknown architectures

    return f"{plat}-{arch}"


def get_binary_name(platform_id: Optional[str] = None) -> str:
    """
    Get binary name for platform.

    Args:
        platform_id: Platform identifier (auto-detect if None)

    Returns:
        Binary filename (e.g., "unity-mcp-server.exe" or "unity-mcp-server")
    """
    if platform_id is None:
        platform_id = get_platform()

    # Check if Windows platform (win-x64, win-x86, win-arm64)
    if platform_id.startswith("win-"):
        return "unity-mcp-server.exe"

    return "unity-mcp-server"


def get_archive_extension(platform_id: Optional[str] = None) -> str:
    """
    Get archive extension for platform.

    Args:
        platform_id: Platform identifier (auto-detect if None)

    Returns:
        Archive extension (e.g., ".zip" or ".tar.gz")
    """
    if platform_id is None:
        platform_id = get_platform()

    # Windows uses .zip, Unix (macOS, Linux) uses .tar.gz
    if platform_id.startswith("win-"):
        return ".zip"

    return ".tar.gz"


def get_platform_arch() -> tuple[str, str]:
    """
    Get the current platform and architecture as separate values.

    Returns:
        Tuple of (platform_name, architecture)
        Platform: win, linux, osx
        Architecture: x64, x86, arm64
    """
    platform_id = get_platform()
    parts = platform_id.split("-")
    return parts[0], parts[1]


def get_platform_binary_name() -> str:
    """
    Get the full binary name for the current platform.

    Returns:
        Binary filename with platform (e.g., "unity-mcp-server-win-x64.exe")

    Note: This is the legacy function for backwards compatibility.
          New code should use get_binary_name() for the simple name
          or construct the full name manually using get_platform().
    """
    plat, arch = get_platform_arch()
    ext = ".exe" if plat == "win" else ""
    return f"unity-mcp-server-{plat}-{arch}{ext}"


def get_asset_name(version: str, platform_id: Optional[str] = None) -> str:
    """
    Get the GitHub release asset name.

    From build-all.sh, the release assets follow this pattern:
        unity-mcp-server-{version}-{platform}.{archive}

    Args:
        version: Release version (e.g., "0.42.0")
        platform_id: Platform identifier (auto-detect if None)

    Returns:
        Full asset name (e.g., "unity-mcp-server-0.42.0-win-x64.zip")
    """
    if platform_id is None:
        platform_id = get_platform()

    extension = get_archive_extension(platform_id)
    return f"unity-mcp-server-{version}-{platform_id}{extension}"


def is_platform_supported(platform_id: Optional[str] = None) -> bool:
    """
    Check if the platform is supported.

    Supported platforms from build-all.sh:
        - win-x64, win-x86, win-arm64
        - osx-x64, osx-arm64
        - linux-x64, linux-arm64

    Args:
        platform_id: Platform identifier (auto-detect if None)

    Returns:
        True if supported, False otherwise
    """
    if platform_id is None:
        platform_id = get_platform()

    supported = [
        "win-x64",
        "win-x86",
        "win-arm64",
        "osx-x64",
        "osx-arm64",
        "linux-x64",
        "linux-arm64",
    ]

    return platform_id in supported


def get_binary_extension(platform_id: Optional[str] = None) -> str:
    """
    Get the binary extension for the platform.

    Args:
        platform_id: Platform identifier (auto-detect if None)

    Returns:
        ".exe" on Windows, empty string otherwise
    """
    if platform_id is None:
        platform_id = get_platform()

    return ".exe" if platform_id.startswith("win-") else ""


def get_supported_platforms() -> list[str]:
    """
    Get list of supported platform/architecture combinations.

    Returns:
        List of supported platform identifiers
    """
    return [
        "win-x64",
        "win-x86",
        "win-arm64",
        "osx-x64",
        "osx-arm64",
        "linux-x64",
        "linux-arm64",
    ]
