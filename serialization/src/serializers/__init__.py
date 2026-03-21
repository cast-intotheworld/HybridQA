"""Serializer package — import all formats to trigger registration."""

from serialization.src.serializers.registry import get_serializer, list_formats

# Import all format modules so @register decorators execute
from serialization.src.serializers import (  # noqa: F401
    csv_format,
    html,
    json_format,
    latex,
    markdown,
    xml_format,
    yaml_format,
)

__all__ = ["get_serializer", "list_formats"]
