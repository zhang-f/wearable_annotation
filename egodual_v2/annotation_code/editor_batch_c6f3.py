from write_editor_batch import *
v='c6f351e626d204f7'
goal=dict(title='Make white-chocolate-dipped pretzels with sprinkles',description='Arrange small pretzels on parchment, microwave white chocolate chips in a mug in repeated short cycles with stirring, then dip the pretzels in the melted coating. Add colored sprinkles, briefly put the parchment of pretzels in the refrigerator, retrieve it and transfer several pretzels to a plate.',final_state='Three decorated white-chocolate pretzels are on the plate, with the remaining decorated pretzels on parchment.',procedure=['Arrange pretzels on parchment.','Heat white chocolate chips in a mug, stirring between microwave cycles.','Stir the softened chocolate until smooth.','Dip each pretzel into chocolate and return it to parchment.','Shake colored sprinkles over the coated pretzels.','Briefly refrigerate and retrieve the decorated pretzels.','Transfer several finished pretzels to a plate.'])
inv=['pretzel','pretzel bowl','parchment','chocolate mug','white chocolate','spoon','microwave door','microwave controls','sprinkles jar','plate','refrigerator door']
lines='''right hand places first pretzel on parchment|place|pretzel||parchment|right||
right hand places second pretzel beside first|place|pretzel||parchment|right||
right hand transfers another pretzel from bowl to parchment|place|pretzel||parchment|right||
right hand adds another pretzel to parchment|place|pretzel||parchment|right||
right hand places fifth pretzel on parchment|place|pretzel||parchment|right||
right hand transfers another pretzel onto parchment|place|pretzel||parchment|right||
right hand arranges last pretzel beside the others|arrange|pretzel||parchment|right||
both hands lift chocolate mug from counter|lift|chocolate mug|||both||chocolate mug
left hand opens microwave while right holds chocolate mug|open|microwave door|||both||chocolate mug
right hand places chocolate mug inside microwave|place|chocolate mug||microwave door|right||
left hand closes microwave door|close|microwave door|||left||
right hand presses microwave controls|press|microwave controls|||right||
right hand presses more microwave buttons then turns aside|press|microwave controls|||right||
left hand touches chocolate bag while right lifts spoon|take|spoon|||both||spoon
left hand picks up sprinkles jar|pick up|sprinkles jar|||left|sprinkles jar|spoon
both hands turn and adjust sprinkles jar|adjust|sprinkles jar|||both||sprinkles jar
idle waiting in front of running microwave|wait||||none||
left hand opens microwave and right removes chocolate mug|remove|chocolate mug||microwave door|both|chocolate mug|spoon
right hand stirs white chocolate chips inside mug|stir|white chocolate|spoon|chocolate mug|right|chocolate mug|spoon
left hand returns chocolate mug to microwave|place|chocolate mug||microwave door|left||spoon
left hand closes microwave while right presses controls|press|microwave controls||microwave door|both||spoon
idle waiting with spoon before opening microwave again|wait||||none||spoon
left hand removes mug while right stirs white chocolate|stir|white chocolate|spoon|chocolate mug|both|chocolate mug|spoon
left hand returns mug and restarts microwave|place|chocolate mug||microwave controls|both||spoon
left hand opens microwave and removes mug|remove|chocolate mug||microwave door|left|chocolate mug|spoon
right hand stirs softened white chocolate in mug|stir|white chocolate|spoon|chocolate mug|right|chocolate mug|spoon
left hand returns mug then closes microwave door|place|chocolate mug||microwave door|left||spoon
idle waiting while chocolate mug heats again|wait||||none||spoon
left hand removes chocolate mug from microwave|remove|chocolate mug||microwave door|left|chocolate mug|spoon
right hand stirs melted chocolate while left carries mug|stir|white chocolate|spoon|chocolate mug|both||
right hand picks up pretzel and lowers it into chocolate|dip|pretzel||chocolate mug|right|chocolate mug|pretzel
right hand turns first pretzel through melted white chocolate|coat|pretzel||white chocolate|right|chocolate mug|pretzel
right hand places coated pretzel onto parchment|place|pretzel||parchment|right|chocolate mug|pretzel
right hand dips and turns second pretzel in chocolate|coat|pretzel||white chocolate|right|chocolate mug|
right hand sets second coated pretzel onto parchment|place|pretzel||parchment|right|chocolate mug|pretzel
right hand dips third pretzel into white chocolate|coat|pretzel||white chocolate|right|chocolate mug|
right hand places third coated pretzel and picks another|place|pretzel||parchment|right|chocolate mug|pretzel
right hand coats fourth pretzel in white chocolate|coat|pretzel||white chocolate|right|chocolate mug|
right hand returns coated pretzel to parchment|place|pretzel||parchment|right|chocolate mug|pretzel
right hand coats fifth pretzel in chocolate|coat|pretzel||white chocolate|right|chocolate mug|
right hand coats another pretzel and lifts it from mug|coat|pretzel||white chocolate|right|chocolate mug|
right hand returns to parchment and takes next pretzel|take|pretzel||parchment|right|chocolate mug|pretzel
right hand turns another pretzel through melted chocolate|coat|pretzel||white chocolate|right|chocolate mug|
right hand places coated pretzel and takes remaining pretzel|take|pretzel||parchment|right|chocolate mug|pretzel
right hand coats last pretzel while left opens sprinkles jar|coat|pretzel||white chocolate|both|sprinkles jar|pretzel
both hands adjust sprinkles jar over parchment|adjust|sprinkles jar|||both||sprinkles jar
right hand shakes colored sprinkles over coated pretzels|shake|sprinkles jar||pretzel|right||sprinkles jar
right hand sets sprinkles jar down and moves plate aside|move|plate||sprinkles jar|right||
both hands lift parchment with decorated pretzels|lift|parchment||pretzel|both|parchment|parchment
left hand opens refrigerator while right supports parchment|open|refrigerator door||parchment|both||parchment
both hands hold parchment beside open refrigerator shelf|hold|parchment||pretzel|both|parchment|parchment
both hands place parchment of pretzels on refrigerator shelf|place|parchment||pretzel|both||
left hand closes refrigerator door|close|refrigerator door|||left||
idle waiting beside closed refrigerator|wait||||none||
left hand pulls refrigerator door open again|open|refrigerator door|||left||
both hands lift parchment of pretzels from refrigerator|lift|parchment||pretzel|both|parchment|parchment
both hands support parchment beside open refrigerator|hold|parchment||pretzel|both|parchment|parchment
both hands carry parchment back and set it on counter|place|parchment||pretzel|both||pretzel
right hand transfers first decorated pretzel onto plate|place|pretzel||plate|right||
right hand picks up next decorated pretzel from parchment|pick up|pretzel||parchment|right||pretzel
right hand places second decorated pretzel on plate|place|pretzel||plate|right||
right hand picks up third decorated pretzel from parchment|pick up|pretzel||parchment|right||pretzel
right hand places third decorated pretzel onto plate|place|pretzel||plate|right||'''
groups=[(0,6,'Arrange pretzels on parchment.','Individual small pretzels are taken from the bowl and spaced on the parchment.','Prepare the pretzels for coating without stacking them.'),(7,16,'Start heating the white chocolate and ready decorations.','The chocolate-chip mug is placed in the microwave, controls pressed, spoon taken and sprinkles jar handled while the mug heats.','Begin melting the coating and bring the spoon and decorations within reach.'),(17,27,'Stir and reheat the white chocolate.','The mug is repeatedly removed, stirred with a spoon, returned and heated in short cycles, with pauses facing the running microwave.','Gradually soften the chocolate chips into a usable coating.'),(28,29,'Remove the mug and finish stirring smooth chocolate.','The mug is carried to the preparation counter while the spoon repeatedly stirs and scrapes the pale melted chocolate.','Finish smoothing the melted coating before dipping.'),(30,44,'Dip the pretzels in white chocolate.','Each pretzel is turned through the chocolate, lifted and returned to parchment. The mug is steadied and the sprinkles jar opened near the last dip.','Coat the pretzels with white chocolate.'),(45,47,'Scatter sprinkles and clear space.','The sprinkles container is adjusted and shaken over the coated pretzels, then put down as the plate is moved aside.','Add colored decorations while leaving the pretzels on parchment.'),(48,57,'Briefly refrigerate and retrieve the pretzels.','The parchment is lifted and placed on a refrigerator shelf. After the door closes and a short pause, it is reopened and the parchment brought back to the counter.','Briefly chill the coated pretzels and return them for serving.'),(58,62,'Transfer decorated pretzels to the plate.','The right hand moves three finished pretzels from the parchment to the two-tone plate.','Plate a small serving of finished pretzels.')]
fix={16:dict(boundary_note='31.58–43.49s begins with jar release and is mostly no interaction, then hand reaches microwave at42s.'),21:dict(boundary_note='56.77–77.08s mostly waiting with spoon; left hand opens door around76s within retained fine.'),23:dict(boundary_note='82.58–101.87s combines mug return, door closure, button press and waiting, ending with door opening.'),27:dict(boundary_note='115.38–135.78s mostly waiting; left hand reaches and opens microwave near135s.'),29:dict(boundary_note='138.27–157.48s includes carrying mug, spoon stirring, mug placement and pretzel pickup near157s.'),40:dict(boundary_note='215.39–220.27s includes returning one coated pretzel, taking another and dipping it; source boundaries preserved.'),44:dict(boundary_note='232.47–246.07s includes final dipping plus mug placement and sprinkles jar pickup/opening around237–241s.'),56:dict(boundary_note='288.8–288.81s is shorter than one15fps frame. Native endpoint repeats288.8s; no separate hand-object event resolvable. Boundary retained.',confidence='low',ambiguous=True),57:dict(boundary_note='288.81–293.86s includes carrying parchment, placing it on counter and picking up first pretzel.')}
write(v,goal,inv,lines,groups,'Viewed all10 overview sheets, all1284 dense frames and all63 native endpoints. Only source fine boundaries retained; coarse groups rebuilt from actual setup, microwave/stir cycles, dipping, sprinkles, refrigerator placement/retrieval and plating. Fine56 lasts0.01s with no separate resolvable event and is flagged low confidence. Predictability pending independent test.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T225030525269Z/manifest.json'))
