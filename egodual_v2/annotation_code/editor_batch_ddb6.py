from write_editor_batch import *
v='ddb63645c6456edb'
goal=dict(title='Make a microwave-cooked egg sandwich',description='Crack and beat an egg in a bowl, microwave it under a cover in several short cycles with checks and stirring, then loosen the cooked egg onto bread and close the sandwich.',final_state='A closed egg sandwich rests on a folded paper towel on the counter.',procedure=['Crack egg into bowl, discard shell beside bread and add a small amount of water from the cup.','Beat the egg thoroughly with a fork.','Put the bowl in the microwave, cover it and heat, checking and stirring between short heating cycles.','Remove the cooked egg, loosen it with a fork and tip it onto a bread slice.','Place the second bread slice on top, press sandwich and fold paper towel beneath it.'])
inv=['egg','eggshell','bowl','bread','paper towel','cup','water','fork','microwave','microwave cover','microwave keypad','sandwich']
lines='''right hand picks up egg beside the bowl|pick up|egg||bowl|right||egg
right hand taps egg against the bowl rim|tap|egg||bowl|right||egg
both hands split eggshell over the bowl|split|egg||bowl|both|eggshell|eggshell
both hands empty egg into bowl then join shell halves|empty|egg||bowl|both|eggshell|eggshell
right hand sets eggshell beside bread|set down|eggshell||paper towel|right||
right hand pinches at egg surface while left takes cup|pinch|egg||cup|both|cup|
left hand tilts cup over egg bowl|pour|water|cup|bowl|left|cup|
left hand sets cup down beside bowl|set down|cup|||left||
right hand picks up fork beside bread|pick up|fork||bread|right||fork
right hand beats egg with fork while left holds bowl|beat|egg|fork|bowl|both|bowl|fork
right hand lifts fork from beaten egg|lift|fork||bowl|right|bowl|fork
right hand sets fork down while left holds bowl|set down|fork||paper towel|both|bowl|
left hand opens microwave while right holds bowl|open|microwave|||both||bowl
right hand sets egg bowl on microwave turntable|place|bowl||microwave|right||
left hand lifts microwave cover from stove|lift|microwave cover||microwave|left|microwave cover|
right hand positions cover over bowl inside microwave|cover|bowl|microwave cover|microwave|right||
right hand closes microwave door|close|microwave|||right||
right hand starts microwave and waits beside it|press|microwave keypad||microwave|right||
right hand holds microwave handle after stopping heating|hold|microwave|||right||
right hand opens microwave and lifts cover|lift|microwave cover||microwave|right||microwave cover
right hand sets cover down and reaches for fork|set down|microwave cover||fork|right||fork
right hand stirs egg inside microwave with fork|stir|egg|fork|bowl|right||fork
right hand withdraws fork from microwave|withdraw|fork||microwave|right||fork
right hand puts fork down then lifts microwave cover|set down|fork||microwave cover|right||microwave cover
right hand covers bowl and closes microwave|cover|bowl|microwave cover|microwave|right||
right hand restarts microwave and waits|press|microwave keypad||microwave|right||
right hand opens microwave door|open|microwave|||right||
right hand lifts cover from bowl|lift|microwave cover||bowl|right||microwave cover
right hand sets cover down then reaches for bowl|set down|microwave cover||bowl|right|bowl|bowl
both hands lift and inspect the partially cooked egg bowl|lift|bowl|||both|bowl|bowl
both hands return bowl to microwave and replace cover|return|bowl||microwave|both||microwave cover
right hand closes microwave door and presses keypad|press|microwave keypad||microwave|right||
right hand presses microwave controls then waits for egg|press|microwave keypad||microwave|right||
right hand stops microwave and opens door|open|microwave|||right||
right hand lifts microwave cover from bowl|lift|microwave cover||bowl|right||microwave cover
both hands grip bowl after cover is set down|grip|bowl|||both|bowl|bowl
both hands lift bowl out of microwave|lift|bowl||microwave|both|bowl|bowl
both hands carry cooked egg bowl to counter|carry|bowl|||both|bowl|bowl
right hand picks up fork beside the bowl|pick up|fork||bowl|right||fork
right hand loosens egg edges with fork while left steadies bowl|loosen|egg|fork|bowl|both|bowl|fork
right hand lays fork down as left lifts bowl|set down|fork||paper towel|both|bowl|
both hands carry bowl back into microwave|carry|bowl||microwave|both|bowl|bowl
right hand covers bowl in microwave|cover|bowl|microwave cover|microwave|right||microwave cover
right hand closes microwave and presses controls|press|microwave keypad||microwave|right||
right hand starts another microwave heating cycle|press|microwave keypad||microwave|right||
right hand presses microwave keypad then waits|press|microwave keypad||microwave|right||
right hand presses microwave stop button|press|microwave keypad||microwave|right||
left hand pulls microwave door open|open|microwave|||left||
right hand lifts cover from egg bowl|lift|microwave cover||bowl|right||microwave cover
both hands lift bowl from microwave after setting cover down|lift|bowl||microwave|both|bowl|bowl
both hands set cooked egg bowl on counter|set down|bowl|||both||
right hand reaches toward fork beside bread|reach|fork||bread|right||
right hand picks up fork|pick up|fork|||right||fork
right hand runs fork around cooked egg inside bowl|loosen|egg|fork|bowl|right||fork
right hand shifts fork over bread beside bowl|move|fork||bread|right||fork
right hand moves bread slice on paper towel|move|bread||paper towel|right||fork
right hand scoops beneath egg with fork|scoop|egg|fork|bowl|right|bowl|fork
left hand tilts bowl while right loosens egg with fork|tilt|bowl|fork|egg|both|bowl|fork
right hand guides egg from tilted bowl onto bread|transfer|egg|fork|bread|both|bowl|fork
left hand lowers empty bowl beside bread|lower|bowl||paper towel|left|bowl|fork
right hand rests fork in empty bowl|set down|fork||bowl|right|bowl|
right hand picks up second bread slice|pick up|bread||paper towel|right||bread
both hands lay bread over egg and press sandwich|press|bread||sandwich|both||
both hands align the sandwich edges|align|sandwich|||both||
right hand removes eggshell while left steadies sandwich|remove|eggshell||sandwich|both||
both hands fold paper towel beneath sandwich|fold|paper towel||sandwich|both|sandwich|paper towel
both hands center sandwich on folded paper towel|center|sandwich||paper towel|both||
idle (hands withdraw from the completed sandwich)|||||none||'''
groups=[(0,8,'Crack the egg and add water.','The egg is tapped and cracked into a bowl, shell set aside, a little water poured from the cup, and a fork picked up.','Gather the raw egg mixture ready for beating.'),(9,11,'Beat the egg in the bowl.','The fork beats egg until the yellow mixture is blended, then is placed beside the bread.','Prepare a mixed egg that can cook evenly in the microwave.'),(12,17,'Cover the bowl and start microwaving.','The microwave is opened, bowl inserted and covered, then door closed and heating started.','Begin cooking the beaten egg.'),(18,25,'Stir the egg and resume heating.','Heating is stopped, the cover removed and egg stirred with a fork inside the microwave before replacing cover and restarting.','Redistribute the partly heated egg before further cooking.'),(26,32,'Inspect the egg and heat it again.','The cover is removed and bowl lifted briefly to inspect the setting egg, then bowl and cover returned and heating resumed.','Check and continue setting the egg.'),(33,39,'Remove bowl and loosen the partly cooked egg.','The bowl is uncovered and carried to the counter, where a fork loosens the egg around its edges.','Inspect the egg and release its edges before another heating pass.'),(40,49,'Return egg for a final short heating cycle.','The bowl is returned and covered; microwave buttons are pressed, heating briefly runs and the covered bowl is retrieved.','Finish cooking the formed egg layer.'),(50,60,'Loosen and transfer the cooked egg onto bread.','The bowl is set on the counter, a fork runs around and under the egg, and the tilted bowl releases the egg onto a bread slice.','Make the egg filling sit on the sandwich base.'),(61,67,'Close the sandwich and tidy its paper base.','The other bread slice covers the egg, hands align and press the sandwich, shell is cleared and paper towel folded underneath.','Leave a finished egg sandwich on a clean folded paper base.')]
fix={17:dict(boundary_note='Keypad presses occur near 50–54s; most of 54–70s is waiting, before a stop press near 71s.'),25:dict(boundary_note='Keypad interaction near 86–87s precedes waiting through 99s and stop/open preparation at 100s.'),32:dict(boundary_note='Includes initial keypad press near 111s, waiting, then stop/open preparation near 119s.'),45:dict(boundary_note='Keypad press near 145s precedes waiting and another button interaction near 150–151s.'),51:dict(confidence='medium',notes='A preserved 0.1-second reach interval; fork pickup is clearer in the following segment.'),6:dict(confidence='medium',notes='Cup tilts above bowl; liquid quantity is not asserted.')}
write(v,goal,inv,lines,groups,'Visually rewritten from all overview, 1008 dense step frames and native endpoint sheets. Fine boundaries retained including very brief reaches and long mixed press/wait intervals. Only egg and bread are visible sandwich ingredients; no cheese or seasoning added is inferred.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T095917167734Z/manifest.json'))
