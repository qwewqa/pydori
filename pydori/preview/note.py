from __future__ import annotations


from sonolus.script.archetype import PreviewArchetype, imported, StandardImport, entity_data
from sonolus.script.timing import beat_to_time

from pydori.lib.layer import get_z, LAYER_NOTE, LAYER_ARROW
from pydori.lib.note import NoteKind, get_note_body_sprite, get_note_arrow_sprite
from pydori.lib.options import Options
from pydori.preview.layout import (
    layout_preview_note,
    layout_preview_flick_arrow,
    layout_preview_directional_flick_arrow,
    PreviewData,
)


class PreviewNote(PreviewArchetype):
    """Common archetype for notes."""

    kind: NoteKind = imported()
    lane: float = imported()
    beat: StandardImport.BEAT = imported()
    direction: int = imported()

    target_time: float = entity_data()

    def preprocess(self):
        if Options.mirror:
            self.lane = -self.lane
            self.direction = -self.direction

        self.target_time = beat_to_time(self.beat)

        PreviewData.last_time = max(PreviewData.last_time, self.target_time)
        PreviewData.last_beat = max(PreviewData.last_beat, self.beat)

    def render(self):
        self.draw_body()
        self.draw_arrow()

    def draw_body(self):
        if self.kind == NoteKind.HOLD_ANCHOR:
            return
        body_sprite = get_note_body_sprite(self.kind, self.direction)
        layout = layout_preview_note(self.lane, self.target_time)
        body_sprite.draw(layout, z=get_z(LAYER_NOTE, lane=self.lane, y=self.target_time))

    def draw_arrow(self):
        arrow_sprite = get_note_arrow_sprite(self.kind, self.direction)
        match self.kind:
            case NoteKind.FLICK:
                layout = layout_preview_flick_arrow(self.lane, self.target_time)
                arrow_sprite.draw(layout, z=get_z(LAYER_ARROW, lane=self.lane, y=self.target_time))
            case NoteKind.DIRECTIONAL_FLICK:
                for i in range(abs(self.direction)):
                    lane_offset = (i + 1) * (1 if self.direction > 0 else -1)
                    arrow_lane = self.lane + lane_offset
                    layout = layout_preview_directional_flick_arrow(
                        arrow_lane, self.target_time, direction=self.direction
                    )
                    arrow_sprite.draw(layout, z=get_z(LAYER_ARROW, lane=arrow_lane, y=self.target_time))
            case _:
                pass


PreviewScoredNote = PreviewNote.derive("Note", is_scored=True)
PreviewUnscoredNote = PreviewNote.derive("UnscoredNote", is_scored=False)
