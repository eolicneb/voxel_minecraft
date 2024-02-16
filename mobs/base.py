from __future__ import annotations
from abc import ABC, abstractmethod, abstractclassmethod


class Mob(ABC):
    """Base class to define a mob"""
    identifier: str
    is_alive: bool
    count: int
    max_count: int | None

    @classmethod
    @abstractmethod
    def spawn(cls, app) -> Mob | None:
        """Must return an instance of the mob or None"""

    def on_init(self):
        pass

    def on_delete(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def render_see_through(self):
        pass
