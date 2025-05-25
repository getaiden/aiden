"""
Unit test for the transformation_state module.
"""

from aiden.common.utils.transformation_state import TransformationState


def test_transformation_state():
    """Test the TransformationState enum values and behavior."""
    # Verify all state values
    states = {
        TransformationState.DRAFT: "draft",
        TransformationState.BUILDING: "building",
        TransformationState.READY: "ready",
        TransformationState.ERROR: "error",
    }

    # Test all enum values in one assertion
    for state, value in states.items():
        assert state.value == value
