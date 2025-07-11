from sonolus.script.archetype import PlayArchetype, callback
from sonolus.script.runtime import time

from pydori.lib.buckets import init_score, init_buckets
from pydori.lib.layout import init_layout
from pydori.lib.note import init_note_life
from pydori.lib.stage import (
    draw_stage,
    init_stage_data,
    StageData,
    play_lane_sfx,
    play_lane_particle,
)
from pydori.lib.streams import EffectLanes, Streams
from pydori.lib.ui import init_ui
from pydori.play.input import refresh_input_state, unclaimed_taps
from pydori.play.note import active_notes, Note


class Stage(PlayArchetype):
    """Draws the stage and performs other global game functions."""

    name = "Stage"

    def preprocess(self):
        init_buckets()
        init_score()
        init_ui()
        init_layout()
        init_stage_data()
        init_note_life(Note)

    def spawn_order(self) -> float:
        return -1e8

    def should_spawn(self) -> bool:
        return True

    @callback(order=-1)
    def update_sequential(self):
        refresh_input_state()
        active_notes.clear()

    def update_parallel(self):
        draw_stage()

    @callback(order=2)
    def touch(self):
        self.handle_empty_lane_taps()

    @staticmethod
    def handle_empty_lane_taps():
        effect_lanes = EffectLanes.new()
        for tap in unclaimed_taps():
            for lane, quad in StageData.lane_layouts.items():
                if quad.contains_point(tap.position):
                    effect_lanes.add(lane)
                    play_lane_particle(lane)
                    play_lane_sfx()
        if len(effect_lanes) > 0:
            Streams.effect_lanes[time()] = effect_lanes
