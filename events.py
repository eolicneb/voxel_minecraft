from typing import Any


class Event:
    """Base class for inner events"""
    origin: Any | None = None
    target: Any | None = None
    when: Any | None = None
    where: Any | None = None
    content: dict | None = None

    def __init__(self, *args, **kwargs):
        self.type = self.__class__


class MobsEvent(Event):
    """Base class for mobs related event"""


class MobDied(MobsEvent):
    def __init__(self, mob):
        super().__init__()
        self.content = {'mob': mob}


class PhysicsEvent(Event):
    """Base class for Physics related events"""


class BorderHit(PhysicsEvent):
    """A movable has hit the borders of the world"""
