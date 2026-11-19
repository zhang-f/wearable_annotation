from write_editor_batch import *
v='ccb5d74c42da3d7d'
goal=dict(title='Make an egg and tomato toast sandwich',description='Toast two bread slices, rinse and slice a tomato, cook egg in an oiled frying pan, then place tomato and cooked egg between the toast slices.',final_state='A closed egg and tomato sandwich rests on a white plate.',procedure=['Load bread into the toaster, connect it and start toasting.','Rinse and dry the tomato, then cut it into thin slices.','Heat a frying pan, add oil, crack egg into a bowl and pour it into the pan.','Break the yolk with a silicone spatula and allow the egg to cook, occasionally shaking the pan and checking the watch timer.','Remove the toast, arrange tomato slices on one piece, transfer the egg with a wooden spatula and close the sandwich.'])
inv=['bread','bread bag','toaster','power cord','wall socket','tomato','faucet','paper towel','knife','cutting board','frying pan','stove controls','white plate','silicone spatula','oil bottle','oil cap','egg','eggshell','bowl','sink','watch','wooden spatula','utensil holder','sandwich']
lines='''both hands pull bread slices from the bag|pull|bread||bread bag|both|bread|bread
both hands separate two bread slices above the toaster|separate|bread||toaster|both|bread|bread
both hands place bread slices in the toaster slots|place|bread||toaster|both||
both hands gather the toaster power cord|gather|power cord||toaster|both|power cord|power cord
right hand inserts the toaster plug into the wall socket|insert|power cord||wall socket|right||
right hand adjusts the toaster dial|adjust|toaster|||right||
right hand starts toaster then reaches faucet beside left-held tomato|press|toaster||faucet|both|tomato|
left hand holds tomato under water while right adjusts faucet|rinse|tomato||faucet|both|tomato|
right hand turns off faucet while left holds tomato|turn off|faucet|||right|tomato|
both hands dry tomato with a paper towel|dry|tomato|paper towel||both|tomato|paper towel
right hand picks up knife while left sets down tomato|pick up|knife||cutting board|both|tomato|knife
right hand starts slicing tomato held by left hand|slice|tomato|knife|cutting board|both|tomato|knife
right hand cuts another tomato slice|slice|tomato|knife|cutting board|both|tomato|knife
right hand slices tomato while left steadies it|slice|tomato|knife|cutting board|both|tomato|knife
right hand continues cutting tomato into slices|slice|tomato|knife|cutting board|both|tomato|knife
right hand cuts tomato while left holds the remaining piece|slice|tomato|knife|cutting board|both|tomato|knife
right hand slices the remaining tomato piece|slice|tomato|knife|cutting board|both|tomato|knife
right hand sets knife beside the sliced tomato|set down|knife||cutting board|right||
idle (turning from tomato counter toward stove)|||||none||
right hand adjusts stove controls beside the repositioned frying pan|adjust|stove controls||frying pan|right||
left hand picks up oil bottle after right adjusts stove|pick up|oil bottle||stove controls|both|oil bottle|
both hands open the oil bottle|open|oil bottle||oil cap|both|oil cap|oil bottle
right hand pours oil into the frying pan|pour|oil bottle||frying pan|right|oil cap|oil bottle
both hands screw cap onto the oil bottle|close|oil bottle||oil cap|both||oil bottle
right hand sets down oil bottle and reaches for egg|set down|oil bottle||egg|right||egg
right hand positions egg over the bowl|position|egg||bowl|right||egg
both hands crack egg into the bowl|crack|egg||bowl|both|eggshell|eggshell
right hand puts eggshell aside while left picks up bowl|set down|eggshell||bowl|both|bowl|
left hand carries the bowl toward the frying pan|carry|bowl||frying pan|left|bowl|
left hand tilts bowl to pour egg into pan|pour|egg|bowl|frying pan|left|bowl|
left hand empties bowl into pan then lowers it toward sink|pour|egg|bowl|frying pan|left|bowl|
left hand sets down bowl while right picks up silicone spatula|pick up|silicone spatula||bowl|both||silicone spatula
right hand breaks yolk and spreads egg with silicone spatula|spread|egg|silicone spatula|frying pan|right||silicone spatula
right hand places silicone spatula on white plate|set down|silicone spatula||white plate|right||
right hand taps watch on left wrist|tap|watch|||right||
idle (watching egg cook in the frying pan)|||||none||
right hand shakes frying pan by its handle|shake|frying pan|||right||frying pan
right hand picks up silicone spatula and stirs egg|stir|egg|silicone spatula|frying pan|right||silicone spatula
right hand lays silicone spatula on plate|set down|silicone spatula||white plate|right||
idle (watching egg cook before turning toward toaster)|||||none||
right hand moves white plate beside toaster|move|white plate||toaster|right||
right hand presses toaster lever then taps watch|press|toaster||watch|right||frying pan
right hand shakes frying pan over stove|shake|frying pan|||right||
idle (watching egg cook without holding utensils)|||||none||
right hand lifts and shakes frying pan|shake|frying pan|||right||
idle (waiting beside the cooking egg)|||||none||
right hand shakes frying pan to loosen egg|shake|frying pan|||right||
idle (waiting beside stove before lifting watch)|||||none||
right hand taps watch on raised left wrist|tap|watch|||right||
idle (watching egg cook and checking watch without utensil interaction)|||||none||
left hand raises watch while right hand rests beside sink|raise|watch|||left||
idle (lowering arms beside the frying pan)|||||none||
right hand shakes frying pan by the handle|shake|frying pan|||right||
right hand shakes pan then releases it and turns toward toaster|shake|frying pan|||right||
right hand transfers first toast slice from toaster to plate|transfer|bread||white plate|right||
left hand removes second toast slice and places it on plate|place|bread||white plate|left||
left hand straightens toast slices on the plate|straighten|bread||white plate|left||
both hands separate tomato slices above the toast|separate|tomato||bread|both|tomato|tomato
right hand places tomato slice on toast|place|tomato||bread|both|tomato|
right hand adds tomato slice beside the first|place|tomato||bread|right||
right hand transfers another tomato slice to toast|transfer|tomato||bread|right||
both hands position tomato slices across toast|position|tomato||bread|both||
right hand picks up another tomato slice|pick up|tomato||cutting board|right||tomato
right hand places tomato slice on the toast|place|tomato||bread|right||
right hand adds tomato slice while left steadies toast|place|tomato||bread|both||
right hand adjusts tomato slices on toast|adjust|tomato||bread|right||
both hands finish arranging tomato then turn toward frying pan|arrange|tomato||bread|both||
left hand lifts frying pan while right reaches utensil holder|lift|frying pan||utensil holder|both|frying pan|
right hand takes wooden spatula while left holds frying pan|take|wooden spatula||utensil holder|both|frying pan|wooden spatula
right hand slides egg from tilted pan onto tomato toast|transfer|egg|wooden spatula|bread|both|frying pan|wooden spatula
right hand scrapes egg from pan onto toast|scrape|egg|wooden spatula|bread|both|frying pan|wooden spatula
right hand scrapes remaining egg onto the sandwich filling|scrape|egg|wooden spatula|bread|both|frying pan|wooden spatula
right hand scrapes pan and presses egg onto toast|scrape|egg|wooden spatula|bread|both|frying pan|wooden spatula
right hand rests wooden spatula across frying pan|set down|wooden spatula||frying pan|right|frying pan|
left hand returns frying pan to stove|set down|frying pan||stove controls|left||
both hands place second toast slice over egg and tomato|place|bread||sandwich|both|sandwich|sandwich'''
groups=[(0,6,'Start toasting the bread.','Two bread slices are loaded, the toaster is plugged in and its controls are adjusted to start heating.','Prepare the two toasted outer sandwich layers.'),(7,18,'Rinse, dry and slice the tomato.','The tomato is rinsed at the faucet, dried with paper towel and sliced repeatedly on the cutting board.','Prepare the fresh tomato filling.'),(19,24,'Heat and oil the frying pan.','Stove controls are set, the pan is positioned, and oil is poured into it before the bottle is put aside.','Prepare the hot oiled surface for cooking egg.'),(25,31,'Crack egg into a bowl and pour it into the pan.','Egg is cracked into the bowl, carried to the stove and tipped into the frying pan; the bowl is set in the sink.','Place the egg in the pan ready to cook.'),(32,39,'Spread the egg and begin cooking it.','The yolk is broken and egg spread with a silicone spatula, the watch is checked, and the pan is shaken and stirred between waits.','Cook and spread the egg filling into a compact layer.'),(40,53,'Set out a plate and let the egg finish cooking.','A plate is moved beside the toaster. The wearer checks toaster and watch controls, waits and repeatedly shakes the pan as the egg sets.','Have a serving plate ready and finish cooking the egg.'),(54,66,'Plate the toast and cover one slice with tomato.','The two toast slices are removed from the toaster and arranged on the plate; tomato slices are added and adjusted across one slice.','Build the tomato layer on the toasted sandwich base.'),(67,75,'Transfer the egg and close the sandwich.','The pan is lifted, a wooden spatula is taken and used to scrape cooked egg onto the tomato toast. The pan is returned and the second toast slice placed on top.','Finish the assembled egg and tomato toast sandwich.')]
fix={6:dict(boundary_note='This preserved segment includes starting the toaster near 22–24s and reaching faucet with tomato near 26–27s.'),19:dict(boundary_note='Pan and plate positioning precede touching stove controls within 55.5–64.27s.'),41:dict(boundary_note='Contains toaster lever interaction near 160–162s, watch taps near 164–173s, and pan pickup at its end.'),53:dict(boundary_note='Contains pan shaking near 267–270s followed by turning to toaster and beginning toast pickup near 273s.'),72:dict(boundary_note='At 302–309s the wooden spatula alternates scraping pan residue and pressing egg onto toast; preserved boundary retained.'),49:dict(confidence='medium',notes='Mostly stationary waiting; brief watch inspection at end is included without inventing a utensil action.')}
write(v,goal,inv,lines,groups,'All summaries and coarse groups rewritten from timestamped overview, every 3/15fps step frame and native endpoint sheets. Fine boundaries unchanged. Source fine stops at 314.24s; real tail to 315.467s shows the completed sandwich without another distinct preparation action. No ingredient beyond visible egg, tomato and bread is asserted.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T095840224631Z/manifest.json'))
