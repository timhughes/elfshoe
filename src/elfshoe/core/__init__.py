"""Core package for iPXE menu generation.

This package contains the core functionality for generating
iPXE menus, including data models, URL validation, and
menu generation.
"""

from .generator import MenuGenerator
from .models import (
    BootEntry,
    DistributionMenu,
    DEFAULT_ARCH_MAPS,
    ARCH_X86_64,
    ARCH_ARM64,
    ARCH_I386,
    ARCH_ARM,
)
from .validator import URLValidator

__all__ = [
    "BootEntry",
    "DistributionMenu",
    "URLValidator",
    "MenuGenerator",
    "DEFAULT_ARCH_MAPS",
    "ARCH_X86_64",
    "ARCH_ARM64",
    "ARCH_I386",
    "ARCH_ARM",
]
