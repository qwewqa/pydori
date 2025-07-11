from sonolus.script.archetype import StandardArchetypeName, StandardImport, imported, WatchArchetype


class WatchBpmChange(WatchArchetype):
    name = StandardArchetypeName.BPM_CHANGE

    beat: StandardImport.BEAT = imported()
    bpm: StandardImport.BPM = imported()


class WatchTimescaleChange(WatchArchetype):
    name = StandardArchetypeName.TIMESCALE_CHANGE

    beat: StandardImport.BEAT = imported()
    timescale: StandardImport.TIMESCALE = imported()
