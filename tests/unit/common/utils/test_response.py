"""
Unit test for the response utility module.
"""

from aiden.common.utils.response import wrap_code, is_valid_python_script, extract_code, extract_jsons, trim_long_string


def test_response_utils():
    """Test the core functionality of response utilities."""
    # Test code wrapping and validation
    assert wrap_code("x = 1") == "```python\nx = 1\n```"
    assert is_valid_python_script("x = 1") is True
    assert is_valid_python_script("x = ") is False

    # Test code extraction from markdown
    code = extract_code("```python\nx = 1\n```")
    assert "x = 1" in code

    # Test JSON extraction
    json_data = extract_jsons('{"a": 1}')
    assert len(json_data) == 1 and json_data[0]["a"] == 1

    # Test string truncation
    long_str = "a" * 6000
    short_str = trim_long_string(long_str, threshold=5000, k=10)
    assert len(short_str) < len(long_str)
