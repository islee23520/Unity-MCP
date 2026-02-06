"""
Unity MCP Server Python Wrapper

This package provides a Python wrapper and downloader for the Unity MCP Server.
"""

__version__ = "0.1.0"
__author__ = "Ivan Murzak"
__email__ = "ivan.murzak@gmail.com"

from .downloader import ServerDownloader
from .platform import get_platform_binary_name, get_supported_platforms

__all__ = [
    "ServerDownloader",
    "get_platform_binary_name",
    "get_supported_platforms",
]
