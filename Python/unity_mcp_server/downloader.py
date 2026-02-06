"""
Server binary downloader for Unity MCP Server.

Handles downloading the appropriate binary for the current platform
from GitHub releases.
"""

import os
import platform
from pathlib import Path
from typing import Optional


class ServerDownloader:
    """Downloads Unity MCP Server binaries from GitHub releases."""

    GITHUB_REPO = "ivanmurzak/unity-mcp"
    BASE_URL = f"https://github.com/{GITHUB_REPO}/releases/download"

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        """
        Initialize the downloader.

        Args:
            output_dir: Directory to download binaries to.
                       Defaults to ~/.unity-mcp-server
        """
        self.output_dir = output_dir or Path.home() / ".unity-mcp-server"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_binary_name(self) -> str:
        """Get the binary name for the current platform."""
        from .platform import get_platform_binary_name

        return get_platform_binary_name()

    def get_download_url(self, version: str) -> str:
        """
        Get the download URL for a specific version.

        Args:
            version: Version tag (e.g., "v1.0.0" or "latest")

        Returns:
            Full download URL
        """
        binary_name = self.get_binary_name()
        if version == "latest":
            return f"{self.BASE_URL}/latest/{binary_name}"
        return f"{self.BASE_URL}/{version}/{binary_name}"

    def download(self, version: str = "latest", force: bool = False) -> Path:
        """
        Download the server binary.

        Args:
            version: Version to download (default: "latest")
            force: Force re-download even if binary exists

        Returns:
            Path to the downloaded binary

        Raises:
            RuntimeError: If download fails
        """
        binary_name = self.get_binary_name()
        binary_path = self.output_dir / binary_name

        if binary_path.exists() and not force:
            print(f"Binary already exists at {binary_path}")
            return binary_path

        url = self.get_download_url(version)
        print(f"Downloading from: {url}")

        # TODO: Implement actual download logic using urllib or requests
        # This is a placeholder for the actual implementation

        return binary_path

    def get_binary_path(self) -> Optional[Path]:
        """
        Get the path to the downloaded binary if it exists.

        Returns:
            Path to binary or None if not downloaded
        """
        binary_name = self.get_binary_name()
        binary_path = self.output_dir / binary_name
        return binary_path if binary_path.exists() else None

    def is_installed(self) -> bool:
        """Check if the binary is already downloaded."""
        return self.get_binary_path() is not None
