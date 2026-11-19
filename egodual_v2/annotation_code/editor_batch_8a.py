from write_editor_batch import *
write('8a24481ff511dc25',dict(title='Make olive and caper spread for toasted bread',description='Retrieve a jar from the refrigerator and spoon capers and green olives into a blender cup. Squeeze in lemon juice, add olive oil and screw on the blade assembly. Slice two pieces of bread, drizzle them with oil and toast them in the countertop oven, turning and checking them. Pulse the olive mixture in the blender, remove the blade lid and spoon the chopped spread over both toast slices. Transfer them to a white plate.',final_state='Two toasted bread slices covered with coarse olive and caper spread are on a white plate.',procedure=['Collect capers and green olives in the blender cup.','Add lemon juice and olive oil, then close the cup with the blade assembly.','Slice and oil two bread pieces and toast them in the countertop oven.','Pulse the olive mixture into a coarse spread.','Spoon the spread over both toasted slices and serve them on a plate.']),['refrigerator door','olive jar','caper jar','spoon','blender cup','capers','olives','lemon','olive oil bottle','bottle cap','blade assembly','blender base','bread','knife','baking tray','oven door','oven control','phone','charging cable','olive spread','plate','counter','blinds','blind cord'],'''
open the refrigerator door|open|refrigerator door|||left||
retrieve the olive jar from the refrigerator|pick up|olive jar|||right||olive jar
close the refrigerator door|close|refrigerator door|||left||olive jar
put the olive jar beside the sink|put down|olive jar||counter|right|caper jar|
pick up the spoon|pick up|spoon|||right|caper jar|spoon
scoop capers from the jar into the blender cup|scoop|capers|spoon|blender cup|right|caper jar|spoon
add another spoonful of capers to the cup|scoop|capers|spoon|blender cup|right|caper jar|spoon
put the caper jar down and take the olive jar|pick up|olive jar|||left|olive jar|spoon
scoop green olives into the blender cup|scoop|olives|spoon|blender cup|right|olive jar|spoon
add more green olives to the cup|scoop|olives|spoon|blender cup|right|olive jar|spoon
scoop another spoonful of olives into the cup|scoop|olives|spoon|blender cup|right|olive jar|spoon
scrape remaining olives from the jar into the cup|scoop|olives|spoon|blender cup|right|olive jar|spoon
put the olive jar down|put down|olive jar||counter|left||spoon
put the spoon down beside the blender cup|put down|spoon||counter|right||
idle: move a shopping bag beside the side table|||||unclear||
idle: return to the food preparation counter|||||unclear||
pick up the lemon half|pick up|lemon|||right||lemon
squeeze the lemon into the blender cup|squeeze|lemon||blender cup|both||
reach for the olive oil bottle|reach|olive oil bottle|||right||olive oil bottle
unscrew the olive oil bottle cap|open|olive oil bottle|||both|olive oil bottle|bottle cap
pour olive oil into the blender cup|pour|olive oil bottle||blender cup|left|olive oil bottle|bottle cap
close the olive oil bottle|close|olive oil bottle|||both|olive oil bottle|
put the olive oil bottle down|put down|olive oil bottle||counter|right||
pick up the blender blade assembly|pick up|blade assembly|||both|blade assembly|blade assembly
screw the blade assembly onto the blender cup|screw|blade assembly||blender cup|both|blender cup|blade assembly
pick up the bread knife|pick up|knife|||right||knife
cut the first slice from the bread loaf|cut|bread|knife||both|bread|knife
cut the second slice from the bread loaf|cut|bread|knife||both|bread|knife
finish the cut through the bread|cut|bread|knife||both|bread|knife
put the knife down and reach for olive oil|pick up|olive oil bottle|||left|olive oil bottle|
open the olive oil bottle|open|olive oil bottle|||both|olive oil bottle|bottle cap
drizzle olive oil over the bread slices|pour|olive oil bottle||bread|left|olive oil bottle|bottle cap
close the olive oil bottle cap|close|olive oil bottle|||both|olive oil bottle|
put the olive oil bottle down|put down|olive oil bottle||counter|left||
place a bread slice on the baking tray|place|bread||baking tray|right||bread
place the other bread slice on the tray|place|bread||baking tray|right||
open the countertop oven door|open|oven door|||left||
lift the tray of bread toward the oven|move|baking tray||oven door|right||baking tray
slide the bread tray into the oven|insert|baking tray||oven door|right||
adjust the bread on the oven tray|adjust|bread||baking tray|right||
close the oven door|close|oven door|||left||
idle: walk away holding the phone|||||left|phone|
idle: connect the phone charging cable|||||both|phone|charging cable
idle: set the phone down and wait beside the oven|||||unclear||
open the countertop oven door|open|oven door|||left||
turn one bread slice on the baking tray|flip|bread||baking tray|right||bread
turn the other bread slice on the baking tray|flip|bread||baking tray|right||bread
adjust the bread and pull the tray forward|move|baking tray|||right||baking tray
remove the tray from the oven|remove|baking tray||oven door|right||baking tray
put the bread tray on top of the oven|put down|baking tray||counter|right||
close the oven door|close|oven door|||left||
turn the oven control knob|turn|oven control|||right||
release the oven control knob|adjust|oven control|||right||
invert the blender cup onto the blender base|place|blender cup||blender base|both|blender base|blender cup
press the cup down to blend the olive mixture|press|blender cup||blender base|right|blender base|blender cup
lift and reseat the blender cup|adjust|blender cup||blender base|right|blender base|blender cup
press the blender cup to continue blending|press|blender cup||blender base|right|blender base|blender cup
lift the blended cup off the base|remove|blender cup||blender base|right|blender base|blender cup
unscrew the blade assembly from the cup|unscrew|blade assembly||blender cup|both|blender cup|blade assembly
put the blade assembly down|put down|blade assembly||counter|right|blender cup|
pick up the spoon beside the cup|pick up|spoon|||right|blender cup|spoon
scoop olive spread from the blender cup|scoop|olive spread|spoon|blender cup|right|blender cup|spoon
put the spread on the first toast slice|place|olive spread|spoon|bread|right|blender cup|spoon
spread the olive mixture over the toast|spread|olive spread|spoon|bread|right|blender cup|spoon
scoop another spoonful of olive spread|scoop|olive spread|spoon|blender cup|right|blender cup|spoon
put olive spread onto the other toast slice|place|olive spread|spoon|bread|right|blender cup|spoon
smooth the spread over the second toast slice|spread|olive spread|spoon|bread|right|blender cup|spoon
scoop more spread from the blender cup|scoop|olive spread|spoon|blender cup|right|blender cup|spoon
add the last spoonful to the toast|place|olive spread|spoon|bread|right|blender cup|spoon
put the cup and spoon down|put down|blender cup||counter|left||
carry one topped toast slice to the plate|place|bread||plate|right||
idle: lower and adjust the window blinds|||||both||
idle: finish adjusting the blind cord|||||right||
idle: return to the toast tray|||||unclear||
carry the other topped toast slice to the plate|place|bread||plate|right||bread
place and arrange both toast slices on the plate|place|bread||plate|both||
pick up the plate of olive toast|pick up|plate|||both|plate|plate
hold up the plate of finished toast|hold|plate|||left|plate|
''',[(0,13,'Portion capers and olives into the blender cup','Retrieve the olive jar from the refrigerator. Spoon capers and then successive spoonfuls of green olives into the clear blender cup and put the jar and spoon down.','Collect the solid ingredients of the coarse olive topping.'),(14,24,'Add lemon and olive oil and close the cup','After briefly moving a shopping bag, return to the counter. Squeeze the lemon into the cup, pour olive oil, replace the bottle cap and screw the blade assembly onto the cup.','Prepare the seasoned olive mixture for blending.'),(25,40,'Slice, oil and toast the bread','Cut two bread slices from the loaf, drizzle them with olive oil, place them on the baking tray and load the tray into the countertop oven.','Prepare the toasted bread base for the spread.'),(41,52,'Wait, turn and remove the toast','Briefly attend to the phone and charging cable while the bread heats. Open the oven, turn and adjust the slices, remove the tray to the oven top, close the door and turn the control.','Finish the visible toasting stage and make the slices accessible for topping.'),(53,59,'Blend the olive mixture','Invert the cup onto the blender base and press it down in repeated pulses. Lift the cup, remove the blade assembly and put it aside.','Chop the ingredients into a coarse olive spread.'),(60,69,'Cover both toast slices with olive spread','Scoop from the cup with the spoon, deposit and smooth spread over the first slice, then repeat for the second. Put the cup and spoon down.','Cover both bread slices with the prepared topping.'),(70,77,'Plate and present the olive toast','Carry one slice to the white plate, pause to lower the window blinds, then move the other toast slice to the plate. Arrange both and lift the plate.','Leave both finished toast slices together on the serving plate.')], 'All 7 overview sheets, all 19 compact dense pages (1159 frames) and all 5 native endpoint sheets reviewed. Actual t=11–19s capers and t=20–33s olives spooned into cup; t=49–56s lemon squeezed; t=59–63s olive oil added. t=144–153s unrelated phone charging; t=197–210s unrelated blind adjustment marked idle despite hand activity. t=143.9–163.1s blender cup held down in repeated pulses. Fine boundaries preserved.',fix={0:{'boundary_note':'Refrigerator door opens and reaching into shelf begins before t=2.24s.'},2:{'boundary_note':'Closes fridge while carrying jar; carried hand intermittently off-frame.','confidence':'medium'},3:{'boundary_note':'Jar placed and caper jar taken by t=8.9s.'},5:{'boundary_note':'Multiple spoon transfers capers between jar and cup.'},6:{'boundary_note':'Continuation of caper transfer loop; no clear new object at t=15.7s.'},7:{'boundary_note':'Brief jar exchange at t=19.8–20.57s.'},8:{'notes':'Larger green olives visible on spoon.'},9:{'boundary_note':'Repeated olive scoops, same objects.'},10:{'boundary_note':'Repeated olive scoops, same objects.'},11:{'boundary_note':'Same spoon/jar transfer sequence continues.'},14:{'notes':'Shopping bag moved from floor to side of cart; unrelated to preparation.','ambiguous':True,'confidence':'medium'},15:{'notes':'Walking back; no task object interaction.'},17:{'notes':'Lemon squeezed directly over cup.'},18:{'boundary_note':'Starts grasping oil bottle during brief 0.6s segment.'},20:{'notes':'Oil bottle label and pouring into cup visible.'},23:{'boundary_note':'Obtains blade assembly while cup nearby; subsecond cut inside pickup.'},24:{'notes':'Screws blade cap onto cup; blender has not yet been run.'},25:{'boundary_note':'Moves bread/tray and picks up knife by t=75.7s.'},26:{'notes':'Repeated sawing strokes through loaf.'},28:{'boundary_note':'0.91s split during final cut through second bread slice.'},29:{'boundary_note':'Knife laid down then oil bottle retrieved.'},31:{'notes':'Drizzles oil over both cut faces.'},32:{'boundary_note':'Cap replacement begins before end of pouring interval; same bottle interaction.'},34:{'boundary_note':'Places first bread slice and grasps next.'},35:{'boundary_note':'0.57s cut within tray-loading bread handling.'},36:{'boundary_note':'Open oven at same time tray is readied.'},38:{'notes':'Tray pushed inside oven; bread still adjusted afterward.'},39:{'boundary_note':'Moves slices and pushes tray, multiple changes.'},41:{'notes':'Phone visible while walking, unrelated idle.'},42:{'notes':'Connects phone cable at side table, unrelated idle.'},43:{'boundary_note':'Phone put down t=113–114s, waits/walks, then starts opening oven by t=124.6s.'},45:{'notes':'Turns first slice with fingertips, does not assume oven temperature.'},46:{'boundary_note':'Checks/turns second slice in same bread handling sequence.'},47:{'boundary_note':'Bread adjusted, then tray drawn forward.'},48:{'boundary_note':'Tray pulled out and placed on oven top.'},50:{'boundary_note':'Closes door and starts control adjustment.'},52:{'boundary_note':'Short continuation of oven knob operation.'},53:{'boundary_note':'Cup inverted and fitted into base before pressing.'},54:{'notes':'Repeated pressing pulses t=144–151.5s.'},55:{'notes':'Cup briefly lifted/reseated before next pulse.'},56:{'notes':'Repeated pressing until t=163s; coarse texture visible afterward.'},57:{'boundary_note':'Removes cup and transfers grip before blade cap unscrewed.'},58:{'boundary_note':'Unscrews and lifts blade assembly.'},60:{'boundary_note':'Gets spoon and brings it toward open cup.'},62:{'boundary_note':'Continued spoon deposit/spread across 1.2s cut.'},64:{'notes':'Dips spoon back in cup before topping other slice.'},66:{'boundary_note':'Repeated smoothing of topping on second slice.'},68:{'boundary_note':'Scoops and deposits another spoonful within interval.'},69:{'boundary_note':'Finishes topping and puts utensils down t=192–194.9s.'},70:{'notes':'First slice placed on white plate at t=196.8s.'},71:{'notes':'Lowers blinds and operates cords; unrelated idle.'},72:{'boundary_note':'Continues same blind handling across subsecond cut.'},73:{'notes':'Walking back to tray; hands empty/out of frame.'},74:{'boundary_note':'Grasps other toast then carries to plate.'},75:{'notes':'Both slices rest on plate by t=217.8s.'},76:{'boundary_note':'Plate pickup begins in 0.74s segment.'},77:{'notes':'Plate lifted for final presentation; no eating shown.'}},evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/8a24481ff511dc25/20261106T055247533472Z/manifest.json')
