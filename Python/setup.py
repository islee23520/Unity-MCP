#!/usr/bin/env python
"""
Setup script for unity-mcp-server package.

This file provides backward compatibility for older pip versions
that do not support pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="unity-mcp-server",
    version="0.1.0",
    description="Python wrapper and downloader for Unity MCP Server",
    author="Ivan Murzak",
    author_email="ivan.murzak@gmail.com",
    python_requires=">=3.8",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "unity-mcp=unity_mcp_server.cli:main",
        ],
    },
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "build>=1.0",
            "twine>=4.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="unity mcp model-context-protocol game-engine ai",
    url="https://github.com/ivanmurzak/unity-mcp",
    license="MIT",
)
