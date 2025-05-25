"""
Unit tests for the callbacks module.
"""

from unittest.mock import Mock

from aiden.callbacks import ChainOfThoughtModelCallback, BuildStateInfo
from aiden.common.utils.cot.callable import ChainOfThoughtCallable


def test_on_build_start():
    """Test on_build_start method."""
    # Setup
    mock_cot_callable = Mock(spec=ChainOfThoughtCallable)
    mock_emitter = Mock()
    mock_cot_callable.emitter = mock_emitter

    callback = ChainOfThoughtModelCallback()
    callback.cot_callable = mock_cot_callable

    # Call the method with test info
    callback.on_build_start(BuildStateInfo(intent="Test intent", provider="openai/gpt-4o"))

    # Verify expected method calls
    mock_cot_callable.clear.assert_called_once()
    mock_emitter.emit_thought.assert_called_once()
    assert "System" in mock_emitter.emit_thought.call_args[0]
    assert "Test intent" in mock_emitter.emit_thought.call_args[0][1]


def test_on_build_end():
    """Test on_build_end method."""
    # Setup and call
    mock_cot_callable = Mock(spec=ChainOfThoughtCallable)
    mock_emitter = Mock()
    mock_cot_callable.emitter = mock_emitter

    callback = ChainOfThoughtModelCallback()
    callback.cot_callable = mock_cot_callable
    callback.on_build_end(BuildStateInfo(intent="Test intent", provider="openai/gpt-4o"))

    # Verify message
    mock_emitter.emit_thought.assert_called_once_with("System", "✅ Model build completed")


def test_on_iteration_start():
    """Test on_iteration_start method."""
    # Setup and call
    mock_cot_callable = Mock(spec=ChainOfThoughtCallable)
    mock_emitter = Mock()
    mock_cot_callable.emitter = mock_emitter

    callback = ChainOfThoughtModelCallback()
    callback.cot_callable = mock_cot_callable
    callback.on_iteration_start(BuildStateInfo(intent="Test", provider="test", iteration=2))

    # Verify correct iteration number in message
    mock_emitter.emit_thought.assert_called_once_with("System", "📊 Starting iteration 3")


def test_on_iteration_end_with_node():
    """Test on_iteration_end method when node is present."""
    # Setup with mock node
    mock_cot_callable = Mock(spec=ChainOfThoughtCallable)
    mock_emitter = Mock()
    mock_cot_callable.emitter = mock_emitter
    mock_node = Mock()

    callback = ChainOfThoughtModelCallback()
    callback.cot_callable = mock_cot_callable
    callback.on_iteration_end(BuildStateInfo(intent="Test", provider="test", iteration=1, node=mock_node))

    # Verify success message
    mock_emitter.emit_thought.assert_called_once_with("System", "📋 Iteration 2 completed.")


def test_on_iteration_end_without_node():
    """Test on_iteration_end method when node is not present."""
    # Setup without node
    mock_cot_callable = Mock(spec=ChainOfThoughtCallable)
    mock_emitter = Mock()
    mock_cot_callable.emitter = mock_emitter

    callback = ChainOfThoughtModelCallback()
    callback.cot_callable = mock_cot_callable
    callback.on_iteration_end(BuildStateInfo(intent="Test", provider="test", iteration=0))

    # Verify failure message
    mock_emitter.emit_thought.assert_called_once_with(
        "System", "📋 Iteration 1 failed: No performance metrics available"
    )


def test_get_chain_of_thought_callable():
    """Test get_chain_of_thought_callable method."""
    mock_cot_callable = Mock(spec=ChainOfThoughtCallable)
    callback = ChainOfThoughtModelCallback()
    callback.cot_callable = mock_cot_callable

    # Verify it returns the callable
    assert callback.get_chain_of_thought_callable() is mock_cot_callable


def test_get_full_chain_of_thought():
    """Test get_full_chain_of_thought method."""
    mock_cot_callable = Mock(spec=ChainOfThoughtCallable)
    mock_steps = [Mock(), Mock()]
    mock_cot_callable.get_full_chain_of_thought.return_value = mock_steps

    callback = ChainOfThoughtModelCallback()
    callback.cot_callable = mock_cot_callable

    # Verify it delegates to the callable and returns its result
    assert callback.get_full_chain_of_thought() is mock_steps
    mock_cot_callable.get_full_chain_of_thought.assert_called_once()
