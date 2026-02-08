"""Core data models for iPXE menu generation."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


# Architecture constants - iPXE buildarch values
ARCH_X86_64 = "x86_64"
ARCH_I386 = "i386"
ARCH_ARM64 = "arm64"
ARCH_ARM = "arm"

# Common architecture mappings: iPXE name -> Distribution name
DEFAULT_ARCH_MAPS = {
    'fedora': {ARCH_X86_64: 'x86_64', ARCH_ARM64: 'aarch64', ARCH_I386: 'i386'},
    'centos': {ARCH_X86_64: 'x86_64', ARCH_ARM64: 'aarch64'},
    'debian': {ARCH_X86_64: 'amd64', ARCH_ARM64: 'arm64', ARCH_I386: 'i386'},
    'ubuntu': {ARCH_X86_64: 'amd64', ARCH_ARM64: 'arm64', ARCH_I386: 'i386'},
}


@dataclass
class BootEntry:
    """Represents a single boot entry (may support multiple architectures)."""

    id: str
    label: str
    kernel_url: str
    initrd_url: str
    boot_params: str
    arch: Optional[str] = None  # Specific architecture (e.g., 'x86_64')
    # For multi-arch entries: map arch -> URLs
    arch_urls: Optional[Dict[str, Dict[str, str]]] = None  # arch -> {kernel, initrd}


@dataclass
class DistributionMenu:
    """Represents a distribution submenu."""

    id: str
    label: str
    entries: List[BootEntry]
    architectures: List[str] = field(default_factory=lambda: [ARCH_X86_64])  # Supported archs
