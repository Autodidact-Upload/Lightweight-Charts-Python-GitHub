"""Delegate pattern implementation for event handling."""
from typing import Callable, List


class Delegate:
    """Implements the delegate pattern for event subscriptions."""

    def __init__(self):
        """Initialize with empty callbacks list."""
        self._callbacks: List[Callable] = []

    def subscribe(self, callback: Callable):
        """Subscribe a callback function to this delegate."""
        self._callbacks.append(callback)
        return lambda: self._callbacks.remove(callback)

    def fire(self, *args, **kwargs):
        """Fire the event and call all subscribed callbacks."""
        for callback in self._callbacks:
            callback(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Make the delegate callable."""
        self.fire(*args, **kwargs)
