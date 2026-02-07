"""Core data models for iPXE menu generation."""

from dataclasses import dataclass
from typing import List


@dataclass
class BootEntry:
    """Represents a single boot entry."""

    id: str
    label: str
    kernel_url: str
    initrd_url: str
    boot_params: str


@dataclass
class DistributionMenu:
    """Represents a distribution submenu."""

    id: str
    label: str
    entries: List[BootEntry]
