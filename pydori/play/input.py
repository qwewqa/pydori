from typing import Iterator

from sonolus.script.containers import ArraySet
from sonolus.script.globals import level_memory
from sonolus.script.runtime import Touch, touches


@level_memory
class InputState:
    claimed_touches: ArraySet[int, 16]


def refresh_input_state():
    """Refresh the input data at the start of each frame."""
    InputState.claimed_touches.clear()


def claim_touch(touch_id: int) -> None:
    InputState.claimed_touches.add(touch_id)


def is_touch_claimed(touch_id: int) -> bool:
    return touch_id in InputState.claimed_touches


def unclaimed_taps() -> Iterator[Touch]:
    return filter(lambda touch: touch.started and not is_touch_claimed(touch.id), touches())


def unclaimed_touches() -> Iterator[Touch]:
    return filter(lambda touch: not is_touch_claimed(touch.id), touches())
