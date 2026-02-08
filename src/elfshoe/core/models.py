"""Core data models for iPXE menu generation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Architecture constants - iPXE buildarch values
ARCH_X86_64 = "x86_64"
ARCH_I386 = "i386"
ARCH_ARM64 = "arm64"
ARCH_ARM = "arm"

# Common architecture mappings: iPXE name -> Distribution name
DEFAULT_ARCH_MAPS = {
    "fedora": {ARCH_X86_64: "x86_64", ARCH_ARM64: "aarch64", ARCH_I386: "i386"},
    "centos": {ARCH_X86_64: "x86_64", ARCH_ARM64: "aarch64"},
    "debian": {ARCH_X86_64: "amd64", ARCH_ARM64: "arm64", ARCH_I386: "i386"},
    "ubuntu": {ARCH_X86_64: "amd64", ARCH_ARM64: "arm64", ARCH_I386: "i386"},
}


@dataclass
class VersionObject:
    """Represents a distribution version with supported architectures."""

    version: str
    architectures: List[str]
    variant: Optional[str] = None  # e.g., "Server" for Fedora
    name: Optional[str] = None  # e.g., "Bookworm" for Debian


@dataclass
class BootEntry:
    """Represents a single boot entry for a specific version and architecture."""

    id: str
    label: str
    kernel_url: str
    initrd_url: str
    boot_params: str
    architecture: Optional[str] = None  # Specific architecture (e.g., 'x86_64')
    version: Optional[str] = None  # Version string
    variant: Optional[str] = None  # Variant (e.g., "Server")
    # For multi-arch entries: map arch -> URLs
    arch_urls: Optional[Dict[str, Dict[str, str]]] = None  # arch -> {kernel, initrd}


@dataclass
class DistributionMenu:
    """Represents a distribution submenu."""

    id: str
    label: str
    entries: List[BootEntry]
    architectures: List[str] = field(default_factory=lambda: [ARCH_X86_64])  # Supported archs
