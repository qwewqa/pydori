from sonolus.script.engine import PlayMode

from pydori.lib.buckets import Buckets
from pydori.lib.effect import Effects
from pydori.lib.particle import Particles
from pydori.lib.skin import Skin
from pydori.play.connector import HoldConnector, SimLine
from pydori.play.event import BpmChange, TimescaleChange
from pydori.play.note import Note, UnscoredNote, HoldManager
from pydori.play.stage import Stage

play_mode = PlayMode(
    archetypes=[
        Stage,
        Note,
        UnscoredNote,
        HoldManager,
        HoldConnector,
        SimLine,
        BpmChange,
        TimescaleChange,
    ],
    skin=Skin,
    effects=Effects,
    particles=Particles,
    buckets=Buckets,
)
