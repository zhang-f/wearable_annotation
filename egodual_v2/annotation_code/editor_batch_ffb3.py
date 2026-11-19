from write_editor_batch import *
v='ffb3c66973fc8f88'
goal=dict(title='Make a black yarn friendship bracelet',description='Draw black yarn from a skein and cut several matching lengths. Gather and knot the strands, trim their ends, and tape the knotted end to the tabletop. Repeatedly cross and tighten the loose strands into a braid, tie the free end, trim excess yarn, and remove the bracelet from the tape.',final_state='A finished black braided loop with short loose ends is lifted and placed on the table near the video end.',procedure=['Pull yarn from the skein and cut the first length.','Match and cut additional yarn lengths.','Gather the strands and knot one end.','Trim loose ends and tape the knot to the table.','Cross the loose strands repeatedly and pull the braid taut.','Knot the free end and trim excess yarn.','Peel the bracelet from its tape anchor, inspect it, and set it down.'])
inv=['yarn skein','yarn','scissors','tape','tape dispenser','table']
lines='''both hands unwind black yarn from skein|unwind|yarn||yarn skein|both|yarn skein|scissors
right hand cuts yarn while left holds its end|cut|yarn|scissors||right|yarn|scissors
both hands align cut yarn with another length|align|yarn|||both|yarn|yarn
right hand stretches yarn across table|stretch|yarn|||right||yarn
right hand cuts another yarn length with scissors|cut|yarn|scissors||right|yarn|scissors
right hand cuts yarn while left pinches strands|cut|yarn|scissors||right|yarn|scissors
both hands measure yarn strands before right retrieves scissors|measure|yarn|||both|yarn|scissors
right hand cuts matching yarn lengths with scissors|cut|yarn|scissors||right|yarn|scissors
both hands align and pinch yarn ends|align|yarn|||both|yarn|yarn
both hands knot yarn ends and right trims loose strands|knot|yarn|scissors||both|yarn|
right hand reaches for green tape dispenser|reach|tape dispenser|||right|yarn|
both hands pull clear tape from dispenser|pull|tape|tape dispenser||both|tape|tape
both hands press taped yarn end onto table|press|yarn|tape|table|both|yarn|yarn
both hands repeatedly cross yarn strands and tighten braid|braid|yarn|||both|yarn|yarn
both hands knot loose yarn ends below braid|knot|yarn|||both|yarn|
right hand trims yarn and both hands loosen taped end|trim|yarn|scissors||both|tape|yarn'''
groups=[(0,5,'Cut matching black yarn lengths','Unwind black yarn, stretch it against the cut strand, and use scissors to prepare matching lengths.','Provides strands of similar length for the bracelet.'),(6,9,'Align, knot, and trim the yarn bundle','Measure the strands together, cut them, gather their ends into a knot, and trim protruding yarn.','Creates a joined end from which to braid.'),(10,12,'Tape the joined yarn end to the table','Retrieve the dispenser, pull out clear tape, and press the gathered yarn end against the tabletop.','Anchors the strands while their loose ends are braided.'),(13,13,'Braid and tighten the loose yarn strands','Alternately cross black strands over the center and pull them taut, repeatedly shifting the grip down the growing braid.','Forms the long braided body of the bracelet.'),(14,15,'Knot and trim the free end','Tie the yarn at the braid end, cut excess strands, and begin loosening the taped anchor.','Secures the braid and removes excess yarn; final release and display occur beyond the retained fine track.')]
fix={10:dict(confidence='medium',ambiguous=True,boundary_note='0.29s interval: at t=75.6–75.9s the right hand begins reaching toward the tape; dispenser pickup continues in the following step.'),13:dict(boundary_note='Preserved 184.97s interval contains many visible hand–strand switches, e.g. t=91–99s, 120–128s and 180–188s; braiding is not an atomic step.'),15:dict(boundary_note='At t=281–285s right hand takes scissors and trims yarn; t=286–287.5s hands begin releasing tape. Multiple hand-object changes occur in this retained interval.')}
write(v,goal,inv,lines,groups,'All 16 fine intervals were visually reviewed at 3fps (15fps for the subsecond interval), with native end frames. Fine boundaries are preserved. The fine track stops at 287.5s, before ffprobe duration 296.267s: at t=288–290s the hands release the taped end, t=290–293s lift and inspect the bracelet, and t=294–295s place it down. This task tail needs additional annotation; no fabricated fine boundaries were added. Predictability remains pending independent past-only testing.',fix,evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/ffb3c66973fc8f88/20261106T225249698173Z/manifest.json')
