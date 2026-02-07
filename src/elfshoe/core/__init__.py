"""Core package for iPXE menu generation.

This package contains the core functionality for generating
iPXE menus, including data models, URL validation, and
menu generation.
"""

from .generator import MenuGenerator
from .models import BootEntry, DistributionMenu
from .validator import URLValidator

__all__ = [
    "BootEntry",
    "DistributionMenu",
    "URLValidator",
    "MenuGenerator",
]
