from pydori.lib.skin import Skin
from sonolus.script.engine import PreviewMode

from pydori.preview.connector import PreviewHoldConnector, PreviewSimLine
from pydori.preview.event import PreviewBpmChange, PreviewTimescaleChange
from pydori.preview.note import PreviewScoredNote, PreviewUnscoredNote
from pydori.preview.stage import PreviewStage

preview_mode = PreviewMode(
    archetypes=[
        PreviewStage,
        PreviewScoredNote,
        PreviewUnscoredNote,
        PreviewHoldConnector,
        PreviewSimLine,
        PreviewBpmChange,
        PreviewTimescaleChange,
    ],
    skin=Skin,
)
