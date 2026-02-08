"""Menu generation using Jinja2 templates."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import DistributionMenu


class MenuGenerator:
    """Generates iPXE menu files using Jinja2 templates."""

    def __init__(self, config: Dict[str, Any], template_dir: Optional[Path] = None):
        """Initialize menu generator.

        Args:
            config: Configuration dictionary
            template_dir: Path to templates directory (defaults to src/templates)
        """
        self.config = config

        # Set up Jinja2 environment
        if template_dir is None:
            # Go up to src/ directory, then into templates/
            template_dir = Path(__file__).parent.parent / "templates"

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, menus: List[DistributionMenu]) -> str:
        """Generate complete iPXE menu using templates.

        Args:
            menus: List of distribution menus to include

        Returns:
            Generated iPXE menu as string
        """
        # Prepare menu configuration
        menu_config = self.config.get("menu", {})
        menu_data = {
            "title": menu_config.get("title", "Network Boot Menu"),
            "default_item": menu_config.get("default_item", "shell"),
            "timeout": menu_config.get("timeout", 30000),
        }

        # Get error timeout (defaults to main timeout if not set)
        error_timeout = menu_config.get("error_timeout", menu_config.get("timeout", 30000))

        # Convert distribution menus to dicts for template
        distributions_data = []
        for menu in menus:
            dist_dict = {
                "id": menu.id,
                "label": menu.label,
                "architectures": menu.architectures,
                "entries": [
                    {
                        "id": entry.id,
                        "label": entry.label,
                        "kernel_url": entry.kernel_url,
                        "initrd_url": entry.initrd_url,
                        "boot_params": entry.boot_params,
                        "arch_urls": entry.arch_urls,  # Include multi-arch URLs
                    }
                    for entry in menu.entries
                ],
            }
            distributions_data.append(dist_dict)

        # Get additional items
        additional_items = self.config.get("additional_items", [])

        # Render main template
        template = self.env.get_template("main_menu.ipxe.j2")
        output = template.render(
            menu=menu_data,
            distributions=distributions_data,
            additional_items=additional_items,
            error_timeout=error_timeout,
        )

        return output
