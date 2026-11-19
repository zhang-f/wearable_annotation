from write_editor_batch import *
v='7c471a0376c4005b'
goal=dict(title='Assemble and taste a filled tortilla wrap',description='Fill a tortilla with spooned cooked crumbled filling, avocado, shredded cheese, yogurt and leafy garnish; fold it around the filling and take several bites.',final_state='A partly eaten folded wrap remains on the plate beside the ingredients.',procedure=['Lay a tortilla on the plate and spoon cooked crumbled filling along its center.','Scoop avocado flesh from its peel onto the filling.','Sprinkle shredded cheese over the avocado and add a spoonful of yogurt.','Add leafy garnish and close the yogurt container.','Fold the tortilla around the filling, lift and taste it, then place the partly eaten wrap back on the plate.'])
inv=['tortilla','plate','avocado','spoon','cooked filling','filling container','cheese bag','shredded cheese','yogurt tub','yogurt lid','yogurt','garnish bag','leafy garnish','table']
lines='''both hands lay the tortilla on the plate|place|tortilla||plate|both||
right hand takes the spoon while left lifts the filling container|pick up|spoon||filling container|both|filling container|spoon
right hand spoons cooked filling onto the tortilla|spoon|cooked filling|spoon|tortilla|right|filling container|spoon
right hand adds another spoonful of filling|spoon|cooked filling|spoon|tortilla|right|filling container|spoon
right hand spreads filling along the tortilla center|spread|cooked filling|spoon|tortilla|right|filling container|spoon
right hand scoops more filling from the container|scoop|cooked filling|spoon|filling container|right|filling container|spoon
right hand deposits the remaining spoonful on the tortilla|spoon|cooked filling|spoon|tortilla|right|filling container|spoon
left hand returns the filling container to the table|place|filling container||table|left||spoon
left hand picks up an avocado half|pick up|avocado|||left|avocado|spoon
right hand scoops avocado flesh onto the tortilla|scoop|avocado|spoon|tortilla|right|avocado|spoon
right hand removes another avocado piece with the spoon|scoop|avocado|spoon|tortilla|right|avocado|spoon
right hand places more avocado onto the filling|place|avocado|spoon|tortilla|right|avocado|spoon
right hand scrapes avocado flesh from the peel|scrape|avocado|spoon|tortilla|right|avocado|spoon
right hand arranges avocado pieces on the filling|arrange|avocado|spoon|tortilla|right|avocado|spoon
right hand scrapes the last avocado pieces onto the tortilla|scrape|avocado|spoon|tortilla|right|avocado|spoon
both hands set the avocado peel and spoon aside|place|avocado||table|both||
both hands pick up the shredded cheese bag|pick up|cheese bag|||both|cheese bag|cheese bag
both hands pull open the cheese bag|open|cheese bag|||both|cheese bag|
right hand sprinkles shredded cheese onto the tortilla|sprinkle|shredded cheese||tortilla|right|cheese bag|
right hand adds cheese and sets the bag aside|sprinkle|shredded cheese||tortilla|right||
right hand lifts the yogurt tub lid|open|yogurt lid||yogurt tub|right||yogurt lid
right hand sets the yogurt lid aside|place|yogurt lid||table|right||
right hand scoops yogurt while left hand holds the tub|scoop|yogurt|spoon|yogurt tub|right|yogurt tub|spoon
right hand deposits yogurt onto the wrap filling|spoon|yogurt|spoon|tortilla|right||spoon
right hand spreads the yogurt over the filling|spread|yogurt|spoon|tortilla|right||spoon
left hand takes leafy garnish and places it on the filling|sprinkle|leafy garnish||tortilla|left||spoon
left hand picks up the yogurt lid|pick up|yogurt lid|||left|yogurt lid|spoon
left hand closes the yogurt tub|close|yogurt lid||yogurt tub|left||spoon
left hand returns the garnish bag beside the yogurt|place|garnish bag||table|left||spoon
both hands fold the tortilla around the filling|fold|tortilla|||both|tortilla|tortilla
both hands tuck the wrap closed and lift it to eat|fold|tortilla|||both|tortilla|tortilla
both hands lower and adjust the partly eaten wrap|place|tortilla||plate|both|tortilla|
left hand lifts the wrap for another bite|lift|tortilla|||left||
idle hands rub together and gesture above the plate|||||none||
left hand briefly touches the avocado peel|touch|avocado|||left||
left hand lifts the folded wrap for another bite|lift|tortilla|||left|tortilla|
left hand lowers the partly eaten wrap onto the plate|place|tortilla||plate|left|tortilla|
left hand holds the wrap against the plate|hold|tortilla||plate|left|tortilla|
idle hands rub together above the plate|||||none||
left hand rests on the folded wrap on the plate|hold|tortilla||plate|left|tortilla|'''
groups=[(0,7,'Fill the tortilla with cooked filling','A tortilla is spread on a plate, and a spoon transfers several portions of browned crumbled filling from a plastic container into a central strip. The container is returned to the table.','Establishes the main filling while leaving tortilla edges available for folding.'),(8,15,'Add avocado pieces','An avocado half is held over the tortilla while a spoon repeatedly scrapes and places its flesh on the cooked filling; the peel and spoon are then put aside.','Adds avocado across the filling strip.'),(16,25,'Add cheese, yogurt and leafy garnish','The cheese bag is opened and shredded cheese sprinkled over the filling. The yogurt tub is opened, a spoonful is deposited and spread, and leafy garnish is added from a bag.','Completes the visible layers of the wrap filling.'),(26,30,'Close containers and fold the wrap','The yogurt tub is closed and the garnish bag returned. Both hands fold and tuck the tortilla around the filling, then lift the assembled wrap to eat.','Encloses the prepared filling in a handheld wrap.'),(31,39,'Taste and set down the wrap','The wrap is lowered, adjusted and lifted for further bites, with pauses and hand gestures between handling. A partly eaten wrap remains on the plate.','Checks the prepared wrap by tasting it and leaves the remainder on the plate.')]
fix={25:dict(ambiguous=True,confidence='medium',notes='66–72s leafy green pieces are pinched from a bag; exact herb variety cannot be established.'),1:dict(boundary_note='3.55–9.9s includes brief avocado handling followed by collecting spoon and filling container; boundaries retained.'),30:dict(boundary_note='82.21–93.5s includes tucking, lifting and eating the wrap; boundaries retained.'),31:dict(boundary_note='93.5–105.73s includes lowering, adjusting and lifting the wrap again; boundaries retained.')}
write(v,goal,inv,lines,groups,'Reviewed all overview sheets, all 602 dense sampled frames and native boundary frames. Brown crumbled filling species is not identifiable; leafy garnish variety also remains unspecified. Late intervals include eating/gesturing rather than additional cooking. All original fine boundaries retained; semantic predictability pending.',fix=fix,evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/7c471a0376c4005b/20261106T060311527681Z/manifest.json')
