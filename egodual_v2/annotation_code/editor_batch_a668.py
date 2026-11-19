from write_editor_batch import *
write('a668107d4cbb61d6',dict(title='Cook a barbecue chicken and cheese quesadilla',description='Open the tortilla bag and set two tortillas on the board. Retrieve the container of cooked chicken from the microwave. Pour barbecue sauce over one tortilla and spread it with a spoon. Cut chicken pieces smaller and scatter them over the sauce, add shredded cheese and cover with the other tortilla. Cook the filled tortilla stack in a frying pan, repeatedly pressing, checking and turning it with a spatula. Transfer it to a plate and cut it into quarters with a rolling cutter.',final_state='The cooked quesadilla is on the plate, cut into four portions. No eating is shown.',procedure=['Lay out two tortillas and retrieve the cooked chicken.','Coat one tortilla with barbecue sauce.','Dice the chicken and add it to the sauced tortilla.','Sprinkle shredded cheese and add the top tortilla.','Cook, press and turn the quesadilla in the frying pan.','Transfer the quesadilla to a plate and cut it into portions.']),['tortilla bag','tortilla','microwave door','chicken container','chicken','barbecue sauce bottle','bottle cap','drawer','spoon','knife','shredded cheese bag','shredded cheese','frying pan','burner knob','spatula','plate','rolling cutter','phone','thermostat','window','counter'],'''
pick up the tortilla bag|pick up|tortilla bag|||both|tortilla bag|tortilla bag
open the tortilla bag|open|tortilla bag|||both|tortilla bag|tortilla bag
pull tortillas from the bag|remove|tortilla||tortilla bag|both|tortilla|tortilla
place one tortilla on the cutting board|place|tortilla|||right||tortilla
place the other tortilla on the board|place|tortilla|||right||
move the tortilla bag aside|move|tortilla bag|||right||
open the microwave door|open|microwave door|||left||
remove the cooked chicken container from the microwave|remove|chicken container||microwave door|right||chicken container
put the chicken container beside the board|put down|chicken container||counter|right||
pick up the barbecue sauce bottle|pick up|barbecue sauce bottle|||both|barbecue sauce bottle|bottle cap
remove the sauce bottle cap|open|barbecue sauce bottle|||right|barbecue sauce bottle|bottle cap
pour barbecue sauce over one tortilla|pour|barbecue sauce bottle||tortilla|right||barbecue sauce bottle
close the barbecue sauce bottle|close|barbecue sauce bottle|||both|barbecue sauce bottle|
put down the sauce bottle|put down|barbecue sauce bottle||counter|right||
open the cutlery drawer|open|drawer|||right||
take a spoon from the drawer|pick up|spoon|||right||spoon
carry the spoon back to the board|move|spoon|||right||spoon
spread barbecue sauce over the tortilla|spread|tortilla|spoon||right||spoon
smooth the sauce across the tortilla|spread|tortilla|spoon||right||spoon
continue spreading the barbecue sauce|spread|tortilla|spoon||right||spoon
put the spoon down|put down|spoon||counter|right||
release the spoon beside the board|put down|spoon||counter|right||
move the chicken container beside the cutting board|move|chicken container|||right||
idle: tap and scroll on the phone|||||right||
move the filled tortilla farther up the board|move|tortilla|||left||
pick up the knife and select chicken pieces|pick up|knife||chicken|both|chicken|knife
lift chicken from the container|pick up|chicken|||left|chicken|knife
place the chicken on the cutting board|place|chicken|||left|chicken|knife
cut the chicken into smaller pieces|cut|chicken|knife||both|chicken|knife
cut another section of chicken|cut|chicken|knife||both|chicken|knife
continue dicing the chicken|cut|chicken|knife||both|chicken|knife
cut the remaining chicken into small pieces|cut|chicken|knife||both|chicken|knife
finish chopping the chicken pieces|cut|chicken|knife||both|chicken|knife
put the knife down beside the chicken|put down|knife||counter|right||
gather chopped chicken with both hands|pick up|chicken|||both|chicken|chicken
scatter chopped chicken over the sauced tortilla|place|chicken||tortilla|both||chicken
add the remaining chicken pieces to the tortilla|place|chicken||tortilla|right||
pick up the shredded cheese bag|pick up|shredded cheese bag|||both|shredded cheese bag|shredded cheese bag
pull at the cheese bag seal|open|shredded cheese bag|||both|shredded cheese bag|shredded cheese bag
turn the stove burner knob|turn|burner knob|||left||shredded cheese bag
pull the cheese bag open|open|shredded cheese bag|||both|shredded cheese bag|shredded cheese bag
tear open the shredded cheese bag|open|shredded cheese bag|||both|shredded cheese bag|shredded cheese
sprinkle shredded cheese over the chicken|place|shredded cheese||tortilla|right|shredded cheese bag|
add more shredded cheese over the tortilla|place|shredded cheese||tortilla|right|shredded cheese bag|
spread the cheese across the filling|adjust|shredded cheese||tortilla|right|shredded cheese bag|
put down the shredded cheese bag|put down|shredded cheese bag||counter|right||
adjust the filling on the tortilla|adjust|shredded cheese||tortilla|left||
pick up the second tortilla|pick up|tortilla|||both|tortilla|tortilla
place the second tortilla over the filling|place|tortilla||tortilla|both||
lift the filled tortilla stack into the pan|place|tortilla||frying pan|both||
press the top tortilla with both hands|press|tortilla||frying pan|both||
idle: walk to the thermostat|||||unclear||
idle: press the thermostat controls|||||right||
idle: walk back to the stove|||||unclear||
press the tortilla stack with the palm|press|tortilla||frying pan|left||
press the tortilla with both hands|press|tortilla||frying pan|both||
press and rotate the tortilla in the pan|adjust|tortilla||frying pan|right||
pick up the spatula from the utensil holder|pick up|spatula|||right||spatula
bring the spatula toward the frying pan|move|spatula||frying pan|right||spatula
press the quesadilla with the spatula|press|tortilla|spatula|frying pan|right||spatula
lift the spatula away from the quesadilla|move|spatula|||right||spatula
press and check the tortilla with the spatula|press|tortilla|spatula|frying pan|right||spatula
lift a tortilla edge with fingers and spatula|lift|tortilla|spatula|frying pan|both||spatula
turn the filled tortilla stack over|flip|tortilla|spatula|frying pan|both||spatula
press the turned quesadilla with the spatula|press|tortilla|spatula|frying pan|right||spatula
put the spatula down briefly|put down|spatula||counter|right||
pick up a serving plate|pick up|plate|||left|plate|spatula
put the plate beside the frying pan|put down|plate||counter|left||spatula
idle: wait while the quesadilla cooks|||||unclear||
slide the spatula under the quesadilla|lift|tortilla|spatula|frying pan|right||spatula
transfer the quesadilla from the pan to the plate|place|tortilla|spatula|plate|both||spatula
put the spatula down beside the plate|put down|spatula||counter|right||
pick up the rolling cutter|pick up|rolling cutter|||right||rolling cutter
cut across the quesadilla with the rolling cutter|cut|tortilla|rolling cutter|plate|both||rolling cutter
idle: turn toward the kitchen window|||||right||rolling cutter
idle: gesture toward the window|||||right||rolling cutter
idle: return to the plate|||||right||rolling cutter
cut the quesadilla into quarters|cut|tortilla|rolling cutter|plate|both||rolling cutter
put the rolling cutter down|put down|rolling cutter||counter|right||
adjust the cut quesadilla portions on the plate|adjust|tortilla||plate|both||
''',[(0,8,'Set out tortillas and cooked chicken','Open the tortilla bag, separate two tortillas onto the board and retrieve the chicken container from the microwave.','Make the bread layers and cooked filling available.'),(9,22,'Coat the bottom tortilla with barbecue sauce','Open the sauce bottle and pour a spiral over one tortilla. Fetch a spoon from the drawer and spread the sauce over its surface, then move the chicken container closer.','Create the sauce layer beneath the filling.'),(23,36,'Dice and add the chicken','Briefly use the phone, reposition the tortilla and take chicken from the container. Cut it into small pieces with the knife, then scatter the pieces over the sauce.','Distribute bite-sized chicken across the bottom tortilla.'),(37,50,'Add cheese and assemble the quesadilla in the pan','Work open the cheese bag, operate the burner and sprinkle cheese over the chicken. Place the second tortilla on top, move the stack into the frying pan and press it flat.','Enclose the filling between tortillas and begin heating it.'),(51,64,'Cook and turn the quesadilla','Briefly leave to operate the thermostat, then return and press the tortilla with the palms. Get the spatula, press and lift the edge repeatedly, turn the quesadilla over and press again.','Heat the filling and cook both tortilla surfaces.'),(65,71,'Finish cooking and plate the quesadilla','Ready the serving plate, wait, work the spatula beneath the quesadilla and transfer it onto the plate. Put the spatula aside.','Remove the cooked quesadilla from the pan onto its serving plate.'),(72,79,'Cut the quesadilla into portions','Take the rolling cutter and cut the plated quesadilla, briefly turn toward the window, then return to finish crossing cuts and adjust the portions.','Leave the quesadilla divided into four portions.')], 'Reviewed all 8 overview sheets, all 19 compact dense pages (1208 frames), and all 5 native endpoint sheets. BBQ sauce visible t=19–26s; cooked chicken cut t=64–87s; shredded cheese added t=111–120s. Thermostat trip t=130–149s and window gestures t=226–234s unrelated idle. Repeated hand/spatula pressing and underside checks shown t=150–194s; turn near t=187s. Filled tortilla removed to plate t=216–219s and rolling cutter portions it t=222–244s. Chicken was already cooked when retrieved; no raw-chicken cooking invented.',fix={0:{'boundary_note':'Starts lifting/adjusting tortilla packaging.'},2:{'boundary_note':'Separates two tortillas, both releases spread over following brief segments.'},3:{'boundary_note':'0.98s cut during tortilla separation.'},4:{'boundary_note':'0.93s cut during second tortilla placement.'},7:{'notes':'Container of browned chicken pieces removed; prior microwave heating outside video.'},9:{'boundary_note':'Bottle pickup and cap unscrew combined.'},10:{'boundary_note':'0.64s cut within cap removal.'},11:{'notes':'Spiral of dark barbecue sauce across tortilla.'},14:{'boundary_note':'Walks to cutlery drawer then starts opening it.'},16:{'notes':'Spoon transported back; hands intermittently out of view.'},18:{'boundary_note':'Continuous same-object sauce spreading across adjacent boundaries.'},19:{'boundary_note':'Continuous sauce spreading, ends when spoon is placed.'},21:{'boundary_note':'0.52s segment within spoon release/reach.'},23:{'notes':'Phone tapping and scrolling unrelated to direct food manipulation.'},25:{'boundary_note':'Selects chicken with left hand and takes knife right.'},26:{'boundary_note':'0.23s cut within chicken selection, no independent intermediate action.'},27:{'boundary_note':'Chicken moved from container to board; knife already held.'},29:{'boundary_note':'Repeated chopping and food repositioning across adjacent segments.'},30:{'boundary_note':'Repeated chopping, same knife/chicken interaction.'},31:{'boundary_note':'Repeated chopping, same knife/chicken interaction.'},32:{'boundary_note':'Finishes chopping; knife lowered near t=86s.'},34:{'boundary_note':'Picks up chopped pieces and begins transfer.'},35:{'notes':'Chicken scattered over sauce, no extra ingredients.'},38:{'notes':'Bag initially resists opening.'},39:{'notes':'Stove knob turned before assembly; no temperature inferred.'},40:{'boundary_note':'Continues opening same cheese bag after knob adjustment.'},41:{'boundary_note':'Bag opens, first pinch of cheese taken and distributed.'},43:{'boundary_note':'Repeated pinch-and-scatter cheese transfers.'},44:{'boundary_note':'Bag retained while right hand spreads cheese.'},45:{'boundary_note':'Short bag placement/release segment.'},46:{'boundary_note':'0.69s adjustment of same filling immediately after bag release.'},47:{'boundary_note':'Both hands take top tortilla and move above filling.'},49:{'notes':'Whole stack lifted into frying pan, not folded in half.'},50:{'notes':'Both palms press stack flat.'},51:{'notes':'Walks away from cooking task toward thermostat.'},52:{'notes':'Thermostat touches are unrelated idle; setpoint not transcribed.'},54:{'boundary_note':'Presses tortilla then adds second hand.'},56:{'boundary_note':'Repeated palm pressing and small rotations.'},57:{'boundary_note':'Turns toward utensil holder and retrieves slotted spatula.'},58:{'boundary_note':'Subsecond transfer toward pan, same held tool.'},59:{'notes':'Repeated spatula pressure/checks; same object.'},60:{'boundary_note':'Withdraws spatula and steps back before next press.'},61:{'boundary_note':'Includes repeated lifts and pressure checks, not just one stroke.'},62:{'notes':'Left fingers grip edge while right spatula supports.'},63:{'notes':'Filled stack turned by t=188s.'},64:{'notes':'Pressed again after turn.'},65:{'boundary_note':'Spatula placed then regrasped in following segment.'},66:{'boundary_note':'Grasps serving plate left and spatula right.'},67:{'boundary_note':'0.84s plate placement interval.'},68:{'boundary_note':'Starts putting spatula down then mostly waiting t=201–212s.'},69:{'notes':'Spatula slides beneath cooked tortilla stack.'},70:{'boundary_note':'Left fingers steady while spatula transfers entire stack.'},72:{'boundary_note':'Retrieves blue rolling cutter and positions it above food.'},73:{'notes':'First straight cut through tortilla stack.'},74:{'notes':'Turns away holding cutter, unrelated idle.'},75:{'notes':'Gestures at window/reflection, no food contact.'},76:{'notes':'Returns attention to plated food.'},77:{'notes':'Perpendicular rolling cuts produce quarters.'},79:{'notes':'Adjusts portions and looks at completed dish; no eating shown.'}},evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/a668107d4cbb61d6/20261106T055326539131Z/manifest.json')
