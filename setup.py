#!/usr/bin/env python3
"""
Setup script for Airspace Checker
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Read version from navpro/__init__.py
def get_version():
    version_file = Path(__file__).parent / "navpro" / "__init__.py"
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', 
                            version_file.read_text(), re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="airspace-checker",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="Flight Profile & Airspace Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ffdumont/nav-profile",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Other/Nonlisted Topic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "colorama",
        "lxml",
        "matplotlib",
        "shapely",
        "rtree",
    ],
    entry_points={
        "console_scripts": [
            "airchk=navpro.navpro:main",
            "airspace-checker=navpro.navpro_gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)