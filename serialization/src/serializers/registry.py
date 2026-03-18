"""Serializer registry with decorator-based registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from serialization.src.serializers.base import BaseSerializer

_REGISTRY: dict[str, type[BaseSerializer]] = {}


def register(name: str):
    """Register a serializer class under the given name.

    :param name: Canonical name for the serializer.
    :return: Class decorator.

    Usage::

        @register("json")
        class JSONSerializer(BaseSerializer):
            ...
    """

    def decorator(cls: type[BaseSerializer]) -> type[BaseSerializer]:
        if name in _REGISTRY:
            raise ValueError(f"Serializer '{name}' is already registered")
        _REGISTRY[name] = cls
        return cls

    return decorator


def get_serializer(name: str, params: dict | None = None) -> BaseSerializer:
    """Retrieve a serializer instance by name.

    :param name: Registered serializer name.
    :param params: Format-specific parameters.
    :return: Instantiated serializer.
    :raises KeyError: If the name is not registered.
    """
    if name not in _REGISTRY:
        raise KeyError(
            f"Serializer '{name}' not found. Available: {list_formats()}"
        )
    return _REGISTRY[name](params=params)


def list_formats() -> list[str]:
    """List all registered serializer format names.

    :return: Sorted list of format names.
    """
    return sorted(_REGISTRY.keys())
