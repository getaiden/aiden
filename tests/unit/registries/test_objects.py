"""
Unit tests for the objects registry module.
"""

from aiden.registries.objects import ObjectRegistry


class SampleItem:
    """Simple class for testing the registry."""

    def __init__(self, value):
        self.value = value


def test_singleton_pattern():
    """Test that ObjectRegistry implements the singleton pattern."""
    # Create two instances and verify they are the same object
    registry1 = ObjectRegistry()
    registry2 = ObjectRegistry()

    assert registry1 is registry2


def test_register_and_get():
    """Test basic register and get functionality."""
    registry = ObjectRegistry()
    registry.clear()  # Start with a clean registry

    # Register and retrieve an item
    test_obj = SampleItem(42)
    registry.register(SampleItem, "test_item", test_obj)
    retrieved = registry.get(SampleItem, "test_item")

    # Verify it's the same object
    assert retrieved is test_obj
    assert retrieved.value == 42


def test_error_handling():
    """Test error handling for duplicates and nonexistent items."""
    registry = ObjectRegistry()
    registry.clear()

    # Test duplicate registration
    registry.register(SampleItem, "duplicate", SampleItem(1))
    try:
        registry.register(SampleItem, "duplicate", SampleItem(2))
        assert False, "Expected ValueError was not raised"
    except ValueError:
        pass  # Expected behavior

    # Test nonexistent item retrieval
    try:
        registry.get(SampleItem, "nonexistent")
        assert False, "Expected KeyError was not raised"
    except KeyError:
        pass  # Expected behavior


def test_bulk_operations():
    """Test bulk register and retrieve operations."""
    registry = ObjectRegistry()
    registry.clear()

    # Register multiple items
    items = {"item1": SampleItem(1), "item2": SampleItem(2), "item3": SampleItem(3)}
    registry.register_multiple(SampleItem, items)

    # Get multiple items
    retrieved = registry.get_multiple(SampleItem, ["item1", "item3"])
    assert retrieved["item1"] is items["item1"]
    assert retrieved["item3"] is items["item3"]

    # Get all items of a type
    class AnotherClass:
        pass

    registry.register(AnotherClass, "another", AnotherClass())

    all_items = registry.get_all(SampleItem)
    assert len(all_items) == 3
    assert all(isinstance(item, SampleItem) for item in all_items.values())


def test_registry_management():
    """Test registry management operations (clear and list)."""
    registry = ObjectRegistry()
    registry.clear()

    # Register items and verify list
    registry.register(SampleItem, "item1", SampleItem(1))
    registry.register(SampleItem, "item2", SampleItem(2))
    items = registry.list()
    assert len(items) == 2

    # Clear registry and verify empty
    registry.clear()
    assert len(registry.list()) == 0

    # Verify items are no longer retrievable
    try:
        registry.get(SampleItem, "item1")
        assert False, "Expected KeyError was not raised"
    except KeyError:
        pass  # Expected behavior
