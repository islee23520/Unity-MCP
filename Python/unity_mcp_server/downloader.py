"""
Server binary downloader for Unity MCP Server.

Handles downloading the appropriate binary for the current platform
from GitHub releases.
"""

import os
import shutil
import stat
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

try:
    import tarfile
except ImportError:
    tarfile = None  # type: ignore

from .platform import (
    get_asset_name,
    get_binary_name,
    get_platform,
    is_platform_supported,
)


class DownloadError(Exception):
    """Raised when a download fails."""

    pass


class PlatformNotSupportedError(Exception):
    """Raised when the platform is not supported."""

    pass


class ServerDownloader:
    """Downloads Unity MCP Server binaries from GitHub releases."""

    GITHUB_REPO = "IvanMurzak/Unity-MCP"
    BASE_URL = f"https://github.com/{GITHUB_REPO}/releases/download"

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        """
        Initialize the downloader.

        Args:
            cache_dir: Directory to cache binaries.
                      Defaults to ~/.cache/unity-mcp-server
        """
        if cache_dir is None:
            self.cache_dir = Path.home() / ".cache" / "unity-mcp-server"
        else:
            self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_platform(self) -> str:
        """Get the current platform identifier."""
        return get_platform()

    def get_binary_name(self, platform_id: Optional[str] = None) -> str:
        """Get the binary name for the platform."""
        return get_binary_name(platform_id)

    def get_cache_path(self, version: str) -> Path:
        """
        Get the cache directory path for a specific version.

        Args:
            version: Release version

        Returns:
            Path to version-specific cache directory
        """
        return self.cache_dir / version

    def get_binary_path(self, version: str, platform_id: Optional[str] = None) -> Path:
        """
        Get the path to the binary executable for a version.

        Args:
            version: Release version
            platform_id: Platform identifier (auto-detect if None)

        Returns:
            Path to binary executable
        """
        if platform_id is None:
            platform_id = get_platform()
        cache_path = self.get_cache_path(version)
        binary_name = self.get_binary_name(platform_id)
        # Archives extract with platform subdirectory (e.g., win-x64/unity-mcp-server.exe)
        return cache_path / platform_id / binary_name

    def is_cached(self, version: str, platform_id: Optional[str] = None) -> bool:
        """
        Check if the binary is already cached.

        Args:
            version: Release version
            platform_id: Platform identifier (auto-detect if None)

        Returns:
            True if binary exists in cache
        """
        binary_path = self.get_binary_path(version, platform_id)
        return binary_path.exists()

    def get_download_url(self, version: str, platform_id: Optional[str] = None) -> str:
        """
        Get the download URL for a specific version.

        Args:
            version: Release version (e.g., "0.42.0")
            platform_id: Platform identifier (auto-detect if None)

        Returns:
            Full download URL for the archive
        """
        asset_name = get_asset_name(version, platform_id)
        return f"{self.BASE_URL}/{version}/{asset_name}"

    def _download_file(self, url: str, dest_path: Path, timeout: int = 300) -> None:
        """
        Download a file from URL to destination path.

        Args:
            url: URL to download from
            dest_path: Destination path for the file
            timeout: Download timeout in seconds

        Raises:
            DownloadError: If download fails
        """
        try:
            # Create a request with headers to avoid potential blocking
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request, timeout=timeout) as response:
                # Check for successful response
                if response.status != 200:
                    raise DownloadError(
                        f"HTTP {response.status} error downloading from {url}"
                    )

                # Read and write in chunks to handle large files
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "wb") as f:
                    chunk_size = 8192
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)

        except urllib.error.HTTPError as e:
            raise DownloadError(
                f"HTTP {e.code} error downloading from {url}: {e.reason}"
            ) from e
        except urllib.error.URLError as e:
            raise DownloadError(
                f"Network error downloading from {url}: {e.reason}"
            ) from e
        except TimeoutError as e:
            raise DownloadError(f"Download timed out after {timeout}s: {url}") from e
        except OSError as e:
            raise DownloadError(f"File system error during download: {e}") from e

    def _extract_archive(
        self, archive_path: Path, dest_dir: Path, platform_id: Optional[str] = None
    ) -> None:
        """
        Extract an archive to the destination directory.

        Args:
            archive_path: Path to the archive file
            dest_dir: Destination directory for extraction
            platform_id: Platform identifier (for determining archive type)

        Raises:
            DownloadError: If extraction fails
        """
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)

            if platform_id is None:
                platform_id = get_platform()

            # Windows uses .zip, Unix uses .tar.gz
            if platform_id.startswith("win-"):
                # Extract ZIP archive
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(dest_dir)
            else:
                # Extract TAR.GZ archive
                if tarfile is None:
                    raise DownloadError(
                        "tarfile module not available for extracting .tar.gz archives"
                    )
                with tarfile.open(archive_path, "r:gz") as tar_ref:
                    tar_ref.extractall(dest_dir)

        except (zipfile.BadZipFile, tarfile.TarError) as e:
            raise DownloadError(f"Invalid or corrupted archive: {e}") from e
        except OSError as e:
            raise DownloadError(f"File system error during extraction: {e}") from e

    def _make_executable(self, binary_path: Path) -> None:
        """
        Make the binary executable on Unix systems.

        Args:
            binary_path: Path to the binary file
        """
        if os.name != "nt":  # Not Windows
            try:
                # Add execute permission (chmod +x equivalent)
                current_mode = binary_path.stat().st_mode
                binary_path.chmod(
                    current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )
            except OSError:
                # If we can't change permissions, the binary might still work
                # if the filesystem was mounted with appropriate permissions
                pass

    def download(
        self, version: str, platform_id: Optional[str] = None, force: bool = False
    ) -> Path:
        """
        Download and cache the server binary.

        Args:
            version: Version to download (e.g., "0.42.0")
            platform_id: Platform identifier (auto-detect if None)
            force: Force re-download even if binary exists

        Returns:
            Path to the cached binary executable

        Raises:
            PlatformNotSupportedError: If platform is not supported
            DownloadError: If download or extraction fails
        """
        # Auto-detect platform if not specified
        if platform_id is None:
            platform_id = get_platform()

        # Check if platform is supported
        if not is_platform_supported(platform_id):
            raise PlatformNotSupportedError(f"Platform not supported: {platform_id}")

        # Check if already cached (unless force=True)
        binary_path = self.get_binary_path(version, platform_id)
        if binary_path.exists() and not force:
            print(f"Binary already cached at {binary_path}")
            return binary_path

        # Prepare cache directory
        cache_path = self.get_cache_path(version)
        cache_path.mkdir(parents=True, exist_ok=True)

        # Get download URL
        url = self.get_download_url(version, platform_id)
        print(f"Downloading Unity MCP Server {version} for {platform_id}...")
        print(f"URL: {url}")

        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            asset_name = get_asset_name(version, platform_id)
            archive_path = temp_path / asset_name

            # Download the archive
            self._download_file(url, archive_path)
            print(f"Downloaded to temporary location: {archive_path}")

            # Extract the archive
            print(f"Extracting to {cache_path}...")
            self._extract_archive(archive_path, cache_path, platform_id)

        # Verify binary exists after extraction
        if not binary_path.exists():
            # The binary might be in a subdirectory (common in archives)
            # Try to find it
            for item in cache_path.rglob(self.get_binary_name(platform_id)):
                if item.is_file():
                    binary_path = item
                    break

            if not binary_path.exists():
                raise DownloadError(
                    f"Binary not found after extraction. Expected at: {binary_path}"
                )

        # Make binary executable on Unix systems
        self._make_executable(binary_path)
        print(f"Binary cached at: {binary_path}")

        return binary_path

    def get_cached_binary(
        self, version: str, platform_id: Optional[str] = None
    ) -> Optional[Path]:
        """
        Get the path to a cached binary if it exists.

        Args:
            version: Release version
            platform_id: Platform identifier (auto-detect if None)

        Returns:
            Path to binary or None if not cached
        """
        binary_path = self.get_binary_path(version, platform_id)
        return binary_path if binary_path.exists() else None

    def clear_cache(self, version: Optional[str] = None) -> None:
        """
        Clear cached binaries.

        Args:
            version: Specific version to clear (clears all if None)
        """
        if version:
            cache_path = self.get_cache_path(version)
            if cache_path.exists():
                shutil.rmtree(cache_path)
                print(f"Cleared cache for version {version}")
        else:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                print("Cleared all cached binaries")


