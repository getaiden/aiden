"""
Unit test for the code module.
"""

from aiden.entities.code import Code


def test_code():
    """Test the Code class basic functionality."""
    # Create a simple code object
    code_str = "print('hello')"
    code_obj = Code(code=code_str)

    # Verify it stores the code correctly
    assert code_obj.code == code_str
