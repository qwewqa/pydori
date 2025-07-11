from sonolus.script.containers import ArraySet
from sonolus.script.stream import streams, Stream, StreamGroup

EffectLanes = ArraySet[float, 16]


@streams
class Streams:
    # Records the set of lanes at each time when the empty tap lane effect was played.
    effect_lanes: Stream[EffectLanes]

    # Records whether a hold is active at a given time.
    # Keyed by the hold head's index.
    hold_activity: StreamGroup[bool, 99999]
