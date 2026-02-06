"""
Platform detection utilities for Unity MCP Server.

Handles detecting the current platform and selecting the appropriate
binary to download.
"""

import platform
import sys
from typing import List, Tuple


def get_platform_arch() -> Tuple[str, str]:
    """
    Get the current platform and architecture.

    Returns:
        Tuple of (platform_name, architecture)
        Platform: win, linux, osx
        Architecture: x64, arm64
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map platform names
    platform_map = {
        "windows": "win",
        "linux": "linux",
        "darwin": "osx",
    }
    plat = platform_map.get(system, system)

    # Map architectures
    arch_map = {
        "amd64": "x64",
        "x86_64": "x64",
        "i386": "x64",
        "i686": "x64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    arch = arch_map.get(machine, "x64")  # Default to x64

    return plat, arch


def get_platform_binary_name() -> str:
    """
    Get the binary name for the current platform.

    Returns:
        Binary filename (e.g., "unity-mcp-server-win-x64.exe")
    """
    plat, arch = get_platform_arch()
    ext = ".exe" if plat == "win" else ""
    return f"unity-mcp-server-{plat}-{arch}{ext}"


def get_supported_platforms() -> List[str]:
    """
    Get list of supported platform/architecture combinations.

    Returns:
        List of binary names for all supported platforms
    """
    platforms = []
    for plat in ["win", "linux", "osx"]:
        for arch in ["x64", "arm64"]:
            ext = ".exe" if plat == "win" else ""
            platforms.append(f"unity-mcp-server-{plat}-{arch}{ext}")
    return platforms


def is_platform_supported() -> bool:
    """
    Check if the current platform is supported.

    Returns:
        True if supported, False otherwise
    """
    try:
        get_platform_binary_name()
        return True
    except Exception:
        return False


def get_binary_extension() -> str:
    """
    Get the binary extension for the current platform.

    Returns:
        ".exe" on Windows, empty string otherwise
    """
    plat, _ = get_platform_arch()
    return ".exe" if plat == "win" else ""
