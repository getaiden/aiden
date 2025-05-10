"""
This module provides utility functions for working with model descriptions and metadata.
"""

from typing import Optional


def format_code_snippet(code: Optional[str]) -> Optional[str]:
    """
    Format a code snippet for display, truncating if necessary.

    :param code: The source code as a string
    :return: A formatted code snippet or None if code doesn't exist
    """
    if not code:
        return None

    # Limit the size of code displayed, possibly add line numbers, etc.
    lines = code.splitlines()
    if len(lines) > 20:
        # Return first 10 and last 10 lines with a note in the middle
        return "\n".join(lines[:10] + ["# ... additional lines omitted ..."] + lines[-10:])
    return code
