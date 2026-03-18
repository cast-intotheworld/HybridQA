"""Serializer package — import all formats to trigger registration."""

from serialization.src.serializers.registry import get_serializer, list_formats

# Import all format modules so @register decorators execute
from serialization.src.serializers import (  # noqa: F401
    col_wise,
    compressed,
    interleaved,
    json_format,
    markdown_html,
    relation_explicit,
    row_wise,
)

__all__ = ["get_serializer", "list_formats"]
