"""Utility functions for data manipulation."""


def deep_merge(a: dict, b: dict) -> dict:
    """Recursively merge dict b into dict a.

    Args:
        a: Base dict (will be mutated).
        b: Dict to merge into a.

    Returns:
        The merged dict (same object as a).
    """
    for key, value in b.items():
        if key in a and isinstance(a[key], dict) and isinstance(value, dict):
            deep_merge(a[key], value)
        else:
            a[key] = value
    return a


def chunk(items: list, size: int) -> list[list]:
    """Split a list into chunks of given size.

    Args:
        items: The list to split.
        size: Maximum size of each chunk.

    Returns:
        A list of chunks.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size)]
