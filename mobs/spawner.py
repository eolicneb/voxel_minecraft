from pathlib import Path
import importlib

from events import *
from settings import *
from mobs.base import Mob


class MobSpawner:
    def __init__(self, app):
        self.app = app

        self.mobs_package = importlib.import_module("mobs")

        self.mob_seeds = {}

        self.mobs = {}

    def register_mob_seed(self, mob_seed_name: str):
        mob_module = getattr(self.mobs_package, mob_seed_name)
        if mob_module is None:
            return
        self.mob_seeds.update(self._get_module_mobs(mob_module))

    @staticmethod
    def _get_module_mobs(module):
        return {mob.__name__: mob for mob in module.__dict__.values() if isinstance(mob, type(Mob)) and mob is not Mob}

    def update(self):
        for mob_seed in self.mob_seeds.values():
            new_mob = mob_seed.spawn(self.app)
            if new_mob is None:
                continue
            self.mobs.update({new_mob.identifier: new_mob})
            new_mob.on_init()
            self.app.scene.register_mob(new_mob.identifier, new_mob)
            self.app.physics.register_movable(new_mob.movable)

        for mob in self.mobs.values():
            mob.update()

    def handle_event(self, event):
        if isinstance(event, MobDied):
            self.handle_mob_died_event(event)

        if event.target and event.target in self.mobs:
            self.mobs[event.target].handle_event(event)
        else:
            for mob in self.mobs.values():
                mob.handle_event(event)

    def handle_mob_died_event(self, event):
        if event.content['mob'].identifier in self.mobs:
            mob = self.app.scene.pop_mob(event.content['mob'].identifier)
            del self.mobs[mob.identifier]
