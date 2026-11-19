from write_editor_batch import *
write('768cf9ecf66b2cee',dict(title='Pan-toast a cheese sandwich and serve it',description='Place two bread slices on a plate and remove a slice of marbled cheese from its packet. Open the spread tub and spread the pale spread over both bread slices with a knife. Put one bread slice in a frying pan, layer the cheese and the second slice on it, and turn on the gas burner. Wait, check the underside repeatedly with a spatula, flip and press the sandwich, then transfer the browned sandwich to the plate. Carry it to the island, wait and take a bite.',final_state='A browned cheese sandwich is served on the green plate and lifted for a bite.',procedure=['Set out bread and remove a cheese slice from its packet.','Spread both bread slices with the tub spread.','Layer bread, cheese and bread in the frying pan and light the burner.','Cook the sandwich, checking and flipping it with the spatula.','Transfer the sandwich to a plate, carry it to the island and taste it.']),['bread','cheese','cheese packet','spread tub','spread lid','knife','plate','frying pan','burner knob','stove control','spatula','sandwich','counter'],'''
move the plate beside the bread bag|move|plate|||left||
put a bread slice on the plate|place|bread||plate|right||bread
arrange the second bread slice on the plate|place|bread||plate|right||
open the cheese packet|open|cheese packet|||both|cheese packet|cheese
pull a cheese slice from the packet|remove|cheese||cheese packet|right|cheese packet|cheese
put the cheese slice on the plate|place|cheese||plate|right||
remove the spread tub lid|open|spread tub|||both|spread lid|
set the spread lid on the counter|put down|spread lid||counter|left||knife
scoop spread from the tub with the knife|scoop|spread tub|knife||right||knife
spread one bread slice with the knife|spread|bread|knife||right||knife
scoop more spread from the tub|scoop|spread tub|knife||right||knife
spread the second bread slice|spread|bread|knife||right||knife
put the knife on the spread tub|put down|knife||spread tub|right||
smooth the spread over the bread with the knife|spread|bread|knife||right||knife
put down the knife and lift a bread slice|pick up|bread|||right||bread
place the bread slice in the frying pan|place|bread||frying pan|right||
pick up the cheese slice|pick up|cheese|||both|cheese|cheese
position the cheese slice on the bread|place|cheese||bread|both||
pick up the remaining bread slice|pick up|bread|||right||bread
place the remaining bread over the cheese|place|bread||cheese|right||
turn the burner knob|turn|burner knob|||right||
idle: wait beside the sandwich cooking in the pan|||||unclear||
pick up the spatula|pick up|spatula|||right||spatula
press a stove control while holding the spatula|press|stove control|||right||spatula
hold the spatula beside the sandwich|hold|spatula||sandwich|right||spatula
idle: wait while the sandwich cooks|||||unclear||spatula
move the plate beside the pan|move|plate|||right||spatula
slide the spatula beneath the sandwich|lift|sandwich|spatula|frying pan|right||spatula
idle: wait with the spatula near the pan|||||right||spatula
lift the sandwich edge with the spatula|lift|sandwich|spatula|frying pan|right||spatula
idle: wait while holding the spatula|||||right||spatula
press the stove control with a finger|press|stove control|||right||spatula
press the sandwich with the spatula|press|sandwich|spatula|frying pan|right||spatula
lift the spatula away from the sandwich|move|spatula|||right||spatula
idle: wait beside the frying pan|||||right||spatula
slide the spatula beneath the sandwich|lift|sandwich|spatula|frying pan|right||spatula
flip the sandwich with the spatula|flip|sandwich|spatula|frying pan|right||spatula
steady the flipped sandwich with the fingertips|adjust|sandwich|||left||spatula
press and reposition the sandwich with the spatula|press|sandwich|spatula|frying pan|right||spatula
press the sandwich repeatedly with the spatula|press|sandwich|spatula|frying pan|right||spatula
lift the spatula away from the sandwich|move|spatula|||right||spatula
idle: wait for the other side to cook|||||unclear||spatula
slide the spatula beneath the cooked sandwich|lift|sandwich|spatula|frying pan|right||spatula
lift the sandwich out of the frying pan|remove|sandwich|spatula|frying pan|right||spatula
place the sandwich on the plate|place|sandwich|spatula|plate|right||spatula
put the spatula beside the plate|put down|spatula||counter|right||
pick up the plate holding the sandwich|pick up|plate|||both|plate|plate
carry the plate to the kitchen island|move|plate|||right||plate
put the plate down and wait|put down|plate||counter|right||
press the sandwich lightly with the fingertips|press|sandwich|||right||
reach toward the sandwich|reach|sandwich|||right||sandwich
lift the sandwich with both hands|pick up|sandwich|||both|sandwich|sandwich
raise the sandwich toward the mouth|move|sandwich|||both|sandwich|sandwich
lower the sandwich onto the plate|put down|sandwich||plate|both||
idle: sit beside the plated sandwich|||||unclear||
''',[(0,7,'Set out the sandwich ingredients','Move the plate, place two bread slices on it and open the cheese packet. Separate one cheese slice and remove the spread tub lid.','Make the bread, cheese and spread accessible for assembling the sandwich.'),(8,14,'Spread both bread slices','Scoop spread from the tub with the knife and coat the bread slices, returning for more spread and smoothing the surfaces. Put the knife down and lift a prepared slice.','Coat the bread surfaces before placing the sandwich in the pan.'),(15,20,'Assemble the sandwich in the pan and light the burner','Place one bread slice in the pan, position the marbled cheese on it and cover it with the other slice. Turn the burner knob until the blue flame is visible.','Begin heating the assembled cheese sandwich.'),(21,36,'Cook and turn the first side','Wait beside the pan, obtain the spatula and press the stove control. Periodically lift an edge to check underneath, then flip the sandwich with the spatula.','Cook the first side and turn the sandwich to expose the other side to the pan.'),(37,43,'Finish cooking the sandwich','Steady the flipped sandwich, press and reposition it with the spatula, then wait before lifting it from the pan.','Finish browning the second side and remove the cooked sandwich.'),(44,54,'Serve and taste the sandwich','Place the sandwich on the plate and put the spatula aside. Carry the plate to the island, wait, touch and lift the sandwich, take it toward the mouth and return it to the plate.','Present the cooked sandwich and check it by tasting.')], 'Reviewed all 11 overview sheets, all 19 dense compact pages (1201 sampled frames) and all 4 native endpoint sheets. t=77–79s visible gas flame appears; t=203–205s sandwich flips; t=269–272s sandwich leaves pan; t=324–326s lifted sandwich moves out of image toward mouth and returns with an edge missing. Spread composition is not identifiable from the image and is called spread. Long waits are idle; actual fine boundaries preserved.',fix={0:{'boundary_note':'t=0–4.5s moves plate and reaches for bread.'},2:{'boundary_note':'t=6.3–8.9s arranges bread then reaches toward cheese packet.'},3:{'boundary_note':'Packet opening and cheese extraction overlap through t=12.8s.'},5:{'boundary_note':'Cheese placed then packet lowered near t=16s.'},7:{'boundary_note':'Lid put down and knife retrieved t=18.3–19.6s.'},9:{'notes':'Repeated spreading strokes across bread; no inferred extra ingredients.'},11:{'notes':'Same knife spreading interaction throughout t=39.4–48.6s.'},13:{'boundary_note':'Continuation of bread spreading after brief knife placement; reaches more spread during interval.'},14:{'boundary_note':'Knife placed on tub then bread lifted by t=62.8s.'},16:{'boundary_note':'t=65.7–67.7s bread released then cheese picked up.'},17:{'notes':'Cheese adjusted with both hands before release in pan.'},20:{'boundary_note':'Withdraws from sandwich and turns burner knob; flame visible t=77–79s.'},21:{'boundary_note':'Mostly waiting t=79–104.9s; briefly looks toward the plate, with no sustained new hand-object interaction.'},23:{'boundary_note':'t=107–112.9s waits with spatula then presses rear stove control near t=111s.'},24:{'confidence':'medium'},25:{'notes':'Waiting; held spatula intermittently outside image.'},26:{'boundary_note':'Plate moved at t=131.4–132s, then spatula readied.'},27:{'boundary_note':'t=133–146s checks edge with spatula, then waits holding tool.'},28:{'notes':'Waiting with no new hand-object interaction; endpoint spatula visible right.'},29:{'boundary_note':'t=170.6–177.5s lifts sandwich edge then withdraws while waiting.'},30:{'confidence':'medium'},31:{'notes':'Control setting itself not legible; no specific temperature inferred.'},33:{'boundary_note':'Continuation of withdrawing spatula after pressing bread; no distinct new object.'},34:{'notes':'Waiting with tool at side.'},35:{'notes':'Spatula works underneath sandwich before the flip.'},36:{'notes':'Sandwich turns over at t=203–205s, revealing browned surface.'},37:{'notes':'Left fingertips touch and reposition sandwich, not holding it at endpoint.'},38:{'boundary_note':'t=208–212.5s fingers withdraw and spatula presses sandwich.'},39:{'notes':'Repeated same-object pressing and repositioning.'},41:{'notes':'No visible hand-object change during long cooking wait.'},43:{'boundary_note':'Several checks/adjustments, then lifts sandwich toward plate t=268–269.4s.'},44:{'notes':'Transfer finishes on plate near t=270s.'},45:{'boundary_note':'Puts spatula down, briefly adjusts sandwich then starts reaching plate.'},46:{'boundary_note':'Grips plate and starts carrying it at t=277–278s.'},48:{'boundary_note':'Plate released near t=287–289s, then extended idle wait until touch at t=318s.'},51:{'notes':'Both hands grasp sandwich; cheese visible between bread.'},52:{'confidence':'medium','notes':'Sandwich moves to mouth outside image; subsequent missing edge supports tasting.'},53:{'boundary_note':'Sandwich lowered back to plate t=329–330s, hands then withdraw.'},54:{'notes':'Hands rest near plate with no active interaction.'}},evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/768cf9ecf66b2cee/20261106T055123753125Z/manifest.json')