def download_binary(version: str, platform: Optional[str] = None) -> Path:
    """
    Download and cache server binary from GitHub Releases.

    This is a convenience function that creates a ServerDownloader instance
    and downloads the binary.

    Args:
        version: Release version (e.g., "0.42.0")
        platform: Platform identifier (auto-detected if None)

    Returns:
        Path to cached binary executable

    Raises:
        PlatformNotSupportedError: If platform not supported
        DownloadError: If download fails

    Example:
        >>> binary_path = download_binary("0.42.0")
        >>> print(binary_path)
        PosixPath('/home/user/.cache/unity-mcp-server/0.42.0/unity-mcp-server')
    """
    downloader = ServerDownloader()
    return downloader.download(version, platform)


def get_cached_binary(version: str, platform: Optional[str] = None) -> Optional[Path]:
    """
    Get the path to a cached binary if it exists.

    Args:
        version: Release version
        platform: Platform identifier (auto-detected if None)

    Returns:
        Path to binary or None if not cached
    """
    downloader = ServerDownloader()
    return downloader.get_cached_binary(version, platform)


def is_cached(version: str, platform: Optional[str] = None) -> bool:
    """
    Check if the binary is already cached.

    Args:
        version: Release version
        platform: Platform identifier (auto-detected if None)

    Returns:
        True if binary exists in cache
    """
    downloader = ServerDownloader()
    return downloader.is_cached(version, platform)
