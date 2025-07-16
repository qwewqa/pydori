import itertools

from sonolus.script.level import LevelData, BpmChange, Level

from pydori.convert.utils import get_sonolus_level_item, convert_sonolus_level_item, parse_entities
from pydori.lib.note import NoteKind
from pydori.play.connector import HoldConnector, SimLine
from pydori.play.note import Note, UnscoredNote
from pydori.play.stage import Stage


def convert_sonolus_bandori_level(name: str, base_url: str = "https://sonolus.bestdori.com/official/") -> Level:
    """Download and convert a Sonolus Bandori level data to pydori level data."""
    item = get_sonolus_level_item(name, base_url)
    return convert_sonolus_level_item(item, base_url, "Bandori", convert_sonolus_bandori_level_data)


def convert_sonolus_bandori_level_data(data: dict) -> LevelData:
    """Convert Sonolus Bandori level data into pydori level data."""
    bgm_offset = data["bgmOffset"]
    entities = parse_entities(data["entities"])

    notes: list[Note] = []
    notes_by_index: dict[int, Note] = {}
    bpm_changes: list[BpmChange] = []
    hold_connectors: list[HoldConnector] = []
    sim_lines: list[SimLine] = []
    for i, (archetype, d) in enumerate(entities):
        match archetype:
            case "#BPM_CHANGE":
                bpm_changes.append(
                    BpmChange(
                        beat=d["#BEAT"],
                        bpm=d["#BPM"],
                    )
                )
            case "TapNote":
                note = Note(
                    kind=NoteKind.TAP,
                    beat=d["#BEAT"],
                    lane=d["lane"],
                )
                notes.append(note)
                notes_by_index[i] = note
            case "FlickNote" | "SlideEndFlickNote":
                note = Note(
                    kind=NoteKind.FLICK,
                    beat=d["#BEAT"],
                    lane=d["lane"],
                )
                notes.append(note)
                notes_by_index[i] = note
            case "DirectionalFlickNote":
                note = Note(
                    kind=NoteKind.DIRECTIONAL_FLICK,
                    beat=d["#BEAT"],
                    lane=d["lane"],
                    direction=d["direction"] * d["size"],
                )
                notes.append(note)
                notes_by_index[i] = note
            case "SlideStartNote":
                note = Note(
                    kind=NoteKind.HOLD_HEAD,
                    beat=d["#BEAT"],
                    lane=d["lane"],
                )
                notes.append(note)
                notes_by_index[i] = note
            case "SlideEndNote":
                note = Note(
                    kind=NoteKind.HOLD_END,
                    beat=d["#BEAT"],
                    lane=d["lane"],
                )
                notes.append(note)
                notes_by_index[i] = note
            case "SlideTickNote":
                note = Note(
                    kind=NoteKind.HOLD_TICK,
                    beat=d["#BEAT"],
                    lane=d["lane"],
                )
                notes.append(note)
                notes_by_index[i] = note
            case "IgnoredNote":
                note = UnscoredNote(
                    kind=NoteKind.HOLD_ANCHOR,
                    beat=d["#BEAT"],
                    lane=d["lane"],
                )
                notes.append(note)
                notes_by_index[i] = note
            case "CurvedSlideConnector" | "StraightSlideConnector" | "Stage" | "Initialization" | "SimLine":
                pass
            case _:
                raise ValueError(f"Unknown archetype: {archetype}")

    for archetype, d in entities:
        match archetype:
            case "CurvedSlideConnector" | "StraightSlideConnector":
                first = notes_by_index[int(d["head"])]
                second = notes_by_index[int(d["tail"])]
                hold_connectors.append(HoldConnector(first_ref=first.ref(), second_ref=second.ref()))
                second.prev_ref = first.ref()
                first.next_ref = second.ref()

    notes.sort(key=lambda note: note.beat)
    for a, b in itertools.pairwise(notes):
        # Resolve minor discrepancies in beat values if they are very close
        if a.beat != b.beat and abs(a.beat - b.beat) < 0.002:
            b.beat = a.beat
    notes_by_beat: dict[float, list[Note]] = {}
    for note in notes:
        notes_by_beat.setdefault(note.beat, []).append(note)
    for group in notes_by_beat.values():
        group.sort(key=lambda note: note.lane)
        for a, b in itertools.pairwise(n for n in group if n.kind not in {NoteKind.HOLD_TICK, NoteKind.HOLD_ANCHOR}):
            sim_lines.append(SimLine(first_ref=a.ref(), second_ref=b.ref()))

    return LevelData(
        bgm_offset=bgm_offset,
        entities=[
            Stage(),
            *bpm_changes,
            *notes,
            *hold_connectors,
            *sim_lines,
        ],
    )
