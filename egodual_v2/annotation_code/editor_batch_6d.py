from write_editor_batch import *
write('6d839f832037b10b',dict(title='Install a wire holder for a pump bottle on a cabinet door',description='Retrieve a tape measure, small hardware and hammer from the cabinet. Measure a position on the closed door and try driving a nail near the hanging towel. Reopen the cabinet, remeasure the door and secure the wire hook at the revised position with the hammer. Hang the green-liquid pump bottle on the hook, adjust its neck and test the pump repeatedly. Remove the bottle, reinforce the hook with additional hammer taps and hang the bottle again.',final_state='The pump bottle hangs from the wire holder on the cabinet door and its pump is pressed again.',procedure=['Gather the tape measure and hammer and measure the door.','Try the initial nail position and remeasure the mounting location.','Hammer the wire holder onto the door.','Hang the bottle and test its pump.','Reinforce the holder and hang the bottle again.']),['tape measure','hammer','nail','wire hook','cabinet door','pump bottle','cabinet shelf'],'''
pick up a nail|pick up|nail|||right||nail
pick up the tape measure|pick up|tape measure|||right||tape measure
pull out the measuring tape|extend|tape measure|||both|tape measure|tape measure
push the cabinet door closed|close|cabinet door|||left||tape measure
move around the cabinet door holding the tape measure|move|tape measure|||right||tape measure
hold the door closed by its knob|close|cabinet door|||left||tape measure
measure vertically along the cabinet door|measure|cabinet door|tape measure||both|tape measure|tape measure
retract and lower the measuring tape|retract|tape measure|||both||tape measure
put the tape measure on the cabinet shelf|put down|tape measure||cabinet shelf|right||
take the hammer and nail|pick up|hammer||nail|both|nail|hammer
position the nail and tap it with the hammer|hammer|nail|hammer|cabinet door|both|nail|hammer
continue hammering the nail into the door|hammer|nail|hammer|cabinet door|both|nail|hammer
pick up the wire hook from the shelf|pick up|wire hook||cabinet shelf|right||wire hook
position the wire hook against the door|position|wire hook||cabinet door|right||tape measure
measure the cabinet door again|measure|cabinet door|tape measure||both|tape measure|tape measure
hold the tape against the door and read it|measure|cabinet door|tape measure||both|tape measure|tape measure
measure another position on the cabinet door|measure|cabinet door|tape measure||both||
retrieve the hammer and position the nail|position|nail|hammer|cabinet door|both|nail|hammer
hammer the nail into the door|hammer|nail|hammer|cabinet door|both|nail|hammer
position the wire hook around the nail|position|wire hook||nail|left|wire hook|hammer
hammer the hook fastener into the door|hammer|nail|hammer|wire hook|both|wire hook|hammer
put the hammer on the cabinet shelf|put down|hammer||cabinet shelf|right||
lift the pump bottle onto the hook|hang|pump bottle||wire hook|right||pump bottle
adjust the hanging bottle and its pump|adjust|pump bottle|||both|pump bottle|pump bottle
press the pump above the open palm|press|pump bottle|||right||
idle: rub hands and turn towards the cabinet|||||both||
test the pump on the hanging bottle|press|pump bottle|||right||
press the pump above the open palm|press|pump bottle|||right||
idle: rub hands and gesture beside the door|||||both||
lift the bottle off the hook and rehang it|hang|pump bottle||wire hook|right||
adjust the bottle on the wire hook|adjust|pump bottle||wire hook|right||pump bottle
press the bottle pump again|press|pump bottle|||right||
idle: release the bottle and pause|||||none||
lift the bottle off the wire hook|remove|pump bottle||wire hook|right||pump bottle
adjust the bottle neck beneath the pump|adjust|pump bottle|||both|pump bottle|pump bottle
put down the bottle and retrieve the hammer|pick up|hammer||cabinet shelf|right||hammer
tap the wire hook fastener with the hammer|hammer|nail|hammer|wire hook|right||hammer
put the hammer back on the shelf|put down|hammer||cabinet shelf|right||
pick up the pump bottle again|pick up|pump bottle|||both|pump bottle|pump bottle
rehang the bottle and press its pump|hang|pump bottle||wire hook|right||
''',[(0,9,'Measure the door and gather the mounting tools.','Retrieve small hardware and the tape measure, close the door and measure vertically before collecting the hammer.','Establish an initial mounting location and collect the tools needed to attach the holder.'),(10,13,'Try the initial fastener position.','Hold the nail against the door below the towel, hammer it and bring the wire hook to the door.','Try the first mounting point before revising its position.'),(14,16,'Remeasure the holder position.','Measure the door repeatedly, including a measurement from lower down, then return the tape measure to the cabinet.','Choose a revised location for mounting the bottle holder.'),(17,21,'Secure the wire hook to the door.','Bring the hammer and nail back to the door, position the wire hook and repeatedly tap its fastener before putting the hammer away.','Attach the holder that will support the pump bottle.'),(22,34,'Hang and test the pump bottle.','Hang the bottle on the hook, adjust it and repeatedly press its pump above the palm; remove and rehang the bottle while checking its support.','Check that the installed holder supports the bottle and permits operating its pump.'),(35,39,'Reinforce the hook and rehang the bottle.','Put the bottle aside, hammer the holder fastener again, return the hammer and hang and operate the bottle once more.','Leave the bottle hanging on the reinforced holder.')], 'Viewed all six overview sheets, eleven dense 3/15 fps contact sheets and three native endpoint sheets. At t=32–39s an initial nail is hammered near the towel; at t=48–76s the door is measured again; t=83–104s shows fastening the wire holder; t=110–152s shows repeated bottle hanging and pumping; t=161–164s shows further hammer taps. Small hardware and some final grips are partly hidden. The source final boundary is 170.18s and true video duration is 171.2s; the remaining brief tail is not assigned a new step.',fix={i:dict(ambiguous=True,confidence='medium',notes='Small hardware or endpoint grip is partly occluded.') for i in [0,1,4,7,8,12,13,16,19,37,38]},evidence_manifest=str(OUT/'frames_v2/6d839f832037b10b/20261106T055945096418Z/manifest.json'))
