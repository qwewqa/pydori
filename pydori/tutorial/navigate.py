from sonolus.script.runtime import navigation_direction

from pydori.tutorial.update import dec_phase, inc_phase


def navigate():
    if navigation_direction() > 0:
        inc_phase()
    else:
        dec_phase()
