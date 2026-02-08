"""iPXE Menu Generator package."""

from .core import BootEntry, DistributionMenu, MenuGenerator, URLValidator
from .distributions import AbstractMetadataFetcher, get_metadata_fetcher

__version__ = "0.1.1"
__all__ = [
    "BootEntry",
    "DistributionMenu",
    "URLValidator",
    "MenuGenerator",
    "get_metadata_fetcher",
    "AbstractMetadataFetcher",
]
