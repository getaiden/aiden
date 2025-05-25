"""
Unit test for the transformation_utils module.
"""

from aiden.common.utils.transformation_utils import format_code_snippet


def test_format_code_snippet():
    """Test code snippet formatting with different inputs."""
    # Test edge cases
    assert format_code_snippet(None) is None
    assert format_code_snippet("") is None  # Empty string is treated as falsy

    # Test normal case - short code is returned unchanged
    short_code = "def test(): pass"
    assert format_code_snippet(short_code) == short_code

    # Test truncation case - long code gets truncated
    long_code = "\n".join([f"line {i}" for i in range(30)])
    result = format_code_snippet(long_code)

    # Verify truncation occurred and format is correct
    assert "additional lines omitted" in result
    assert "line 0" in result and "line 29" in result
