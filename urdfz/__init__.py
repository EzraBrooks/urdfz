"""
urdfz - Self-contained, portable, actually UNIFIED Robot Description Files (URDFs)

A CLI tool for creating and unpacking URDFZ archives that contain URDFs and all
their associated mesh files and assets in a single portable archive.
"""

from .pack import make_urdfz_file
from .unpack import unpack_urdfz_file

__version__ = "0.2.1"
__all__ = ["make_urdfz_file", "unpack_urdfz_file", "__version__"]
