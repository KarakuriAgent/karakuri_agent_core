def convert_none_to_null(obj):
    """Convert None values to 'null' string for JSON serialization.

    Args:
        obj: Any Python object that might be None

    Returns:
        str: 'null' if the input is None, otherwise returns the input unchanged
    """
    if obj is None:
        return "null"
    return obj
