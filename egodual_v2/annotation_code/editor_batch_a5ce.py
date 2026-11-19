from write_editor_batch import *
v='a5ce90da9a5cc07a'
goal=dict(title='Decorate a plate with clear and purple gems',description='Trial-arrange clear and purple decorative gems on a blue-green plate, gather them again, then use hot glue to attach the central clear motif and purple pieces extending around it.',final_state='Clear gems form a central motif with purple gems extending horizontally and vertically across the plate, which is lifted and displayed.',procedure=['Position the plate and lay out the clear gems near its center.','Arrange purple gems around the clear pieces to test a cross-like pattern.','Gather the loose gems and prepare the hot-glue gun.','Glue and press the clear center pieces into position.','Glue the purple gems around the center, press the pieces, remove fine glue strands, and display the decorated plate.'])
lines='''both hands position the plate on the newspaper|position|plate||newspaper|both||
right hand places a clear gem near the plate center|place|clear gem||plate|right||
right hand adds another clear gem beside the first|place|clear gem||plate|right||
right hand places another clear gem in the center motif|place|clear gem||plate|right||
right hand adjusts the clear gems on the plate|arrange|clear gem||plate|right||
right hand adds another clear gem to the arrangement|place|clear gem||plate|right||
right hand places a purple gem beside the clear motif|place|purple gem||plate|right||
right hand places another purple gem across the plate|place|purple gem||plate|right||
right hand adds a purple gem to the left side|place|purple gem||plate|right||
right hand moves a purple gem above the center|place|purple gem||plate|right||
right hand arranges purple gems below and beside the center|arrange|purple gem||plate|right||
right hand adjusts the spacing between the purple gems|arrange|purple gem||plate|right||
right hand repositions several gems on the plate|arrange|purple gem||plate|right||
right hand gathers the loose gems into a cluster|gather|decorative gem||plate|right||
right hand picks up the glue gun and applies glue|apply|glue gun||clear gem|both||glue gun
left hand places and presses a clear gem onto the plate|place|clear gem||plate|both||glue gun
left hand glues and places another clear gem|place|clear gem|glue gun|plate|both||glue gun
left hand presses another clear gem beside the first pieces|press|clear gem||plate|both||glue gun
left hand holds a clear gem against the plate|press|clear gem||plate|both||glue gun
left hand presses another clear gem into the center motif|press|clear gem||plate|both||glue gun
right hand applies glue before another clear gem is placed|apply|glue gun||clear gem|both||glue gun
left hand presses the clear gem into position|press|clear gem||plate|both||glue gun
right hand applies glue to a purple gem|apply|glue gun||purple gem|both|purple gem|glue gun
left hand places and presses the purple gem beside the center|place|purple gem||plate|both||glue gun
right hand applies glue to another purple gem|apply|glue gun||purple gem|both|purple gem|glue gun
left hand presses the purple gem onto the plate|press|purple gem||plate|both||glue gun
right hand applies glue to the next purple gem|apply|glue gun||purple gem|both|purple gem|glue gun
left hand presses another purple gem into the pattern|press|purple gem||plate|both||glue gun
right hand applies glue to another purple gem|apply|glue gun||purple gem|both|purple gem|glue gun
left hand presses the purple gem into place|press|purple gem||plate|both||glue gun
right hand applies glue to the next purple gem|apply|glue gun||purple gem|both|purple gem|glue gun
left hand presses another purple gem onto the plate|press|purple gem||plate|both||glue gun
right hand applies glue to another purple gem|apply|glue gun||purple gem|both|purple gem|glue gun
left hand places and presses another purple gem|place|purple gem||plate|both||glue gun
right hand applies glue to the remaining purple gem|apply|glue gun||purple gem|both|purple gem|glue gun
left hand places the last purple gem into the pattern|place|purple gem||plate|both||glue gun
right hand sets down the glue gun and presses gems|press|decorative gem||plate|right||
both hands press gems and pull away fine glue strands|remove|glue strand||plate|both||
both hands lift and tilt the decorated plate|lift|plate|||both||'''
groups=[(0,5,'Lay out the central clear motif','The plate is positioned on newspaper and clear decorative pieces placed and adjusted near its center.','Establishes the center of the planned decoration.'),(6,13,'Trial-arrange the purple pieces','Purple gems are spaced to either side, above, and below the center, then the loose pieces gathered again before gluing.','Tests the overall pattern and prepares the pieces for permanent attachment.'),(14,21,'Glue the clear center pieces','The glue gun is picked up and clear pieces are individually glued, placed, and held against the plate.','Secures the central motif.'),(22,35,'Glue the surrounding purple gems','Purple gems are picked up one at a time, receive hot glue, and are pressed into the horizontal and vertical extensions around the clear center.','Completes the surrounding colored pattern.'),(36,38,'Press, tidy, and display the decoration','The glue gun is put down, individual gems pressed again, fine glue strands pulled away, and the plate lifted and tilted for inspection.','Finishes the plate surface and shows the completed arrangement.')]
fix={14:dict(boundary_note='Includes picking up and orienting glue gun t=46–49s, selecting gem around t=51s, and applying glue t=52–57s.'),16:dict(boundary_note='Contains applying glue to next gem at t=63–64s then placing and pressing it t=65–68s.'),20:dict(boundary_note='Contains pause at t=80–81s, picking up gem near t=82s, glue application t=83–85s and positioning at end.'),30:dict(boundary_note='Begins by finishing pressure on previous gem near t=119s, then applies glue around t=120–122s.'),32:dict(boundary_note='Finishes positioning previous gem near t=125s, then selects and glues next piece around t=128–131s.'),34:dict(boundary_note='Finishes pressing near t=135–136s before glue application around t=137–138s.'),35:dict(boundary_note='Glue application continues t=138–140s before placement and pressing t=140–142s.'),36:dict(boundary_note='Includes setting glue gun down near t=144s and pressing several different gems t=146–159s.'),37:dict(boundary_note='Includes pressing multiple gems and pulling fine glue strands with both hands at t=165–171s.'),38:dict(boundary_note='Plate is lifted and tilted t=177–181s, then set down and hands withdrawn by t=182s.')}
write(v,goal,['plate','newspaper','clear gem','purple gem','decorative gem','glue gun','glue strand'],lines,groups,'Reviewed six overview sheets, all 672 dense step frames and 39 native endpoints. Only inherited fine boundaries retained; several gluing intervals contain the finish of one placement and preparation of the next, noted explicitly. Gem material is not inferred beyond decorative appearance; no unsupported glass/acrylic claim.',fix=fix,evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/a5ce90da9a5cc07a/20261106T075510553425Z/manifest.json')
