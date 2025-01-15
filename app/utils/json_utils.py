# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
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
